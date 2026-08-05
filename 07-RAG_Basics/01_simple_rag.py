"""
====================================================
Simple RAG Question Answering System

Flow:

Text File
    |
    v
Loader
    |
    v
Text Splitter
    |
    v
Embeddings
    |
    v
FAISS
    |
    v
Retriever
    |
    v
Llama3
    |
    v
Answer

====================================================
First RAG System
==================================================

RAG combines:

Retrieval:
Find relevant information

Generation:
LLM creates answer


Pipeline:

Document
   |
Loader
   |
Splitter
   |
Embedding
   |
FAISS
   |
Retriever
   |
LLM
   |
Answer

Embedding model:
nomic-embed-text
Generation model:
llama3
==================================================
"""
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import FAISS

# ==========================
# 1. Load Document
# ==========================
loader = TextLoader(
    "C:/ML/LangChain_Learning/07-RAG_Basics/sample_policy.txt",
    encoding="utf-8"
)
documents = loader.load()
print("Documents loaded:")
print(len(documents))
# ==========================
# 2. Split Document
# ==========================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=50
)
chunks = splitter.split_documents(
    documents
)
print("\nChunks created:")
print(len(chunks))

# ==========================
# 3. Create Embeddings
# ==========================
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

# ==========================
# 4. Create FAISS Database
# ==========================
vector_store = FAISS.from_documents(
    chunks,
    embeddings
)

print("\nFAISS database created")

# ==========================
# 5. Retrieve Documents
# ==========================

question = "How many days do I have to report an accident?"
retrieved_docs = vector_store.similarity_search(
    question,
    k=1
)

'''k=2 means:

Return the top 2 most similar chunks.'''


print("\nRetrieved Documents")
print("===================")

for doc in retrieved_docs:
    print(doc.page_content)

# ==========================
# 6. Send Context to LLM
# ==========================


context = "\n\n".join(

    doc.page_content

    for doc in retrieved_docs

)

llm = ChatOllama(
    model="llama3:latest"
)

prompt = f"""
Answer the question using only the context below.
Context:
{context}
Question:
{question}
"""

response = llm.invoke(prompt)
print("\nFinal Answer")
print("================")
print(response.content)