import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from backend.extract_cv_data import extract_text_from_pdf, get_json_resume, get_api_key
import json

import math

from langchain.chat_models import init_chat_model
from backend.schema import autofill_json_schema

from supabase import create_client, Client

# Initialize Flask app
app = Flask(__name__)

# Supabase Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Define upload folder
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file types
ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename):
    """Check if file has a valid extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_cv():
    """Handles file upload and updates structured CV data in Supabase."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    email = request.form.get("email")

    if not email:
        return jsonify({"error": "User email not provided"}), 400

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        extracted_text = extract_text_from_pdf(file)
        if not extracted_text:
            return jsonify({"error": "Failed to extract text"}), 500

        structured_data = get_json_resume(extracted_text)
        if not structured_data:
            return jsonify({"error": "Failed to process CV data"}), 400

        try:
            # Check if user exists
            existing_user = (
                supabase.table("users")
                .select("cv_json")
                .eq("email", email)
                .execute()
            )

            print("🔍 EXISTING USER DATA:", existing_user.data)

            if existing_user.data:  # User exists, update the cv_json
                print("✅ USER EXISTS, UPDATING CV_JSON")

                response = (
                    supabase.table("users")
                    .update({"cv_json":structured_data})  # Ensure proper JSON formatting
                    .eq("email", email)
                    .execute()
                )

                print("🛠 SUPABASE UPDATE RESPONSE:", response)

                if response.data:
                    return jsonify({"message": "CV uploaded successfully", "data": structured_data}), 200
                else:
                    return jsonify({"error": "Failed to update CV data in Supabase"}), 500

            else:
                return jsonify({"error": "User does not exist"}), 404

        except Exception as e:
            print("🚨 ERROR:", str(e))
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid file format"}), 400



@app.route("/check-user", methods=["POST"])
def check_user():
    """Check if the entered email exists in the database.
       If found, return the stored password."""
    
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Query Supabase for the user
        response = supabase.table("users").select("password").eq("email", email).execute()

        if response.data:
            return jsonify({"password": response.data[0]["password"]}), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500  


@app.route("/create-user", methods=["POST"])
def create_user():
    """Create a new user if the email doesn't exist in Supabase."""
    
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        # Check if user already exists
        existing_user = supabase.table("users").select("*").eq("email", email).execute()

        if existing_user.data:
            return jsonify({"error": "User already exists"}), 400

        # Insert new user into Supabase
        response = supabase.table("users").insert({"email": email, "password": password}).execute()

        if response.data:
            return jsonify({"message": "User created successfully"}), 201
        else:
            return jsonify({"error": "Failed to create user"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/users/<email>", methods=["GET"])
def get_user_profile(email):
    """Fetch the user profile from Supabase."""
    
    try:
        print(f"🔍 Checking for user: {email}")  # Debugging

        response = supabase.table("users").select("email, cv_json").eq("email", email).execute()

        print(f"🛠 Supabase Response: {response.data}")  # Debugging


        if response.data:
            return jsonify(response.data[0]), 200
        else:
            return jsonify({"error": "Profile not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_autofill_prompt(form_fields, profile_data):
    experience_count = len(profile_data.get("experience", []))
    education_count = len(profile_data.get("education", []))
    return f"""
You are a smart job application assistant.

Your job is to update ONLY the fields listed in Form Fields below by using data from Resume Data.

Form Fields:
{json.dumps(form_fields, indent=2)}

Instructions:
- Add a "value" for fields with "action": "type" or "select", based on Resume Data.
- For "click" actions like "Add Education" or "Add Experience", add a "times" value.
    - times = Total items in Resume Data section - already present form entries
    - If no entries exist yet in the form, times = Total items in Resume Data section
- DO NOT return the field if no value can be found.

Resume Data:
{json.dumps(profile_data, indent=2)}

🛑 STRICT JSON RULES:
- No markdown formatting like ```json
- No explanation text before or after JSON
- No extra fields that are not listed under Form Fields
- No guessing if Resume Data does not have the correct information
- If the result is too large to return in one response, truncate cleanly at the last full field object. Do NOT return partial or broken JSON.

Return ONLY a strict JSON array of the updated fields.
"""


def clean_output(data):
    for item in data:
        if 'times' in item and item['times'] is None:
            del item['times']
        if 'value' in item and item['value'] is None:
            del item['value']
    return data

def chunk_form_fields(form_fields, chunk_size=20):
    for i in range(0, len(form_fields), chunk_size):
        yield form_fields[i:i + chunk_size]

@app.route("/ai-autofill", methods=["POST"])
def ai_autofill():
    data = request.json
    form_fields = data.get("form_fields", [])
    profile_data = data.get("profile_data", {})

    if not form_fields or not profile_data:
        return jsonify({"error": "Missing form fields or profile data"}), 400

    print("✅ Received Form Fields:", form_fields)
    print("✅ Received Profile Data:", profile_data)

    os.environ["GROQ_API_KEY"] = get_api_key()
    try:
        llm = init_chat_model("llama3-8b-8192", model_provider="groq",temperature=0.3)
        print("✅ LLM Initialized")
        print("📐 Setting Up Structured LLM Output...")
        structured_llm = llm.with_structured_output(autofill_json_schema)
    except Exception as e:
        print(f"❌ LLM Initialization Error: {e}")
        return {"error": "Failed to initialize LLM"}
    
    final_filled_fields = []

    for chunk in chunk_form_fields(form_fields, chunk_size=20):
        print('CHUNK',chunk)
    
        print("📝 Generating Prompt for LLM...")
        prompt = generate_autofill_prompt(chunk, profile_data)
        print("📜 Prompt Preview:\n", prompt[:30], "...")

        try : 
            structured_output = structured_llm.invoke(prompt)
            structured_output = clean_output(structured_output)
            print('STRUCTURED OUTPUT RECEIVED',structured_output)
            final_filled_fields.extend(structured_output)
            print('FINAL LIST COMBINED OUTPUTS',final_filled_fields)
        except Exception as e:
            print("Failed to invoke prompt",e)
            return {"error": "Failed to invoke prompt"}

    if not isinstance(final_filled_fields, list):
        print("Invalid JSON structure received from LLM",final_filled_fields)
        raise ValueError("Invalid JSON structure received from LLM")

    print("✅ Structured Output Received",final_filled_fields)

    return jsonify(final_filled_fields)


if __name__ == "__main__":
    if not os.path.exists(USERS_FOLDER):
        os.makedirs(USERS_FOLDER)
    app.run(debug=True)