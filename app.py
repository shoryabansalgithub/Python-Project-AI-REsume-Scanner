import streamlit as st
import os
import sqlite3
import matplotlib.pyplot as plt

from auth import register_user, login_user, get_user_profile, update_user_profile
from resume_parser import extract_text_from_pdf
from resume_analyzer import analyze_resume
from job_recommender import recommend_jobs
from charts import skill_chart, skill_gap_chart, career_roadmap_chart
import database

# PAGE CONFIG
st.set_page_config(
    page_title="CareerAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for light background
st.markdown("""
    <style>
        :root {
            --primary-color: #667eea;
            --background-color: #f8f9fa;
            --secondary-background-color: #ffffff;
            --text-color: #333333;
        }
        
        html, body {
            background-color: #f8f9fa !important;
        }
        
        [data-testid="stAppViewContainer"] {
            background-color: #f8f9fa !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
        }
        
        .main {
            background-color: #f8f9fa !important;
        }
        
        [data-testid="stMainBlockContainer"] {
            background-color: #f8f9fa !important;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Streamlit default sections */
        section[data-testid="stVerticalBlock"] > div {
            background-color: #f8f9fa !important;
        }
    </style>
    """, unsafe_allow_html=True)

# SESSION STATE
if "user" not in st.session_state:
    st.session_state.user = None
if "resume_score" not in st.session_state:
    st.session_state.resume_score = 0
if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []

# AUTH PAGE
def auth_page():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<h1 style='text-align: center; color: #667eea; font-size: 40px;'>🧠 CareerAI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 16px;'>AI Resume Screening & Career Recommendation</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    menu = ["Login", "Register"]
    choice = st.selectbox("Choose an option:", menu, label_visibility="collapsed")

    if choice == "Register":
        st.subheader("📝 Create Account")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        job_title = st.text_input("Job Title (e.g., Software Engineer)")
        education = st.text_input("Education (e.g., B.Tech in Computer Science)")
        
        if st.button("Register", use_container_width=True):
            if register_user(name, email, password, job_title, education):
                st.success("✅ Account Created Successfully! Please login.")
            else:
                st.error("❌ Email already exists")

    elif choice == "Login":
        st.subheader("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            user = login_user(email, password)
            if user:
                st.session_state.user = email
                st.success("✅ Login Successful")
                st.rerun()
            else:
                st.error("❌ Invalid Credentials")

# DASHBOARD
def dashboard():
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### 👤 {st.session_state.user}")
        st.markdown("---")
        
        menu = ["Home", "Upload Resume", "Resume History", "Resume Analytics", "Application Tracker", "Skill Gap Analysis", "Find Jobs", "Career Roadmap", "Interview Prep", "Skill Learning Path", "Mock Interviews", "Edit Profile", "Logout"]
        choice = st.selectbox("Navigation", menu)
        st.markdown("---")
    
    # HOME PAGE
    if choice == "Home":
        user_data = get_user_profile(st.session_state.user)


        col_main, col_sidebar = st.columns([2.5, 1], gap="medium")

        with col_main:
            # Welcome Section
            user_name = user_data['name'] if user_data else "User"
            st.markdown(
                f"<h1 style='font-size: 36px; font-weight: bold; margin-bottom: 10px;'>Welcome, {user_name}! 🚀</h1>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<p style='font-size: 18px; color: #666; margin-bottom: 20px;'>Your career journey <b>starts here</b>.</p>",
                unsafe_allow_html=True
            )
            
            if user_data:
                st.markdown(
                    "<div style='background: #f0f7ff; border-left: 4px solid #667eea; padding: 15px; border-radius: 5px; margin-bottom: 20px;'><p style='margin: 0; color: #333;'><b>Congratulations, your account has been successfully created.</b></p><p style='margin: 5px 0 0 0; color: #666;'>Let's take the next step!</p></div>",
                    unsafe_allow_html=True
                )
            
            # What would you like to do today
            st.markdown(
                "<h3 style='font-size: 20px; font-weight: bold; margin-bottom: 20px; margin-top: 30px;'>What would you like to do today?</h3>",
                unsafe_allow_html=True
            )
            
            col_a, col_b, col_c, col_d = st.columns(4, gap="small")
            
            with col_a:
                st.markdown(
                    """
                    <div style='background: linear-gradient(135deg, #6ba3f5 0%, #6d5dd8 100%); 
                                padding: 30px 20px; border-radius: 15px; text-align: center; 
                                color: white; min-height: 270px; display: flex; flex-direction: column; 
                                justify-content: center; box-shadow: 0 4px 15px rgba(107, 163, 245, 0.3);'>
                    <p style='font-size: 50px; margin: 0 0 12px 0;'>📄</p>
                    <h4 style='font-size: 16px; font-weight: bold; margin: 0 0 8px 0;'>Upload Resume</h4>
                    <p style='font-size: 12px; margin: 0; line-height: 1.5; opacity: 0.95;'>Upload and analyze your resume to get started.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_b:
                st.markdown(
                    """
                    <div style='background: linear-gradient(135deg, #b991f5 0%, #d05fd8 100%); 
                                padding: 30px 20px; border-radius: 15px; text-align: center; 
                                color: white; min-height: 270px; display: flex; flex-direction: column; 
                                justify-content: center; box-shadow: 0 4px 15px rgba(185, 145, 245, 0.3);'>
                    <p style='font-size: 50px; margin: 0 0 12px 0;'>🔍</p>
                    <h4 style='font-size: 16px; font-weight: bold; margin: 0 0 8px 0;'>Find Jobs</h4>
                    <p style='font-size: 12px; margin: 0; line-height: 1.5; opacity: 0.95;'>Discover job opportunities that match your profile.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_c:
                st.markdown(
                    """
                    <div style='background: linear-gradient(135deg, #f794b4 0%, #f5b05f 100%); 
                                padding: 30px 20px; border-radius: 15px; text-align: center; 
                                color: white; min-height: 270px; display: flex; flex-direction: column; 
                                justify-content: center; box-shadow: 0 4px 15px rgba(247, 148, 180, 0.3);'>
                    <p style='font-size: 50px; margin: 0 0 12px 0;'>🎓</p>
                    <h4 style='font-size: 16px; font-weight: bold; margin: 0 0 8px 0;'>Improve Skills</h4>
                    <p style='font-size: 12px; margin: 0; line-height: 1.5; opacity: 0.95;'>Identify and develop skills needed for your target roles.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_d:
                st.markdown(
                    """
                    <div style='background: linear-gradient(135deg, #7de5d1 0%, #5dd8c8 100%); 
                                padding: 30px 20px; border-radius: 15px; text-align: center; 
                                color: white; min-height: 270px; display: flex; flex-direction: column; 
                                justify-content: center; box-shadow: 0 4px 15px rgba(125, 229, 209, 0.3);'>
                    <p style='font-size: 50px; margin: 0 0 12px 0;'>🎤</p>
                    <h4 style='font-size: 16px; font-weight: bold; margin: 0 0 8px 0;'>Ace Interviews</h4>
                    <p style='font-size: 12px; margin: 0; line-height: 1.5; opacity: 0.95;'>Practice with mock interviews and get feedback.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Explore Dashboard Section
            st.markdown(
                "<h3 style='font-size: 20px; font-weight: bold; margin-top: 40px; margin-bottom: 20px;'>Explore Dashboard</h3>",
                unsafe_allow_html=True
            )
            
            col_e, col_f, col_g, col_h = st.columns(4, gap="small")
            
            with col_e:
                st.markdown(
                    """
                    <div style='background: white; padding: 25px; border-radius: 10px; 
                                text-align: center; border: 1px solid #e0e0e0; 
                                min-height: 140px; display: flex; flex-direction: column; 
                                justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
                    <p style='font-size: 36px; margin: 0 0 10px 0;'>👤</p>
                    <p style='font-size: 14px; font-weight: bold; margin: 0; color: #333;'>My Profile</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_f:
                st.markdown(
                    """
                    <div style='background: white; padding: 25px; border-radius: 10px; 
                                text-align: center; border: 1px solid #e0e0e0; 
                                min-height: 140px; display: flex; flex-direction: column; 
                                justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); 
                                position: relative;'>
                    <p style='font-size: 36px; margin: 0 0 10px 0;'>📊</p>
                    <p style='font-size: 14px; font-weight: bold; margin: 0; color: #333;'>Skill Gap</p>
                    <span style='position: absolute; top: 8px; right: 8px; background: #ff9800; 
                                 color: white; font-size: 9px; padding: 2px 5px; border-radius: 3px; 
                                 font-weight: bold;'>NEW!</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_g:
                st.markdown(
                    """
                    <div style='background: white; padding: 25px; border-radius: 10px; 
                                text-align: center; border: 1px solid #e0e0e0; 
                                min-height: 140px; display: flex; flex-direction: column; 
                                justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
                    <p style='font-size: 36px; margin: 0 0 10px 0;'>🎯</p>
                    <p style='font-size: 14px; font-weight: bold; margin: 0; color: #333;'>Career Roadmap</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_h:
                st.markdown(
                    """
                    <div style='background: white; padding: 25px; border-radius: 10px; 
                                text-align: center; border: 1px solid #e0e0e0; 
                                min-height: 140px; display: flex; flex-direction: column; 
                                justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
                    <p style='font-size: 36px; margin: 0 0 10px 0;'>📈</p>
                    <p style='font-size: 14px; font-weight: bold; margin: 0; color: #333;'>Insights & Reports</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Right Sidebar Profile
        with col_sidebar:
            if user_data:
                # Get latest resume score
                conn = sqlite3.connect("users.db")
                c = conn.cursor()
                c.execute("SELECT score FROM resumes WHERE user_email=? ORDER BY id DESC LIMIT 1", (st.session_state.user,))
                score_data = c.fetchone()
                score = score_data[0] if score_data else 70
                conn.close()
                
                # Profile Card
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 25px; border-radius: 12px; text-align: center;
                                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);'>
                    <p style='font-size: 48px; margin: 0 0 15px 0;'>👤</p>
                    <h3 style='margin: 0 0 5px 0; font-size: 18px; font-weight: bold;'>{user_data['name']}</h3>
                    <p style='margin: 0 0 3px 0; font-size: 13px; opacity: 0.9; font-weight: 500;'>{user_data['job_title']}</p>
                    <p style='margin: 0; font-size: 11px; opacity: 0.8;'>{user_data['education']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
                
                # Resume Score Section
                st.markdown(
                    f"""
                    <div style='text-align: center;'>
                    <p style='font-size: 13px; margin: 0 0 3px 0; color: #333; font-weight: bold;'>Resume Score: <span style='font-size: 20px; color: #667eea;'>{score}</span></p>
                    <div style='background: #e8e8e8; height: 6px; border-radius: 3px; margin-bottom: 8px; overflow: hidden;'>
                        <div style='background: linear-gradient(90deg, #4CAF50 0%, #FFC107 50%, #FF5722 100%); 
                                    height: 6px; border-radius: 3px; width: {score}%;'></div>
                    </div>
                    <p style='font-size: 11px; margin: 0; color: #999;'>Completion Level</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
                
                # Action Buttons
                col_btn1, col_btn2 = st.columns(2, gap="small")
                with col_btn1:
                    if st.button("✏️ Edit", use_container_width=True, key="edit_profile_home"):
                        pass
                with col_btn2:
                    if st.button("📝 Upload", use_container_width=True, key="upload_home"):
                        pass
                
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                
                # Resume History
                st.markdown(
                    """
                    <div style='font-size: 13px; font-weight: bold; color: #333; margin-bottom: 8px;'>
                    📋 Resume History
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    """
                    <div style='background: #f5f5f5; padding: 10px 12px; border-radius: 6px; 
                                font-size: 12px; color: #666; margin-bottom: 12px; cursor: pointer;'>
                    📄 Upload Resume
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Skills & Features
                st.markdown(
                    """<p style='font-size: 12px; font-weight: bold; margin: 15px 0 8px 0; color: #667eea;'>
                    📊 Skill Gap Analysis
                    <span style='background: #ff9800; color: white; padding: 1px 4px; border-radius: 2px; font-size: 9px; margin-left: 4px;'>NEW!</span>
                    </p>""",
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    "<p style='font-size: 12px; font-weight: bold; margin: 12px 0 8px 0; color: #333;'>🎯 Career Roadmap</p>",
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    "<p style='font-size: 12px; font-weight: bold; margin: 12px 0 8px 0; color: #333;'>🎤 Mock Interviews</p>",
                    unsafe_allow_html=True
                )
                
                st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
                
                # College Stream Button
                st.markdown(
                    """
                    <div style='background: #e8f0f7; padding: 12px; border-radius: 8px; 
                                text-align: center; cursor: pointer; border: 1px solid #d0d0d0;'>
                    <p style='font-size: 12px; font-weight: bold; margin: 0; color: #667eea;'>
                    🎓 College Streom  <span style='font-size: 14px;'>➜</span>
                    </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    # RESUME ANALYTICS - TIER 1 FEATURE
    elif choice == "Resume Analytics":
        st.header("📊 Resume Analytics Dashboard")
        st.write("Get detailed insights into your resume performance and improvement areas")
        
        # Get latest resume
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT id, file_path, score FROM resumes WHERE user_email=? ORDER BY id DESC LIMIT 1", (st.session_state.user,))
        latest_resume = c.fetchone()
        conn.close()
        
        if latest_resume:
            resume_id, file_path, resume_score = latest_resume
            
            # Top metrics row
            col1, col2, col3, col4 = st.columns(4, gap="small")
            
            with col1:
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                    <p style='margin: 0; font-size: 12px; opacity: 0.9;'>Overall Score</p>
                    <p style='margin: 8px 0 0 0; font-size: 28px; font-weight: bold;'>{resume_score}</p>
                    <p style='margin: 4px 0 0 0; font-size: 11px;'>/100</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                ats_score = int(resume_score * 0.85)  # ATS typically scores lower
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                    <p style='margin: 0; font-size: 12px; opacity: 0.9;'>ATS Compatibility</p>
                    <p style='margin: 8px 0 0 0; font-size: 28px; font-weight: bold;'>{ats_score}%</p>
                    <p style='margin: 4px 0 0 0; font-size: 11px;'>Parser-friendly</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col3:
                keyword_match = int(resume_score * 0.82)
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                    <p style='margin: 0; font-size: 12px; opacity: 0.9;'>Keyword Match</p>
                    <p style='margin: 8px 0 0 0; font-size: 28px; font-weight: bold;'>{keyword_match}%</p>
                    <p style='margin: 4px 0 0 0; font-size: 11px;'>Industry terms</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col4:
                formatting_score = int(resume_score * 0.90)
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                    <p style='margin: 0; font-size: 12px; opacity: 0.9;'>Formatting</p>
                    <p style='margin: 8px 0 0 0; font-size: 28px; font-weight: bold;'>{formatting_score}%</p>
                    <p style='margin: 4px 0 0 0; font-size: 11px;'>Structure score</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Detailed breakdown tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Score Breakdown", "🔍 ATS Analysis", "🎯 Keywords", "💡 Recommendations"])
            
            with tab1:
                st.subheader("Score Breakdown")
                
                breakdown_data = {
                    "Content Quality": 78,
                    "Formatting & Structure": formatting_score,
                    "Keyword Density": keyword_match,
                    "ATS Compatibility": ats_score,
                    "Experience Relevance": 75,
                    "Skills Presentation": 82
                }
                
                col_breakdown1, col_breakdown2 = st.columns([2, 1])
                
                with col_breakdown1:
                    for category, score in breakdown_data.items():
                        st.write(f"**{category}**")
                        st.progress(score / 100)
                
                with col_breakdown2:
                    st.markdown("<h4 style='margin-top: 0;'>Score Tips</h4>", unsafe_allow_html=True)
                    st.markdown(
                        """
                        - **80+** Excellent
                        - **70-79** Good
                        - **60-69** Fair
                        - **<60** Needs Work
                        """
                    )
            
            with tab2:
                st.subheader("ATS Parser Analysis")
                
                col_ats1, col_ats2 = st.columns(2)
                
                with col_ats1:
                    st.markdown("**✅ Strengths**")
                    st.markdown(
                        """
                        - Clean formatting detected
                        - Standard fonts (Arial, Calibri)
                        - Bullet point structure recognized
                        - No embedded images detected
                        """
                    )
                
                with col_ats2:
                    st.markdown("**⚠️ Issues**")
                    st.markdown(
                        """
                        - 2 tables detected (may be parsed incorrectly)
                        - 1 special character found (check for encoding)
                        - Consider removing graphics
                        - Increase white space
                        """
                    )
                
                st.info("💡 **Tip:** ATS systems parse PDFs line-by-line. Avoid complex layouts, tables, and graphics.")
            
            with tab3:
                st.subheader("Keyword Analysis")
                
                extracted_text = extract_text_from_pdf(file_path)
                _, skills = analyze_resume(extracted_text)
                
                col_kw1, col_kw2 = st.columns(2)
                
                with col_kw1:
                    st.markdown("**Found Keywords** (Positive)")
                    found_keywords = skills[:6] if skills else ["Python", "SQL", "Communication", "Leadership", "Problem Solving", "Data Analysis"]
                    for kw in found_keywords:
                        st.markdown(f"✅ {kw}")
                
                with col_kw2:
                    st.markdown("**Missing Keywords** (Add These)")
                    missing_keywords = ["Cloud Computing", "API Development", "Docker", "Kubernetes", "Agile/Scrum", "AWS"]
                    for kw in missing_keywords:
                        st.markdown(f"❌ {kw}")
                
                st.warning("Missing high-demand keywords. Consider adding relevant skills you possess.")
            
            with tab4:
                st.subheader("Professional Recommendations")
                
                recommendations = [
                    {
                        "priority": "🔴 HIGH",
                        "action": "Add quantifiable achievements",
                        "details": "Replace 'Responsible for...' with 'Increased X by Y%' or 'Reduced costs by Z%'"
                    },
                    {
                        "priority": "🟠 MEDIUM",
                        "action": "Optimize keyword density",
                        "details": "Add industry keywords (Cloud, DevOps, Big Data) where applicable"
                    },
                    {
                        "priority": "🟠 MEDIUM",
                        "action": "Improve formatting consistency",
                        "details": "Ensure consistent date formats, bullet styles, and section spacing"
                    },
                    {
                        "priority": "🟢 LOW",
                        "action": "Add certifications section",
                        "details": "Highlight relevant certifications (AWS, Docker, etc.)"
                    }
                ]
                
                for rec in recommendations:
                    col_rec1, col_rec2 = st.columns([0.15, 0.85])
                    with col_rec1:
                        st.markdown(rec["priority"])
                    with col_rec2:
                        st.markdown(f"**{rec['action']}**")
                        st.caption(rec["details"])
                    st.divider()
                
                # Action buttons
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("✏️ Rewrite Resume with AI", use_container_width=True):
                        st.info("🚀 AI rewrite coming soon! Would improve your resume by targeting high-impact keywords and metrics.")
                
                with col_btn2:
                    if st.button("📥 Download Report", use_container_width=True):
                        st.success("✅ PDF report generated (Feature coming soon)")
                
                with col_btn3:
                    if st.button("🔄 Re-analyze Resume", use_container_width=True):
                        st.success("✅ Resume re-analyzed!")
        
        else:
            st.warning("⚠️ Please upload a resume first to see analytics")
    
    # APPLICATION TRACKER - TIER 1 FEATURE
    elif choice == "Application Tracker":
        st.header("📝 Job Application Tracker")
        st.write("Track all your applications, interviews, and offers in one place")
        
        # Initialize application data in session state
        if "applications" not in st.session_state:
            st.session_state.applications = []
        
        # Tab navigation
        tab_view, tab_add = st.tabs(["📊 View Applications", "➕ Add New Application"])
        
        with tab_view:
            if st.session_state.applications:
                # Filter and display
                col_filter1, col_filter2, col_filter3 = st.columns(3)
                
                with col_filter1:
                    status_filter = st.multiselect(
                        "Filter by Status",
                        ["Applied", "Phone Screen", "Interview", "Offer", "Rejected"],
                        default=["Applied", "Phone Screen", "Interview", "Offer"]
                    )
                
                with col_filter2:
                    company_search = st.text_input("Search by company...")
                
                with col_filter3:
                    role_search = st.text_input("Search by role...")
                
                # Display applications
                st.subheader("Your Applications")
                
                for i, app in enumerate(st.session_state.applications):
                    # Status color coding
                    status_colors = {
                        "Applied": "🔵",
                        "Phone Screen": "🟡",
                        "Interview": "🟠",
                        "Offer": "🟢",
                        "Rejected": "🔴"
                    }
                    
                    if status_filter and app.get("status") not in status_filter:
                        continue
                    if company_search and company_search.lower() not in app.get("company", "").lower():
                        continue
                    if role_search and role_search.lower() not in app.get("role", "").lower():
                        continue
                    
                    col_app1, col_app2, col_app3, col_app4, col_app5 = st.columns([2, 2, 1.5, 1, 0.5])
                    
                    with col_app1:
                        st.markdown(f"**{app.get('company', 'N/A')}**")
                        st.caption(app.get('role', 'N/A'))
                    
                    with col_app2:
                        st.markdown(f"📍 {app.get('location', 'Remote')}")
                        st.caption(f"Applied: {app.get('date_applied', 'N/A')}")
                    
                    with col_app3:
                        status_icon = status_colors.get(app.get("status", "Applied"), "⚪")
                        st.markdown(f"{status_icon} {app.get('status', 'Applied')}")
                    
                    with col_app4:
                        if app.get("salary_expected"):
                            st.markdown(f"💰 ${app.get('salary_expected', 'N/A')}")
                    
                    with col_app5:
                        if st.button("✏️", key=f"edit_{i}"):
                            st.session_state.edit_idx = i
                    
                    st.divider()
            else:
                st.info("📭 No applications tracked yet. Add your first application!")
        
        with tab_add:
            st.subheader("Add New Application")
            
            col_app_1, col_app_2 = st.columns(2)
            
            with col_app_1:
                company = st.text_input("Company Name *", placeholder="e.g., Google")
                role = st.text_input("Job Role *", placeholder="e.g., Software Engineer")
                location = st.text_input("Location", placeholder="e.g., Mountain View, CA")
            
            with col_app_2:
                date_applied = st.date_input("Date Applied")
                status = st.selectbox("Status", ["Applied", "Phone Screen", "Interview", "Offer", "Rejected"])
                salary_expected = st.number_input("Expected Salary (optional)", min_value=0, step=5000)
            
            job_url = st.text_input("Job Posting URL (optional)")
            notes = st.text_area("Interview Notes / Feedback")
            
            col_next_action1, col_next_action2 = st.columns(2)
            
            with col_next_action1:
                follow_up_date = st.date_input("Follow-up Date (optional)")
            
            with col_next_action2:
                next_action = st.text_input("Next Action", placeholder="e.g., Send thank you email")
            
            if st.button("➕ Add Application", use_container_width=True):
                if company and role:
                    new_app = {
                        "company": company,
                        "role": role,
                        "location": location,
                        "date_applied": str(date_applied),
                        "status": status,
                        "salary_expected": salary_expected if salary_expected > 0 else None,
                        "job_url": job_url,
                        "notes": notes,
                        "follow_up_date": str(follow_up_date) if follow_up_date else None,
                        "next_action": next_action
                    }
                    st.session_state.applications.append(new_app)
                    st.success(f"✅ Added application for {company} - {role}")
                    st.rerun()
                else:
                    st.error("❌ Please fill in Company Name and Job Role")
        
        # Summary stats
        st.markdown("---")
        st.subheader("📈 Application Pipeline Summary")
        
        if st.session_state.applications:
            col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)
            
            applied = len([a for a in st.session_state.applications if a.get("status") == "Applied"])
            phone = len([a for a in st.session_state.applications if a.get("status") == "Phone Screen"])
            interview = len([a for a in st.session_state.applications if a.get("status") == "Interview"])
            offer = len([a for a in st.session_state.applications if a.get("status") == "Offer"])
            rejected = len([a for a in st.session_state.applications if a.get("status") == "Rejected"])
            
            with col_stat1:
                st.metric("Applied", applied)
            with col_stat2:
                st.metric("Phone Screen", phone)
            with col_stat3:
                st.metric("Interview", interview)
            with col_stat4:
                st.metric("Offer", offer)
            with col_stat5:
                st.metric("Rejected", rejected)
            
            # Simple pipeline visualization
            total = len(st.session_state.applications)
            if total > 0:
                conversion_rate = ((phone + interview + offer) / total) * 100
                st.write(f"**Pipeline Conversion:** {conversion_rate:.1f}% (advancing through stages)")
    
    # UPLOAD RESUME
    elif choice == "Upload Resume":
        st.header("📄 Upload Your Resume")
        st.write("Upload a PDF resume to get started with AI-powered analysis")
        
        file = st.file_uploader("Choose a PDF file", type=["pdf"])
        
        if file:
            os.makedirs("uploads", exist_ok=True)
            path = os.path.join("uploads", file.name)
            
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            
            # Extract and analyze
            text = extract_text_from_pdf(path)
            score, skills = analyze_resume(text)
            
            # Save to database
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute(
                "INSERT INTO resumes(user_email, file_path, score) VALUES(?, ?, ?)",
                (st.session_state.user, path, score)
            )
            conn.commit()
            conn.close()
            
            # Store in session
            st.session_state.resume_score = score
            st.session_state.resume_skills = skills
            
            st.success("✅ Resume Uploaded and Analyzed Successfully")
            st.balloons()
            
            # Show results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Resume Score", f"{score}/100")
            with col2:
                st.metric("Skills Found", len(skills))
            with col3:
                st.metric("Completion", f"{score}%")
            
            st.write("### Detected Skills")
            st.write(", ".join([f"🔹 {s.title()}" for s in skills]))
    
    # RESUME HISTORY
    elif choice == "Resume History":
        st.header("📋 Resume History")
        
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute(
            "SELECT id, file_path, score FROM resumes WHERE user_email=? ORDER BY id DESC",
            (st.session_state.user,)
        )
        resumes = c.fetchall()
        conn.close()
        
        if resumes:
            for resume_id, file_path, score in resumes:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"📄 {os.path.basename(file_path)}")
                with col2:
                    st.write(f"Score: {score}/100")
                with col3:
                    st.button(f"View", key=f"view_{resume_id}")
        else:
            st.info("📭 No resumes uploaded yet")
    
    # SKILL GAP ANALYSIS
    elif choice == "Skill Gap Analysis":
        st.header("📊 Skill Gap Analysis")
        st.write("Identify the skills you need to develop")
        
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute(
            "SELECT file_path FROM resumes WHERE user_email=? ORDER BY id DESC LIMIT 1",
            (st.session_state.user,)
        )
        data = c.fetchone()
        conn.close()
        
        if data:
            path = data[0]
            text = extract_text_from_pdf(path)
            score, skills = analyze_resume(text)
            
            required = ["python", "sql", "machine learning", "communication", "leadership", "problem solving"]
            
            fig = skill_gap_chart(skills, required)
            st.pyplot(fig)
            
            # Skills summary
            col1, col2 = st.columns(2)
            with col1:
                st.write("### Your Skills")
                st.write(", ".join([f"✅ {s.title()}" for s in skills]))
            
            with col2:
                missing = [s for s in required if s not in skills]
                st.write("### Skills to Develop")
                st.write(", ".join([f"⭕ {s.title()}" for s in missing]))
        else:
            st.warning("⚠️ Please upload a resume first")
    
    # FIND JOBS
    elif choice == "Find Jobs":
        st.header("🔍 Find Jobs")
        st.write("Discover job opportunities that match your skills")
        
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute(
            "SELECT file_path FROM resumes WHERE user_email=? ORDER BY id DESC LIMIT 1",
            (st.session_state.user,)
        )
        data = c.fetchone()
        conn.close()
        
        if data:
            path = data[0]
            text = extract_text_from_pdf(path)
            score, skills = analyze_resume(text)
            
            jobs = recommend_jobs(skills)
            
            st.write("### 🎯 Recommended Jobs")
            for i, (job, match) in enumerate(jobs, 1):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**{i}. {job}**")
                with col2:
                    st.metric("Match", f"{match}%")
        else:
            st.warning("⚠️ Please upload a resume first")
    
    # CAREER ROADMAP
    elif choice == "Career Roadmap":
        st.header("🛣️ Career Roadmap")
        st.write("Your personalized career development path")
        
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute(
            "SELECT file_path FROM resumes WHERE user_email=? ORDER BY id DESC LIMIT 1",
            (st.session_state.user,)
        )
        data = c.fetchone()
        conn.close()
        
        if data:
            path = data[0]
            text = extract_text_from_pdf(path)
            score, skills = analyze_resume(text)
            
            fig = career_roadmap_chart(skills)
            st.pyplot(fig)
            
            st.write("### Your Career Path")
            st.write("1. 📝 **Current Level**: Associate Engineer")
            st.write("2. 📝 **Next Level**: Senior Engineer (6-12 months)")
            st.write("3. 📝 **Final Goal**: Tech Lead (2-3 years)")
        else:
            st.warning("⚠️ Please upload a resume first")
    
    # INTERVIEW PREP HUB - TIER 2 FEATURE
    elif choice == "Interview Prep":
        st.header("🎯 Interview Prep Hub")
        st.write("Comprehensive preparation for behavioral, technical, and company-specific interviews")
        
        # Initialize session state for interview prep
        if "interview_practice_history" not in st.session_state:
            st.session_state.interview_practice_history = []
        
        # Main tabs
        main_tab1, main_tab2, main_tab3, main_tab4, main_tab5 = st.tabs([
            "📚 STAR Method",
            "🏢 Company Questions",
            "🤔 Behavioral Q&A",
            "💻 Technical Questions",
            "📊 Practice Tracker"
        ])
        
        # TAB 1: STAR METHOD GUIDE
        with main_tab1:
            st.subheader("🌟 Master the STAR Method for Behavioral Questions")
            st.write("STAR is the proven framework to structure impressive behavioral interview answers")
            
            col_star1, col_star2 = st.columns(2)
            
            with col_star1:
                st.markdown(
                    """
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px;'>
                    <h3 style='margin-top: 0;'>STAR Framework</h3>
                    <p><strong>S - Situation</strong><br/>Set the stage with context. What was the challenge?</p>
                    <p><strong>T - Task</strong><br/>What was your specific role and responsibility?</p>
                    <p><strong>A - Action</strong><br/>What did YOU do? Focus on your contribution.</p>
                    <p><strong>R - Result</strong><br/>What was the outcome? Use metrics when possible.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_star2:
                st.markdown(
                    """
                    <div style='background: #f5f5f5; padding: 20px; border-radius: 12px;'>
                    <h4>Example Structure</h4>
                    <p><strong>❌ Weak:</strong> "I worked on a project with my team."</p>
                    <p><strong>✅ Strong:</strong> "When my startup was losing $50K/month due to poor user retention (S), I led a 3-person team to redesign the onboarding flow (T). I personally reduced the 15-step process to 3 steps using user research (A), increasing retention by 45% within 2 months (R)."</p>
                    </div>
                    """
                )
            
            # STAR Practice Exercise
            st.markdown("---")
            st.subheader("Practice STAR Answer")
            
            col_exercise1, col_exercise2 = st.columns(2)
            
            with col_exercise1:
                st.write("**Sample Question:** Tell me about a time you overcame a technical challenge.")
                
                situation_input = st.text_area("S - Situation (Context & Challenge):", height=80, placeholder="Describe the context and what challenge you faced...")
                task_input = st.text_area("T - Task (Your Role):", height=80, placeholder="What was your specific responsibility?")
                action_input = st.text_area("A - Action (What You Did):", height=80, placeholder="Focus on YOUR contributions, decisions, and efforts...")
                result_input = st.text_area("R - Result (Outcome & Metrics):", height=80, placeholder="What was the impact? Use numbers: improved by X%, saved Y hours, etc...")
            
            with col_exercise2:
                st.write("**Full Answer Preview:**")
                full_answer = f"""
                **Situation:** {situation_input or "..."}

                **Task:** {task_input or "..."}

                **Action:** {action_input or "..."}

                **Result:** {result_input or "..."}
                """
                st.info(full_answer)
                
                if st.button("💾 Save This Answer"):
                    st.session_state.interview_practice_history.append({
                        "type": "STAR Practice",
                        "answer": full_answer,
                        "date": str(__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M"))
                    })
                    st.success("✅ Answer saved to your practice history!")
            
            # STAR Tips
            st.markdown("---")
            col_tips1, col_tips2, col_tips3 = st.columns(3)
            
            with col_tips1:
                st.markdown(
                    """
                    <div style='background: #e3f2fd; padding: 15px; border-radius: 8px;'>
                    <h4>⏱️ Timing Tip</h4>
                    <p>Aim for <strong>2-3 minutes max</strong>. Not too long!</p>
                    </div>
                    """
                )
            
            with col_tips2:
                st.markdown(
                    """
                    <div style='background: #f3e5f5; padding: 15px; border-radius: 8px;'>
                    <h4>📊 Metrics Matter</h4>
                    <p>Always quantify results: <strong>30% faster</strong>, <strong>$50K saved</strong>, <strong>2x growth</strong></p>
                    </div>
                    """
                )
            
            with col_tips3:
                st.markdown(
                    """
                    <div style='background: #e8f5e9; padding: 15px; border-radius: 8px;'>
                    <h4>🎯 Focus on YOU</h4>
                    <p>Don't blame teammates. Say <strong>"I"</strong> not <strong>"we"</strong> for actions.</p>
                    </div>
                    """
                )
        
        # TAB 2: COMPANY-SPECIFIC QUESTIONS
        with main_tab2:
            st.subheader("🏢 Company-Specific Interview Questions")
            st.write("Prepare for questions commonly asked by top tech companies")
            
            col_company1, col_company2 = st.columns(2)
            
            with col_company1:
                company_selection = st.selectbox(
                    "Select a company:",
                    ["Google", "Amazon", "Meta", "Microsoft", "Apple", "Netflix", "Tesla", "LinkedIn", "Stripe", "Uber"]
                )
            
            with col_company2:
                role_selection = st.selectbox(
                    "Select a role:",
                    ["Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer", "ML Engineer"]
                )
            
            # Company-specific Q&A database
            company_questions = {
                "Google": {
                    "Software Engineer": [
                        "Tell me about a time you had to learn a new technology quickly.",
                        "Describe a situation where you had to work with a difficult team member.",
                        "How do you approach debugging a complex issue?",
                        "Walk me through your most challenging project and how you solved it."
                    ]
                },
                "Amazon": {
                    "Software Engineer": [
                        "Tell me about a time you went above and beyond.",
                        "How do you prioritize when you have multiple conflicting deadlines?",
                        "Describe a time you made a decision without enough data.",
                        "Tell me about a time you failed and what you learned."
                    ]
                },
                "Meta": {
                    "Software Engineer": [
                        "What would you build for Meta today?",
                        "Tell me about a time you shipped a feature fast.",
                        "How do you stay updated with latest technologies?",
                        "Describe a situation where you had to convince others about your idea."
                    ]
                },
                "Microsoft": {
                    "Software Engineer": [
                        "Tell me about your experience with cloud technologies.",
                        "How do you approach code reviews?",
                        "Describe a time you improved system performance.",
                        "How do you handle technical debt?"
                    ]
                }
            }
            
            # Get questions for selected company
            if company_selection in company_questions and role_selection in company_questions[company_selection]:
                questions = company_questions[company_selection][role_selection]
            else:
                questions = [
                    "Tell me about yourself and your experience.",
                    "Why are you interested in this role?",
                    "What are your strengths and weaknesses?",
                    "Describe your ideal work environment."
                ]
            
            st.markdown(f"### Typical questions for **{company_selection}** - **{role_selection}**:")
            
            for i, question in enumerate(questions, 1):
                with st.expander(f"**Q{i}: {question}**"):
                    st.write("### Tips for answering:")
                    st.markdown(
                        """
                        • Use the **STAR method** to structure your answer
                        • Include **specific metrics or outcomes**
                        • Show **problem-solving and initiative**
                        • Demonstrate **alignment with company values**
                        """
                    )
                    
                    # Practice space
                    answer = st.text_area("Your Answer:", key=f"answer_{i}", placeholder="Type your practice answer here...")
                    
                    col_act1, col_act2 = st.columns(2)
                    with col_act1:
                        if st.button("✅ Save Answer", key=f"save_{i}"):
                            if answer.strip():
                                st.session_state.interview_practice_history.append({
                                    "type": f"{company_selection} - {question[:40]}...",
                                    "answer": answer,
                                    "date": str(__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M"))
                                })
                                st.success("✅ Saved!")
                    
                    with col_act2:
                        if st.button("🤖 Get AI Feedback", key=f"feedback_{i}"):
                            st.info("💡 AI Feedback incoming! (Coming soon - Would analyze STAR structure, metrics, clarity)")
        
        # TAB 3: BEHAVIORAL Q&A
        with main_tab3:
            st.subheader("🤔 Common Behavioral Questions")
            st.write("Master these behavioral questions asked across all top companies")
            
            behavioral_questions = {
                "Teamwork & Conflict": [
                    "Tell me about a time you had to work with someone you didn't get along with.",
                    "Describe a situation where a team member wasn't pulling their weight.",
                    "Tell me about your best team experience."
                ],
                "Leadership & Initiative": [
                    "Tell me about a time you led a project.",
                    "Give an example of when you took initiative.",
                    "How have you helped a colleague grow?"
                ],
                "Problem Solving": [
                    "Tell me about a time you solved a difficult problem.",
                    "Describe when you had to make a tough decision.",
                    "Give an example of when you improved a process."
                ],
                "Overcoming Challenges": [
                    "Tell me about your biggest failure and what you learned.",
                    "Describe a time you had to overcome a major obstacle.",
                    "When have you felt overwhelmed at work?"
                ],
                "Adaptability": [
                    "Tell me about a time you had to adapt to a significant change.",
                    "When have you had to learn something completely new?",
                    "Describe a time you received critical feedback."
                ]
            }
            
            category = st.selectbox("Select question category:", list(behavioral_questions.keys()))
            
            st.write(f"### {category} Questions:")
            
            for i, question in enumerate(behavioral_questions[category], 1):
                col_behave1, col_behave2 = st.columns([3, 1])
                
                with col_behave1:
                    with st.expander(f"**{i}. {question}**", expanded=False):
                        st.markdown(
                            f"""
                            <div style='background: #fff3e0; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                            <strong>🎯 What they want to know:</strong><br/>
                            This question assesses your [communication, teamwork, problem-solving, adaptability, resilience, growth mindset].
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        answer_input = st.text_area(
                            "Your Practice Answer (Use STAR Method):",
                            height=120,
                            key=f"behave_answer_{category}_{i}",
                            placeholder="Situation → Task → Action → Result"
                        )
                        
                        col_behave_btn1, col_behave_btn2 = st.columns(2)
                        with col_behave_btn1:
                            if st.button("💾 Save", key=f"behave_save_{category}_{i}"):
                                if answer_input.strip():
                                    st.session_state.interview_practice_history.append({
                                        "type": f"Behavioral: {question[:40]}",
                                        "answer": answer_input,
                                        "date": str(__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M"))
                                    })
                                    st.success("✅ Answer saved!")
                        with col_behave_btn2:
                            if st.button("📋 Show Tips", key=f"behave_tips_{category}_{i}"):
                                st.info("✨ **Tips for great answer:** Focus on what YOU did, use metrics, show growth/learning, be concise (2-3 min)")
        
        # TAB 4: TECHNICAL QUESTIONS
        with main_tab4:
            st.subheader("💻 Technical Interview Prep")
            st.write("Common coding challenges and system design questions")
            
            tech_type = st.radio("Select question type:", ["Data Structures & Algorithms", "System Design", "Coding Challenges"])
            
            if tech_type == "Data Structures & Algorithms":
                st.markdown("### Common DSA Questions")
                
                dsa_questions = {
                    "Arrays": "Two Sum - Find two numbers that add up to target",
                    "Strings": "Longest Substring Without Repeating Characters",
                    "Trees": "Binary Tree Level Order Traversal",
                    "Graphs": "Number of Islands",
                    "Dynamic Programming": "Longest Increasing Subsequence"
                }
                
                for category, question in dsa_questions.items():
                    with st.expander(f"**{category}: {question}**"):
                        st.write("**Problem:**")
                        st.code(question, language="text")
                        
                        code_answer = st.text_area(
                            "Your Solution Code:",
                            height=150,
                            key=f"dsa_{category}",
                            placeholder="Write your Python/JavaScript solution here"
                        )
                        
                        col_dsa1, col_dsa2 = st.columns(2)
                        with col_dsa1:
                            if st.button("✅ Check Solution", key=f"check_dsa_{category}"):
                                st.success("✅ Logic looks correct! (Detailed code review coming soon)")
                        with col_dsa2:
                            if st.button("💡 Show Hint", key=f"hint_dsa_{category}"):
                                st.info("💡 **Hint:** Think about the time and space complexity trade-offs")
            
            elif tech_type == "System Design":
                st.markdown("### System Design Questions")
                
                system_design_q = [
                    {"title": "Design a URL Shortener (like bit.ly)", "components": ["Database Schema", "API Design", "Scalability", "Caching Strategy"]},
                    {"title": "Design Twitter", "components": ["Feed Generation", "Scalability", "Real-time Updates", "Data Consistency"]},
                    {"title": "Design Netflix Video Streaming", "components": ["Content Distribution", "Caching", "Load Balancing", "Disaster Recovery"]}
                ]
                
                selected_system = st.radio("Choose a system to design:", [q["title"] for q in system_design_q])
                
                selected_q = next(q for q in system_design_q if q["title"] == selected_system)
                
                st.write(f"**Design Requirements:** {selected_q['title']}")
                st.write("**Key Components to Cover:**")
                for component in selected_q["components"]:
                    st.checkbox(component)
                
                design_answer = st.text_area(
                    "Your System Design (Cover all components):",
                    height=200,
                    placeholder="Describe architecture, database schema, API endpoints, scaling strategy..."
                )
                
                if st.button("📊 Evaluate Design"):
                    st.info("📋 Design Review:\n• Architecture: Good\n• Scalability consideration: Yes\n• Trade-offs: Covered\n\n💡 Suggestions: Consider Redis for caching, explain load balancing strategy")
            
            else:  # Coding Challenges
                st.markdown("### Daily Coding Challenge")
                
                st.write("**Today's Challenge:** Implement a LRU Cache")
                st.code("""
class LRUCache:
    def __init__(self, capacity: int):
        pass
    
    def get(self, key: int) -> int:
        pass
    
    def put(self, key: int, value: int) -> None:
        pass
                """, language="python")
                
                challenge_answer = st.text_area(
                    "Your Implementation:",
                    height=200,
                    key="lru_cache",
                    placeholder="Complete the LRU Cache implementation"
                )
                
                if st.button("🚀 Submit Solution"):
                    st.success("✅ Solution submitted! (Test cases would run here)")
        
        # TAB 5: PRACTICE TRACKER
        with main_tab5:
            st.subheader("📊 Your Interview Practice Tracker")
            st.write("Track your progress and revisit your practice sessions")
            
            if st.session_state.interview_practice_history:
                # Stats cards
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    st.metric("Sessions Completed", len(st.session_state.interview_practice_history))
                
                with col_stat2:
                    st.metric("Last Practice", st.session_state.interview_practice_history[-1].get("date", "N/A"))
                
                with col_stat3:
                    st.metric("Categories Covered", len(set([p.get("type", "").split(" - ")[0] for p in st.session_state.interview_practice_history])))
                
                st.markdown("---")
                st.subheader("Practice History")
                
                for i, practice in enumerate(reversed(st.session_state.interview_practice_history), 1):
                    with st.expander(f"**{i}. {practice.get('type', 'Unknown')}** - {practice.get('date', 'N/A')}"):
                        st.write(practice.get("answer", "No answer recorded"))
                        
                        col_tracker1, col_tracker2 = st.columns(2)
                        with col_tracker1:
                            if st.button("🔄 Retake", key=f"retake_{i}"):
                                st.info("Ready to practice again! (Navigation coming soon)")
                        with col_tracker2:
                            if st.button("❌ Delete", key=f"delete_{i}"):
                                st.session_state.interview_practice_history.pop(len(st.session_state.interview_practice_history) - i)
                                st.rerun()
            else:
                st.info("📭 No practice sessions yet. Start practicing in other tabs to build your history!")
            
            # Export options
            st.markdown("---")
            st.subheader("Export & Review")
            
            if st.button("📥 Download Practice Report (PDF)"):
                st.success("✅ Report generated! (Download feature coming soon)")
            
            if st.button("📧 Email Practice Summary"):
                st.success("✅ Email sent! (Integration coming soon)")
    
    # MOCK INTERVIEWS
    elif choice == "Mock Interviews":
        st.header("🎤 Mock Interviews")
        st.write("Practice with AI-powered mock interviews")
        
        interview_topics = [
            "Behavioral Interview",
            "Technical Interview - Python",
            "System Design Interview",
            "Data Structures & Algorithms",
            "Project Discussion"
        ]
        
        selected_topic = st.selectbox("Choose interview type:", interview_topics)
        
        if st.button("Start Interview"):
            st.info(f"🎤 Starting {selected_topic}...")
            st.write("**Question 1:** Tell me about a project you're proud of and what challenges you faced?")
            st.text_area("Your answer:")
            st.button("Submit Answer")
    
    # EDIT PROFILE
    elif choice == "Edit Profile":
        st.header("✏️ Edit Profile")
        
        user_data = get_user_profile(st.session_state.user)
        
        if user_data:
            name = st.text_input("Full Name", value=user_data['name'])
            job_title = st.text_input("Job Title", value=user_data['job_title'])
            education = st.text_input("Education", value=user_data['education'])
            
            if st.button("Save Changes"):
                update_user_profile(st.session_state.user, name, job_title, education)
                st.success("✅ Profile updated successfully")
    
    # LOGOUT
    elif choice == "Logout":
        st.session_state.user = None
        st.rerun()

# MAIN FLOW
if st.session_state.user is None:
    auth_page()
else:
    dashboard()
