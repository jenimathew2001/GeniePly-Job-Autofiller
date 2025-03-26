import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from backend.extract_cv_data import extract_text_from_pdf, get_json_resume
import json

from langchain.chat_models import init_chat_model
from backend.extract_cv_data import get_api_key
from backend.schema import autofill_schema

# Initialize Flask app
app = Flask(__name__)

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
    """Handles file upload and extracts structured data."""
    if "file" not in request.files: 
        return jsonify({"error": "No file part"}), 400
    print(request.form)

    file = request.files["file"]
    email = request.form.get("email")

    if not email:
        return jsonify({"error": "User email not provided"}), 400


    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)  # Secure filename
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)  # Save file

        # Extract text from the PDF
        print('IN SERVER FILE PATH',file_path)
        extracted_text = extract_text_from_pdf(file_path)
        print('IN SERVER pdf text',extracted_text)
        if not extracted_text:
            return jsonify({"error": "Failed to extract text"}), 500

        # Process extracted text into structured JSON
        structured_data = get_json_resume(extracted_text, filename=file_path.replace(".pdf", ".json"))
        print('IN SERVER structured data',structured_data)

        # Save structured data to user's JSON file
        user_file_path = os.path.join(USERS_FOLDER, f"{email}.json")
        if os.path.exists(user_file_path):
            with open(user_file_path, "r", encoding="utf-8") as user_file:
                existing_data = json.load(user_file)
        else:
            return jsonify({"error": "User not found. Please create an account first."}), 404

        # Merge new CV data with existing data
        # existing_data.append(structured_data)

        if structured_data:
            # Ensure the structure follows: [ {credentials}, {cv details} ]
            if len(existing_data) == 1:
                # If only credentials exist, add the CV data
                existing_data.append(structured_data)
            elif len(existing_data) == 2:
                # If both entries exist, replace the CV details
                existing_data[1] = structured_data
            else:
                return jsonify({"error": "Invalid user data structure. Please contact support."}), 500
            
            # Save updated data
            with open(user_file_path, 'w') as user_file:
                json.dump(existing_data, user_file, indent=4)

            return jsonify(existing_data[1])
        else:
            return jsonify({"error": "Failed to extract data from CV. Please try again."}), 400


USERS_FOLDER = "users"

@app.route("/check-user", methods=["POST"])
def check_user():
    """Check if the entered email exists as a JSON file in the users folder.
       If found, return the stored password."""
    
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Construct the expected filename
        file_path = os.path.join(USERS_FOLDER, f"{email}.json")

        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                user_data = json.load(file)  # Load the JSON data
                # print(user_data[0])
                
                # Ensure 'password' exists in the JSON structure
                if "password" in user_data[0]:
                    return jsonify({"password": user_data[0]["password"]}), 200
                else:
                    return jsonify({"error": "Password not found in user file"}), 400
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500  

@app.route("/create-user", methods=["POST"])
def create_user():
    """Create a new user if the email doesn't exist."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        if not os.path.exists(USERS_FOLDER):
            os.makedirs(USERS_FOLDER)

        user_file = os.path.join(USERS_FOLDER, f"{email}.json")
        if os.path.exists(user_file):
            return jsonify({"error": "User already exists"}), 400
        
        # Save user data
        user_data = [{"username": email, "password": password}]
        with open(user_file, "w") as file:
            json.dump(user_data, file, indent=4)

        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route("/users/<email>.json", methods=["GET"])
def get_user_profile(email):
    try:
        # Construct file path
        user_file = os.path.join(USERS_FOLDER, f"{email}.json")

        # Check if the file exists
        if not os.path.exists(user_file):
            return jsonify({"error": "Profile not found"}), 404

        # Serve the JSON file directly
        return send_from_directory(USERS_FOLDER, f"{email}.json")

    except Exception as e:
        print(f"Error fetching profile for {email}: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the profile"}), 500


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

