# 💼 AI-Powered ATS Resume Tailor & Cover Letter Generator

An intelligent web application engineered to analyze target Job Descriptions, identify technical skill gaps, and dynamically tailor professional resumes and cover letters to pass automated Applicant Tracking Systems (ATS).

## 🚀 Key Features
- **Live Streaming Optimization**: Uses Google Gemini to dynamically align resume terminology to specific target job scopes.
- **Two-Way UI Synchronization**: Fully interactive plain-text canvas allowing manual editing with real-time PDF preview generation.
- **Universal Layout Parser**: A custom Python structure engine that automatically translates plain text into beautifully formatted, single-column, ATS-compliant PDFs.
- **Anti-Hallucination Guardrails**: Rigid system prompt logic ensuring the AI never fabricates historical projects or experience while still closing matching skill gaps.

## 🛠️ Installation & Setup

1. **Clone the repository:**
```bash
   git clone https://github.com/LeoJoychan/ai-resume-tailor.git
   cd ai-resume-tailor
```
2. **Install core dependencies:**
```bash
    pip install streamlit pypdf pdfplumber reportlab google-generativeai
```
3. **Configure Local Secrets:**
```bash
    Create a directory and file at .streamlit/secrets.toml and add your API key:
    GEMINI_API_KEY = "your_actual_gemini_api_key_here"
```
4. **Launch the application workspace:**
```bash
    streamlit run app.py
```
