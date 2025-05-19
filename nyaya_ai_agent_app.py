import streamlit as st
import openai
import os
import requests
from dotenv import load_dotenv

# Load environment variables (fallback for local development)
load_dotenv()

# Set API keys from Streamlit secrets or environment variables
openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
github_token = st.secrets.get("GITHUB_TOKEN", os.getenv("GITHUB_TOKEN"))

if openai_api_key:
    openai.api_key = openai_api_key

# GitHub API functions with authentication
def get_github_headers():
    """Get GitHub API headers with authentication if available"""
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    return headers

def search_github_repos(query, sort="stars", order="desc", per_page=5):
    """Search for repositories on GitHub"""
    try:
        url = f"https://api.github.com/search/repositories"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page
        }
        response = requests.get(url, headers=get_github_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_repo_info(owner, repo):
    """Get information about a specific repository"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url, headers=get_github_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_repo_readme(owner, repo):
    """Get the README content of a repository"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        headers = get_github_headers()
        headers["Accept"] = "application/vnd.github.v3.raw"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching README: {str(e)}"

# OpenAI functions with manual guardrails
def get_legal_response(query):
    """Get legal response with manual guardrails"""
    if not openai_api_key:
        return "Error: OpenAI API key not found. Please set it in the Streamlit secrets or .env file."

    try:
        system_prompt = """
        You are Nyaya_AI_Agent, an AI legal expert on Indian law.

        Answer the following legal query in a respectful, factual, and helpful manner.
        Always include:
        - Legal provisions or case references where applicable
        - Clear next steps
        - This disclaimer: ⚠️ This response is for informational purposes only and does not constitute legal advice.

        Never provide specific legal advice that could be construed as practicing law.
        Always maintain a professional tone and acknowledge limitations of AI in legal contexts.
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

def analyze_repository(repo_info, readme):
    """Analyze repository with manual guardrails"""
    if not openai_api_key:
        return "Error: OpenAI API key not found. Please set it in the Streamlit secrets or .env file."

    try:
        system_prompt = """
        You are Nyaya_AI_Agent, an AI expert on legal technology and GitHub repositories.

        Analyze the following repository from a legal tech perspective.
        Focus on:
        1. What legal problems this repository helps solve
        2. Its relevance to legal professionals
        3. Potential applications in Indian legal practice
        4. Any legal compliance considerations
        5. How it compares to other legal tech solutions

        Maintain a professional tone and provide factual analysis based on the repository information.
        """

        user_prompt = f"""
        Repository: {repo_info.get('full_name', 'Unknown')}
        Description: {repo_info.get('description', 'No description')}
        Language: {repo_info.get('language', 'Not specified')}
        Stars: {repo_info.get('stargazers_count', 0)}
        Forks: {repo_info.get('forks_count', 0)}

        README excerpt:
        {readme[:1000]}... (truncated)
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing repository: {str(e)}"

# Streamlit page config
st.set_page_config(page_title="Nyaya_AI_Agent – Indian Legal AI Assistant", page_icon="⚖️", layout="wide")

st.title("⚖️ Nyaya_AI_Agent – Your Indian Legal AI Assistant")
st.markdown(
    """
    Welcome to **Nyaya_AI_Agent**, your AI assistant specializing in Indian Judiciary Law.
    Ask any legal question – from property disputes to criminal law.
    Get plain-English answers backed by real Indian statutes 🇮🇳
    """
)
st.info("🛑 **Disclaimer**: Nyaya_AI_Agent provides *informational* legal responses only. It does **not** replace advice from a licensed lawyer.")

# Check if API keys are set
if not openai_api_key:
    st.warning("⚠️ OpenAI API key not found. Please set it in the Streamlit secrets or .env file.")
    with st.expander("How to set up your OpenAI API key"):
        st.markdown("""
        ### Option 1: Using Streamlit Secrets (recommended for deployment)
        1. Create a file at `.streamlit/secrets.toml`
        2. Add the following line: `OPENAI_API_KEY = "your_key_here"`

        ### Option 2: Using .env file (for local development)
        1. Create a file named `.env` in the same directory as this app
        2. Add the following line: `OPENAI_API_KEY=your_key_here`
        """)

# GitHub authentication status
if github_token:
    st.sidebar.success("✅ GitHub API: Authenticated")
else:
    st.sidebar.info("ℹ️ GitHub API: Using unauthenticated access (rate limited)")
    with st.sidebar.expander("Set up GitHub authentication"):
        st.markdown("""
        To increase GitHub API rate limits:
        1. Create a GitHub personal access token
        2. Add it to `.streamlit/secrets.toml` as `GITHUB_TOKEN = "your_token_here"`
        """)

# Sidebar for navigation
st.sidebar.title("Nyaya AI Tools")
option = st.sidebar.radio(
    "Select a tool",
    ["Legal AI Assistant", "Search Legal Tech Repositories", "Analyze Repository"]
)

# Legal AI Assistant
if option == "Legal AI Assistant":
    # Input from user
    user_query = st.text_input("📩 Enter your legal question below:")

    # Display result
    if user_query:
        with st.spinner("🔍 Analyzing Indian law..."):
            response = get_legal_response(user_query)
            st.markdown(f"""### 📜 Legal Response:

{response}
""")

# Search Repositories
elif option == "Search Legal Tech Repositories":
    st.header("Search Legal Tech GitHub Repositories")

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        search_query = st.text_input("Search query", placeholder="e.g., legal nlp contract analysis")

    with col2:
        sort_by = st.selectbox("Sort by", ["stars", "forks", "updated"])

    with col3:
        per_page = st.slider("Results", 1, 10, 5)

    if st.button("Search"):
        if not search_query:
            st.error("Please enter a search query.")
        else:
            # Add "legal" to the search query if not already present
            if "legal" not in search_query.lower():
                search_query = f"legal {search_query}"

            with st.spinner("Searching repositories..."):
                results = search_github_repos(search_query, sort_by, "desc", per_page)

                if "error" in results:
                    st.error(f"Error: {results['error']}")
                else:
                    st.success(f"Found {results.get('total_count', 0)} repositories")

                    for item in results.get("items", []):
                        with st.expander(f"{item['full_name']} - ⭐ {item['stargazers_count']}"):
                            st.markdown(f"**Description:** {item['description'] or 'No description'}")
                            st.markdown(f"**Language:** {item['language'] or 'Not specified'}")
                            st.markdown(f"**URL:** [{item['html_url']}]({item['html_url']})")

                            if st.button(f"Analyze with Nyaya AI", key=f"analyze_{item['id']}"):
                                with st.spinner("Analyzing repository..."):
                                    readme = get_repo_readme(item['owner']['login'], item['name'])
                                    analysis = analyze_repository(item, readme)
                                    st.markdown("### Nyaya AI Analysis")
                                    st.markdown(analysis)

# Analyze Repository
elif option == "Analyze Repository":
    st.header("Analyze GitHub Repository")

    repo_url = st.text_input("Repository URL", placeholder="e.g., https://github.com/username/repo")

    if st.button("Analyze"):
        if not repo_url:
            st.error("Please enter a repository URL.")
        else:
            # Extract owner and repo name from URL
            parts = repo_url.strip("/").split("/")
            if len(parts) >= 5 and parts[2] == "github.com":
                owner = parts[3]
                repo = parts[4]

                with st.spinner(f"Analyzing {owner}/{repo}..."):
                    # Get repository info
                    repo_info = get_repo_info(owner, repo)

                    if "error" in repo_info:
                        st.error(f"Error: {repo_info['error']}")
                    else:
                        # Display repository info
                        st.subheader("Repository Information")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Stars", repo_info.get("stargazers_count", 0))
                        col2.metric("Forks", repo_info.get("forks_count", 0))
                        col3.metric("Open Issues", repo_info.get("open_issues_count", 0))

                        st.markdown(f"**Description:** {repo_info.get('description', 'No description')}")
                        st.markdown(f"**Language:** {repo_info.get('language', 'Not specified')}")

                        # Get README
                        readme = get_repo_readme(owner, repo)

                        # Get AI analysis
                        analysis = analyze_repository(repo_info, readme)

                        # Display AI analysis
                        st.subheader("Nyaya AI Analysis")
                        st.markdown(analysis)

                        # Display README
                        with st.expander("View README"):
                            st.markdown(readme)
            else:
                st.error("Invalid GitHub repository URL. Please use the format: https://github.com/username/repo")

# Footer
st.markdown("---")
st.markdown("Nyaya AI Agent | Built with Streamlit, OpenAI, and GitHub API")