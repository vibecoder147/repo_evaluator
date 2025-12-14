import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
import altair as alt
import json
import base64

# --- CONFIGURATION ---
st.set_page_config(page_title="GitGrade AI", page_icon="🛡️", layout="wide")

# Custom CSS for a "Beautiful" Dark/Glassmorphism look
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #41424b;
        text-align: center;
    }
    .badge {
        font-size: 24px; 
        font-weight: bold; 
        padding: 10px 20px; 
        border-radius: 20px;
        display: inline-block;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: API KEYS ---
with st.sidebar:
    st.header("🔑 Configuration")
    GEMINI_API_KEY = st.text_input("Gemini API Key", type="password")
    GITHUB_TOKEN = st.text_input("GitHub Token (Optional)", type="password", help="Use if you hit rate limits")
    
    st.info("💡 **Tip:** Public repos only. Large repos may hit token limits.")

# --- HELPER FUNCTIONS ---

def fetch_github_data(repo_url, token=None):
    """Fetches repository structure and key file contents."""
    try:
        parts = repo_url.rstrip("/").split("/")
        owner, repo = parts[-2], parts[-1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
        
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"
            
        # 1. Fetch File Tree
        response = requests.get(api_url, headers=headers)
        if response.status_code == 404: # Try master branch if main fails
             api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
             response = requests.get(api_url, headers=headers)
             
        if response.status_code != 200:
            return None, f"Error fetching repo: {response.status_code}"
        
        tree_data = response.json()
        
        # 2. Extract File Extensions for Visuals
        files = [item['path'] for item in tree_data.get('tree', []) if item['type'] == 'blob']
        extensions = [f.split('.')[-1] for f in files if '.' in f]
        
        # 3. Fetch Key Files (README, main.py, etc.) for Context
        important_files = ['README.md', 'requirements.txt', 'package.json', 'main.py', 'app.py', 'index.html']
        file_contents = ""
        
        for file_path in files[:15]: # Limit to first 15 files to save context
            if any(file_path.endswith(x) for x in important_files) or file_path.count('/') < 2:
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{file_path}"
                content_resp = requests.get(raw_url)
                if content_resp.status_code == 200:
                    # Truncate large files
                    content = content_resp.text[:2000] 
                    file_contents += f"\n--- FILE: {file_path} ---\n{content}\n"

        repo_context = {
            "owner": owner,
            "repo": repo,
            "tree": files,
            "extensions": extensions,
            "contents": file_contents
        }
        return repo_context, None
        
    except Exception as e:
        return None, str(e)

def get_badge_html(score):
    """Generates HTML for the Gamification Badge."""
    if score >= 90:
        return f'<div class="metric-card"><div style="font-size: 40px;">🏆</div><div class="badge" style="background-color: #FFD700; color: #000;">GOLD TIER</div><p>Production Ready</p></div>'
    elif score >= 75:
        return f'<div class="metric-card"><div style="font-size: 40px;">🥈</div><div class="badge" style="background-color: #C0C0C0; color: #000;">SILVER TIER</div><p>Solid Student Work</p></div>'
    else:
        return f'<div class="metric-card"><div style="font-size: 40px;">🥉</div><div class="badge" style="background-color: #CD7F32; color: #000;">BRONZE TIER</div><p>Needs Improvement</p></div>'

def analyze_repo(repo_context, api_key):
    """Sends context to Gemini for the comprehensive audit."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    You are a Senior Staff Engineer conducting a strict code audit. 
    Analyze this student submission. Be honest, direct, and constructive ("tough love").
    
    REPO DATA:
    - Files: {repo_context['tree'][:50]}...
    - Key Contents: {repo_context['contents']}
    
    CRITERIA:
    1. Structure (Modularity, Folder org)
    2. Documentation (README quality)
    3. Best Practices (Tests, Linting, Git usage)
    4. Completeness (Prototype vs Production)

    STRICT OUTPUT FORMAT (Do not deviate):
    
    🛡️ GitHub Repository Audit
    📊 GitGrade Score: [0-100]/100
    
    📝 Executive Summary
    [2-3 sentences]
    
    🔍 Deep Dive Analysis
    ✅ Strengths: [Points]
    ⚠️ Weaknesses: [Points]
    📂 Structure: [Critique]
    📘 Documentation: [Critique]
    
    🗺️ Personalized Roadmap to Success
    [Action Item 1]: [Specific task]
    [Action Item 2]: [Specific task]
    [Action Item 3]: [Specific task]
    [Action Item 4]: [Specific task]
    """
    
    response = model.generate_content(prompt)
    return response.text

def generate_ai_content(repo_context, task_type, api_key):
    """Helper for One-Click Actions."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash') # Use flash for speed
    model = genai.GenerativeModel('gemini-pro') # Use flash for speed
    
    if task_type == "readme":
        prompt = f"Write a professional README.md for this project based on these files: {repo_context['contents']}. Include Install, Usage, and Features sections."
    elif task_type == "tests":
        prompt = f"Write a basic Python unit test file (test_main.py) using 'unittest' for this project code: {repo_context['contents']}. If code is missing, generate a template."
    
    response = model.generate_content(prompt)
    return response.text

# --- MAIN UI ---
st.title("🛡️ GitGrade: AI Repo Auditor")
st.markdown("### Unfold Success from Untold Experiences [cite: 4, 29]")
st.markdown("Analyze your GitHub repository to get a Score, Summary, and Personalized Roadmap. [cite: 8]")

repo_url = st.text_input("🔗 Paste GitHub Repository URL", placeholder="https://github.com/username/project")

if st.button("🚀 Analyze Repository"):
    if not GEMINI_API_KEY:
        st.error("Please provide a Gemini API Key in the sidebar.")
    elif not repo_url:
        st.error("Please enter a repository URL.")
    else:
        with st.spinner("🔍 Cloning repo metadata & analyzing with Gemini..."):
            # 1. Fetch Data
            data, error = fetch_github_data(repo_url, GITHUB_TOKEN)
            
            if error:
                st.error(error)
            else:
                # 2. Analyze with LLM
                analysis_result = analyze_repo(data, GEMINI_API_KEY)
                
                # Extract Score for Badge Logic (Simple parsing)
                try:
                    import re
                    score_match = re.search(r"Score:\s*(\d+)", analysis_result)
                    score = int(score_match.group(1)) if score_match else 0
                except:
                    score = 0
                
                # --- DISPLAY RESULTS ---
                
                # Top Row: Badge + Tech Stack Chart
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("### Grade Badge")
                    st.markdown(get_badge_html(score), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### Tech Stack DNA")
                    if data['extensions']:
                        df = pd.DataFrame({'Language': data['extensions']})
                        chart = alt.Chart(df).mark_arc(innerRadius=50).encode(
                            theta=alt.Theta("count()", stack=True),
                            color=alt.Color("Language", scale={"scheme": "tableau20"}),
                            tooltip=["Language", "count()"]
                        ).properties(height=250)
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        st.warning("No file extensions detected.")

                st.divider()
                
                # Main Analysis Output
                st.markdown(analysis_result)
                
                st.divider()
                
                # --- ONE-CLICK ACTIONS ---
                st.subheader("⚡ AI Assistant Actions")
                ac_col1, ac_col2 = st.columns(2)
                
                with ac_col1:
                    if st.button("📝 Generate Better README"):
                        with st.spinner("Writing documentation..."):
                            readme = generate_ai_content(data, "readme", GEMINI_API_KEY)
                            st.code(readme, language='markdown')
                            
                with ac_col2:
                    if st.button("🧪 Generate Unit Tests"):
                        with st.spinner("Writing tests..."):
                            tests = generate_ai_content(data, "tests", GEMINI_API_KEY)
                            st.code(tests, language='python')
