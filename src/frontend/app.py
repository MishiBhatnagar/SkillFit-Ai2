import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

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
    .match-card {
        padding: 1rem;
        border-radius: 10px;
        background: #f8f9fa;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .score-high {
        color: #28a745;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .score-medium {
        color: #ffc107;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .score-low {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .skill-tag {
        background-color: #e9ecef;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>🎯 SkillFit AI - Resume Analyzer</h1></div>', 
            unsafe_allow_html=True)
st.markdown("### AI-Powered Resume Matching using RAG Technology")

# API Configuration
API_URL = "http://localhost:8000"

# Initialize session state
if 'matches' not in st.session_state:
    st.session_state.matches = []
if 'resumes' not in st.session_state:
    st.session_state.resumes = []
if 'upload_status' not in st.session_state:
    st.session_state.upload_status = {}

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
            st.metric("Resumes in Memory", data['resumes_loaded'])
            st.metric("Model Status", "✅ Loaded" if data['model_loaded'] else "⚠️ Basic Mode")
            
            # Fetch resumes for display
            try:
                resumes_response = requests.get(f"{API_URL}/resumes/", timeout=2)
                if resumes_response.status_code == 200:
                    st.session_state.resumes = resumes_response.json()
            except:
                pass
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
    st.markdown("- MishiBhatnagar (Core RAG, Backend)")
    st.markdown("- ojcodes2 (Frontend, Integration)")
    
    # Last updated
    st.markdown("---")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload Resumes", "🎯 Match Job", "📊 Dashboard"])

