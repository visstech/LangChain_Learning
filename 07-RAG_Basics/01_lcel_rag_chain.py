"""
====================================================
LCEL RAG Chain

Flow:

Question
   |
   v
Retriever
   |
   v
Relevant Documents
   |
   v
Prompt Template
   |
   v
LLM
   |
   v
Output Parser
   |
   v
Answer


====================================================
"""

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# =====================================
# 1. Load Document
# =====================================
loader = TextLoader(
    "C:/ML/LangChain_Learning/07-RAG_Basics/sample_policy.txt",
    encoding="utf-8"
)
documents = loader.load()

# =====================================
# 2. Split Documents
# =====================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=50
)

chunks = splitter.split_documents(
    documents
)

# =====================================
# 3. Create Embeddings
# =====================================
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

# =====================================
# 4. Create Vector Store
# =====================================
vector_store = FAISS.from_documents(
    chunks,
    embeddings
)

# Convert Vector Store into Retriever
retriever = vector_store.as_retriever(
    search_kwargs={
        "k":2
    }

)

# =====================================
# 5. Prompt
# =====================================

prompt = ChatPromptTemplate.from_template(
"""
Answer the question using only the context.

Context:

{context}


Question:

{question}

"""
)

# =====================================
# 6. LLM
# =====================================

llm = ChatOllama(
    model="llama3:latest"
)

# =====================================
# 7. LCEL RAG Chain
# =====================================

rag_chain = (

    {
        "context": retriever,
        "question": RunnablePassthrough()

    }

    | prompt

    | llm

    | StrOutputParser()

)
# =====================================
# 8. Ask Question
# =====================================
response = rag_chain.invoke(
    "How many days do I have to report an accident?"
)
print(response)