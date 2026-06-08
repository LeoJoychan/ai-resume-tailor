import streamlit as st
import pypdf
import google.generativeai as genai
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import pdfplumber

def extract_clean_text_from_pdf(uploaded_file):
    text_content = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(layout=False) # Flattens tables so words aren't skipped
            if page_text:
                text_content += page_text + "\n"
                
    # Clean up extra spaces, weird tabs, and hidden characters that break keyword matching
    cleaned_lines = []
    for line in text_content.split("\n"):
        cleaned_line = " ".join(line.split()) # Collapses multiple spaces into one
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
            
    return "\n".join(cleaned_lines)

import re
from reportlab.platypus import Table, TableStyle

def make_links_clickable(text):
    """
    Scans text for domain links (github.com, linkedin.com, etc.) and turns them 
    into clickable HTML anchor links for the PDF layout.
    """
    # Matches common patterns like github.com/... or linkedin.com/... with or without http/https
    link_pattern = r'((?:https?://)?(?:www\.)?(?:github\.com|linkedin\.com|leetcode\.com|hackerrank\.com)[^\s|]+)'
    
    def replace_with_link(match):
        url = match.group(1)
        # Ensure the URL has a proper scheme for the PDF reader to open it
        full_url = url if url.startswith("http") else f"https://{url}"
        # Return cleanly styled blue clickable text
        return f'<a href="{full_url}" color="#0F4C81"><u>{url}</u></a>'
        
    return re.sub(link_pattern, replace_with_link, text)