# ============================================
# TAB 1: UPLOAD RESUMES
# ============================================
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
        
        # Show sample files that exist
        st.markdown("### Available Samples")
        sample_files = ["alex_chen_python.pdf", "sarah_johnson_ml.pdf", "mike_zhang_devops.pdf"]
        for sample in sample_files:
            st.markdown(f"- {sample}")
    
    if uploaded_files:
        if st.button("🚀 Upload and Process", use_container_width=True, type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_container = st.container()
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Processing {file.name}...")
                files = {"file": (file.name, file.getvalue(), "application/pdf")}
                
                try:
                    response = requests.post(f"{API_URL}/upload-resume/", files=files, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        with results_container:
                            st.success(f"✅ {result['candidate']} - {result['email']} ({result['skill_count']} skills)")
                        st.session_state.upload_status[file.name] = "success"
                    else:
                        with results_container:
                            st.error(f"❌ Error with {file.name}: {response.text}")
                        st.session_state.upload_status[file.name] = "error"
                except Exception as e:
                    with results_container:
                        st.error(f"❌ Failed: {file.name} - {str(e)}")
                    st.session_state.upload_status[file.name] = "error"
                
                progress_bar.progress((i + 1) / len(uploaded_files))
                time.sleep(0.5)
            
            status_text.text("✅ All resumes processed!")
            st.balloons()
            
            # Refresh resume list
            try:
                response = requests.get(f"{API_URL}/resumes/")
                if response.status_code == 200:
                    st.session_state.resumes = response.json()
            except:
                pass

# ============================================
# TAB 2: MATCH JOB
# ============================================
with tab2:
    st.header("Match Job Description")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        job_desc = st.text_area(
            "Paste Job Description",
            height=250,
            placeholder="e.g., Looking for a Senior Python Developer with machine learning experience...",
            help="Paste the full job description here",
            key="job_desc_input"
        )
    
    with col2:
        top_k = st.slider("Number of matches", 1, 10, 5)
        st.markdown("### Match Settings")
        st.caption("Higher number shows more candidates")
        
        # Example job descriptions
        with st.expander("📋 Examples"):
            if st.button("Python Developer"):
                st.session_state.job_desc_input = "Looking for a Python developer with FastAPI, Docker, and AWS experience"
                st.rerun()
            if st.button("Data Scientist"):
                st.session_state.job_desc_input = "Seeking Data Scientist with Python, TensorFlow, and SQL skills"
                st.rerun()
            if st.button("DevOps Engineer"):
                st.session_state.job_desc_input = "Need DevOps engineer with Kubernetes, Docker, and CI/CD experience"
                st.rerun()
        
        if st.button("🔍 Find Matches", use_container_width=True, type="primary"):
            if job_desc:
                with st.spinner("Analyzing and matching..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/match-job/", 
                            json={"text": job_desc, "top_k": top_k},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            st.session_state.matches = response.json()
                            st.success(f"Found {len(st.session_state.matches)} matches!")
                        elif response.status_code == 400:
                            st.error("No resumes loaded. Please upload resumes first.")
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to backend. Make sure it's running on port 8000!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a job description")
    
    # Display matches
    if st.session_state.matches:
        st.markdown("---")
        st.subheader("📊 Matching Results")
        
        # Create DataFrame for visualization
        df = pd.DataFrame(st.session_state.matches)
        
        if not df.empty:
            # Score distribution chart
            fig = px.bar(
                df,
                x='candidate_name',
                y='score',
                title='Match Scores by Candidate',
                color='score',
                color_continuous_scale='viridis',
                range_color=[0, 100],
                text='score'
            )
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Top Score", f"{df['score'].max():.1f}")
            with col2:
                st.metric("Average Score", f"{df['score'].mean():.1f}")
            with col3:
                st.metric("Candidates", len(df))
        
        # Detailed results
        for match in st.session_state.matches:
            score = match['score']
            
            # Determine score class
            if score >= 70:
                score_class = "score-high"
                badge = "🔥 Excellent Match"
            elif score >= 40:
                score_class = "score-medium"
                badge = "⭐ Good Match"
            else:
                score_class = "score-low"
                badge = "📌 Potential Match"
            
            with st.expander(f"📄 {match['candidate_name']} - Score: {match['score']} {badge}"):
                cols = st.columns([1, 2])
                
                with cols[0]:
                    st.markdown(f"**📧 Email:** {match['email']}")
                    st.markdown(f"**📊 Score:** <span class='{score_class}'>{score}</span>", unsafe_allow_html=True)
                    st.markdown("**🛠️ Skills:**")
                    
                    # Show skills as tags
                    skills_html = ""
                    for skill in match['skills'][:8]:
                        skills_html += f'<span class="skill-tag">{skill}</span> '
                    st.markdown(skills_html, unsafe_allow_html=True)
                    
                    if len(match['skills']) > 8:
                        st.caption(f"... and {len(match['skills']) - 8} more")
                
                with cols[1]:
                    st.markdown("**📝 Matched Content:**")
                    st.info(match['matched_chunk'])

# ============================================
# TAB 3: DASHBOARD
# ============================================
with tab3:
    st.header("Analytics Dashboard")
    
    # Refresh button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()
    
    # Fetch resumes
    try:
        response = requests.get(f"{API_URL}/resumes/", timeout=5)
        if response.status_code == 200:
            resumes = response.json()
            st.session_state.resumes = resumes
            
            if resumes:
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Resumes", len(resumes))
                
                with col2:
                    total_skills = sum(r['skill_count'] for r in resumes)
                    st.metric("Total Skills", total_skills)
                
                with col3:
                    avg_skills = total_skills / len(resumes) if resumes else 0
                    st.metric("Avg Skills per Resume", f"{avg_skills:.1f}")
                
                with col4:
                    unique_emails = len(set(r['email'] for r in resumes if r['email'] != 'Not found'))
                    st.metric("Unique Candidates", unique_emails)
                
                # Skills distribution
                st.subheader("🎯 Skills Distribution")
                
                # Collect all skills
                all_skills = []
                for r in resumes:
                    all_skills.extend(r['skills'])
                
                if all_skills:
                    skill_counts = pd.Series(all_skills).value_counts().head(15)
                    
                    fig = px.bar(
                        x=skill_counts.values,
                        y=skill_counts.index,
                        orientation='h',
                        title='Top 15 Skills Across All Resumes',
                        labels={'x': 'Count', 'y': 'Skill'},
                        color=skill_counts.values,
                        color_continuous_scale='viridis'
                    )
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Resume list
                st.subheader("📋 Processed Resumes")
                df = pd.DataFrame(resumes)
                
                # Format for display
                display_df = df[['candidate_name', 'email', 'filename', 'skills', 'skill_count']].copy()
                display_df['skills'] = display_df['skills'].apply(lambda x: ', '.join(x[:5]) + ('...' if len(x) > 5 else ''))
                
                st.dataframe(
                    display_df,
                    column_config={
                        "candidate_name": "Candidate",
                        "email": "Email",
                        "filename": "File",
                        "skills": "Top Skills",
                        "skill_count": "Skills"
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Resume Data (CSV)",
                    data=csv,
                    file_name=f"skillfit_resumes_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No resumes uploaded yet. Go to the Upload tab to add resumes.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Make sure it's running on port 8000!")
        st.code("python src/backend/main.py", language="bash")
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<center>Built with RAG, FastAPI, and Streamlit 🚀 | Day 3 - Frontend Integration Complete</center>",
    unsafe_allow_html=True
)