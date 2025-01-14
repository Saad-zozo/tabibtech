import os
import streamlit as st
from streamlit_chat import message
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Load API key from environment variable
OPENAI_API_KEY = st.secrets["general"]["OPENAI_API_KEY"]

if not OPENAI_API_KEY:
    st.error("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

# Initialize ChatOpenAI with the API key
chat = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model="gpt-4",
    temperature=0.7,
)

# Set up Streamlit page configuration
st.set_page_config(
    page_title="Tabib Tech",
    page_icon="🩺",
    layout="wide",
)

# Title
st.title("Tabib Tech 🩺")

# Define questions in English and Urdu
questions_en = [
    "Hello! I'm MediBot. Let's begin with some basic information. What's your name?",
    "Could you please tell me your age?",
    "What is your gender?",
    "What is your weight in kilograms?",
    "Can you describe the medical issues you are facing?",
]

questions_ur = [
    "ہیلو! میں میڈی بوٹ ہوں۔ آئیے کچھ بنیادی معلومات سے آغاز کرتے ہیں۔ آپ کا نام کیا ہے؟",
    "براہ کرم آپ کی عمر بتائیں؟",
    "آپ کا جنس کیا ہے؟",
    "آپ کا وزن کلوگرام میں کیا ہے؟",
    "آپ کو درپیش طبی مسائل کی وضاحت کر سکتے ہیں؟",
]

# Function to get system message based on language
def get_system_message(language):
    if language == "English":
        return SystemMessage(content="You are MediBot, a virtual doctor specializing in diagnosing patients and prescribing medicine available in Pakistan. Please communicate in English and ask one question at a time.")
    else:
        return SystemMessage(content="آپ میڈی بوٹ ہیں، ایک ورچوئل ڈاکٹر جو مریضوں کی تشخیص اور پاکستان میں دستیاب ادویات تجویز کرنے میں مہارت رکھتے ہیں۔ براہ کرم اردو میں بات چیت کریں اور ایک وقت میں ایک سوال پوچھیں۔")

# Initialize session state for language selection
if 'language' not in st.session_state:
    st.session_state.language = None

# Language selection
if st.session_state.language is None:
    st.markdown("## انتخاب کریں | Select Language")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("English"):
            st.session_state.language = "English"
    with col2:
        if st.button("اردو"):
            st.session_state.language = "Urdu"
    st.stop()

# Initialize session state for conversation history and user input stage
if 'messages' not in st.session_state:
    initial_message = (
        questions_en[0] if st.session_state.language == "English" else questions_ur[0]
    )
    st.session_state.messages = [
        get_system_message(st.session_state.language),
        AIMessage(content=initial_message)
    ]
    st.session_state.stage = 0

# Define a list of questions based on language
if st.session_state.language == "English":
    questions = questions_en
else:
    questions = questions_ur

# Callback function to handle sending messages
def send_message():
    if st.session_state.user_input.strip() != "":
        user_response = st.session_state.user_input.strip()
        st.session_state.messages.append(HumanMessage(content=user_response))
        
        if st.session_state.stage < len(questions) - 1:
            st.session_state.stage += 1  # Move to the next question stage
            next_question = questions[st.session_state.stage]
            st.session_state.messages.append(AIMessage(content=next_question))
        else:
            # Final analysis and prescription
            with st.spinner("Thinking..."):
                response = chat(st.session_state.messages)
            st.session_state.messages.append(AIMessage(content=response.content))
        
        st.session_state.user_input = ""  # Clear the input after sending

# Main chat interface
st.markdown("### Your Virtual Medical Assistant!")

# Display the conversation using message component
for i, msg in enumerate(st.session_state.messages):
    if isinstance(msg, HumanMessage):
        message(msg.content, is_user=True, key=f"user_{i}")
    elif isinstance(msg, AIMessage):
        message(msg.content, is_user=False, key=f"bot_{i}")

# Input section is placed after the chat messages
st.text_input("Your Response:", value="", key="user_input", on_change=send_message)

# Sidebar for Conversation History and Language Display
with st.sidebar:
    st.header("📝 Conversation History")
    if st.session_state.messages:
        for i, msg in enumerate(st.session_state.messages):
            if isinstance(msg, HumanMessage):
                prefix = "**User:**" if st.session_state.language == "English" else "**صارف:**"
                st.markdown(f"{prefix} {msg.content}")
            elif isinstance(msg, AIMessage):
                prefix = "**MediBot:**" if st.session_state.language == "English" else "**میڈی بوٹ:**"
                st.markdown(f"{prefix} {msg.content}")
            if i < len(st.session_state.messages) - 1:
                st.markdown("---")
                
    st.markdown("---")
    st.write(f"**Selected Language:** {st.session_state.language}")
