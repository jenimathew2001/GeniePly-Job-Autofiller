import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from backend.extract_cv_data import extract_text_from_pdf, get_json_resume, get_api_key
import json

from langchain.chat_models import init_chat_model
from backend.schema import autofill_schema, autofill_agent_schema

from supabase import create_client, Client

# Initialize Flask app
app = Flask(__name__)

# Supabase Configuration
SUPABASE_URL = "https://rhszylxaumugoiloyxgj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoc3p5bHhhdW11Z29pbG95eGdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMwMTMwMzAsImV4cCI6MjA1ODU4OTAzMH0.Zf0VHHkvUjfAuuVU3pPzPgodqFsopk-STRyI9uVp40E"  # Replace with your secure key
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
        llm = init_chat_model("llama3-8b-8192", model_provider="groq")
        print("✅ LLM Initialized")

        prompt = f"""
You are a smart job application AI assistant.

Your task is to update ONLY the following fields listed under "Form Fields" below.

### Form Fields:
{json.dumps(form_fields, indent=2)}

Each form field must be rewritten following these rules:
- `action`: one of "click", "type", "select", or "check"
- `selector`: use a valid CSS selector (preferably field's "id", "name" or class or based on "label")
- `value`: required only for "type" and "select" actions (must be extracted from the Resume Data)
- `times`: optional, only if "click" action needs to be repeated (e.g., clicking an "Add Education" button multiple times)

### Special Rule for "Add" Buttons:
- If there is an "Add" button (example: to add Education, Experience, Skills, etc.), you MUST click it multiple times.
- The number of clicks should be (Total number of entries in Resume Data).
- Example: If there are 3 Experiences in resume, and the form already shows 1 entry, you need to click "Add Experience" **2 times** (`times: 2`).

You MUST carefully go through the Resume Data and fill appropriate values.

### Resume Data:
{json.dumps(profile_data, indent=2)}

---
Return ONLY a strict JSON array. 
No extra text, no explanation, no comments outside the array.

Example 1:
If a field from Form Fields looks like:
{{
    "fieldType": "text",
    "id": "address--city",
    "label": "City or Town",
    "name": "city",
    "type": "input"
}}

You should update it like:
{{
    "action": "type",
    "selector": "#address--city",
    "value": "London"
}}

Example 2:
Final JSON array must look like:
[
  {{
    "action": "click",
    "selector": "button.add-education",
    "times": 3
  }},
  {{
    "action": "type",
    "selector": "input[name='institution']",
    "value": "IIT Delhi"
  }}
]

---

🛑 STRICT JSON RULES:
- No markdown formatting like ```json
- No explanation text before or after JSON
- No extra fields that are not listed under Form Fields
- No guessing if Resume Data does not have the correct information

Remember if n number of fields are being given to you I want only those updated n in the response!
and
ONLY return the JSON array as final output.
"""


        # response = llm.invoke(prompt)

        ai_message = llm.invoke(prompt)
        text_output = ai_message.content if hasattr(ai_message, 'content') else ai_message

        try:
            import re

            # Extract the JSON array from the response text
            match = re.search(r'\[\s*{.*}\s*]', text_output, re.DOTALL)
            if not match:
                return jsonify({"error": "Failed to locate JSON array in response", "raw": text_output}), 500

            json_text = match.group(0)
            response_json = json.loads(json_text)


            # response_json = json.loads(text_output)
        except Exception as e:
            print("❌ Failed to parse AI response:", text_output)
            return jsonify({"error": "Failed to parse LLM output", "details": str(e)}), 500



        # if isinstance(response, str):
        #     try:
        #         response = json.loads(response)
        #     except Exception as e:
        #         return jsonify({"error": "Invalid JSON from LLM", "details": str(e)}), 500

        # return jsonify(response_json)
        return jsonify({"form_fields_filled": response_json})


    except Exception as e:
        print(f"❌ AI Processing Failed: {e}")
        return jsonify({"error": "AI Processing Failed", "details": str(e)}), 500




if __name__ == "__main__":
    if not os.path.exists(USERS_FOLDER):
        os.makedirs(USERS_FOLDER)
    app.run(debug=True)
