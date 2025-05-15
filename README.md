# 🧞 GeniePly - Smart Job Form Autofiller

GeniePly is a Chrome extension + backend service that **automatically fills out job application forms** using your resume (CV). It blends traditional data matching with advanced AI to reduce manual typing during job applications.

### 🌟 Features

✅ Upload your CV (PDF) once  
✅ Structured profile generated automatically  
✅ Autofills job application forms on external websites  
✅ Supports repeating sections (Education, Experience)  
✅ Hybrid logic: rule-based + LLM for intelligent matching  
✅ Works on most job portals

---

## 🔧 How It Works

1. **Upload CV**  
   You upload your resume once. It's parsed into structured JSON using LLMs (e.g., LLaMA 3 via Groq).

2. **Field Extraction (in the tab)**  
   GeniePly scans the web form on the current tab and extracts:
   - All inputs, textareas, selects, buttons
   - Labels and sections using smart DOM traversal

3. **Field Matching**  
   - Direct matches: e.g., `first name`, `email`, `phone`, `degree`
   - Repeating sections like Education/Experience → clicks "Add" buttons if needed
   - Unknown fields → sent to AI

4. **AI-assisted Autofill**  
   If any field isn't matched directly, GeniePly sends the unknown fields + user profile to the backend. The AI model:
   - Analyzes what can be safely filled
   - Follows strict instructions to avoid guessing sensitive info
   - Returns only clean, structured JSON steps

5. **Filling the Form**  
   GeniePly types or selects the right values, triggers events (`input`, `change`), and even clicks buttons if needed.

---

## 🧠 Tech Stack

- **Frontend**: Chrome Extension (`popup.js`)
- **Backend**: Flask + Supabase (`server.py`,`extract_cv_data.py`)
- **LLM Integration**: Groq + LLaMA3

---

## 🚀 Getting Started

1. Clone the repo:  
   ```bash
   git clone https://github.com/jenimathew2001/GeniePly-Job-Autofiller
   cd GeniePly-Job-Autofiller
2. Load the Chrome Extension:

🙋‍♀️ Author
Built by @jenimathew2001

📸 Demo
