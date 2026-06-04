import streamlit as st
import pypdf
import google.generativeai as genai
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- NEW: ATS-FRIENDLY PDF GENERATION HELPER ---
def convert_text_to_pdf(text_content):
    """Converts pure text/markdown structure into an ATS-friendly, machine-readable PDF byte stream."""
    pdf_buffer = BytesIO()
    
    # Setup document geometry with safe 0.75-inch margins
    doc = SimpleDocTemplate(
        pdf_buffer, 
        pagesize=letter,
        rightMargin=54, leftMargin=54, 
        topMargin=54, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom ATS-optimized typography style (Using clear, standard Helvetica font)
    ats_style = ParagraphStyle(
        'ATS_Normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        spaceAfter=6
    )
    
    story = []
    # Process text line by line, preserving clean formatting
    lines = text_content.split('\n')
    for line in lines:
        if line.strip():
            # Convert raw text into safe paragraph text blocks
            clean_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(clean_line, ats_style))
        else:
            # Replicate empty line breaks gracefully
            story.append(Spacer(1, 8))
            
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


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

    if st.button("🚀 Run Live AI Analysis", type="primary"):
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
                st.success("Inputs verified! Interface logic maps correctly. Ready for live API integration.")
                
                # --- VISUAL PANELS ---
                st.header("2. AI Analysis & Optimized Outputs")
                tab1, tab2, tab3 = st.tabs(["📊 ATS Score & Gaps", "📝 Optimized Resume", "✉️ Drafted Cover Letter"])
                
                with tab1:
                    st.subheader("ATS Match Score & Keyword Analysis")
                    st.metric(label="Estimated ATS Match Score", value="-- %", delta="Pending Live Call")
                    st.info("Missing keywords and professional alignment details will stream here.")
                    
                with tab2:
                    st.subheader("Editable Optimized Resume Draft")
                    edited_resume = st.text_area("Your Optimized Resume Content", value="[Your AI-tailored resume draft will generate here word-by-word in real time...]", height=300)
                    st.download_button(
                        label="📥 Download Tailored Resume (.pdf)", 
                        data=convert_text_to_pdf(edited_resume), 
                        file_name="tailored_resume.pdf", 
                        mime="application/pdf"
                    )
                    
                with tab3:
                    st.subheader("Tailored Cover Letter Draft")
                    if generate_cover_letter:
                        edited_letter = st.text_area("Your Cover Letter Content", value="[Your personalized cover letter tailored specifically to this JD will generate here...]", height=250)
                        st.download_button(
                            label="📥 Download Cover Letter (.pdf)", 
                            data=convert_text_to_pdf(edited_letter), 
                            file_name="cover_letter.pdf", 
                            mime="application/pdf"
                        )
                    else:
                        st.warning("You did not toggle the Cover Letter generation option on the input panel.")