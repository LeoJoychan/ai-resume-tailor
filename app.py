import streamlit as st
import pypdf
import google.generativeai as genai
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

def convert_text_to_pdf(text_content, template_style="Classic Professional (Elegant Serif)"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    # Base configuration templates
    styles = getSampleStyleSheet()
    
    if "Modern Minimalist" in template_style:
        body_font = "Helvetica"
        header_font = "Helvetica-Bold"
        primary_color = colors.HexColor("#2C3E50")
    elif "Tech Executive" in template_style:
        body_font = "Courier"
        header_font = "Courier-Bold"
        primary_color = colors.HexColor("#16A085")
    else: # Classic Professional
        body_font = "Times-Roman"
        header_font = "Times-Bold"
        primary_color = colors.HexColor("#000000")

    # Creating customized dynamic styles based on selection
    custom_body = ParagraphStyle(
        'CustomBody',
        fontName=body_font,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#333333")
    )
    
    custom_header = ParagraphStyle(
        'CustomHeader',
        fontName=header_font,
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4
    )

    # Simple layout parsing
    lines = text_content.split('\n')
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            story.append(Spacer(1, 8))
            continue
            
        # Treat completely capitalized lines as section headers
        if cleaned_line.isupper() and len(cleaned_line) < 40:
            story.append(Paragraph(cleaned_line, custom_header))
        else:
            story.append(Paragraph(cleaned_line, custom_body))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Configure page layout
st.set_page_config(page_title="AI Resume Tailor", page_icon="💼", layout="centered")

# Initialize navigation states
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "generated_demo_resume" not in st.session_state:
    st.session_state.generated_demo_resume = None

# --- NEW: Initialize Dynamic Section Counters ---
if "social_count" not in st.session_state: st.session_state.social_count = 1
if "edu_count" not in st.session_state: st.session_state.edu_count = 1
if "project_count" not in st.session_state: st.session_state.project_count = 1
if "cert_count" not in st.session_state: st.session_state.cert_count = 1

# Dropdown helper lists
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
years = [str(y) for y in range(2026, 2015, -1)]

# --- PAGE 2: ADVANCED RESUME BUILDER WIZARD ---
if st.session_state.current_page == "builder":
    st.title("📝 Create a Brand New Resume")
    st.write("Fill out your details systematically to generate a baseline professional resume.")
    
    # We remove the global st.form because dynamic "Add More" buttons inside st.form require complex hacks. 
    # Instead, we use normal layout blocks which handle dynamic rendering flawlessly!
    
    # 1. Contact & Basics
    st.subheader("1. Contact Information")
    full_name = st.text_input("Full Name *", placeholder="Leo Joychan")
    email = st.text_input("Email Address *")
    phone = st.text_input("Contact Number *", placeholder="+91 XXXXX XXXXX")
    summary = st.text_area("Professional Summary", placeholder="A brief narrative about your career aspirations...")

    st.markdown("---")

    # 2. Dynamic Social Media Links
    st.subheader("2. Social Media Profiles")
    socials_data = []
    for i in range(st.session_state.social_count):
        c1, c2 = st.columns([1, 2])
        with c1:
            platform = st.selectbox(f"Platform {i+1}", ["None", "LinkedIn", "GitHub", "Portfolio", "Instagram", "Twitter"], key=f"plat_{i}")
        with c2:
            link = st.text_input(f"Profile URL {i+1}", placeholder="https://...", key=f"link_{i}")
        if platform != "None" and link:
            socials_data.append(f"{platform}: {link}")
    
    if st.button("➕ Add More Social Profile", key="add_social"):
        st.session_state.social_count += 1
        st.rerun()

    st.markdown("---")

    # 3. Experience Section (Clean fields - can be left blank for freshers)
    st.subheader("3. Work Experience (Leave blank if you are a Fresher)")
    comp_name = st.text_input("Company Name", placeholder="e.g., Tech Solutions Inc.")
    role_name = st.text_input("Role / Job Title", placeholder="e.g., Software Engineer Intern")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: start_m_exp = st.selectbox("Start Month", ["-"] + months, key="sm_exp")
    with c2: start_y_exp = st.selectbox("Start Year", ["-"] + years, key="sy_exp")
    with c3: end_m_exp = st.selectbox("End Month", ["-"] + months, key="em_exp")
    with c4: end_y_exp = st.selectbox("End Year", ["-"] + years, key="ey_exp")
    exp_desc = st.text_area("Responsibilities / Achievements", placeholder="Describe what you worked on...")

    st.markdown("---")

    # 4. Dynamic Education History
    st.subheader("4. Education History")
    edu_data = []
    for i in range(st.session_state.edu_count):
        st.markdown(f"**Degree / Education Slot {i+1}**")
        inst = st.text_input("College / University Name", key=f"inst_{i}", placeholder="e.g., MG University")
        course = st.text_input("Course / Degree Title", key=f"course_{i}", placeholder="e.g., Master of Computer Applications")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: sm = st.selectbox("Start Month", months, key=f"esm_{i}")
        with c2: sy = st.selectbox("Start Year", years, key=f"esy_{i}")
        with c3: em = st.selectbox("End Month", months, key=f"eem_{i}")
        with c4: ey = st.selectbox("End Year", years, key=f"eey_{i}")
        
        if inst and course:
            edu_data.append(f"Institution: {inst}, Course: {course} ({sm} {sy} - {em} {ey})")
            
    if st.button("➕ Add More Education", key="add_edu"):
        st.session_state.edu_count += 1
        st.rerun()

    st.markdown("---")

    # 5. Dynamic Key Projects
    st.subheader("5. Key Projects")
    project_data = []
    for i in range(st.session_state.project_count):
        st.markdown(f"**Project {i+1}**")
        p_title = st.text_input("Project Title", key=f"p_title_{i}", placeholder="e.g., AI Farm Yield Predictor")
        p_desc = st.text_area("Short Description", key=f"p_desc_{i}", placeholder="Explain what the project does and the tech stack used...")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: psm = st.selectbox("Start Month", months, key=f"psm_{i}")
        with c2: psy = st.selectbox("Start Year", years, key=f"psy_{i}")
        with c3: pem = st.selectbox("End Month", months, key=f"pem_{i}")
        with c4: pey = st.selectbox("End Year", years, key=f"pey_{i}")
        
        if p_title:
            project_data.append(f"Title: {p_title} ({psm} {psy} - {pem} {pey})\nDescription: {p_desc}")
            
    if st.button("➕ Add More Project", key="add_project"):
        st.session_state.project_count += 1
        st.rerun()

    st.markdown("---")

    # 6. Dynamic Certifications
    st.subheader("6. Certifications")
    cert_data = []
    for i in range(st.session_state.cert_count):
        st.markdown(f"**Certificate {i+1}**")
        c_title = st.text_input("Certificate Title", key=f"ctitle_{i}")
        c_org = st.text_input("Issuing Organization", key=f"corg_{i}")
        c_year = st.selectbox("Issued Year", years, key=f"cyear_{i}")
        c_desc = st.text_input("Brief Description (Optional)", key=f"cdesc_{i}")
        
        if c_title:
            cert_data.append(f"Title: {c_title}, Org: {c_org}, Year: {c_year}, Details: {c_desc}")
            
    if st.button("➕ Add More Certificate", key="add_cert"):
        st.session_state.cert_count += 1
        st.rerun()

    st.markdown("---")

    # 7. Hobbies
    st.subheader("7. Hobbies & Interests (Optional)")
    hobbies = st.text_input("Hobbies (Comma-separated)", placeholder="Football, Calisthenics, Music")

    st.markdown("---")

    # 8. Action Buttons
    st.subheader("8. Finalize Resume")
    
    # Process inputs when "Create" is clicked
    if st.button("🚀 Create Baseline Resume", type="primary", use_container_width=True):
        if not full_name or not email or not phone:
            st.error("Please fill out all required fields (*) before processing.")
        else:
            # Format the optional experience block safely
            exp_block = "None (Fresher)"
            if comp_name and role_name:
                exp_block = f"Company: {comp_name}, Role: {role_name} ({start_m_exp} {start_y_exp} - {end_m_exp} {end_y_exp})\nDetails: {exp_desc}"

            # Bundle everything together cleanly
            profile_summary_block = f"""
            NAME: {full_name}
            EMAIL: {email}
            PHONE: {phone}
            SUMMARY: {summary}
            SOCIAL PROFILES: {', '.join(socials_data) if socials_data else 'None'}
            EXPERIENCE: {exp_block}
            EDUCATION: {' | '.join(edu_data) if edu_data else 'None'}
            PROJECTS: {' | '.join(project_data) if project_data else 'None'}
            CERTIFICATIONS: {' | '.join(cert_data) if cert_data else 'None'}
            HOBBIES: {hobbies if hobbies else 'None'}
            """
            st.session_state.user_profile = profile_summary_block
            
            # 9. Create the demo resume text layout for preview and download
            st.session_state.generated_demo_resume = f"""=========================================
{full_name.upper()}
{email} | {phone}
{', '.join(socials_data) if socials_data else ''}
=========================================

PROFESSIONAL SUMMARY
{summary}

WORK EXPERIENCE
{exp_block}

EDUCATION
{chr(10).join(['- ' + e for e in edu_data]) if edu_data else 'None'}

PROJECTS
{chr(10).join(['- ' + p for p in project_data]) if project_data else 'None'}

CERTIFICATIONS
{chr(10).join(['- ' + c for c in cert_data]) if cert_data else 'None'}

HOBBIES & INTERESTS
{hobbies if hobbies else 'None'}
"""
            st.success("✓ Baseline Profile parameters registered successfully! Scroll down to download.")

    # Show the generated demo resume window right after creation
    if st.session_state.generated_demo_resume:
        st.markdown("### 📄 Your Generated Demo Resume")
        st.text_area("Preview Draft Layout", st.session_state.generated_demo_resume, height=300)
        
        st.download_button(
            label="📥 Download Baseline Resume (.pdf)",
            data=convert_text_to_pdf(st.session_state.generated_demo_resume),
            file_name=f"{full_name.replace(' ', '_')}_Resume.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        if st.button("🎯 Go to Home Page & Run Optimization Matcher", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
            
    if st.button("⬅ Cancel & Return Home"):
        st.session_state.current_page = "home"
        st.rerun()


# --- PAGE 1: HOME PANEL INTERFACE ---
elif st.session_state.current_page == "home":
    st.title("💼 AI-Powered Resume Tailor & Cover Letter Builder")
    st.write("Optimize your resume against any job description using real-time LLM analysis.")

    st.markdown("---")
    st.header("1. Provide Your Details")

    job_desc = st.text_area(
        "Paste the target Job Description (JD) here:", 
        height=150, 
        placeholder="Paste the full job requirements, responsibilities, and qualifications..."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "📤 Upload your current Resume (PDF format):", 
            type=["pdf"],
            help="The system will extract text from this PDF file automatically."
        )
    with col2:
        st.write("💡 Don't have a resume?")
        if st.button("➕ Create New Resume", use_container_width=True):
            st.session_state.generated_demo_resume = None  # Flush history
            st.session_state.current_page = "builder"
            st.rerun()

    if "user_profile" in st.session_state and uploaded_file is None:
        st.success("✓ Custom wizard profile loaded and locked for matching engine optimization!")
    elif uploaded_file is not None:
        st.success(f"✓ '{uploaded_file.name}' loaded successfully.")

    generate_cover_letter = st.toggle("📄 Generate a matching Cover Letter for this role", value=False)

    st.markdown("---")

    # --- SINGLE BUTTON TRIGGER ---
    if st.button("🚀 Run Live AI Analysis", type="primary", use_container_width=True):
        if not job_desc.strip():
            st.warning("Please paste a Job Description to compare against.")
        else:
            resume_content = ""
            if uploaded_file is not None:
                try:
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    parsed_text = []
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text: parsed_text.append(text)
                    resume_content = "\n".join(parsed_text)
                except Exception as e:
                    st.error(f"Failed to read PDF file layout: {e}")
            elif "user_profile" in st.session_state:
                resume_content = st.session_state.user_profile
                
            if not resume_content.strip():
                st.error("Please provide structural parameters via either PDF upload or profile generation wizard.")
            else:
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
                    # Dynamically inject today's exact date from your system
                    import datetime
                    current_date_str = datetime.date.today().strftime("%B %d, %Y")

                    # --- REFINED MASTER PROMPT WITH REVENUE-GRADE RECRUITER LOGIC ---
                    master_prompt = f"""
                    You are an expert recruiter and strict ATS parser. Analyze the Resume against the Job Description.
                    Perform your breakdown, optimize the resume, and generate a cover letter if requested.
                    
                    CRITICAL KEYWORD BOUNDARY RULES (STRICT INTERSECTION ONLY):
                    You must perform a strict mathematical intersection comparison between the Job Description (JD) and the Original Resume.
                    
                    - [FOUND_KEYWORDS] MUST ONLY contain keywords, technical skills, or frameworks that are explicitly present in BOTH the Job Description AND the Original Resume text. If a word is in the resume but NOT requested in the JD, do NOT include it here.
                    
                    - [MISSING_KEYWORDS] MUST ONLY contain keywords, technical skills, or frameworks that are explicitly requested in the Job Description but are completely ABSENT from the Original Resume text.
                    
                    Do not hallucinate broad match definitions, synonyms, or general resume high points. If it is not explicitly mentioned in the JD, it has no business appearing in either keyword block.

                    CRITICAL COVER LETTER DATE & HOOK RULE: 
                    - You must use exactly "{current_date_str}" as the formal date of the letter. Do NOT write "[CURRENT DATE]" or leave brackets anywhere.
                    - Do NOT output any generic bracketed placeholders like [Your Name], [Your Phone Number], [Company Name], or [Platform].
                    - Extract the candidate's real name and contact details from the original resume. Extract the target company name and role title from the Job Description. 

                    CRITICAL PLAIN-TEXT RULES: 
                    The output must be strictly plain text. Do NOT use markdown bolding, do NOT use asterisks (*) anywhere. 
                    Use ALL CAPS for section headings. Use simple dashes (-) for bullet points.

                    Provide your entire response parsed strictly inside the matching text blocks below:

                    [ATS_SCORE]
                    (Provide only a number between 0 and 100 based strictly on hard skill text match)
                    [/ATS_SCORE]

                    [MATCH_SCORE]
                    (Provide only a number between 0 and 100 based on role level alignment)
                    [/MATCH_SCORE]

                    [FOUND_KEYWORDS]
                    (Provide a comma-separated list of ONLY terms present in BOTH the JD and the original resume text)
                    [/FOUND_KEYWORDS]

                    [MISSING_KEYWORDS]
                    (Provide a comma-separated list of terms present in the JD but missing from the original resume text)
                    [/MISSING_KEYWORDS]

                    [GAPS]
                    - (Bullet 1 of structural missing qualifications)
                    - (Bullet 2)
                    - (Bullet 3)
                    [/GAPS]

                    [TAILORED_RESUME]
                    (Rewrite the full resume to integrate keywords authentically. No asterisks allowed.)
                    [/TAILORED_RESUME]

                    [COVER_LETTER]
                    (Write the complete formal tailored cover letter using {current_date_str} as the header date. Ensure ALL placeholders are completely resolved with real text.)
                    [/COVER_LETTER]

                    JOB DESCRIPTION:
                    {job_desc}

                    ORIGINAL RESUME:
                    {resume_content}
                    """
                    
                    try:
                        # Stream the contents safely
                        response_stream = model.generate_content(master_prompt, stream=True)
                        
                        st.write("### 🎙️ Live AI Analysis Stream")
                        stream_placeholder = st.empty()
                        
                        full_response_text = ""
                        
                        for chunk in response_stream:
                            if chunk.text:
                                full_response_text += chunk.text
                                stream_placeholder.text(full_response_text)
                        
                        # 1. Parse basic metrics out first
                        st.session_state.ats_score = full_response_text.split("[ATS_SCORE]")[1].split("[/ATS_SCORE]")[0].strip()
                        st.session_state.match_score = full_response_text.split("[MATCH_SCORE]")[1].split("[/MATCH_SCORE]")[0].strip()
                        st.session_state.missing_quals = full_response_text.split("[GAPS]")[1].split("[/GAPS]")[0].strip()
                        st.session_state.final_resume = full_response_text.split("[TAILORED_RESUME]")[1].split("[/TAILORED_RESUME]")[0].strip()
                        st.session_state.final_letter = full_response_text.split("[COVER_LETTER]")[1].split("[/COVER_LETTER]")[0].strip()
                        
                        # 2. Extract raw keywords identified by LLM from the JD
                        raw_found = full_response_text.split("[FOUND_KEYWORDS]")[1].split("[/FOUND_KEYWORDS]")[0].strip()
                        raw_missing = full_response_text.split("[MISSING_KEYWORDS]")[1].split("[/MISSING_KEYWORDS]")[0].strip()
                        
                        # Combine both lists to get every target keyword the JD is looking for
                        all_jd_keywords = [k.strip() for k in f"{raw_found},{raw_missing}".split(",") if k.strip()]
                        # Remove duplicates
                        all_jd_keywords = list(set(all_jd_keywords))
                        
                        # 3. RUN DETERMINISTIC PYTHON FILTERING
                        resume_lower = resume_content.lower()
                        true_matched = []
                        true_missing = []
                        
                        for keyword in all_jd_keywords:
                            # Clean up phrasing for precise checking
                            clean_keyword = keyword.strip()
                            if not clean_keyword:
                                continue
                            
                            # Check if the keyword exists verbatim in your resume text
                            if clean_keyword.lower() in resume_lower:
                                true_matched.append(clean_keyword)
                            else:
                                true_missing.append(clean_keyword)
                        
                        # 4. Save the true python-verified results to session state
                        st.session_state.found_kw = ", ".join(true_matched)
                        st.session_state.missing_kw = ", ".join(true_missing)
                        
                        st.session_state.ai_processed = True
                        st.rerun()

                    except IndexError:
                        st.error("The model response structure wasn't fully generated. Please try running the tool again.")
                    except Exception as e:
                        if "429" in str(e) or "Quota exceeded" in str(e):
                            st.error("🛑 Gemini API Free Tier Quota Exceeded! Please switch projects or update your API Key.")
                        else:
                            st.error(f"Processing Error: {e}")

    # --- RENDER THE UI OUTSIDE OF THE BUTTON CLICK ---
    if st.session_state.get("ai_processed", False):
        st.success("✓ Optimization Complete! Results saved to memory.")
        
        tab1, tab2, tab3 = st.tabs(["📊 ATS Analysis", "📝 Optimized Resume", "✉️ Drafted Cover Letter"])

        # TAB 1: Granular ATS & Match Score Breakdown
        with tab1:
            st.subheader("Alignment Evaluation Metrics")
            score_col1, score_col2 = st.columns(2)
            with score_col1:
                st.metric(label="🎯 ATS Keyword Optimization Score", value=f"{st.session_state.ats_score}%")
            with score_col2:
                st.metric(label="👔 Holistic Role Match Rating", value=f"{st.session_state.match_score}%")
                
            st.markdown("---")
            
            # Key points shown cleanly as bullet layouts instead of comma blocks
            kw_col1, kw_col2 = st.columns(2)
            with kw_col1:
                st.success("✅ Keywords Matched")
                matched_items = [item.strip() for item in st.session_state.found_kw.split(",") if item.strip()]
                if matched_items:
                    for item in matched_items:
                        st.markdown(f"• {item}")
                else:
                    st.write("No matching keywords identified.")
                    
            with kw_col2:
                st.error("❌ Missing Keywords (Add these!)")
                missing_items = [item.strip() for item in st.session_state.missing_kw.split(",") if item.strip()]
                if missing_items:
                    for item in missing_items:
                        st.markdown(f"• {item}")
                else:
                    st.write("No missing keywords detected!")
                
            st.markdown("---")
            st.warning("⚠️ Experience & Qualification Gaps")
            st.write(st.session_state.missing_quals)

        # TAB 2: Resume Download with Template Selection
        with tab2:
            st.subheader("Tailored Resume Panel")
            st.text_area("Review Content (Plain Text Format)", st.session_state.final_resume, height=300)
            
            st.markdown("### 🎨 Select Document Export Layout")
            resume_template = st.selectbox(
                "Choose a layout template for your generated PDF:",
                ["Classic Professional (Elegant Serif)", "Modern Minimalist (Clean Clean-cut Sans)", "Tech Executive (Bold Left-Border Accent)"]
            )
            
            res_filename = st.text_input("Name your Resume PDF file:", value="Tailored_Resume.pdf")
            
            # Passing template selection style directly into the PDF compilation generator
            st.download_button(
                label="📥 Download Tailored Resume (.pdf)", 
                data=convert_text_to_pdf(st.session_state.final_resume, template_style=resume_template), 
                file_name=res_filename, 
                mime="application/pdf"
            )

        # TAB 3: Cover Letter Download Panel
        with tab3:
            st.subheader("Tailored Cover Letter Panel")
            if generate_cover_letter and "final_letter" in st.session_state:
                st.text_area("Review Content (Plain Text Format)", st.session_state.final_letter, height=300)
                
                cl_filename = st.text_input("Name your Cover Letter PDF file:", value="Cover_Letter.pdf")
                st.download_button(
                    label="📥 Download Cover Letter (.pdf)", 
                    data=convert_text_to_pdf(st.session_state.final_letter, template_style="Classic Professional (Elegant Serif)"), 
                    file_name=cl_filename, 
                    mime="application/pdf"
                )
            else:
                st.info("Cover letter generation was not selected during initial execution parameter processing.")