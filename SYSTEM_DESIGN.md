# System Design Documentation: AI Resume Tailor Engine

## 1. System Architecture & Data Flow
The application follows a decoupled three-tier workflow consisting of an Interactive Presentation Layer, a Core Orchestration Engine, and a Structured PDF Generation Pipeline.

1. **Presentation Layer (Streamlit)**: Captures unstructured text fields (Job Descriptions) and parses uploaded binary streams (User Resumes). It maintains strict state continuity by utilizing dynamic session binding keys (`st.session_state`), bypassing Streamlit's native page refresh performance penalties during user manual overrides.
2. **AI Orchestration Layer (Gemini API)**: Intercepts user details and executes a structured multi-factor Master Prompt template. It utilizes exact block tag structures (`[TAILORED_RESUME]`, `[COVER_LETTER]`) to slice the response chunks seamlessly, preventing text-parsing index crashes during content extraction.
3. **PDF Generation Pipeline (ReportLab)**: Uses a custom case-insensitive lexical scanner to parse content streams. It standardizes heading layouts independently of incoming casing variants and builds custom multi-column tabular frames for right-aligned dates.

## 2. Prompt Engineering & Anti-Hallucination Guardrails
To enforce total historical document accuracy, the hidden prompt tier uses explicit functional constraints:
- **Zero Project Fabrication**: A hard system restriction bans the LLM from inventing fake projects or certificates. New technical skills can only be added directly into the Technical Skills section or professional summary.
- **Deterministic Structural Enclosures**: Forcing the AI model to wrap blocks inside structured tags guarantees that the front-end string manipulation logic cleanly splits fields every single time, making the runtime environment error-proof.

## 3. Engineering Trade-offs: ATS Parsability vs. Graphic Design
A core design trade-off was prioritizing a clean, single-column linear text layout over visually elaborate multi-column templates:
- **The Problem with Graphic Layouts**: Side-by-side columns and non-standard visual elements frequently fail parsing stages in real-world ATS software by corrupting natural reading paths and causing encoding extraction errors.
- **The Solution**: Implementing a standard, clean single-column structure with distinct divider bars ensures 100% readable text extractions for digital sorting pipelines, while using premium, sharp typography styles for human hiring managers.