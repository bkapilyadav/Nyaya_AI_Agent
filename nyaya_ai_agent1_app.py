
import streamlit as st
import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page config
st.set_page_config(page_title="Nyaya_AI_Agent – Indian Legal AI Assistant", page_icon="⚖️", layout="centered")

# App title and description
st.title("⚖️ Nyaya_AI_Agent – Your Indian Legal AI Assistant")
st.markdown(
    """
    Welcome to **Nyaya_AI_Agent**, your AI assistant specializing in Indian Judiciary Law.  
    Ask any legal question – from property disputes to criminal law.  
    Get plain-English answers backed by real Indian statutes 🇮🇳
    """
)

# Disclaimer
st.info("🛑 **Disclaimer**: Nyaya_AI_Agent provides *informational* legal responses only. It does **not** replace advice from a licensed lawyer.")

# User input
user_query = st.text_input("📩 Enter your legal question below:")

# Generate legal response
def get_legal_response(query):
    prompt = f"""
You are “Nyaya_AI_Agent,” an expert AI legal assistant specializing in Indian Judiciary Law.

Respond to the user's question below in plain language, backed by Indian statutes or case law. Always include:
- Relevant legal provisions or sections
- Practical next steps (what the user can do)
- This final disclaimer:

⚠️ This response is for informational purposes only and does not constitute legal advice.

User Question: {query}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message["content"].strip()

# Show result
if user_query:
    with st.spinner("🔍 Analyzing Indian law..."):
        legal_answer = get_legal_response(user_query)
        st.markdown(f"""### 📜 Legal Response:

{legal_answer}
""")

