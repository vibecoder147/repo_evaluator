import streamlit as st
from github import Github
import google.generativeai as genai
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="GitGrade: AI Repo Auditor", page_icon="🚀", layout="wide")

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("Get your free API key at aistudio.google.com")
    gemini_api_key = st.text_input("Gemini API Key", type="password")
    github_token = st.text_input("GitHub Token (Optional)", type="password", help="Use to avoid rate limits")

# --- HELPER FUNCTIONS ---

def get_repo_content(repo_url, gh_token=None):
    """
    Fetches the 'skeleton' of the repo: README, file structure, and key files.
    """
    try:
        if "github.com/" not in repo_url:
            return None, "Invalid GitHub URL"
        
        parts = repo_url.rstrip("/").split("github.com/")[-1].split("/")
        if len(parts) < 2:
            return None, "Invalid URL format"
        
        repo_name = f"{parts[0]}/{parts[1]}"
        
        # Initialize GitHub API
        g = Github(gh_token) if gh_token else Github()
        repo = g.get_repo(repo_name)
        
        # 1. Get Project Structure (File Tree)
        contents = repo.get_contents("")
        file_tree = []
        project_files = {}
        
        # Limit depth to avoid timeout
        while contents:
            file_content = contents.pop(0)
            file_tree.append(file_content.path)
            
            if file_content.type == "dir":
                # Only go one level deep to save time
                if file_tree.count('/') < 2: 
                    try:
                        contents.extend(repo.get_contents(file_content.path))
                    except:
                        pass
            else:
                lower_name = file_content.name.lower()
                # We fetch specific files to judge quality
                if lower_name in ["readme.md", "requirements.txt", "package.json", "dockerfile", "main.py", "app.py", "index.js"]:
                    try:
                        # Decode and store file content
                        project_files[file_content.path] = file_content.decoded_content.decode("utf-8")
                    except:
                        pass
                        
        return {
            "name": repo.name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "tree": file_tree,
            "files": project_files
        }, None

    except Exception as e:
        return None, str(e)

def analyze_repo_with_gemini(repo_data, api_key):
    """
    Sends the repo skeleton to Gemini 1.5 Flash for the 'CTO' analysis.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Construct the prompt based on your problem statement
        prompt = f"""
        You are an elite Senior Software Architect and Tech Lead acting as a judge for a student hackathon.
        You are analyzing a GitHub repository to provide a "Score + Summary + Personalized Roadmap".

        REPO METADATA:
        Name: {repo_data['name']}
        Stars: {repo_data['stars']}
        File Structure: {repo_data['tree']}
        
        KEY CODE ARTIFACTS:
        {str(repo_data['files'])[:25000]} 

        INSTRUCTIONS:
        Analyze the code structure, best practices, documentation, and readability.
        Be critical but constructive.
        
        OUTPUT FORMAT (Strict Markdown):
        
        ## 📊 Score: [0-100]/100
        
        ## 📝 Executive Summary
        [2-3 sentences describing the repo quality, tech stack, and main purpose. Mention if it's "Hireable" or "Needs Work".]
        
        ## 🔍 Deep Dive Analysis
        * **Structure & Organization:** [Critique folder structure and modularity]
        * **Code Quality:** [Critique readability, linting, and complexity based on snippets]
        * **Documentation:** [Critique README and comments]
        * **Best Practices:** [Check for tests, CI/CD, .gitignore, requirements]
        
        ## 🗺️ Personalized Roadmap
        Actionable steps the student must follow to improve this specific project:
        1. [Step 1 - Specific to this project]
        2. [Step 2 - Specific to this project]
        3. [Step 3 - Specific to this project]
        4. [Step 4 - Specific to this project]
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error contacting Gemini API: {e}"

# --- MAIN UI ---
st.title("🤖 GitGrade: AI Code Reviewer")
st.markdown("### Paste a GitHub repository link below to get an instant audit.")

repo_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/username/project")

if st.button("Analyze Repository"):
    if not gemini_api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif not repo_url:
        st.warning("Please enter a URL.")
    else:
        with st.spinner("🔍 Fetching Repository Data..."):
            repo_data, error = get_repo_content(repo_url, github_token)
            
        if error:
            st.error(f"Error fetching repo: {error}")
        else:
            st.success("Data fetched! Analyzing with Gemini 1.5 Flash...")
            
            # Display basic stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Repository", repo_data['name'])
            with col2:
                st.metric("Stars", repo_data['stars'])
            
            with st.spinner("🧠 Generating Score & Roadmap..."):
                analysis = analyze_repo_with_gemini(repo_data, gemini_api_key)
                
            st.markdown("---")
            st.markdown(analysis)
            st.balloons()