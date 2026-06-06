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

                    # --- DYNAMIC MULTI-FACTOR MASTER PROMPT ---
                    master_prompt = f"""
                    You are an expert recruiter and strict ATS parser. Analyze the Resume against the Job Description.
                    Perform your breakdown, optimize the resume, and generate a cover letter.

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
                    - Resolve all placeholders using real candidate details from the resume and target details from the JD.

                    CRITICAL PLAIN-TEXT RULES: 
                    The output must be strictly plain text. Do NOT use markdown bolding, do NOT use asterisks (*) anywhere. Use ALL CAPS for section headings.

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

                    [COVER_LETTER]
                    (Write the complete formal tailored cover letter using {current_date_str})
                    [/COVER_LETTER]

                    JOB DESCRIPTION:
                    {job_desc}

                    ORIGINAL RESUME:
                    {resume_content}
                    """
                    
                    try:
                        # --- ROBUST RETRY LOOP FOR GOOGLE SERVER OVERLOADS ---
                        import time
                        from google.api_core.exceptions import ServiceUnavailable

                        max_retries = 3
                        response_stream = None
                        
                        for attempt in range(max_retries):
                            try:
                                # Stream the contents safely
                                response_stream = model.generate_content(master_prompt, stream=True)
                                break  # Success! Break out of the retry loop
                            except ServiceUnavailable:
                                if attempt < max_retries - 1:
                                    st.warning(f"⚠️ Google AI servers are busy. Retrying automatically (Attempt {attempt + 2}/{max_retries})...")
                                    time.sleep(2)  # Pause for 2 seconds before trying again
                                else:
                                    raise  # Re-raise the error if all 3 attempts fail
                        
                        st.write("### 🎙️ Live AI Analysis Stream")
                        stream_placeholder = st.empty()
                        full_response_text = ""
                        
                        for chunk in response_stream:
                            if chunk.text:
                                full_response_text += chunk.text
                                stream_placeholder.text(full_response_text)
                        
                        # 1. Parse base blocks
                        st.session_state.ats_friendly = full_response_text.split("[ATS_FRIENDLY]")[1].split("[/ATS_FRIENDLY]")[0].strip().upper()
                        st.session_state.missing_quals = full_response_text.split("[GAPS]")[1].split("[/GAPS]")[0].strip()
                        st.session_state.final_resume = full_response_text.split("[TAILORED_RESUME]")[1].split("[/TAILORED_RESUME]")[0].strip()
                        st.session_state.final_letter = full_response_text.split("[COVER_LETTER]")[1].split("[/COVER_LETTER]")[0].strip()
                        
                        # 2. Hard Keyword Parsing & Python Intersection Filter Check
                        raw_found = full_response_text.split("[FOUND_KEYWORDS]")[1].split("[/FOUND_KEYWORDS]")[0].strip()
                        raw_missing = full_response_text.split("[MISSING_KEYWORDS]")[1].split("[/MISSING_KEYWORDS]")[0].strip()
                        all_jd_keywords = list(set([k.strip() for k in f"{raw_found},{raw_missing}".split(",") if k.strip()]))
                        
                        resume_lower = resume_content.lower()
                        true_matched = [k.strip() for k in all_jd_keywords if k.strip().lower() in resume_lower]
                        true_missing = [k.strip() for k in all_jd_keywords if k.strip().lower() not in resume_lower]
                        
                        # Calculate raw technical keyword percentage
                        total_kw = len(true_matched) + len(true_missing)
                        kw_score = int((len(true_matched) / total_kw) * 100) if total_kw > 0 else 70
                        
                        # 3. Read sub-scores to see what the company actually requested
                        exp_raw = full_response_text.split("[EXPERIENCE_SCORE]")[1].split("[/EXPERIENCE_SCORE]")[0].strip()
                        edu_raw = full_response_text.split("[EDUCATION_SCORE]")[1].split("[/EDUCATION_SCORE]")[0].strip()
                        
                        # DYNAMIC WEIGHT ALLOCATION ENGINE
                        factors = {"keywords": kw_score}
                        
                        # Clean and extract numbers using safe list comprehensions
                        if exp_raw != "NOT_SPECIFIED":
                            exp_digits = "".join([char for char in exp_raw if char.isdigit()])
                            if exp_digits:
                                factors["experience"] = int(exp_digits)
                            
                        if edu_raw != "NOT_SPECIFIED":
                            edu_digits = "".join([char for char in edu_raw if char.isdigit()])
                            if edu_digits:
                                factors["education"] = int(edu_digits)
                        
                        # Calculate weighted math depending on active factors
                        num_factors = len(factors)
                        if num_factors == 3:
                            # Keywords (40%), Experience (40%), Education (20%)
                            final_score = int((factors["keywords"] * 0.4) + (factors["experience"] * 0.4) + (factors["education"] * 0.2))
                        elif num_factors == 2:
                            if "experience" in factors:
                                # Keywords (50%), Experience (50%)
                                final_score = int((factors["keywords"] * 0.5) + (factors["experience"] * 0.5))
                            else:
                                # Keywords (70%), Education (30%)
                                final_score = int((factors["keywords"] * 0.7) + (factors["education"] * 0.3))
                        else:
                            # Keywords only (100%)
                            final_score = factors["keywords"]

                        # Save values safely to memory states
                        st.session_state.resume_match_score = final_score
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
        # TAB 1: Cleaned Single Metric Breakdown
        # TAB 1: Cleaned Single Metric Breakdown (Fixed Duplication Bug)
        # TAB 1: Streamlined Score & Scan Check Breakdown
        with tab1:
            st.subheader("Alignment Evaluation Metrics")
            
            # Place metrics cleanly side-by-side
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.metric(
                    label="🎯 Unified Resume Match Score", 
                    value=f"{st.session_state.resume_match_score}%",
                    help="Calculated dynamically based ONLY on the criteria explicitly stated by the company inside the Job Description."
                )
            with m_col2:
                # Colorful status indicator text format depending on response token
                is_friendly = st.session_state.get("ats_friendly", "YES")
                if "YES" in is_friendly:
                    st.metric(label="📄 ATS Parsing Scannable Status", value="✅ YES (Pass)")
                else:
                    st.metric(label="📄 ATS Parsing Scannable Status", value="🛑 NO (Structure Error)")
                
            st.markdown("---")
            
            kw_col1, kw_col2 = st.columns(2)
            with kw_col1:
                st.success("✅ Keywords Matched")
                matched_items = [item.strip() for item in st.session_state.found_kw.split(",") if item.strip()]
                if matched_items:
                    for item in matched_items: st.markdown(f"• {item}")
                else:
                    st.write("No matching technical keys identified.")
                    
            with kw_col2:
                st.error("❌ Missing Keywords (Add these!)")
                
                # Parse out missing keywords into a clean Python list
                missing_items = [item.strip() for item in st.session_state.missing_kw.split(",") if item.strip()]
                
                if missing_items:
                    st.markdown("##### Click to select the keywords you want to add:")
                    
                    # 1. Use a dictionary to track which keyword buttons are selected
                    selected_keywords = []
                    
                    # Display them nicely as individual selection checkboxes
                    for item in missing_items:
                        # This creates an individual selection item for every keyword
                        if st.checkbox(f"➕ {item}", key=f"chk_{item}"):
                            selected_keywords.append(item)
                    
                    st.markdown("---")
                    
                    # 2. Add the dynamic injection button below your selections
                    if st.button("🚀 Add Selected Keywords to Resume", type="primary", use_container_width=True):
                        if not selected_keywords:
                            st.warning("Please check at least one keyword button above first.")
                        else:
                            # Pull the current tailored resume text from session state
                            current_resume = st.session_state.final_resume
                            
                            # Build a clean plain-text skills append block
                            skills_to_add = ", ".join(selected_keywords)
                            injection_block = f"\n\nADDITIONAL TECHNICAL SKILLS:\n- {skills_to_add}\n"
                            
                            # Append it instantly to the optimized file copy in memory
                            st.session_state.final_resume = current_resume + injection_block
                            
                            # 3. Dynamic Re-evaluation Math: Move selected items from Missing to Matched instantly
                            updated_matched = [i.strip() for i in st.session_state.found_kw.split(",") if i.strip()]
                            updated_matched.extend(selected_keywords)
                            
                            updated_missing = [i for i in missing_items if i not in selected_keywords]
                            
                            # Recalculate your dynamic percentage right on the fly
                            total_kw = len(updated_matched) + len(updated_missing)
                            if total_kw > 0:
                                st.session_state.resume_match_score = int((len(updated_matched) / total_kw) * 100)
                            
                            # Save the freshly balanced collections back to session state variables
                            st.session_state.found_kw = ", ".join(updated_matched)
                            st.session_state.missing_kw = ", ".join(updated_missing)
                            
                            st.success(f"Successfully injected [{skills_to_add}] into your Optimized Resume! Your Match Score has updated.")
                            st.rerun()
                else:
                    st.write("Your tech stack perfectly overlaps with the target JD!")

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