"""
interview.py
------------
The core logic: turning a resume + job posting into tailored
interview questions, and evaluating spoken answers afterward.

Unlike the bank agent and learning agent, this doesn't need
tool-calling — there's no external data to fetch or action to take,
just two well-designed prompts. This is a good example of when a
simpler LLM chain is the right tool, not every problem needs an
agent framework.
"""

import re
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", google_api_key=GEMINI_API_KEY)

QUESTION_PROMPT = """You are an experienced interviewer preparing
questions for a candidate. Based on the resume and job posting below,
write {count} interview questions that a real interviewer would
likely ask — a mix of behavioral questions ("tell me about a time...")
and questions specific to the role's requirements.

RESUME:
{resume}

JOB POSTING:
{job_posting}

Output ONLY the questions, one per line, numbered 1 to {count}.
No preamble, no explanations."""

EVAL_PROMPT = """You are an interview coach giving feedback on a
spoken answer. Be encouraging but honest — this is practice, so
useful feedback matters more than empty praise.

QUESTION ASKED:
{question}

CANDIDATE'S SPOKEN ANSWER (transcribed from audio, so it may have
minor transcription errors — don't penalize small transcription
artifacts):
{answer}

Give feedback covering:
1. Did they actually answer the question asked?
2. For behavioral questions: did they use a clear structure (like
   situation, task, action, result)? For technical/role questions:
   was the answer specific and relevant?
3. One concrete thing they did well.
4. One concrete thing to improve next time.

Keep it conversational and under 120 words — this will be read aloud."""

SUMMARY_PROMPT = """You are an interview coach wrapping up a practice
session. Based on the full transcript of questions, answers, and
feedback below, give a short overall summary: 2-3 patterns you
noticed across their answers (strengths and areas to work on), and
one piece of encouragement to end on.

TRANSCRIPT:
{transcript}

Keep it under 150 words, conversational, since this will be read aloud."""


def generate_questions(resume_text: str, job_posting_text: str, count: int = 5) -> list:
    """Returns a list of `count` interview question strings."""
    prompt = QUESTION_PROMPT.format(resume=resume_text, job_posting=job_posting_text, count=count)
    response = llm.invoke(prompt)
    text = response.content if isinstance(response.content, str) else str(response.content)

    # Strip leading numbering like "1. " or "1)" from each line.
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    questions = [re.sub(r"^\d+[\.\)]\s*", "", line) for line in lines]
    return questions[:count]


def evaluate_answer(question: str, answer_text: str) -> str:
    """Returns feedback text for one question/answer pair."""
    prompt = EVAL_PROMPT.format(question=question, answer=answer_text)
    response = llm.invoke(prompt)
    return response.content if isinstance(response.content, str) else str(response.content)


def generate_summary(transcript: list) -> str:
    """
    transcript: list of dicts like
        {"question": ..., "answer": ..., "feedback": ...}
    Returns an overall summary of the practice session.
    """
    transcript_text = "\n\n".join(
        f"Q: {item['question']}\nA: {item['answer']}\nFeedback: {item['feedback']}"
        for item in transcript
    )
    prompt = SUMMARY_PROMPT.format(transcript=transcript_text)
    response = llm.invoke(prompt)
    return response.content if isinstance(response.content, str) else str(response.content)
