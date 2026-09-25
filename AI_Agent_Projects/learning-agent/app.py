"""
app.py
------
Run with: streamlit run app.py

Two phases:
1. Upload a PDF/text file — it gets chunked and embedded into a
   vector store.
2. Chat — ask questions, the agent decides when to search the
   document, and every answer can be played back as audio.
"""

import uuid
import streamlit as st
import tools
from ingest import build_vectorstore_from_upload
from agent import send_message
from voice import text_to_speech

st.set_page_config(page_title="Learning Agent", page_icon="📚")
st.title("📚 Learning Agent")
st.caption("Upload a PDF or text file and learn from it — with text and voice explanations.")

# One conversation "thread" per browser session, so memory doesn't
# bleed between different people using the app.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_ready" not in st.session_state:
    st.session_state.document_ready = False

# --- Upload phase ---
uploaded_file = st.file_uploader("Upload a PDF or .txt file", type=["pdf", "txt"])

if uploaded_file and not st.session_state.document_ready:
    with st.spinner("Reading and indexing your document..."):
        vectorstore = build_vectorstore_from_upload(uploaded_file)
        tools.CURRENT_VECTORSTORE = vectorstore
        st.session_state.document_ready = True
    st.success(f"Loaded {uploaded_file.name} — ask me anything about it!")

# --- Chat phase ---
if st.session_state.document_ready:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and "audio" in msg:
                st.audio(msg["audio"])

    user_input = st.chat_input("Ask a question about the document...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Make sure the tool is pointed at this session's document
                # in case Streamlit reran the script.
                reply = send_message(st.session_state.session_id, user_input)
                st.write(reply)

                with st.spinner("Generating audio..."):
                    audio = text_to_speech(reply)
                st.audio(audio)

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "audio": audio,
        })
else:
    st.info("Upload a document above to get started.")
