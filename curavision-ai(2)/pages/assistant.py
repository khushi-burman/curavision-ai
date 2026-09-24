import requests
import streamlit as st
from theme import inject_theme, top_nav, page_header
from backend import clinical_chat

st.set_page_config(page_title="Assistant | CuraVision AI", page_icon="🩺", layout="wide", initial_sidebar_state="collapsed")
if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

inject_theme()
top_nav()
page_header("Clinical assistant", "Ask a clinical question. The supplied backend grounds responses in its local clinical knowledge base.", "chat")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "text": "Hi. Ask me a clinical question and I’ll use the configured CuraVision knowledge base."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["text"])

text = st.chat_input("Ask a clinical question")
if text:
    st.session_state.messages.append({"role": "user", "text": text})
    try:
        with st.spinner("Searching the clinical knowledge base..."):
            result = clinical_chat(text)
        answer = result.get("clinical_response", "No answer was returned.")
    except requests.RequestException as exc:
        answer = f"The clinical backend is not reachable right now: {exc}"
    except Exception as exc:
        answer = f"The assistant could not complete the request: {exc}"
    st.session_state.messages.append({"role": "assistant", "text": answer})
    st.rerun()

st.caption("AI-generated clinical information is for decision support only and should be reviewed by a qualified healthcare professional.")
