GitGrade: AI Code Reviewer 🤖🚀
GitGrade is an intelligent web application designed to help developers and hackathon judges quickly assess the quality and structure of GitHub repositories. Leveraging the power of Google's Gemini 1.5 Flash AI, it provides an instant, comprehensive audit including a score, executive summary, deep dive analysis, and a personalized roadmap for improvement.

Whether you're a student looking to improve your projects, a mentor evaluating submissions, or just curious about best practices, GitGrade offers critical yet constructive feedback to elevate your code.

✨ Features
AI-Powered Repository Audit: Get an objective evaluation of your GitHub repository using Google Gemini 1.5 Flash.
Comprehensive Score & Summary: Receive a clear numerical score (0-100) and an executive summary highlighting the repo's strengths and weaknesses.
Deep Dive Analysis: Detailed feedback on:
Structure & Organization: Critiques folder structure and modularity.
Code Quality: Assesses readability, linting, and complexity based on code snippets.
Documentation: Evaluates the quality of READMEs and in-code comments.
Best Practices: Checks for adherence to standards like testing, CI/CD, and proper dependency management.
Personalized Improvement Roadmap: Get actionable, project-specific steps to enhance your repository.
Interactive Streamlit UI: A user-friendly interface for seamless interaction.
GitHub Token Support: Optionally use a GitHub Personal Access Token to avoid API rate limits during repository content fetching.
🛠️ Tech Stack
| Technology | Description | |---|---| |Python| Primary programming language | |Streamlit| Web application framework for the UI | |Google Generative AI| Powers the AI analysis (Gemini 1.5 Flash) | |PyGithub| Python wrapper for the GitHub API to fetch repository data |

🚀 Getting Started
Follow these instructions to set up and run GitGrade locally.

Prerequisites
Python 3.8+
A Google Gemini API Key (get yours for free at aistudio.google.com)
(Optional) A GitHub Personal Access Token for higher rate limits (create one here)
Installation
Clone the repository:

git clone https://github.com/vibecoder147/repo_evaluator.git
cd repo_evaluator
Create and activate a virtual environment:

python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
Install the required dependencies:

pip install -r requirements.txt
Usage
Run the Streamlit application:

streamlit run app.py
Open your web browser: The application will automatically open in your default web browser (usually at http://localhost:8501).

Configure API Keys:

In the sidebar, enter your Gemini API Key. This is mandatory for the AI analysis.
Optionally, enter your GitHub Token to avoid rate limits when fetching repository data from GitHub.
Analyze a Repository:

Paste the full GitHub repository URL (e.g., https://github.com/streamlit/streamlit) into the input field.
Click the "Analyze Repo" button.
View the Results: The application will display the AI-generated score, summary, deep dive analysis, and a personalized roadmap for the given repository.

📂 Project Structure
.
├── README.md             # Project overview and documentation
├── app.py                # Main Streamlit application logic, UI, GitHub interaction, and Gemini API calls
└── requirements.txt      # List of Python dependencies
