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

| Layer       | Technology                                |
|-------------|--------------------------------------------|
| Frontend    | Chrome Extension (`popup.js`, `popup.html`, `styles.css`) |
| Backend     | Flask (`server.py`), Supabase for DB/storage |
| CV Parsing  | `extract_cv_data.py` using pdfplumber + Groq LLaMA3 |
| AI Model    | Groq API (LLaMA 3) |
| Database    | Supabase |

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/jenimathew2001/GeniePly-Job-Autofiller
cd GeniePly-Job-Autofiller
```

### 2. Backend Setup (Flask API)

#### ✅ For Local Development

1. **Create a `.env` file** in the root directory with the following content:

    ```ini
    GROQ_API_KEY=your-groq-api-key
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_KEY=your-supabase-service-role-key
    ```

    > ⚠️ **Never commit your `.env` or API keys to GitHub.**

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Start the Flask server:**

    ```bash
    python server.py
    ```

#### 🚀 Deploy to Render

1. **Push this repo to your GitHub account.**
2. Go to [https://render.com](https://render.com)
3. Create a new Web Service and connect your repo.
4. Set the following commands:
    - Build Command: (Leave empty or set as needed)
    - **Start Command:**
      ```bash
      gunicorn backend.server:app
      ```
5. **Add the Environment Variables in Render**

### 3. Frontend Setup (Chrome Extension)

1. Open Google Chrome
2. Go to: `chrome://extensions`
3. Enable Developer Mode (top-right)
4. Click Load unpacked
5. Select the `chrome-extension/` folder containing:
    - `manifest.json`
    - `popup.html`
    - `popup.js`
    - `styles.css`

### 4. Usage

1. Open the extension popup.
2. Sign up or log in.
3. Upload your CV (**PDF**).
4. Visit any job application form.
5. Click **Autofill** to automatically populate the fields.

---

## 🙋‍♀️ Author
Built by @jenimathew2001

## 📸 Demo
