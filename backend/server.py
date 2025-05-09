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


def generate_autofill_prompt(form_fields, profile_data):
    experience_count = len(profile_data.get("experience", []))
    education_count = len(profile_data.get("education", []))
    return f"""
You are a smart job application AI assistant.

Your task is to update ONLY the following fields listed under "Form Fields" below.

### Form Fields:
{json.dumps(form_fields, indent=2)}

In each form field you must add the following:
- `value`: required only for "type" and "select" actions (must be extracted from the Resume Data)
- `times`: optional, only if "click" action needs to be repeated (e.g., clicking an "Add Education" button multiple times)

### Special Rule for "Add" Buttons:
- If there is an "Add" button (example: to add Education, Experience, Skills, etc.), you MUST click it multiple times.
- The number of clicks should be (Total number of entries in Resume Data).
  - For Experience: {experience_count} times
  - For Education: {education_count} times
  - (Assuming 0 field already exists on the form)

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
    "label": "City or Town",
    "action": "type",
    "selector": "#address--city",
    "sectionLabel" : "Address", 
    "sectionSelector" : "#Address-section"
}}

You should update it like:
{{
    "fieldType": "text",
    "label": "City or Town",
    "action": "type",
    "selector": "#address--city",
    "sectionLabel" : "Address", 
    "sectionSelector" : "#Address-section",
    "value":"London"
}}

Example 2:
If a field from Form Fields looks like:
{{
    "fieldType": "submit",
    "label": "Add",
    "action": "click",
    "selector": ".css-r6gqv6",
    "sectionLabel" : "Education", 
    "sectionSelector" : "#Education-section"
}}

You should update it like({experience_count} experience to be filled and there is 1 existing fill, so {experience_count-1} times click add button):
{{
    "fieldType": "submit",
    "label": "Add",
    "action": "click",
    "selector": ".css-r6gqv6",
    "sectionLabel" : "Education", 
    "sectionSelector" : "#Education-section",
    "times":{experience_count-1}
}}

Example 3:
Final JSON array must look like:
[
  {{
    "fieldType": "text",
    "label": "LinkedIn",
    "action": "type",
    "selector": "#socialNetworkAccounts--linkedInAccount",
    "sectionLabel" : "Social Network URLs", 
    "sectionSelector" : "#Social-Network-URLs-section",
    "value":"https://www.linkedin.com/in/jeni-mathew-346253209/"
  }},
  {{
    "fieldType": "submit",
    "label": "Add",
    "action": "click",
    "selector": ".css-r6gqv6",
    "sectionLabel" : "..sectionLabel", 
    "sectionSelector" : "..sectionSelector",
    "times":{experience_count}
  }}
]

---

🛑 STRICT JSON RULES:
- No markdown formatting like ```json
- No explanation text before or after JSON
- No extra fields that are not listed under Form Fields
- No guessing if Resume Data does not have the correct information

Make sure to return all the fields that were given to you by adding value or times
And don't do anything with other properties like selectors,labels etc. Return them as they are , all you are allowewd to do is add value and times
and
ONLY return the JSON array as final output.
"""


def clean_output(data):
    for item in data:
        if 'times' in item and item['times'] is None:
            del item['times']
        if 'value' in item and item['value'] is None:
            del item['value']
    return data


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
        llm = init_chat_model("llama3-8b-8192", model_provider="groq",temperature=0.0)
        print("✅ LLM Initialized")
        print("📐 Setting Up Structured LLM Output...")
        structured_llm = llm.with_structured_output(autofill_json_schema)
    except Exception as e:
        print(f"❌ LLM Initialization Error: {e}")
        return {"error": "Failed to initialize LLM"}
    
    print("📝 Generating Prompt for LLM...")
    
    prompt = generate_autofill_prompt(form_fields, profile_data)
    print("📜 Prompt Preview:\n", prompt[:30], "...")

    try : 
        structured_output = structured_llm.invoke(prompt)
        structured_output = clean_output(structured_output)
        print(structured_output)
    except Exception as e:
        print("Failed to invoke prompt",e)
        return {"error": "Failed to invoke prompt"}

    if not isinstance(structured_output['fields'], list):
        print("Invalid JSON structure received from LLM",structured_output)
        raise ValueError("Invalid JSON structure received from LLM")

    print("✅ Structured Output Received",structured_output)

    return jsonify(structured_output)



# def estimate_tokens(text_or_dict):
#     """Estimate token count using a basic heuristic (~4 chars/token)."""
#     if isinstance(text_or_dict, dict):
#         text_or_dict = json.dumps(text_or_dict)
#     return len(str(text_or_dict)) // 4  # rough estimate

# def chunk_form_fields(form_fields, profile_data, max_tokens=7000):
#     profile_tokens = estimate_tokens(profile_data)
#     instruction_tokens = 4000  # fixed rough estimate for the static instructions
#     available_tokens = max_tokens - profile_tokens - instruction_tokens

#     chunks = []
#     current_chunk = []
#     current_tokens = 0

#     for field in form_fields:
#         field_tokens = estimate_tokens(field)
#         if current_tokens + field_tokens > available_tokens and current_chunk:
#             chunks.append(current_chunk)
#             current_chunk = []
#             current_tokens = 0
#         current_chunk.append(field)
#         current_tokens += field_tokens

#     if current_chunk:
#         chunks.append(current_chunk)

#     return chunks


# @app.route("/ai-autofill", methods=["POST"])
# def ai_autofill():
#     data = request.json
#     form_fields = data.get("form_fields", [])
#     profile_data = data.get("profile_data", {})

#     if not form_fields or not profile_data:
#         return jsonify({"error": "Missing form fields or profile data"}), 400

#     print("✅ Received Form Fields:", form_fields)
#     print("✅ Received Profile Data:", profile_data)

#     os.environ["GROQ_API_KEY"] = get_api_key()
#     try:
#         llm = init_chat_model("llama3-8b-8192", model_provider="groq")
#         print("✅ LLM Initialized")
#         structured_llm = llm.with_structured_output(autofill_json_schema)
#     except Exception as e:
#         print(f"❌ LLM Initialization Error: {e}")
#         return jsonify({"error": "Failed to initialize LLM"})

#     # Chunk the fields to avoid context length issues
#     try:
#         field_chunks = chunk_form_fields(form_fields, profile_data)
#         all_results = []

#         for idx, chunk in enumerate(field_chunks):
#             print(f"🚧 Processing chunk {idx+1}/{len(field_chunks)}")
#             prompt = generate_autofill_prompt(chunk, profile_data)
#             chunk_output = structured_llm.invoke(prompt)
#             cleaned_output = clean_output(chunk_output)
#             all_results.extend(cleaned_output.get("fields", []))

#         if len(all_results) != len(form_fields):
#             print("⚠️ Mismatch in field count:", len(all_results), "!=", len(form_fields))

#         return jsonify({ "fields": all_results })

#     except Exception as e:
#         print("❌ Failed during chunked LLM calls:", e)
#         return jsonify({"error": "Failed to invoke prompt"})


if __name__ == "__main__":
    if not os.path.exists(USERS_FOLDER):
        os.makedirs(USERS_FOLDER)
    app.run(debug=True)