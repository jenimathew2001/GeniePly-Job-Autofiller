import pdfplumber
import json
import os
from langchain.chat_models import init_chat_model
from backend.schema import json_schema
# from schema import json_schema
def get_api_key(file_path="backend/groq_api_key.txt"):
# def get_api_key(file_path="groq_api_key.txt"):
    """Reads and validates API key from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            api_key = f.read().strip()
            if not api_key:
                raise ValueError("API key file is empty!")
            return api_key
    except FileNotFoundError:
        print("API key file not found!")
        return None
    except ValueError as e:
        print(f"API Key Error: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""



def generate_prompt(text):
    """Creates a structured prompt for LLM with strict schema adherence."""
    return f"""
    Extract structured information from the following resume.
    
    **IMPORTANT INSTRUCTIONS:**  
    - **Use ONLY the provided field names** from the schema below.  
    - **DO NOT add extra fields** beyond those listed in the schema.  
    - If any field is missing, **use "N/A"** instead of leaving it blank.  
    - **Ignore sections that do not match the schema.**  
    - Extract responsibilities as **bullet points** (list format).  
    - Keep descriptions concise (max **100 words per section**).  
    - Ensure output is **strictly valid JSON format**—NO extra text, comments, or explanations.  

    **Schema (Use these exact field names):**  
    ```json
    {json.dumps(json_schema, indent=4)}
    ```

    **Resume Content:**  
    {text}
    """

def save_json(data, filename="structured_resume.json"):
    """Saves structured output to JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"✅ Saved structured resume to {filename}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

def get_json_resume(cv_text):
    """Processes CV text and returns structured JSON output."""
    print("🔑 Fetching API Key...")
    # api_key = get_api_key()

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return {"error": "Missing API Key"}
    
    # print(f"📝 API Key Retrieved: {api_key if api_key else '❌ MISSING!'}")

    # os.environ["GROQ_API_KEY"] = api_key

    print("🤖 Initializing LLM Model...")
    try : 
        llm = init_chat_model("llama3-8b-8192", model_provider="groq")
        print(f"✅ LLM Model Initialized: {llm}")

        print("📐 Setting Up Structured LLM Output...")
        structured_llm = llm.with_structured_output(json_schema)
    except Exception as e:
        print(f"❌ LLM Initialization Error: {e}")
        return {"error": "Failed to initialize LLM"}

    print("📝 Generating Prompt for LLM...")
    prompt = generate_prompt(cv_text)
    print(f"📜 Prompt Preview:\n{prompt[:300]}...")
    
    try:
        print("🚀 Sending Request to LLM...")
        structured_output = structured_llm.invoke(prompt)
        print(f" STRUCTURED OUTPUT:\n{structured_output}")

        # Validate response format
        if not isinstance(structured_output, dict):
            raise ValueError("Invalid JSON structure received from LLM")
        
        print(f"✅ LLM Response Received:\n{structured_output}")
        
        # print(f"💾 Saving JSON Output as {filename}...")
        # save_json(structured_output,filename)
        # print(f"✅ JSON Saved Successfully: {filename}")
        return structured_output
    except Exception as e:
        print(f"Failed to get structured JSON: {e}")



# Example Usage
# cv_text = extract_text_from_pdf("uploads/arun.pdf")
# if cv_text:
#     get_json_resume(cv_text)
