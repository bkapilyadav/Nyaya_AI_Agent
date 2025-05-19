import streamlit as st
import openai
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="NyayaBot - Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-family: 'Serif';
        color: #1a365d;
    }
    .gold-text {
        color: #c9b037;
    }
    .chat-message-user {
        background-color: #1a365d;
        color: white;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
        text-align: right;
        max-width: 80%;
        margin-left: auto;
    }
    .chat-message-bot {
        background-color: #f0f2f6;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
        text-align: left;
        max-width: 80%;
    }
    .chat-timestamp {
        font-size: 0.8em;
        color: #888;
        margin-top: 5px;
    }
    .disclaimer {
        background-color: #f8f9fa;
        border-left: 5px solid #c9b037;
        padding: 10px;
        margin: 10px 0;
        font-size: 0.9em;
    }
    .stTextInput>div>div>input {
        border-radius: 10px 0 0 10px !important;
    }
    .send-button {
        border-radius: 0 10px 10px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# NyayaBot system prompt
NYAYABOT_SYSTEM_PROMPT = """You are "NyayaBot," an expert AI legal assistant specializing in Indian Judiciary Law. Respond to users' legal queries with the accuracy, clarity, and professionalism of a seasoned Indian lawyer. Provide concise, reliable, and up-to-date information on Indian laws, court procedures, and legal rights.

Your knowledge covers:
1. Indian Legal System - Constitution, judiciary structure, landmark cases
2. Criminal Laws - IPC, CrPC, Evidence Act, FIR procedures
3. Civil Laws - CPC, Contract Act, Property laws, tenancy rights
4. Family Laws - Marriage, divorce, maintenance across different personal laws
5. Consumer Protection - Rights, complaint procedures, remedies
6. Constitutional Rights - Fundamental rights, remedies, enforcement

Always follow these guidelines:
1. Begin with a clear, direct answer to the legal question
2. Provide relevant legal context and background
3. Explain applicable laws, statutes, or precedents
4. Use plain language with necessary legal terms explained
5. Include citations to relevant statutes or case law when appropriate
6. Suggest potential next steps or resources

Always end your response with this disclaimer: "Please note that this information is provided for educational purposes only and does not constitute legal advice. For specific legal concerns, please consult with a qualified legal professional who can provide personalized guidance based on your particular situation."

For complex matters, use this enhanced disclaimer: "This matter involves complex legal considerations that may require professional legal representation. The information provided is general in nature, and I strongly recommend consulting with a qualified advocate who specializes in this area of law for personalized advice."
"""

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am NyayaBot, an expert AI legal assistant specializing in Indian Judiciary Law. How can I help you today?", "timestamp": datetime.now().strftime("%H:%M")}
    ]

if 'api_key' not in st.session_state:
    st.session_state.api_key = os.environ.get("OPENAI_API_KEY", "")

if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False

# Function to validate OpenAI API key
def validate_api_key(api_key):
    if not api_key or len(api_key.strip()) < 10:
        return False
    
    try:
        client = openai.OpenAI(api_key=api_key)
        # Make a minimal API call to validate the key
        models = client.models.list(limit=1)
        return True
    except Exception as e:
        st.error(f"API key validation error: {str(e)}")
        return False

# Function to generate response from OpenAI
def generate_response(messages, api_key):
    try:
        # Prepare conversation history for API
        conversation = [{"role": "system", "content": NYAYABOT_SYSTEM_PROMPT}]
        
        # Add user messages and assistant responses
        for msg in messages:
            if msg["role"] in ["user", "assistant"]:
                conversation.append({"role": msg["role"], "content": msg["content"]})
        
        # Create OpenAI client with the provided API key
        client = openai.OpenAI(api_key=api_key)
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            temperature=0.7,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return f"I apologize, but I encountered an error while processing your request. Please check your API key or try again later.\n\nError details: {str(e)}"

