
import streamlit as st
import openai
import os
from guardrails import Guard
from guardrails.hooks import validators

# Set your OpenAI API key (automatically from Streamlit secrets or env)
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# Streamlit page config
st.set_page_config(page_title="Nyaya_AI_Agent – Indian Legal AI Assistant", page_icon="⚖️", layout="centered")

st.title("⚖️ Nyaya_AI_Agent – Your Indian Legal AI Assistant")
st.markdown(
    """
    Welcome to **Nyaya_AI_Agent**, your AI assistant specializing in Indian Judiciary Law.  
    Ask any legal question – from property disputes to criminal law.  
    Get plain-English answers backed by real Indian statutes 🇮🇳
    """
)
st.info("🛑 **Disclaimer**: Nyaya_AI_Agent provides *informational* legal responses only. It does **not** replace advice from a licensed lawyer.")

# Input from user
user_query = st.text_input("📩 Enter your legal question below:")

# Define a guardrail to validate safe legal responses
guard = Guard.from_pydantic(output_class=dict, prompt_template="""
You are Nyaya_AI_Agent, an AI legal expert on Indian law.

Answer the following legal query in a respectful, factual, and helpful manner.
Always include:
- Legal provisions or case references where applicable
- Clear next steps
- This disclaimer: ⚠️ This response is for informational purposes only and does not constitute legal advice.

Legal Query: {{query}}

@output
{{answer: string}}
""")

# Generate legal response with validation
def get_guarded_response(query):
    raw_prompt = f"Legal Query: {query}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": raw_prompt}]
    )
    raw_output = {"answer": response['choices'][0]['message']['content']}
    validated_output, _ = guard.parse(raw_prompt, llm_output=raw_output["answer"])
    return validated_output["answer"]

# Display result
if user_query:
    with st.spinner("🔍 Analyzing Indian law..."):
        response = get_guarded_response(user_query)
        st.markdown(f"""### 📜 Legal Response:

{response}
""")
