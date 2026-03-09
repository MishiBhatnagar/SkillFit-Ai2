import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# Page configuration
st.set_page_config(
    page_title="SkillFit AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102,126,234,0.4);
    }
    .status-box {
        padding: 1rem;
        border-radius: 10px;
        background: #f0f2f6;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>🎯 SkillFit AI - Resume Analyzer</h1></div>', 
            unsafe_allow_html=True)
st.markdown("### AI-Powered Resume Matching using RAG Technology")

# API Configuration
API_URL = "http://localhost:8000"

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png")
    st.markdown("## 🔍 API Status")
    
    # Check API connection
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            st.success("✅ Backend Connected")
            st.metric("Model Status", "✅ Loaded" if data['model_loaded'] else "❌ Not Loaded")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Not Connected")
        st.info("Run: python src/backend/main.py")
    
    st.markdown("---")
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. **Upload** resumes in the Upload tab
    2. **Match** against job descriptions
    3. **View** analytics in Dashboard
    """)
    
    st.markdown("---")
    st.markdown("### 👥 Team")
    st.markdown("- MishiBhatnagar (Core RAG)")
    st.markdown("- ojcodes2 (Frontend)")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload Resumes", "🎯 Match Job", "📊 Dashboard"])

# Tab 1: Upload Resumes
with tab1:
    st.header("Upload Resumes")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Choose PDF resumes", 
            type="pdf", 
            accept_multiple_files=True,
            help="Select one or more PDF resumes to upload"
        )
    
    with col2:
        st.markdown("### Quick Tips")
        st.info("📌 PDF files only\n📌 Multiple files allowed\n📌 Max 10MB per file")
    
    if uploaded_files:
        if st.button("🚀 Upload and Process", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Processing {file.name}...")
                files = {"file": (file.name, file.getvalue(), "application/pdf")}
                
                try:
                    response = requests.post(f"{API_URL}/upload-resume/", files=files)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result.get('candidate', file.name)} uploaded")
                    else:
                        st.error(f"❌ Error with {file.name}")
                except Exception as e:
                    st.error(f"❌ Failed: {file.name}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))
                time.sleep(0.5)
            
            status_text.text("✅ All resumes processed!")
            st.balloons()

# Tab 2: Match Job (Placeholder)
with tab2:
    st.header("Match Job Description")
    st.info("🔧 Coming soon: Job matching functionality will be added here")
    
    with st.container():
        st.markdown("### Preview")
        st.text_area(
            "Job Description",
            height=200,
            placeholder="Paste job description here...",
            disabled=True
        )
        st.button("Find Matches", disabled=True)

# Tab 3: Dashboard (Placeholder)
with tab3:
    st.header("Analytics Dashboard")
    st.info("📊 Coming soon: Analytics and visualizations will be added here")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Resumes", "0", "Coming soon")
    with col2:
        st.metric("Total Skills", "0", "Coming soon")
    with col3:
        st.metric("Matches Made", "0", "Coming soon")

# Footer
st.markdown("---")
st.markdown(
    "<center>Built with RAG, FastAPI, and Streamlit 🚀 | Day 2 - Frontend Setup</center>",
    unsafe_allow_html=True
)