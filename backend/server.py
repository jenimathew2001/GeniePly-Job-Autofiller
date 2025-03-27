import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from backend.extract_cv_data import extract_text_from_pdf, get_json_resume, get_api_key
import json

from langchain.chat_models import init_chat_model
from backend.schema import autofill_schema

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
            print("EXISTING USERRR", existing_user )
            print("EXISTING USERRR existing_user.data", existing_user.data )

            if existing_user.data:
                # Update existing record
                response = (
                    supabase.table("users")
                    .update({"cv_json": structured_data})
                    .eq("email", email)
                    .execute()
                )
            else:
                # Insert new record if user does not exist
                response = (
                    supabase.table("users")
                    .insert({"email": email, "cv_json": structured_data})
                    .execute()
                )

            # Debugging logs
            print("Supabase Response:", response)

            if response.data:
                return jsonify({"message": "CV uploaded successfully", "data": structured_data}), 201
            else:
                return jsonify({"error": "Failed to store data in Supabase"}), 500

        except Exception as e:
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
    """Matches form fields with user profile using Llama3 AI"""
    data = request.json
    form_fields = data.get("form_fields", [])
    profile_data = data.get("profile_data", {})

    if not form_fields or not profile_data:
        return jsonify({"error": "Missing form fields or profile data"}), 400

    print("✅ Received Form Fields:", form_fields)
    print("✅ Received Profile Data:", profile_data)

    # Initialize Llama3 Model
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "Missing API Key"}), 500

    os.environ["GROQ_API_KEY"] = api_key

    try:
        llm = init_chat_model("llama3-8b-8192", model_provider="groq")
        structured_llm = llm.with_structured_output(autofill_schema)
        print("✅ LLM Model Initialized Successfully")

    except Exception as e:
        print(f"🚨 ERROR: LLM Initialization Failed: {e}")
        return jsonify({"error": "LLM Initialization Failed", "details": str(e)}), 500

    # Generate LLM prompt
    prompt = f"""
    Match the following form fields with the correct values from the user profile.

    **Form Fields:** {form_fields}

    **User Profile Data:** {profile_data}

    **Output format:** (strictly JSON, no explanations)
    {autofill_schema}
    """

    

    # Invoke AI model
    try:
        structured_output = structured_llm.invoke(prompt)
        
        # Validate JSON response
        if not isinstance(structured_output, dict):
            return jsonify({"error": "AI returned invalid JSON"}), 500

        print(f"✅ LLM Response:\n{structured_output}")
        return jsonify(structured_output)

    except Exception as e:
        print(f"🚨 ERROR: AI Matching Failed: {e}")
        return jsonify({"error": "AI Processing Failed", "details": str(e)}), 500

if __name__ == "__main__":
    if not os.path.exists(USERS_FOLDER):
        os.makedirs(USERS_FOLDER)
    app.run(debug=True)

