"""
app.py
------
Run with: streamlit run app.py

Flow:
1. Setup — paste resume + job posting, generate questions
2. Interview — for each question: hear it (TTS), speak your answer
   (mic recording -> Whisper transcription), get feedback (text + audio)
3. Summary — overall feedback across the whole session
"""

import streamlit as st
from streamlit_mic_recorder import mic_recorder
from interview import generate_questions, evaluate_answer, generate_summary
from stt import transcribe_audio
from voice import text_to_speech

st.set_page_config(page_title="Interview Coach", page_icon="🎤")
st.title("🎤 Voice Interview Coach")
st.caption("Practice interview questions tailored to a real job posting — answer out loud, get real feedback.")

# --- Session state setup ---
if "stage" not in st.session_state:
    st.session_state.stage = "setup"  # setup -> interview -> summary
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "transcript" not in st.session_state:
    st.session_state.transcript = []
if "current_feedback" not in st.session_state:
    st.session_state.current_feedback = None


def reset_session():
    st.session_state.stage = "setup"
    st.session_state.questions = []
    st.session_state.current_index = 0
    st.session_state.transcript = []
    st.session_state.current_feedback = None


# --- Stage 1: Setup ---
if st.session_state.stage == "setup":
    resume_text = st.text_area("Paste your resume text", height=200)
    job_posting_text = st.text_area("Paste the job posting text", height=200)
    count = st.slider("Number of questions", 3, 8, 5)

    if st.button("Generate questions", type="primary"):
        if not resume_text.strip() or not job_posting_text.strip():
            st.error("Please paste both your resume and the job posting.")
        else:
            with st.spinner("Preparing tailored interview questions..."):
                st.session_state.questions = generate_questions(resume_text, job_posting_text, count)
            st.session_state.stage = "interview"
            st.rerun()

# --- Stage 2: Interview ---
elif st.session_state.stage == "interview":
    idx = st.session_state.current_index
    total = len(st.session_state.questions)

    if idx >= total:
        st.session_state.stage = "summary"
        st.rerun()

    question = st.session_state.questions[idx]
    st.subheader(f"Question {idx + 1} of {total}")
    st.write(question)

    # Play the question aloud
    question_audio = text_to_speech(question)
    st.audio(question_audio)

    if st.session_state.current_feedback is None:
        st.write("Record your answer when you're ready:")
        audio = mic_recorder(start_prompt="🎙️ Start recording", stop_prompt="⏹️ Stop", key=f"rec_{idx}")

        if audio:
            with st.spinner("Transcribing your answer..."):
                answer_text = transcribe_audio(audio["bytes"])
            st.write(f"**You said:** {answer_text}")

            with st.spinner("Getting feedback..."):
                feedback = evaluate_answer(question, answer_text)

            st.session_state.transcript.append({
                "question": question,
                "answer": answer_text,
                "feedback": feedback,
            })
            st.session_state.current_feedback = feedback
            st.rerun()
    else:
        st.write(f"**You said:** {st.session_state.transcript[idx]['answer']}")
        st.info(st.session_state.current_feedback)
        feedback_audio = text_to_speech(st.session_state.current_feedback)
        st.audio(feedback_audio)

        button_label = "Next question" if idx + 1 < total else "See final summary"
        if st.button(button_label, type="primary"):
            st.session_state.current_index += 1
            st.session_state.current_feedback = None
            st.rerun()

# --- Stage 3: Summary ---
elif st.session_state.stage == "summary":
    st.subheader("Practice session summary")
    with st.spinner("Putting together your overall feedback..."):
        summary = generate_summary(st.session_state.transcript)
    st.write(summary)
    summary_audio = text_to_speech(summary)
    st.audio(summary_audio)

    with st.expander("Full transcript"):
        for i, item in enumerate(st.session_state.transcript, 1):
            st.markdown(f"**Q{i}: {item['question']}**")
            st.write(f"Your answer: {item['answer']}")
            st.write(f"Feedback: {item['feedback']}")
            st.divider()

    if st.button("Start a new practice session"):
        reset_session()
        st.rerun()