def convert_text_to_pdf(text_content, template_style="Jake's Resume Format"):
    buffer = io.BytesIO()
    # Fixed compact margins (0.5 inch / 36 points) for all core formats
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=36, 
        leftMargin=36, 
        topMargin=36, 
        bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()
    body_color = colors.HexColor("#000000")

    # --- CONFIGURING CORE FORMAT ENGINE VARS ---
    if "Deedy" in template_style:
        font_family = "Helvetica"
        font_family_bold = "Helvetica-Bold"
        accent_color = colors.HexColor("#333333")
    elif "Awesome" in template_style:
        font_family = "Helvetica"
        font_family_bold = "Helvetica-Bold"
        accent_color = colors.HexColor("#0F4C81") 
    else: # Default: Jake's Resume Format
        font_family = "Times-Roman"
        font_family_bold = "Times-Bold"
        accent_color = colors.HexColor("#000000")

    # Typography Styling Setup
    style_name = ParagraphStyle(
        'FormatName',
        fontName=font_family_bold,
        fontSize=19 if "Awesome" in template_style else 17,
        leading=23,
        alignment=0 if "Deedy" in template_style else 1, 
        textColor=accent_color,
        spaceAfter=2
    )
    
    style_contact = ParagraphStyle(
        'FormatContact',
        fontName=font_family,
        fontSize=9.5,
        leading=13,
        alignment=0 if "Deedy" in template_style else 1,
        textColor=colors.HexColor("#555555") if "Awesome" in template_style else body_color,
        spaceAfter=10
    )

    style_body = ParagraphStyle(
        'FormatBody',
        parent=styles['Normal'],
        fontName=font_family,
        fontSize=9.5 if "Deedy" in template_style else 10,
        leading=13.5 if "Deedy" in template_style else 14,
        textColor=body_color,
        spaceAfter=2
    )
    
    style_body_bold = ParagraphStyle(
        'FormatBodyBold',
        parent=style_body,
        fontName=font_family_bold
    )

    style_header = ParagraphStyle(
        'FormatHeader',
        parent=style_body,
        fontName=font_family_bold,
        fontSize=11.5,
        leading=15,
        textColor=accent_color,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    lines = text_content.split('\n')
    is_first_line = True
    is_header_rendered = False
    
    # Track how many text lines we have processed to identify if we are at the top of the document
    line_count = 0

    # Process layout text streams
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        line_count += 1
            
        # 1. Profile Identity Contact Headers (Only center if it's the very top of a Resume)
        if is_first_line:
            # If it looks like a date (Cover letter start), don't treat it as a centered resume name header
            if any(month in cleaned_line for month in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]):
                story.append(Paragraph(cleaned_line, style_body))
                is_header_rendered = True # Prevents downstream centering inside cover letters
            else:
                story.append(Paragraph(cleaned_line, style_name))
            is_first_line = False
            continue
            
        # Only center an info line if we are within the first 4 lines of the page (Resume Header territory)
        if not is_header_rendered and line_count <= 4 and ("@" in cleaned_line or "|" in cleaned_line):
            clickable_contact_info = make_links_clickable(cleaned_line)
            story.append(Paragraph(clickable_contact_info, style_contact))
            is_header_rendered = True
            continue

        # 2. Main Section Header Mappings
        if cleaned_line.isupper() and len(cleaned_line) < 30 and not any(x in cleaned_line for x in ["@", "|", ".COM"]):
            story.append(Spacer(1, 2))
            story.append(Paragraph(cleaned_line, style_header))
            thickness = 1.25 if "Awesome" in template_style else 0.75
            story.append(HRFlowable(width="100%", thickness=thickness, color=accent_color, spaceBefore=1, spaceAfter=4))
            
        # 3. Dynamic Section Header Mapping (100% Universal & Case-Insensitive)
        # Convert the line to uppercase and strip formatting characters to perform a perfect check
        normalized_clean = cleaned_line.strip().rstrip(":").upper()
        
        # A comprehensive list of standard section names used across all global resumes
        standard_headers = [
            "ABOUT", "SUMMARY", "PROFESSIONAL SUMMARY", "OBJECTIVE",
            "EDUCATION", "ACADEMIC BACKGROUND",
            "EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT HISTORY", "PROFESSIONAL EXPERIENCE",
            "PROJECTS", "KEY PROJECTS", "ACADEMIC PROJECTS", "PERSONAL PROJECTS",
            "CAMPUS LEADERSHIP", "LEADERSHIP", "EXTRA-CURRICULAR ACTIVITIES", "COORDINATION",
            "TECHNICAL SKILLS", "SKILLS", "CORE COMPETENCIES", "EXPERTISE",
            "CERTIFICATES", "CERTIFICATIONS", "AWARDS", "ACHIEVEMENTS",
            "HOBBIES & INTERESTS", "HOBBIES AND INTERESTS", "INTERESTS", "FITNESS & LEISURE"
        ]
        
        # Check conditions: It's a short line, matches our list, and doesn't contain contact/bullet markers
        is_standalone_title = len(cleaned_line.strip()) < 35
        has_no_separators = not any(symbol in cleaned_line for symbol in ["@", "|", "•", "-", "*", ".COM"])
        
        if is_standalone_title and has_no_separators and (normalized_clean in standard_headers):
            story.append(Spacer(1, 4))
            # FORCE the title to be printed in pure, beautiful ALL CAPS on the PDF layout
            story.append(Paragraph(normalized_clean, style_header))
            thickness = 1.25 if "Awesome" in template_style else 0.75
            story.append(HRFlowable(width="100%", thickness=thickness, color=accent_color, spaceBefore=1, spaceAfter=4))
            continue
                
        # 4. Standard Bullet Strings
        elif cleaned_line.startswith("-") or cleaned_line.startswith("•"):
            bullet_text = cleaned_line[1:].strip()
            story.append(Paragraph(f"&bull; {bullet_text}", style_body))
            
        # 5. Fallback Base Strings (Keeps link clickable but left-aligned)
        else:
            if "@" in cleaned_line or "linkedin.com" in cleaned_line or "github.com" in cleaned_line:
                clickable_line = make_links_clickable(cleaned_line)
                story.append(Paragraph(clickable_line, style_body))
            else:
                story.append(Paragraph(cleaned_line, style_body))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Configure page layout
st.set_page_config(page_title="AI Resume Tailor", page_icon="💼", layout="wide")

