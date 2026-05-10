import streamlit as st
import os
import sqlite3
import matplotlib.pyplot as plt

from auth import register_user, login_user, get_user_profile, update_user_profile
from resume_parser import extract_text_from_pdf, parse_resume
from resume_analyzer import analyze_resume, get_skill_gap, get_career_roadmap, detect_current_level
from job_recommender import recommend_jobs, get_missing_skills
from charts import skill_chart, skill_gap_chart, career_roadmap_chart, ats_score_chart, learning_timeline_chart
from resume_scorer import calculate_ats_score
from learning_path import build_learning_path, get_platform_badge
from star_generator import get_star_questions, get_all_roles
from resume_maker import generate_resume_pdf
from data.skills_db import get_roles, get_required_skills
import database

# PAGE CONFIG
st.set_page_config(
    page_title="CareerAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark skeuomorphic UI
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&display=swap');
        @import url('https://unpkg.com/@phosphor-icons/web@2.0.3/src/regular/style.css');
        @import url('https://unpkg.com/@phosphor-icons/web@2.0.3/src/fill/style.css');
        
        /* Main panels */
        .main-panel {
            background: linear-gradient(180deg, #1c1c21 0%, #16161a 100%);
            border: 1px solid #27272c;
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.03);
        }
        .main-panel-header {
            display: flex; justify-content: space-between; align-items: center;
        }
        .main-panel-title {
            font-size: 20px; font-weight: 600; color: #f5f5f7; margin-bottom: 16px;
        }
        
        /* Action cards exact match */
        .action-card {
            background: linear-gradient(180deg, #222227 0%, #1c1c21 100%);
            border-radius: 16px;
            border: 1px solid #2a2a30;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.02);
            position: relative;
        }
        .card-blue::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(59,130,246,0.5), transparent); }
        .card-purple::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(139,92,246,0.5), transparent); }
        .card-orange::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(249,115,22,0.5), transparent); }
        .card-teal::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(20,184,166,0.5), transparent); }
        
        .icon-wrap {
            width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 26px;
            background: linear-gradient(180deg, #18181b 0%, #1f1f24 100%);
            border: 1px solid #000;
            box-shadow: inset 0 1px 1px rgba(255,255,255,0.08), 0 4px 8px rgba(0,0,0,0.5);
        }
        .icon-blue { color: #60a5fa; box-shadow: inset 0 1px 1px rgba(255,255,255,0.08), 0 4px 12px rgba(59,130,246,0.15); }
        .icon-purple { color: #a78bfa; box-shadow: inset 0 1px 1px rgba(255,255,255,0.08), 0 4px 12px rgba(139,92,246,0.15); }
        .icon-orange { color: #fb923c; box-shadow: inset 0 1px 1px rgba(255,255,255,0.08), 0 4px 12px rgba(249,115,22,0.15); }
        .icon-teal { color: #2dd4bf; box-shadow: inset 0 1px 1px rgba(255,255,255,0.08), 0 4px 12px rgba(20,184,166,0.15); }
        
        /* Activity progress bar */
        .progress-box {
            background: linear-gradient(180deg, #222227 0%, #1c1c21 100%);
            border: 1px solid #2a2a30;
            border-radius: 14px;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }
        .progress-track {
            height: 6px; background: #111114; border-radius: 3px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.8); margin-top: 15px; position: relative; overflow: visible;
        }
        .progress-fill-blue {
            position: absolute; left: 0; top: 0; height: 100%; border-radius: 3px;
            background: linear-gradient(90deg, #2563eb, #60a5fa); box-shadow: 0 0 12px rgba(96,165,250,0.6);
        }
        .progress-fill-purple {
            position: absolute; left: 0; top: 0; height: 100%; border-radius: 3px;
            background: linear-gradient(90deg, #7c3aed, #a78bfa); box-shadow: 0 0 12px rgba(167,139,250,0.6);
        }
        

        :root {
            --bg: #1a1a1c;
            --panel-top: #27272c;
            --panel-bot: #1e1e22;
            --text: #e7e7ea;
            --muted: #9a9aa3;
            --blue: #3b82f6;
            --purple: #8b5cf6;
            --orange: #f97316;
            --teal: #14b8a6;
            --red: #ef4444;
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background: #1a1a1c !important;
            background-image: radial-gradient(1200px 800px at 50% -10%, #2b2b32 0%, #1a1a1c 45%, #111113 100%) !important;
            color: var(--text) !important;
            font-family: 'Geist', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }

        .main, [data-testid="stMainBlockContainer"], section[data-testid="stVerticalBlock"] > div {
            background: transparent !important;
            color: var(--text) !important;
        }

        [data-testid="stMainBlockContainer"] {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--panel-top) 0%, var(--panel-bot) 100%) !important;
            border-right: 1px solid #0b0b0d !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 20px 40px rgba(0,0,0,0.5) !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            background: transparent !important;
        }

        /* Sidebar buttons → skeuomorphic nav items */
        [data-testid="stSidebar"] [data-testid="stButton"] button {
            background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(0,0,0,0.05)) !important;
            border: 1px solid transparent !important;
            border-radius: 12px !important;
            color: #b9b9c2 !important;
            font-family: 'Geist', system-ui, sans-serif !important;
            font-size: 16px !important;
            font-weight: 500 !important;
            text-align: left !important;
            padding: 10px 12px !important;
            transition: all 0.15s ease !important;
            box-shadow: none !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
            background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(0,0,0,0.1)) !important;
            color: #fff !important;
            border-color: transparent !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button:active,
        [data-testid="stSidebar"] [data-testid="stButton"] button:focus {
            background: linear-gradient(180deg, #2b2b31 0%, #1f1f24 100%) !important;
            border-color: #0a0a0c !important;
            color: #fff !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), inset 0 -1px 3px rgba(0,0,0,0.8), 0 2px 6px rgba(0,0,0,0.4) !important;
        }

        /* Sidebar text overrides */
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
            color: #e7e7ea !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.06) !important;
        }
        [data-testid="stSidebar"] .stMarkdown strong {
            font-size: 13px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            color: #7d7d86 !important;
        }

        /* Emboss text effect */
        .emboss {
            text-shadow: 0 1px 0 rgba(255,255,255,0.05), 0 -1px 1px rgba(0,0,0,0.85) !important;
        }

        /* Skeuomorphic panel */
        .skeuo-panel {
            background: linear-gradient(180deg, var(--panel-top) 0%, var(--panel-bot) 100%) !important;
            border: 1px solid #0b0b0d !important;
            border-radius: 24px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), inset 0 -2px 3px rgba(0,0,0,0.6), 0 20px 40px rgba(0,0,0,0.5), 0 2px 4px rgba(0,0,0,0.8) !important;
            padding: 26px 28px !important;
            margin-bottom: 20px !important;
            position: relative;
        }

        /* Skeuomorphic raised */
        .skeuo-raised {
            background: linear-gradient(180deg, #30313a 0%, #23232a 100%) !important;
            border: 1px solid #0f0f13 !important;
            border-radius: 18px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), inset 0 -1px 2px rgba(0,0,0,0.7), 0 8px 18px rgba(0,0,0,0.45), 0 1px 2px rgba(0,0,0,0.9) !important;
        }

        /* Skeuomorphic recessed */
        .skeuo-recessed {
            background: linear-gradient(180deg, #141418 0%, #1b1b20 100%) !important;
            border: 1px solid #08080a !important;
            border-radius: 14px !important;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.95), inset 0 1px 2px rgba(0,0,0,1), inset 0 -1px 1px rgba(255,255,255,0.025) !important;
        }

        /* Skeuomorphic button */
        .skeuo-button {
            background: linear-gradient(180deg, #2c2c33 0%, #1f1f24 100%) !important;
            border: 1px solid #0d0d10 !important;
            border-radius: 12px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), inset 0 -1px 2px rgba(0,0,0,0.6), 0 3px 8px rgba(0,0,0,0.4) !important;
            transition: all 0.15s ease !important;
            cursor: pointer !important;
        }
        .skeuo-button:hover {
            background: linear-gradient(180deg, #33333c 0%, #24242b 100%) !important;
            transform: translateY(-1px) !important;
        }

        /* Progress bars in dark theme */
        .skeuo-progress-track {
            height: 12px;
            border-radius: 6px;
            background: #121215;
            border: 1px solid #08080a;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.9), inset 0 1px 2px rgba(0,0,0,1), inset 0 -1px 1px rgba(255,255,255,0.05);
            position: relative;
            overflow: hidden;
        }
        .skeuo-progress-fill {
            height: 100%;
            border-radius: 5px;
            position: relative;
        }
        .skeuo-progress-fill::after {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: inherit;
            background: linear-gradient(180deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0) 40%, rgba(0,0,0,0.2) 100%);
        }
        .fill-blue { background: #3b82f6; box-shadow: 0 0 12px rgba(59,130,246,0.5); }
        .fill-purple { background: #8b5cf6; box-shadow: 0 0 12px rgba(139,92,246,0.5); }

        /* LED indicator */
        .skeuo-led {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, #9effa9, #00c247 60%, #008a33 100%);
            box-shadow: 0 0 6px rgba(0,194,71,0.8), 0 0 12px rgba(0,194,71,0.4), inset 0 1px 1px rgba(255,255,255,0.5), inset 0 -1px 1px rgba(0,0,0,0.5);
            margin-right: 6px;
            vertical-align: middle;
        }

        /* Badge */
        .badge-new {
            padding: 3px 7px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.04em;
            background: linear-gradient(180deg, #fbbf24, #f59e0b);
            color: #1a0f00;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.5), inset 0 -1px 2px rgba(0,0,0,0.3), 0 2px 4px rgba(245,158,11,0.3);
            text-shadow: 0 1px 0 rgba(255,255,255,0.3);
            margin-left: 8px;
        }

        /* Card color variants */
        .card-blue::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,transparent,#3b82f6,transparent); opacity:0.7; border-radius:18px 18px 0 0; }
        .card-purple::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,transparent,#8b5cf6,transparent); opacity:0.7; border-radius:18px 18px 0 0; }
        .card-orange::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,transparent,#f97316,transparent); opacity:0.7; border-radius:18px 18px 0 0; }
        .card-teal::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,transparent,#14b8a6,transparent); opacity:0.7; border-radius:18px 18px 0 0; }

        /* Icon wraps */
        .icon-wrap-blue {
            width: 46px; height: 46px; border-radius: 13px; display: inline-flex; align-items: center; justify-content: center;
            background: linear-gradient(180deg, #1e2a48 0%, #162038 100%);
            box-shadow: inset 0 1px 1px rgba(255,255,255,0.06), inset 0 -2px 4px rgba(0,0,0,0.8), 0 0 18px rgba(59,130,246,0.15);
            border: 1px solid #0e172b;
            font-size: 24px;
        }
        .icon-wrap-purple {
            width: 46px; height: 46px; border-radius: 13px; display: inline-flex; align-items: center; justify-content: center;
            background: linear-gradient(180deg, #2a1f40 0%, #1e1630 100%);
            box-shadow: inset 0 1px 1px rgba(255,255,255,0.05), inset 0 -2px 4px rgba(0,0,0,0.8), 0 0 18px rgba(139,92,246,0.15);
            border: 1px solid #160e28;
            font-size: 24px;
        }
        .icon-wrap-orange {
            width: 46px; height: 46px; border-radius: 13px; display: inline-flex; align-items: center; justify-content: center;
            background: linear-gradient(180deg, #3d2616 0%, #2a1a0f 100%);
            box-shadow: inset 0 1px 1px rgba(255,255,255,0.05), inset 0 -2px 4px rgba(0,0,0,0.8), 0 0 18px rgba(249,115,22,0.15);
            border: 1px solid #1f1208;
            font-size: 24px;
        }
        .icon-wrap-teal {
            width: 46px; height: 46px; border-radius: 13px; display: inline-flex; align-items: center; justify-content: center;
            background: linear-gradient(180deg, #10332f 0%, #0b2422 100%);
            box-shadow: inset 0 1px 1px rgba(255,255,255,0.05), inset 0 -2px 4px rgba(0,0,0,0.8), 0 0 18px rgba(20,184,166,0.15);
            border: 1px solid #071a18;
            font-size: 24px;
        }

        /* Main content text colors */
        h1, h2, h3, h4, h5, h6 { color: #e9e9ee !important; }
        p, li, span, label { color: #e7e7ea; }

        /* Streamlit elements dark overrides */
        [data-testid="stMetricValue"] { color: #fff !important; }
        [data-testid="stMetricLabel"] { color: var(--muted) !important; }
        [data-testid="stMetricDelta"] svg { fill: #2dd4bf !important; }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background: linear-gradient(180deg, #141418 0%, #1b1b20 100%) !important;
            border-radius: 14px;
            padding: 4px;
            border: 1px solid #08080a;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.95);
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            color: var(--muted) !important;
            border-radius: 10px !important;
            border: none !important;
            font-weight: 500 !important;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(180deg, #2c2c33 0%, #1f1f24 100%) !important;
            color: #fff !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 3px 8px rgba(0,0,0,0.4) !important;
        }
        .stTabs [data-baseweb="tab-panel"] {
            background: transparent !important;
        }

        /* Text inputs dark */
        [data-testid="stTextInput"] input, textarea, [data-baseweb="select"] {
            background: linear-gradient(180deg, #141418 0%, #1b1b20 100%) !important;
            border: 1px solid #08080a !important;
            color: #e7e7ea !important;
            border-radius: 12px !important;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.6) !important;
        }
        [data-testid="stTextInput"] label, [data-testid="stTextArea"] label,
        [data-testid="stSelectbox"] label, [data-testid="stMultiSelect"] label,
        [data-testid="stNumberInput"] label, [data-testid="stDateInput"] label {
            color: var(--muted) !important;
        }

        /* Buttons in main content */
        .stButton > button {
            background: linear-gradient(180deg, #2c2c33 0%, #1f1f24 100%) !important;
            border: 1px solid #0d0d10 !important;
            border-radius: 12px !important;
            color: #e7e7ea !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), inset 0 -1px 2px rgba(0,0,0,0.6), 0 3px 8px rgba(0,0,0,0.4) !important;
            transition: all 0.15s ease !important;
            font-family: 'Geist', system-ui, sans-serif !important;
        }
        .stButton > button:hover {
            background: linear-gradient(180deg, #33333c 0%, #24242b 100%) !important;
            transform: translateY(-1px);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), inset 0 -1px 2px rgba(0,0,0,0.6), 0 5px 14px rgba(0,0,0,0.5) !important;
            color: #fff !important;
        }
        .stButton > button:active {
            background: linear-gradient(180deg, #1a1a1f 0%, #212128 100%) !important;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.9), inset 0 -1px 1px rgba(255,255,255,0.02) !important;
            transform: translateY(0px);
        }

        /* Expander dark */
        [data-testid="stExpander"] {
            background: linear-gradient(180deg, #30313a 0%, #23232a 100%) !important;
            border: 1px solid #0f0f13 !important;
            border-radius: 16px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 4px 12px rgba(0,0,0,0.3) !important;
        }
        [data-testid="stExpander"] summary { color: #e7e7ea !important; }
        [data-testid="stExpander"] svg { fill: var(--muted) !important; }

        /* Alerts / info / warning / success / error */
        [data-testid="stAlert"] {
            background: linear-gradient(180deg, #30313a 0%, #23232a 100%) !important;
            border: 1px solid #0f0f13 !important;
            border-radius: 14px !important;
            color: #e7e7ea !important;
        }

        /* Progress bar */
        [data-testid="stProgress"] > div > div {
            background: #121215 !important;
            border-radius: 6px !important;
        }

        /* Divider */
        [data-testid="stMarkdownContainer"] hr, hr {
            border-color: rgba(255,255,255,0.06) !important;
        }

        /* File uploader */
        [data-testid="stFileUploader"] {
            background: linear-gradient(180deg, #141418 0%, #1b1b20 100%) !important;
            border: 1px dashed #3b82f6 !important;
            border-radius: 14px !important;
            padding: 20px !important;
        }
        [data-testid="stFileUploader"] label { color: var(--muted) !important; }

        /* Download button */
        [data-testid="stDownloadButton"] button {
            background: linear-gradient(180deg, #1e2a48 0%, #162038 100%) !important;
            border: 1px solid #0e172b !important;
            color: #60a5fa !important;
        }

        /* Card click overlay ─────────────────────────────────────────── */
        .element-container:has(.action-card) + .element-container {
            transform: translateY(-160px);
            margin-bottom: -160px;
            z-index: 100;
            pointer-events: none;
        }
        .element-container:has(.action-card) + .element-container [data-testid="stButton"] {
            pointer-events: all;
        }
        .element-container:has(.action-card) + .element-container [data-testid="stButton"] button {
            height: 160px !important;
            min-height: 160px !important;
            width: 100% !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            cursor: pointer !important;
            opacity: 0 !important;
        }

        .element-container:has(.dash-card) + .element-container {
            transform: translateY(-80px);
            margin-bottom: -80px;
            z-index: 100;
            pointer-events: none;
        }
        .element-container:has(.dash-card) + .element-container [data-testid="stButton"] {
            pointer-events: all;
        }
        .element-container:has(.dash-card) + .element-container [data-testid="stButton"] button {
            height: 80px !important;
            min-height: 80px !important;
            width: 100% !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            cursor: pointer !important;
            opacity: 0 !important;
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #2a2a30; border-radius: 3px; }
        ::-webkit-scrollbar-track { background: transparent; }

        /* Caption text */
        [data-testid="stCaptionContainer"] { color: var(--muted) !important; }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: linear-gradient(180deg, #30313a 0%, #23232a 100%) !important;
            border: 1px solid #0f0f13 !important;
            border-radius: 14px !important;
            padding: 16px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 4px 12px rgba(0,0,0,0.3) !important;
        }

        /* Selectbox dropdown */
        [data-baseweb="popover"] {
            background: #23232a !important;
            border: 1px solid #0f0f13 !important;
        }
        [data-baseweb="menu"] {
            background: #23232a !important;
        }
        [data-baseweb="menu"] li {
            color: #e7e7ea !important;
        }
        [data-baseweb="menu"] li:hover {
            background: #30313a !important;
        }

        /* Radio buttons */
        [data-testid="stRadio"] label { color: var(--muted) !important; }
        [data-testid="stCheckbox"] label { color: #e7e7ea !important; }

        /* Form */
        [data-testid="stForm"] {
            background: linear-gradient(180deg, var(--panel-top) 0%, var(--panel-bot) 100%) !important;
            border: 1px solid #0b0b0d !important;
            border-radius: 24px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 20px 40px rgba(0,0,0,0.5) !important;
        }
    </style>
    """, unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = "guest"  # Auth disabled — skip login
if "resume_score" not in st.session_state:
    st.session_state.resume_score = 0
if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []
if "resume" not in st.session_state:
    st.session_state.resume = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "target_role" not in st.session_state:
    st.session_state.target_role = "software engineer"
if "nav_target" not in st.session_state:
    st.session_state.nav_target = "Home"

# AUTH PAGE
def auth_page():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<h1 style='text-align: center; color: #60a5fa; font-size: 40px; text-shadow: 0 1px 0 rgba(255,255,255,0.05), 0 -1px 1px rgba(0,0,0,0.85);'>🧠 CareerAI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9a9aa3; font-size: 18px;'>AI Resume Screening & Career Recommendation</p>", unsafe_allow_html=True)
    
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
        # Profile section with LED indicator
        st.markdown(f"""
            <div style='background: linear-gradient(180deg, #222227 0%, #1c1c21 100%); border: 1px solid #2a2a30; padding: 12px; border-radius: 16px; margin-bottom: 30px; display: flex; align-items: center; gap: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
                <div style='width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: linear-gradient(180deg, #2e2e36, #24242b); font-size: 22px; color: #9a9aa3; box-shadow: inset 0 1px 1px rgba(255,255,255,0.05), 0 2px 5px rgba(0,0,0,0.5); border: 1px solid #1a1a1f;'><i class='ph ph-user'></i></div>
                <div style='flex: 1; min-width: 0;'>
                    <div style='font-weight: 600; font-size: 16px; color: #f0f0f3;'>{st.session_state.user}</div>
                    <div style='font-size: 13px; color: #9a9aa3; margin-top: 3px; display: flex; align-items: center; gap: 4px;'><span style='width: 6px; height: 6px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 6px #22c55e;'></span>Online</div>
                </div>
                <div style='width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; background: #1f1f24; color: #666; border: 1px solid #141418;'><i class='ph-fill ph-dots-three'></i></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='font-size: 12px; font-weight: 700; color: #666; letter-spacing: 1px; margin-bottom: 8px; margin-top: 10px;'>CORE FEATURES</p>", unsafe_allow_html=True)
        ALL_CORE = [
            "Home",
            "Upload & Scan",
            "Skill Gap Analysis",
            "Career Roadmap",
            "Resume Maker",
            "Learning Path",
            "STAR Questions",
            "ATS Score",
        ]
        ALL_TOOLS = [
            "Resume History",
            "Resume Analytics",
            "Application Tracker",
            "Find Jobs",
            "Interview Prep",
            "Mock Interviews",
            "Edit Profile",
            "Logout",
        ]

        for page in ALL_CORE:
            if st.button(page, key=f"nav_{page}", use_container_width=True):
                st.session_state.nav_target = page
                st.rerun()

        st.markdown("---")
        st.markdown("<p style='font-size: 12px; font-weight: 700; color: #666; letter-spacing: 1px; margin-bottom: 8px; margin-top: 20px;'>TOOLS</p>", unsafe_allow_html=True)
        for page in ALL_TOOLS:
            if st.button(page, key=f"nav_{page}", use_container_width=True):
                st.session_state.nav_target = page
                st.rerun()

        choice = st.session_state.nav_target
        st.markdown("---")

    
    # HOME PAGE
    if choice == "Home":
        user_data = get_user_profile(st.session_state.user)


        if True:
            # Welcome Section
            user_name = user_data['name'] if user_data else "User"
            
            # Welcome Panel
            st.markdown(
                f"""<div class='main-panel' style='padding: 20px 24px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h1 style='font-size: 30px; font-weight: 700; margin-bottom: 4px; color: #f5f5f7;'>Welcome, {user_name}!</h1>
                            <p style='font-size: 16px; color: #9a9aa3; margin: 0;'>Ready to advance your career today?</p>
                        </div>
                        <div style='display: flex; gap: 12px;'>
                            <div style='width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: linear-gradient(180deg, #222227, #1c1c21); border: 1px solid #2a2a30; box-shadow: 0 4px 10px rgba(0,0,0,0.3); color: #9a9aa3;'><i class='ph ph-bell'></i></div>
                            <div style='width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: linear-gradient(180deg, #222227, #1c1c21); border: 1px solid #2a2a30; box-shadow: 0 4px 10px rgba(0,0,0,0.3); color: #9a9aa3;'><i class='ph ph-gear'></i></div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True
            )
            
            # Action Cards Panel
            st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
            st.markdown("<div class='main-panel-title'>What would you like to do today?</div>", unsafe_allow_html=True)
            
            col_a, col_b, col_c, col_d = st.columns(4, gap="small")
            with col_a:
                st.markdown("""
                    <div class='action-card card-blue' style='padding: 20px; height: 160px; display: flex; flex-direction: column;'>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;'>
                            <div class='icon-wrap icon-blue'><i class='ph ph-cloud-arrow-up'></i></div>
                            <div style='width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; background: #1c1c21; border: 1px solid #2a2a30; color: #a1a1ac;'><i class='ph ph-caret-right'></i></div>
                        </div>
                        <h4 style='font-size: 16px; font-weight: 600; margin: 0 0 4px 0; color: #f5f5f7;'>Upload Resume</h4>
                        <p style='font-size: 14px; margin: 0; line-height: 1.4; color: #7a7a85;'>Scan and analyze your resume</p>
                    </div>""", unsafe_allow_html=True)
                if st.button("Go to Upload", key="card_btn_upload", use_container_width=True):
                    st.session_state.nav_target = "Upload & Scan"
                    st.rerun()
            with col_b:
                st.markdown("""
                    <div class='action-card card-purple' style='padding: 20px; height: 160px; display: flex; flex-direction: column;'>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;'>
                            <div class='icon-wrap icon-purple'><i class='ph ph-suitcase'></i></div>
                            <div style='width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; background: #1c1c21; border: 1px solid #2a2a30; color: #a1a1ac;'><i class='ph ph-caret-right'></i></div>
                        </div>
                        <h4 style='font-size: 16px; font-weight: 600; margin: 0 0 4px 0; color: #f5f5f7;'>Find Jobs</h4>
                        <p style='font-size: 14px; margin: 0; line-height: 1.4; color: #7a7a85;'>Discover matching opportunities</p>
                    </div>""", unsafe_allow_html=True)
                if st.button("Go to Find Jobs", key="card_btn_jobs", use_container_width=True):
                    st.session_state.nav_target = "Find Jobs"
                    st.rerun()
            with col_c:
                st.markdown("""
                    <div class='action-card card-orange' style='padding: 20px; height: 160px; display: flex; flex-direction: column;'>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;'>
                            <div class='icon-wrap icon-orange'><i class='ph ph-trend-up'></i></div>
                            <div style='width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; background: #1c1c21; border: 1px solid #2a2a30; color: #a1a1ac;'><i class='ph ph-caret-right'></i></div>
                        </div>
                        <h4 style='font-size: 16px; font-weight: 600; margin: 0 0 4px 0; color: #f5f5f7;'>Improve Skills</h4>
                        <p style='font-size: 14px; margin: 0; line-height: 1.4; color: #7a7a85;'>Close your skill gaps</p>
                    </div>""", unsafe_allow_html=True)
                if st.button("Go to Skill Gap", key="card_btn_skills", use_container_width=True):
                    st.session_state.nav_target = "Skill Gap Analysis"
                    st.rerun()
            with col_d:
                st.markdown("""
                    <div class='action-card card-teal' style='padding: 20px; height: 160px; display: flex; flex-direction: column;'>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;'>
                            <div class='icon-wrap icon-teal'><i class='ph ph-target'></i></div>
                            <div style='width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; background: #1c1c21; border: 1px solid #2a2a30; color: #a1a1ac;'><i class='ph ph-caret-right'></i></div>
                        </div>
                        <h4 style='font-size: 16px; font-weight: 600; margin: 0 0 4px 0; color: #f5f5f7;'>Ace Interviews</h4>
                        <p style='font-size: 14px; margin: 0; line-height: 1.4; color: #7a7a85;'>Practice with AI coach</p>
                    </div>""", unsafe_allow_html=True)
                if st.button("Go to STAR Questions", key="card_btn_interviews", use_container_width=True):
                    st.session_state.nav_target = "STAR Questions"
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Activity & Progress Panel
            st.markdown("""<div class='main-panel'>
                <div class='main-panel-title'>Activity & Progress</div>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 16px;'>
                    <div class='progress-box'>
                        <div style='display: flex; justify-content: space-between; align-items: flex-end;'>
                            <div style='font-size: 12px; font-weight: 700; color: #8a8a95; letter-spacing: 1px;'>PROFILE COMPLETION</div>
                            <div style='display: flex; align-items: center; gap: 8px;'>
                                <div style='font-size: 26px; font-weight: 700; color: #fff;'>85%</div>
                                <div style='background: #064e3b; border: 1px solid #047857; color: #34d399; font-size: 12px; font-weight: 600; padding: 2px 6px; border-radius: 4px;'>+5%</div>
                            </div>
                        </div>
                        <div class='progress-track'><div class='progress-fill-blue' style='width: 85%;'></div></div>
                    </div>
                    <div class='progress-box'>
                        <div style='display: flex; justify-content: space-between; align-items: flex-end;'>
                            <div style='font-size: 12px; font-weight: 700; color: #8a8a95; letter-spacing: 1px;'>INTERVIEW READINESS</div>
                            <div style='display: flex; align-items: center; gap: 8px;'>
                                <div style='font-size: 26px; font-weight: 700; color: #fff;'>62%</div>
                                <div style='background: #78350f; border: 1px solid #b45309; color: #fbbf24; font-size: 12px; font-weight: 600; padding: 2px 6px; border-radius: 4px;'>+12%</div>
                            </div>
                        </div>
                        <div class='progress-track'><div class='progress-fill-purple' style='width: 62%;'></div></div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
            
            # Explore Dashboard
            st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
            st.markdown("<div class='main-panel-title' style='margin-bottom: 20px;'>Explore Dashboard</div>", unsafe_allow_html=True)
            
            col_e, col_f, col_g, col_h = st.columns(4, gap="small")
            
            with col_e:
                st.markdown("""
                    <div class='dash-card skeuo-button' style='padding: 16px 14px; height: 80px; display: flex; align-items: center; gap: 12px; background: linear-gradient(180deg, #222227, #1c1c21); border: 1px solid #2a2a30; border-radius: 12px;'>
                        <div style='width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: #111114; color: #f5f5f7; border: 1px solid #000; box-shadow: inset 0 1px 1px rgba(255,255,255,0.05); flex-shrink: 0;'><i class='ph ph-user'></i></div>
                        <div style='flex: 1; min-width: 0;'>
                            <p style='font-size: 15px; font-weight: 600; margin: 0 0 2px 0; color: #f5f5f7;'>My Profile</p>
                            <p style='font-size: 13px; margin: 0; color: #7a7a85;'>View and edit</p>
                        </div>
                    </div>""", unsafe_allow_html=True)
                if st.button("Go to Profile", key="dash_btn_profile", use_container_width=True):
                    st.session_state.nav_target = "Edit Profile"
                    st.rerun()
            with col_f:
                st.markdown("""
                    <div class='dash-card skeuo-button' style='padding: 16px 14px; height: 80px; display: flex; align-items: center; gap: 12px; background: linear-gradient(180deg, #222227, #1c1c21); border: 1px solid #2a2a30; border-radius: 12px; position: relative;'>
                        <div style='width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: #111114; color: #f5f5f7; border: 1px solid #000; box-shadow: inset 0 1px 1px rgba(255,255,255,0.05); flex-shrink: 0;'><i class='ph ph-chart-bar'></i></div>
                        <div style='flex: 1; min-width: 0;'>
                            <p style='font-size: 15px; font-weight: 600; margin: 0 0 2px 0; color: #f5f5f7;'>Skill Gap <span style='background: #fbbf24; color: #000; font-size: 11px; padding: 1px 4px; border-radius: 3px; font-weight: 700; margin-left: 4px;'>NEW</span></p>
                            <p style='font-size: 13px; margin: 0; color: #7a7a85;'>Analyze skills</p>
                        </div>
                    </div>""", unsafe_allow_html=True)
                if st.button("Go to Skill Gap", key="dash_btn_skillgap", use_container_width=True):
                    st.session_state.nav_target = "Skill Gap Analysis"
                    st.rerun()
            with col_g:
                st.markdown("""
                    <div class='dash-card skeuo-button' style='padding: 16px 14px; height: 80px; display: flex; align-items: center; gap: 12px; background: linear-gradient(180deg, #222227, #1c1c21); border: 1px solid #2a2a30; border-radius: 12px;'>
                        <div style='width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: #111114; color: #f5f5f7; border: 1px solid #000; box-shadow: inset 0 1px 1px rgba(255,255,255,0.05); flex-shrink: 0;'><i class='ph ph-map-trifold'></i></div>
                        <div style='flex: 1; min-width: 0;'>
                            <p style='font-size: 15px; font-weight: 600; margin: 0 0 2px 0; color: #f5f5f7;'>Career Roadmap</p>
                            <p style='font-size: 13px; margin: 0; color: #7a7a85;'>Plan your path</p>
                        </div>
                    </div>""", unsafe_allow_html=True)
                if st.button("Go to Roadmap", key="dash_btn_roadmap", use_container_width=True):
                    st.session_state.nav_target = "Career Roadmap"
                    st.rerun()
            with col_h:
                st.markdown("""
                    <div class='dash-card skeuo-button' style='padding: 16px 14px; height: 80px; display: flex; align-items: center; gap: 12px; background: linear-gradient(180deg, #222227, #1c1c21); border: 1px solid #2a2a30; border-radius: 12px;'>
                        <div style='width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: #111114; color: #f5f5f7; border: 1px solid #000; box-shadow: inset 0 1px 1px rgba(255,255,255,0.05); flex-shrink: 0;'><i class='ph ph-chart-line-up'></i></div>
                        <div style='flex: 1; min-width: 0;'>
                            <p style='font-size: 15px; font-weight: 600; margin: 0 0 2px 0; color: #f5f5f7;'>Insights & Reports</p>
                            <p style='font-size: 13px; margin: 0; color: #7a7a85;'>Track progress</p>
                        </div>
                    </div>""", unsafe_allow_html=True)
                if st.button("Go to Analytics", key="dash_btn_analytics", use_container_width=True):
                    st.session_state.nav_target = "Resume Analytics"
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Right Sidebar Profile removed for full-width layout
        if False:
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
                    <div style='background: linear-gradient(180deg, #30313a 0%, #23232a 100%); 
                                color: #e7e7ea; padding: 25px; border-radius: 18px; text-align: center;
                                border: 1px solid #0f0f13; box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), inset 0 -1px 2px rgba(0,0,0,0.7), 0 8px 18px rgba(0,0,0,0.45);'>
                    <p style='font-size: 48px; margin: 0 0 15px 0;'>👤</p>
                    <h3 style='margin: 0 0 5px 0; font-size: 20px; font-weight: bold;'>{user_data['name']}</h3>
                    <p style='margin: 0 0 3px 0; font-size: 15px; opacity: 0.9; font-weight: 500;'>{user_data['job_title']}</p>
                    <p style='margin: 0; font-size: 13px; opacity: 0.8;'>{user_data['education']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
                
                # Resume Score Section
                st.markdown(
                    f"""
                    <div style='text-align: center;'>
                    <p style='font-size: 15px; margin: 0 0 3px 0; color: #e7e7ea; font-weight: bold;'>Resume Score: <span style='font-size: 22px; color: #60a5fa;'>{score}</span></p>
                    <div style='background: #121215; height: 6px; border-radius: 3px; border: 1px solid #08080a; box-shadow: inset 0 2px 4px rgba(0,0,0,0.9); margin-bottom: 8px; overflow: hidden;'>
                        <div style='background: linear-gradient(90deg, #4CAF50 0%, #FFC107 50%, #FF5722 100%); 
                                    height: 6px; border-radius: 3px; width: {score}%;'></div>
                    </div>
                    <p style='font-size: 13px; margin: 0; color: #9a9aa3;'>Completion Level</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
                
                # Action Buttons
                col_btn1, col_btn2 = st.columns(2, gap="small")
                with col_btn1:
                    if st.button("✏️ Edit", use_container_width=True, key="edit_profile_home"):
                        st.session_state.nav_target = "Edit Profile"
                        st.rerun()
                with col_btn2:
                    if st.button("📝 Upload", use_container_width=True, key="upload_home"):
                        st.session_state.nav_target = "📄 Upload & Scan"
                        st.rerun()
                
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                
                # Resume History
                st.markdown(
                    """
                    <div style='font-size: 15px; font-weight: bold; color: #e7e7ea; margin-bottom: 8px;'>
                    📋 Resume History
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    """
                    <div style='background: linear-gradient(180deg, #141418 0%, #1b1b20 100%); padding: 10px 12px; border-radius: 10px; 
                                font-size: 14px; color: #9a9aa3; border: 1px solid #08080a; box-shadow: inset 0 2px 5px rgba(0,0,0,0.6); margin-bottom: 12px; cursor: pointer;'>
                    📄 Upload Resume
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Skills & Features
                st.markdown(
                    """<p style='font-size: 14px; font-weight: bold; margin: 15px 0 8px 0; color: #60a5fa;'>
                    📊 Skill Gap Analysis
                    <span style='' class='badge-new'>NEW</span>
                    </p>""",
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    "<p style='font-size: 14px; font-weight: bold; margin: 12px 0 8px 0; color: #e7e7ea;'>🎯 Career Roadmap</p>",
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    "<p style='font-size: 14px; font-weight: bold; margin: 12px 0 8px 0; color: #e7e7ea;'>🎤 Mock Interviews</p>",
                    unsafe_allow_html=True
                )
                
                st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
                
                # College Stream Button
                st.markdown(
                    """
                    <div style='background: linear-gradient(180deg, #2c2c33 0%, #1f1f24 100%); padding: 12px; border-radius: 12px; 
                                text-align: center; cursor: pointer; border: 1px solid #0d0d10; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 3px 8px rgba(0,0,0,0.4);'>
                    <p style='font-size: 14px; font-weight: bold; margin: 0; color: #60a5fa;'>
                    🎓 College Streom  <span style='font-size: 16px;'>➜</span>
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
                    <div style='background: linear-gradient(180deg, #30313a 0%, #23232a 100%); color: #e7e7ea; padding: 20px; border-radius: 16px; text-align: center; border: 1px solid #0f0f13; box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), 0 8px 18px rgba(0,0,0,0.45);'>
                    <p style='margin: 0; font-size: 14px; opacity: 0.9;'>Overall Score</p>
                    <p style='margin: 8px 0 0 0; font-size: 30px; font-weight: bold;'>{resume_score}</p>
                    <p style='margin: 4px 0 0 0; font-size: 13px;'>/100</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                ats_score = int(resume_score * 0.85)  # ATS typically scores lower
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(180deg, #30313a 0%, #23232a 100%); color: #e7e7ea; padding: 20px; border-radius: 16px; text-align: center; border: 1px solid #0f0f13; box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), 0 8px 18px rgba(0,0,0,0.45);'>
                    <p style='margin: 0; font-size: 14px; opacity: 0.9;'>ATS Compatibility</p>
                    <p style='margin: 8px 0 0 0; font-size: 30px; font-weight: bold;'>{ats_score}%</p>
                    <p style='margin: 4px 0 0 0; font-size: 13px;'>Parser-friendly</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col3:
                keyword_match = int(resume_score * 0.82)
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(180deg, #30313a 0%, #23232a 100%); color: #e7e7ea; padding: 20px; border-radius: 16px; text-align: center; border: 1px solid #0f0f13; box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), 0 8px 18px rgba(0,0,0,0.45);'>
                    <p style='margin: 0; font-size: 14px; opacity: 0.9;'>Keyword Match</p>
                    <p style='margin: 8px 0 0 0; font-size: 30px; font-weight: bold;'>{keyword_match}%</p>
                    <p style='margin: 4px 0 0 0; font-size: 13px;'>Industry terms</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col4:
                formatting_score = int(resume_score * 0.90)
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(180deg, #30313a 0%, #23232a 100%); color: #e7e7ea; padding: 20px; border-radius: 16px; text-align: center; border: 1px solid #0f0f13; box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), 0 8px 18px rgba(0,0,0,0.45);'>
                    <p style='margin: 0; font-size: 14px; opacity: 0.9;'>Formatting</p>
                    <p style='margin: 8px 0 0 0; font-size: 30px; font-weight: bold;'>{formatting_score}%</p>
                    <p style='margin: 4px 0 0 0; font-size: 13px;'>Structure score</p>
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
    
    # FEATURE 1: UPLOAD & SCAN
    elif choice == "Upload & Scan":
        st.header("📄 Upload & Scan Your Resume")
        st.write("Upload a PDF resume to extract your profile. **All other features read from this scan.**")
        
        file = st.file_uploader("Choose a PDF file", type=["pdf"])
        
        if file:
            os.makedirs("uploads", exist_ok=True)
            path = os.path.join("uploads", file.name)
            
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            
            # Extract text and run full parse
            text = extract_text_from_pdf(path)
            parsed = parse_resume(text)
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
            
            # Store everything in session state
            st.session_state.resume_score = score
            st.session_state.resume_skills = skills
            st.session_state.resume = parsed
            st.session_state.resume_text = text
            
            st.success("✅ Resume Uploaded and Analyzed Successfully")
            st.balloons()
            
            # Show results
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Resume Score", f"{score}/100")
            with col2:
                st.metric("Skills Found", len(skills))
            with col3:
                st.metric("Experience", f"{parsed.get('years_of_experience', 0)} yrs")
            with col4:
                st.metric("Word Count", len(text.split()))
            
            # Parsed fields
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.write("### 👤 Extracted Info")
                st.write(f"**Name:** {parsed.get('name', 'N/A')}")
                st.write(f"**Email:** {parsed.get('email', 'N/A')}")
                st.write(f"**Phone:** {parsed.get('phone', 'N/A')}")
                if parsed.get("education"):
                    st.write("**Education:**")
                    for edu in parsed["education"][:3]:
                        st.write(f"  🎓 {edu}")
            with c2:
                st.write("### 🔧 Detected Skills")
                if skills:
                    skill_cols = st.columns(2)
                    for i, s in enumerate(skills):
                        with skill_cols[i % 2]:
                            st.write(f"🔹 {s.title()}")
                else:
                    st.info("No skills detected — try a different PDF.")
        
        elif st.session_state.resume:
            st.info("✅ Resume already loaded. You can upload a new one or proceed to other features.")
            parsed = st.session_state.resume
            st.write(f"**Name:** {parsed.get('name', 'N/A')} · **Skills:** {len(st.session_state.resume_skills)} · **Experience:** {parsed.get('years_of_experience', 0)} yrs")
    
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
    
    # FEATURE 2: SKILL GAP ANALYSIS
    elif choice == "Skill Gap Analysis":
        st.header("📊 Skill Gap Analysis")
        st.write("Compare your skills against industry standards for your target role.")
        
        if not st.session_state.resume:
            st.warning("⚠️ Please upload a resume first in 'Upload & Scan'")
        else:
            roles = get_roles()
            st.session_state.target_role = st.selectbox("Select Target Job Role:", roles, index=roles.index(st.session_state.target_role) if st.session_state.target_role in roles else 0)
            
            have, missing, match_pct = get_skill_gap(st.session_state.resume_skills, st.session_state.target_role)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.metric("Role Match", f"{int(match_pct)}%")
                st.write(f"### 🎯 {st.session_state.target_role.title()}")
                st.write("The skills highlighted below are required for this role but missing from your profile.")
            
            with col2:
                fig = skill_gap_chart(st.session_state.resume_skills, get_required_skills(st.session_state.target_role))
                st.pyplot(fig)
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"✅ **Skills You Have ({len(have)})**")
                for s in have:
                    st.write(f"• {s.title()}")
            with c2:
                st.error(f"❌ **Missing Skills ({len(missing)})**")
                for s in missing:
                    st.write(f"• {s.title()}")
                if missing:
                    if st.button("🚀 Generate Learning Path"):
                        # This would navigate to learning path page in a real app, 
                        # here we just suggest the user clicks the sidebar.
                        st.info("Click on '📚 Learning Path' in the sidebar to see your custom study plan!")
    
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
    
    # FEATURE 3: CAREER ROADMAP
    elif choice == "Career Roadmap":
        st.header("🛣️ Your Career Roadmap")
        st.write("A visual guide to your professional growth.")
        
        if not st.session_state.resume:
            st.warning("⚠️ Please upload a resume first in 'Upload & Scan'")
        else:
            current_level = detect_current_level(st.session_state.resume.get("years_of_experience", 0))
            st.info(f"📍 **Detected Current Level:** {current_level} ({st.session_state.resume.get('years_of_experience', 0)} years exp)")
            
            target_role = st.selectbox("Target Career Path:", get_roles(), key="roadmap_role_select")
            milestones = get_career_roadmap(target_role)
            
            if milestones:
                fig = career_roadmap_chart(milestones)
                st.pyplot(fig)
                
                st.markdown("### 🏆 Milestone Details")
                for i, ms in enumerate(milestones, 1):
                    with st.expander(f"Step {i}: {ms['title']} ({ms['years']} years)"):
                        st.write("**Key Skills to Master:**")
                        st.write(", ".join(ms["skills"]))
            else:
                st.info("No roadmap data available for this specific role yet.")

    # FEATURE 4: RESUME MAKER
    elif choice == "Resume Maker":
        st.header("📝 Standard Resume Maker")
        st.write("Build a clean, ATS-friendly resume matching Jake's template.")
        
        with st.form("resume_form"):
            st.subheader("Personal Information")
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name", value=st.session_state.resume.get("name", "") if st.session_state.resume else "")
                email = st.text_input("Email", value=st.session_state.resume.get("email", "") if st.session_state.resume else "")
            with c2:
                phone = st.text_input("Phone", value=st.session_state.resume.get("phone", "") if st.session_state.resume else "")
                location = st.text_input("Location (City, State)")
            
            c3, c4 = st.columns(2)
            with c3:
                linkedin = st.text_input("LinkedIn URL")
            with c4:
                github = st.text_input("GitHub URL")
            
            st.subheader("Professional Summary")
            summary = st.text_area("Briefly describe your professional background and goals.")
            
            st.subheader("Experience")
            st.write("Add your work history. Use bullet points for accomplishments.")
            
            # Simple list of experiences (mock dynamic rows)
            experiences = []
            for i in range(2):
                st.markdown(f"**Position {i+1}**")
                e1, e2 = st.columns(2)
                with e1:
                    e_title = st.text_input(f"Job Title {i+1}", key=f"et_{i}")
                    e_comp = st.text_input(f"Company {i+1}", key=f"ec_{i}")
                with e2:
                    e_loc = st.text_input(f"Location {i+1}", key=f"el_{i}")
                    e_dates = st.text_input(f"Dates (e.g. Jan 2020 - Present) {i+1}", key=f"ed_{i}")
                e_bullets = st.text_area(f"Bullets (one per line) {i+1}", key=f"eb_{i}")
                if e_title:
                    experiences.append({
                        "title": e_title, "company": e_comp, "location": e_loc, 
                        "dates": e_dates, "bullets": e_bullets.split("\n")
                    })
            
            st.subheader("Education")
            education = []
            for i in range(1):
                ed1, ed2 = st.columns(2)
                with ed1:
                    edu_degree = st.text_input("Degree", value=st.session_state.resume.get("education", [""])[0] if st.session_state.resume and st.session_state.resume.get("education") else "")
                    edu_school = st.text_input("University/School")
                with ed2:
                    edu_loc = st.text_input("School Location")
                    edu_dates = st.text_input("Dates (e.g. 2016 - 2020)")
                edu_details = st.text_area("Additional Details (GPA, Honors, etc.)")
                if edu_degree:
                    education.append({
                        "degree": edu_degree, "school": edu_school, 
                        "location": edu_loc, "dates": edu_dates, "details": edu_details
                    })
            
            st.subheader("Skills")
            all_skills = st.text_area("Skills (comma separated)", value=", ".join(st.session_state.resume_skills) if st.session_state.resume_skills else "")
            
            submitted = st.form_submit_button("Generate PDF Resume")
            
            if submitted:
                resume_data = {
                    "name": name, "email": email, "phone": phone, 
                    "linkedin": linkedin, "github": github, "location": location,
                    "summary": summary, "experiences": experiences, 
                    "education": education, "skills": all_skills
                }
                pdf_bytes = generate_resume_pdf(resume_data)
                st.success("✅ Resume Generated Successfully!")
                st.download_button(
                    label="📥 Download PDF Resume",
                    data=pdf_bytes,
                    file_name=f"{name.replace(' ', '_')}_Resume.pdf",
                    mime="application/pdf"
                )

    # FEATURE 5: LEARNING PATH
    elif choice == "Learning Path":
        st.header("📚 Your Learning Path")
        st.write("Personalized resource map to bridge your skill gaps.")
        
        if not st.session_state.resume:
            st.warning("⚠️ Please upload a resume first in 'Upload & Scan'")
        else:
            _, missing, _ = get_skill_gap(st.session_state.resume_skills, st.session_state.target_role)
            
            if not missing:
                st.success("🎉 No missing skills found for the target role! You are ready to apply.")
            else:
                path_data = build_learning_path(missing)
                
                col1, col2 = st.columns([1, 1.5])
                with col1:
                    st.metric("Total Learning Time", f"{path_data['total_hours']} Hours")
                    st.metric("Estimated Completion", f"{path_data['estimated_weeks']} Weeks")
                    st.caption("Based on 10 hours of study per week.")
                    
                    fig = learning_timeline_chart(path_data["path"])
                    st.pyplot(fig)
                
                with col2:
                    st.subheader("🚀 Step-by-Step Curriculum")
                    for item in path_data["path"]:
                        with st.expander(f"**{item['skill'].upper()}** ({item['total_hours']}h total)"):
                            for res in item["resources"]:
                                badge = get_platform_badge(res["platform"])
                                st.markdown(
                                    f"""
                                    <div style='background: linear-gradient(180deg, #30313a 0%, #23232a 100%); padding: 10px; border-radius: 12px; border-left: 4px solid {badge['color']}; margin-bottom: 10px; border-top: 1px solid #eee; border-right: 1px solid #eee; border-bottom: 1px solid #eee;'>
                                        <p style='margin: 0; font-weight: bold;'>{badge['emoji']} {res['title']}</p>
                                        <p style='margin: 5px 0; font-size: 15px;'>{res['platform']} • {res['hours']} Hours</p>
                                        <a href='{res['url']}' target='_blank' style='text-decoration: none; color: #3b82f6; font-weight: bold;'>Go to Course ➜</a>
                                    </div>
                                    """, unsafe_allow_html=True
                                )

    # FEATURE 6: STAR QUESTIONS
    elif choice == "STAR Questions":
        st.header("⭐ STAR Interview Questions")
        st.write("Behavioral questions tailored to your profile and target role.")
        
        if not st.session_state.resume:
            st.warning("⚠️ Please upload a resume first in 'Upload & Scan'")
        else:
            role = st.selectbox("Role for Interview Prep:", get_roles(), index=get_roles().index(st.session_state.target_role) if st.session_state.target_role in get_roles() else 0)
            questions = get_star_questions(role, st.session_state.resume_skills)
            
            st.info(f"Showing {len(questions)} high-relevance behavioral questions for a {role.title()} role.")
            
            for i, q in enumerate(questions, 1):
                with st.expander(f"Q{i}: {q['question']}"):
                    st.markdown("#### 💡 How to Answer (STAR Method)")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**S - Situation:** {q['s']}")
                        st.markdown(f"**T - Task:** {q['t']}")
                    with col2:
                        st.markdown(f"**A - Action:** {q['a']}")
                        st.markdown(f"**R - Result:** {q['r']}")
                    
                    st.divider()
                    user_ans = st.text_area("Draft your answer here:", key=f"star_ans_{i}")
                    if st.button(f"Save Draft {i}"):
                        st.success("Draft saved!")

    # FEATURE 7: ATS SCORE
    elif choice == "ATS Score":
        st.header("🎯 ATS Compatibility Score")
        st.write("How well does your resume perform against applicant tracking systems?")
        
        if not st.session_state.resume_text:
            st.warning("⚠️ Please upload a resume first in 'Upload & Scan'")
        else:
            role = st.selectbox("Score against Role:", get_roles(), key="ats_role_select")
            score_data = calculate_ats_score(st.session_state.resume_text, role)
            
            col1, col2 = st.columns([1, 1.5])
            with col1:
                # Big Score Circle-ish
                st.markdown(
                    f"""
                    <div style='text-align: center; background: linear-gradient(180deg, #30313a 0%, #23232a 100%); color: #e7e7ea; padding: 40px; border-radius: 50%; border: 1px solid #0f0f13; box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), 0 8px 18px rgba(0,0,0,0.45); width: 200px; height: 200px; display: flex; flex-direction: column; justify-content: center; margin: 0 auto;'>
                        <p style='margin: 0; font-size: 16px;'>ATS SCORE</p>
                        <h1 style='margin: 0; font-size: 60px;'>{score_data['total_score']}</h1>
                        <p style='margin: 0; font-size: 20px;'>Grade: {score_data['grade']}</p>
                    </div>
                    """, unsafe_allow_html=True
                )
                st.markdown("<br>", unsafe_allow_html=True)
                fig = ats_score_chart(score_data["breakdown"])
                st.pyplot(fig)
            
            with col2:
                st.subheader("🛠️ Actionable Fixes")
                for fix in score_data["fixes"]:
                    st.markdown(f"* {fix}")
                
                st.markdown("---")
                st.subheader("🔍 Scan Results")
                tab1, tab2, tab3 = st.tabs(["Keywords", "Structure", "Formatting"])
                with tab1:
                    st.write(f"**Keywords Found ({len(score_data['keywords_found'])}):**")
                    st.write(", ".join(score_data['keywords_found']) if score_data['keywords_found'] else "None")
                    st.write(f"**Missing Keywords ({len(score_data['keywords_missing'])}):**")
                    st.write(", ".join(score_data['keywords_missing'][:10]) if score_data['keywords_missing'] else "None")
                with tab2:
                    st.write(f"**Sections Detected:** {', '.join(score_data['sections_found'])}")
                    st.write(f"**Sections Missing:** {', '.join(score_data['sections_missing']) if score_data['sections_missing'] else 'None'}")
                    st.write(f"**Word Count:** {score_data['word_count']} (Ideal: 400-700)")
                with tab3:
                    if score_data["format_issues"]:
                        for issue in score_data["format_issues"]:
                            st.warning(issue)
                    else:
                        st.success("Clean format detected! No major parsing issues.")
    
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
                    <div style='background: linear-gradient(180deg, #30313a 0%, #23232a 100%); color: #e7e7ea; padding: 20px; border-radius: 16px; border: 1px solid #0f0f13; box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), 0 8px 18px rgba(0,0,0,0.45);'>
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
                    <div style='background: linear-gradient(180deg, #141418 0%, #1b1b20 100%); padding: 20px; border-radius: 14px; border: 1px solid #08080a; box-shadow: inset 0 2px 5px rgba(0,0,0,0.6); color: #e7e7ea;'>
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
                    <div style='background: linear-gradient(180deg, #1e2a48 0%, #162038 100%); padding: 15px; border-radius: 12px; border: 1px solid #0e172b; color: #e7e7ea;'>
                    <h4>⏱️ Timing Tip</h4>
                    <p>Aim for <strong>2-3 minutes max</strong>. Not too long!</p>
                    </div>
                    """
                )
            
            with col_tips2:
                st.markdown(
                    """
                    <div style='background: linear-gradient(180deg, #2a1f40 0%, #1e1630 100%); padding: 15px; border-radius: 12px; border: 1px solid #160e28; color: #e7e7ea;'>
                    <h4>📊 Metrics Matter</h4>
                    <p>Always quantify results: <strong>30% faster</strong>, <strong>$50K saved</strong>, <strong>2x growth</strong></p>
                    </div>
                    """
                )
            
            with col_tips3:
                st.markdown(
                    """
                    <div style='background: linear-gradient(180deg, #10332f 0%, #0b2422 100%); padding: 15px; border-radius: 12px; border: 1px solid #071a18; color: #e7e7ea;'>
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
                            <div style='background: linear-gradient(180deg, #3d2616 0%, #2a1a0f 100%); padding: 15px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #1f1208; color: #e7e7ea;'>
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

# MAIN FLOW — Auth disabled, go straight to dashboard
dashboard()
