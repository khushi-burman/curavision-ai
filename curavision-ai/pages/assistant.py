import time
import streamlit as st

st.set_page_config(
    page_title="Assistant | CuraVision AI",
    page_icon="🩺",
    layout="wide"
)

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "text": "Hi! I'm CuraVision AI. How can I help you today?"}
    ]

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

.stApp {
    background: linear-gradient(180deg, #040914 0%, #071224 100%);
}

[data-testid="stSidebar"] {
    background: rgba(9,15,28,0.9);
    border-right: 1px solid rgba(148,163,184,0.12);
}

.nav-logo {
    font-weight: 800;
    font-size: 1.2rem;
    color: #e2e8f0;
}

.bubble {
    padding: 12px 16px;
    border-radius: 14px;
    margin: 6px 0;
    max-width: 75%;
    font-size: 0.92rem;
    line-height: 1.5;
}
.bubble.user {
    background: linear-gradient(90deg, #0ea5e9, #6366f1);
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}
.bubble.assistant {
    background: rgba(15,23,42,0.6);
    border: 1px solid rgba(148,163,184,0.15);
    color: #e2e8f0;
    margin-right: auto;
    border-bottom-left-radius: 4px;
}

.typing {
    color: #94a3b8;
    font-size: 0.85rem;
    font-style: italic;
    margin: 6px 0;
}
</style>
""", unsafe_allow_html=True)


def get_reply(message):
    message = message.lower()
    if "symptom" in message:
        return "Can you tell me your symptoms in more detail? How long have you been experiencing them?"
    elif "medicine" in message or "tablet" in message:
        return "I can provide general information about medicines. Please tell me the medicine name."
    elif "diet" in message or "exercise" in message:
        return "A healthy diet and regular exercise are important. What health goal are you trying to achieve?"
    elif "emergency" in message:
        return "If this is an emergency, please contact your nearest hospital or emergency service immediately."
    else:
        return "Can you explain your problem in a little more detail?"


# ---- nav bar ----
# ---------------- Navigation Bar ----------------

left, right = st.columns([1, 3])

with left:
    st.markdown("## 🩺 CuraVision AI")

with right:
    nav1, nav2, nav3, nav4, nav5, nav6, nav7 = st.columns(7)

    with nav1:
        st.page_link("pages/home.py", label="🏠 Home")

    with nav2:
        st.page_link("pages/assistant.py", label="💬 Assistant")

    with nav3:
        st.page_link("pages/disease_detection.py", label="🩺 Detection")

    with nav4:
        st.page_link("pages/reports.py", label="📄 Reports")

    with nav5:
        st.page_link("pages/dashboard.py", label="📊 Dashboard")

    with nav6:
        st.page_link("pages/profile.py", label="👤 Profile")

    with nav7:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.switch_page("app.py")

st.divider()

# ---- sidebar: chat controls ----
with st.sidebar:
    st.header("Chat")

    if st.button("Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "text": "Hi! I'm CuraVision AI. How can I help you today?"}
        ]
        st.rerun()

    chat_log = ""
    for message in st.session_state.messages:
        chat_log += f'{message["role"].title()}: {message["text"]}\n\n'

    st.download_button("Export Chat", chat_log, file_name="chat.txt")

# ---- quick actions ----
st.subheader("Quick Actions")
b1, b2, b3, b4 = st.columns(4)

question = None
with b1:
    if st.button("Symptoms"):
        question = "I have some symptoms."
with b2:
    if st.button("Medicine"):
        question = "Tell me about a medicine."
with b3:
    if st.button("Lifestyle"):
        question = "Give me lifestyle advice."
with b4:
    if st.button("Emergency"):
        question = "This is an emergency."

# ---- chat window ----
chat_window = st.container(height=420)

with chat_window:
    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["text"])

text = st.chat_input("Type your message")

if question:
    text = question

if text:
    st.session_state.messages.append({"role": "user", "text": text})
    time.sleep(0.5)
    answer = get_reply(text)
    st.session_state.messages.append({"role": "assistant", "text": answer})
    st.rerun()