# --- HOME PANEL INTERFACE ---
st.title("💼 AI-Powered Resume Tailor & Target Optimization Engine")
st.write("Optimize your resume against any job description using real-time LLM tracking analysis.")

st.markdown("---")
st.header("1. Provide Target Job Context Data")

job_desc = st.text_area(
    "Paste the target Job Description (JD) here:", 
    height=150, 
    placeholder="Paste the full job requirements, responsibilities, and qualifications..."
)

uploaded_file = st.file_uploader(
    "📤 Upload your current Resume (PDF format):", 
    type=["pdf"],
    help="The system will extract text from this PDF file automatically."
)

if uploaded_file is not None:
    st.success(f"✓ '{uploaded_file.name}' loaded successfully into context memory.")

generate_cover_letter = st.toggle("📄 Generate a matching Cover Letter for this role", value=False)

st.markdown("---")

# Reset active analytical memory if inputs change
if "last_job_desc" not in st.session_state: st.session_state.last_job_desc = ""

if job_desc != st.session_state.last_job_desc:
    st.session_state.ai_processed = False
    st.session_state.last_job_desc = job_desc

# --- SINGLE BUTTON TRIGGER ---
if st.button("🚀 Run Live AI Analysis", type="primary", use_container_width=True):
    if not job_desc.strip():
        st.warning("Please paste a Job Description to compare against.")
    elif uploaded_file is None:
        st.warning("Please upload a base Resume PDF file first.")
    else:
        resume_content = ""
        try:
            pdf_reader = pypdf.PdfReader(uploaded_file)
            parsed_text = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text: parsed_text.append(text)
            resume_content = "\n".join(parsed_text)
        except Exception as e:
            st.error(f"Failed to read PDF file layout: {e}")
            
        if resume_content.strip():
            # Initialize Gemini Model
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel(
                    "gemini-2.5-flash",
                    generation_config={"temperature": 0.0} 
                )
            except Exception as e:
                st.error(f"API Authentication failed: {e}")
                st.stop()

            with st.spinner("Establishing live stream connection with Gemini Engine..."):
                import datetime
                current_date_str = datetime.date.today().strftime("%B %d, %Y")

                # --- DYNAMIC MULTI-FACTOR MASTER PROMPT ---
                # Build the cover letter section instructions dynamically
                if generate_cover_letter:
                    cover_letter_instruction = f"""
[COVER_LETTER]
(Write the complete formal tailored cover letter using {current_date_str})
[/COVER_LETTER]
"""
                else:
                    cover_letter_instruction = """
[COVER_LETTER]
NOT_REQUESTED
[/COVER_LETTER]
"""

                master_prompt = f"""
                You are an expert recruiter and strict ATS parser. Analyze the Resume against the Job Description.
                Perform your breakdown, optimize the resume, and generate a cover letter if requested.

                CRITICAL RESUME ALTERATION RULE:
                - You may integrate missing keywords into the existing SUMMARY/ABOUT or TECHNICAL SKILLS sections if appropriate.
                - STRICTLY FORBIDDEN: Do NOT invent, hallucinate, or add entire new projects, job experiences, or certificates that do not exist in the ORIGINAL RESUME. Keep the project list exactly as provided.

                CRITICAL ATS FRIENDLINESS RULE:
                Analyze the ORIGINAL RESUME text for structural compliance. Is it missing essential contact info? Does it use un-parsable characters or completely messy formatting layout rules? 
                Output exactly "YES" if it is cleanly scannable by a basic machine, or "NO" if it fails basic readability metrics.

                CRITICAL DYNAMIC WEIGHTING RULE:
                1. Read the JOB DESCRIPTION carefully. Does it explicitly mention an experience level requirement or a specific number of years/internship background? If yes, evaluate how well the candidate aligns and provide an [EXPERIENCE_SCORE] between 0 and 100. If NOT mentioned, write "NOT_SPECIFIED".
                2. Does the JD explicitly ask for specific educational degrees or fields (e.g., BCA, MCA, Computer Science)? If yes, evaluate alignment and provide an [EDUCATION_SCORE] between 0 and 100. If NOT mentioned, write "NOT_SPECIFIED".

                CRITICAL HARD-SKILL ONLY KEYWORD RULES:
                - Extract core technical tools, languages, and frameworks required by the JD.
                - STRICTLY FORBIDDEN keywords: Do NOT extract generic soft text like "hands on experience", "bachelor's degree", "work", "projects", "communication", etc.

                CRITICAL COVER LETTER DATE RULE: 
                - You must use exactly "{current_date_str}" as the formal date. Do NOT write "[CURRENT DATE]" or leave brackets anywhere.
                - STRICTLY FORBIDDEN: Do not leave placeholder text like "[Platform where job was seen]" or "[Company Name]". If a detail is missing from the context, substitute a natural professional fallback phrasing instead (e.g., "advertised online position" or "your job opening").
                - Resolve all placeholders cleanly using real candidate details from the resume and target details from the JD.

                CRITICAL PLAIN-TEXT RULES: 
                - The output must be strictly plain text. Do NOT use markdown bolding (double asterisks), do NOT use bullet symbols or asterisks (*) on section header title lines.
                - Use clear section headers on their own individual lines (e.g., About, Education, Experience, Projects, Technical Skills, Certificates, Hobbies & Interests).
                - Use standard bullet symbols (- or •) only for descriptive points beneath those headers.

                Provide your entire response parsed strictly inside the matching text blocks below:

                [ATS_FRIENDLY]
                (Write exactly YES or NO)
                [/ATS_FRIENDLY]

                [EXPERIENCE_SCORE]
                (Write a number 0-100 OR write NOT_SPECIFIED)
                [/EXPERIENCE_SCORE]

                [EDUCATION_SCORE]
                (Write a number 0-100 OR write NOT_SPECIFIED)
                [/EDUCATION_SCORE]

                [FOUND_KEYWORDS]
                (Comma-separated list of technical skills present in BOTH the JD and the resume)
                [/FOUND_KEYWORDS]

                [MISSING_KEYWORDS]
                (Comma-separated list of technical skills present in the JD but missing from the resume)
                [/MISSING_KEYWORDS]

                [GAPS]
                - (Bullet points of missing qualifications)
                [/GAPS]

                [TAILORED_RESUME]
                (Rewrite the full resume to integrate keywords cleanly)
                [/TAILORED_RESUME]
                {cover_letter_instruction}

                JOB DESCRIPTION:
                {job_desc}

                ORIGINAL RESUME:
                {resume_content}
                """
                
                try:
                    import time
                    from google.api_core.exceptions import ServiceUnavailable

                    max_retries = 3
                    response_stream = None
                    
                    for attempt in range(max_retries):
                        try:
                            response_stream = model.generate_content(master_prompt, stream=True)
                            break
                        except ServiceUnavailable:
                            if attempt < max_retries - 1:
                                st.warning(f"⚠️ Google AI servers are busy. Retrying automatically (Attempt {attempt + 2}/{max_retries})...")
                                time.sleep(2)
                            else:
                                raise
                    
                    st.write("### 🎙️ Live AI Analysis Stream")
                    stream_placeholder = st.empty()
                    full_response_text = ""
                    
                    for chunk in response_stream:
                        if chunk.text:
                            full_response_text += chunk.text
                            stream_placeholder.text(full_response_text)
                    
                    def extract_block(text, tag):
                        try:
                            return text.split(f"[{tag}]")[1].split(f"[/{tag}]")[0].strip()
                        except IndexError:
                            return "NOT_SPECIFIED" if "SCORE" in tag else ""

                    st.session_state.ats_friendly = extract_block(full_response_text, "ATS_FRIENDLY").upper() or "YES"
                    st.session_state.missing_quals = extract_block(full_response_text, "GAPS")
                    
                    # Extract the freshly generated resume text
                    st.session_state.final_resume = extract_block(full_response_text, "TAILORED_RESUME")
                    
                    # FORCE RESET: Clear the old editor memory cache so the text area updates cleanly
                    if "editor_content" in st.session_state:
                        del st.session_state["editor_content"]
                    if "resume_preview_text_editor" in st.session_state:
                        del st.session_state["resume_preview_text_editor"]
                        
                    st.session_state.final_letter = extract_block(full_response_text, "COVER_LETTER")
                    
                    raw_found = extract_block(full_response_text, "FOUND_KEYWORDS")
                    raw_missing = extract_block(full_response_text, "MISSING_KEYWORDS")
                    
                    exp_raw = extract_block(full_response_text, "EXPERIENCE_SCORE")
                    edu_raw = extract_block(full_response_text, "EDUCATION_SCORE")
                    
                    all_jd_keywords = list(set([k.strip() for k in f"{raw_found},{raw_missing}".split(",") if k.strip()]))
                    
                    resume_lower = resume_content.lower()
                    true_matched = [k.strip() for k in all_jd_keywords if k.strip().lower() in resume_lower]
                    true_missing = [k.strip() for k in all_jd_keywords if k.strip().lower() not in resume_lower]
                    
                    total_kw = len(true_matched) + len(true_missing)
                    kw_score = int((len(true_matched) / total_kw) * 100) if total_kw > 0 else 70
                    
                    factors = {"keywords": kw_score}
                    
                    if exp_raw != "NOT_SPECIFIED":
                        exp_digits = "".join([char for char in exp_raw if char.isdigit()])
                        if exp_digits: factors["experience"] = int(exp_digits)
                        
                    if edu_raw != "NOT_SPECIFIED":
                        edu_digits = "".join([char for char in edu_raw if char.isdigit()])
                        if edu_digits: factors["education"] = int(edu_digits)
                    
                    num_factors = len(factors)
                    if num_factors == 3:
                        final_score = int((factors["keywords"] * 0.4) + (factors["experience"] * 0.4) + (factors["education"] * 0.2))
                    elif num_factors == 2:
                        if "experience" in factors:
                            final_score = int((factors["keywords"] * 0.5) + (factors["experience"] * 0.5))
                        else:
                            final_score = int((factors["keywords"] * 0.7) + (factors["education"] * 0.3))
                    else:
                        final_score = factors["keywords"]

                    st.session_state.resume_match_score = final_score
                    st.session_state.found_kw = ", ".join(true_matched)
                    st.session_state.missing_kw = ", ".join(true_missing)
                    
                    st.session_state.ai_processed = True
                    st.rerun()

                except IndexError:
                    st.error("The model response structure wasn't fully generated. Please try running the tool again.")
                except Exception as e:
                    if "429" in str(e) or "Quota exceeded" in str(e):
                        st.error("🛑 Gemini API Free Tier Quota Exceeded! Please update your API key context configurations.")
                    else:
                        st.error(f"Processing Error: {e}")