# Function to simulate response for demo purposes when no API key is provided
def simulate_response(query):
    query = query.lower()
    
    if "fir" in query or "police complaint" in query:
        return """An FIR (First Information Report) can be filed at any police station by visiting in person, submitting a written complaint, or in some cases, filing online through state police portals.

The process typically involves:
1. Approaching the police station with jurisdiction over the area where the crime occurred
2. Providing details of the incident to the officer in charge
3. The officer will record your statement and register the FIR under Section 154 of the Criminal Procedure Code, 1973
4. You should receive a free copy of the FIR

If the police refuse to register your FIR, you have legal remedies including:
- Approaching a senior police officer
- Filing a complaint directly to the Judicial Magistrate under Section 156(3) CrPC
- Filing a writ petition in the High Court

Please note that this information is provided for educational purposes only and does not constitute legal advice. For specific legal concerns, please consult with a qualified legal professional who can provide personalized guidance based on your particular situation."""
    
    elif "landlord" in query or "tenant" in query or "rent" in query or "evict" in query:
        return """In India, landlord-tenant relationships are primarily governed by state-specific Rent Control Acts. A landlord cannot legally evict a tenant without proper notice and following due process under the applicable Rent Control Act.

A landlord must typically provide a valid reason for eviction as specified in the relevant Act, such as:
- Non-payment of rent
- Subletting without permission
- Using the premises for purposes other than those agreed upon
- Causing damage to the property
- The landlord requiring the premises for personal use

Even with valid grounds, the landlord must:
1. Serve a legal notice specifying the reason for eviction
2. File an eviction petition in the Rent Controller's court
3. Obtain a court order before attempting to evict you

This matter involves complex legal considerations that may require professional legal representation. The information provided is general in nature, and I strongly recommend consulting with a qualified advocate who specializes in this area of law for personalized advice."""
    
    else:
        return f"""Thank you for your question about "{query}". To provide you with accurate information, I would need to understand more specific details about your legal concern.

Indian law covers various domains including constitutional law, criminal law, civil law, family law, property law, and more. Each area has specific statutes, procedures, and case precedents.

Please feel free to ask more specific questions about your legal concern, and I'll do my best to provide relevant information.

Please note that this information is provided for educational purposes only and does not constitute legal advice. For specific legal concerns, please consult with a qualified legal professional who can provide personalized guidance based on your particular situation."""

# Sidebar for API key configuration
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/scales--v1.png", width=80)
    st.markdown("<h1 class='main-header'><span>Nyaya</span><span class='gold-text'>Bot</span></h1>", unsafe_allow_html=True)
    st.markdown("### Indian Legal Assistant")
    
    st.markdown("---")
    
    st.markdown("### OpenAI API Key Configuration")
    api_key = st.text_input("Enter your OpenAI API key", 
                           value=st.session_state.api_key, 
                           type="password",
                           help="Your API key is stored in this session only and not saved on any server.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Validate Key"):
            if validate_api_key(api_key):
                st.session_state.api_key = api_key
                st.session_state.api_key_valid = True
                st.success("API key is valid!")
            else:
                st.session_state.api_key_valid = False
                st.error("Invalid API key")
    
    with col2:
        if st.button("Clear Key"):
            st.session_state.api_key = ""
            st.session_state.api_key_valid = False
            st.info("API key cleared")
    
    if not api_key:
        st.warning("No API key provided. The app will run in demo mode with simulated responses.")
    
    st.markdown("---")
    
    st.markdown("### About")
    st.markdown("""
    NyayaBot is an AI legal assistant specializing in Indian Judiciary Law. It provides information on:
    - Indian legal system
    - Criminal and civil laws
    - Family laws
    - Consumer protection
    - Constitutional rights
    """)
    
    st.markdown("---")
    
    st.markdown("### Resources")
    st.markdown("""
    - [Supreme Court of India](https://main.sci.gov.in/)
    - [India Code](https://www.indiacode.nic.in/)
    - [e-Courts Services](https://ecourts.gov.in/ecourts_home/)
    - [National Legal Services Authority](https://nalsa.gov.in/)
    """)

# Main chat interface
st.markdown("<h1 class='main-header'>Chat with <span>Nyaya</span><span class='gold-text'>Bot</span></h1>", unsafe_allow_html=True)
st.markdown("Ask any question about Indian law and legal procedures")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div class='chat-message-user'>{message['content']}<div class='chat-timestamp'>{message['timestamp']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-message-bot'>{message['content']}<div class='chat-timestamp'>{message['timestamp']}</div></div>", unsafe_allow_html=True)

# Input area for user questions
st.markdown("---")
with st.container():
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input("Your legal question:", key="user_question", placeholder="e.g., How do I file an FIR in India?")
    with col2:
        send_button = st.button("Send", use_container_width=True)

# Process user input
if send_button and user_input:
    # Add user message to chat
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
    
    # Display user message immediately
    st.markdown(f"<div class='chat-message-user'>{user_input}<div class='chat-timestamp'>{timestamp}</div></div>", unsafe_allow_html=True)
    
    # Show loading spinner while generating response
    with st.spinner("NyayaBot is thinking..."):
        # Generate response based on whether API key is valid
        if st.session_state.api_key and st.session_state.api_key_valid:
            response = generate_response(st.session_state.messages, st.session_state.api_key)
        else:
            response = simulate_response(user_input)
    
    # Add assistant response to chat
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
    
    # Display assistant response
    st.markdown(f"<div class='chat-message-bot'>{response}<div class='chat-timestamp'>{timestamp}</div></div>", unsafe_allow_html=True)
    
    # Clear the input box
    st.session_state.user_question = ""
    st.experimental_rerun()

# Legal disclaimer at the bottom
st.markdown("---")
st.markdown("<div class='disclaimer'>⚠️ <strong>Legal Disclaimer:</strong> Information provided by NyayaBot is for educational purposes only and does not constitute legal advice. For specific legal concerns, please consult with a qualified legal professional.</div>", unsafe_allow_html=True)
