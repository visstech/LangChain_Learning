"""
ingest.py
---------
Turns an uploaded PDF or text file into a searchable vector store.

The process (this is what "RAG" — Retrieval-Augmented Generation —
actually means in practice):
1. Load the raw text out of the file
2. Split it into small overlapping chunks (a whole textbook is too
   big to hand the model at once, and models answer better from a
   few focused chunks than one giant wall of text)
3. Turn each chunk into a vector embedding (a list of numbers that
   captures its meaning) and store it in Chroma, a local vector
   database
4. Later, when the agent has a question, it embeds the question the
   same way and finds the chunks whose embeddings are closest —
   i.e. the most relevant material — instead of searching for exact
   keyword matches.
"""

import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from config import GEMINI_API_KEY

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",  # check Google's docs if this is ever retired
    google_api_key=GEMINI_API_KEY,
)


def build_vectorstore_from_upload(uploaded_file) -> Chroma:
    """
    uploaded_file: a Streamlit UploadedFile object (from st.file_uploader).

    Returns a Chroma vector store ready to be searched.
    """
    # Streamlit gives us the file in memory; LangChain's loaders expect
    # a real file path, so we write it to a temporary file first.
    suffix = ".pdf" if uploaded_file.name.lower().endswith(".pdf") else ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path, encoding="utf-8")

        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,      # characters per chunk
            chunk_overlap=150,    # slight overlap so ideas aren't cut mid-thought
        )
        chunks = splitter.split_documents(documents)

        # Each Streamlit session gets its own in-memory collection —
        # we don't persist to disk, so nothing lingers between uploads.
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
        )
        return vectorstore
    finally:
        os.unlink(tmp_path)  # clean up the temp file either way