# --- RENDER DASHBOARD RESULTS PANEL ---
if st.session_state.get("ai_processed", False):
    st.success("✓ Optimization Complete!")
    
    st.subheader("Alignment Evaluation Metrics")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(
            label="🎯 Unified Resume Match Score", 
            value=f"{st.session_state.resume_match_score}%",
            help="Calculated dynamically based on structural Job Description demands."
        )
    with m_col2:
        is_friendly = st.session_state.get("ats_friendly", "YES")
        if "YES" in is_friendly:
            st.metric(label="📄 ATS Parsing Scannable Status", value="✅ YES (Pass)")
        else:
            st.metric(label="📄 ATS Parsing Scannable Status", value="🛑 NO (Structure Error)")
            
    st.markdown("---")
    
    # 2. Side-by-Side Split: Left Side = Keywords Management | Right Side = Live Resume Preview & Export
    left_panel, right_panel = st.columns([1, 1.2], gap="large")
    
    with left_panel:
        st.markdown("### 📊 Skill Gap Management")
        kw_col1, kw_col2 = st.columns(2)
        with kw_col1:
            st.success("✅ Matched")
            matched_items = [item.strip() for item in st.session_state.found_kw.split(",") if item.strip()]
            if matched_items:
                for item in matched_items: st.markdown(f"• {item}")
            else:
                st.write("No matching technical keys identified.")
                
        with kw_col2:
            st.error("❌ Missing")
            missing_items = [item.strip() for item in st.session_state.missing_kw.split(",") if item.strip()]
            
            if missing_items:
                with st.form(key="keyword_injection_form"):
                    st.markdown("##### Select to add:")
                    selected_keywords = []
                    for item in missing_items:
                        if st.checkbox(f"➕ {item}", key=f"chk_{item}"):
                            selected_keywords.append(item)
                    
                    submit_injection = st.form_submit_button("🚀 Inject Selected Skills", type="primary", use_container_width=True)
                
                if submit_injection:
                    if not selected_keywords:
                        st.warning("Please check at least one keyword first.")
                    else:
                        current_resume = st.session_state.final_resume
                        skills_to_add = ", ".join(selected_keywords)
                        
                        if "TECHNICAL SKILLS" in current_resume:
                            updated_resume = current_resume.replace(
                                "TECHNICAL SKILLS", 
                                f"TECHNICAL SKILLS\nConcepts: {skills_to_add},"
                            )
                            st.session_state.final_resume = updated_resume
                        else:
                            st.session_state.final_resume = current_resume + f"\n\nTECHNICAL SKILLS\n{skills_to_add}"
                        
                        updated_matched = [i.strip() for i in st.session_state.found_kw.split(",") if i.strip()]
                        updated_matched.extend(selected_keywords)
                        updated_missing = [i for i in missing_items if i not in selected_keywords]
                        
                        total_kw = len(updated_matched) + len(updated_missing)
                        if total_kw > 0:
                            st.session_state.resume_match_score = int((len(updated_matched) / total_kw) * 100)
                        
                        st.session_state.found_kw = ", ".join(updated_matched)
                        st.session_state.missing_kw = ", ".join(updated_missing)
                        
                        st.success(f"Successfully integrated [{skills_to_add}] straight into your Technical Skills stack!")
                        st.rerun()
            else:
                st.write("Perfect tech stack overlap!")
                
        if generate_cover_letter and "final_letter" in st.session_state:
            st.markdown("---")
            st.markdown("### ✉️ Drafted Cover Letter")
            st.text_area("Cover Letter Preview", st.session_state.final_letter, height=250)
            cl_filename = st.text_input("Cover Letter PDF Name:", value="Cover_Letter.pdf")
            st.download_button(
                label="📥 Download Cover Letter (.pdf)", 
                data=convert_text_to_pdf(st.session_state.final_letter, template_style="Classic Professional (Elegant Serif)"), 
                file_name=cl_filename, 
                mime="application/pdf",
                use_container_width=True
            )

    with right_panel:
        st.markdown("### 📝 Tailored Resume Preview")
        
        # Safe initialization check
        if "final_resume" not in st.session_state:
            st.session_state.final_resume = ""
            
        # Render the text box. The 'key' automatically syncs changes to st.session_state.resume_preview_text_editor
        st.text_area(
            "Live Document Preview (Plain Text) - Changes made here will be captured on download:", 
            value=st.session_state.final_resume, 
            height=450,
            key="resume_preview_text_editor"
        )
        
        st.markdown("##### 🎨 Export Settings")
        resume_template = st.selectbox(
            "Choose a layout template for PDF generation:",
            ["Jake's Resume Format", "Deedy Tech Layout", "Awesome CV / Modern Executive"]
        )
        res_filename = st.text_input("Resume PDF Name:", value="Tailored_Resume.pdf")
        
        # When clicking download, dynamically pull the text directly out of the active text area widget's memory state
        edited_content = st.session_state.get("resume_preview_text_editor", st.session_state.final_resume)
        
        st.download_button(
            label="📥 Download Tailored Resume (.pdf)", 
            data=convert_text_to_pdf(edited_content, template_style=resume_template), 
            file_name=res_filename, 
            mime="application/pdf",
            use_container_width=True
        )