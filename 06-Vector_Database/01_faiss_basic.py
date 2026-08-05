"""
====================================================
FAISS Vector Database Basic Example
====================================================

Flow:

Documents
    |
    v
Embeddings
    |
    v
FAISS Vector Store
    |
    v
Similarity Search


====================================================
"""


from langchain_core.documents import Document

from langchain_community.vectorstores import FAISS

from langchain_ollama import OllamaEmbeddings



# Create embedding model

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)



# Create documents

documents = [

    Document(
        page_content="LangChain helps developers build AI applications",
        metadata={"source":"langchain"}
    ),

    Document(
        page_content="Python is a popular programming language",
        metadata={"source":"python"}
    ),

    Document(
        page_content="RAG combines retrieval with large language models",
        metadata={"source":"rag"}
    )

]



# Create FAISS vector database

vector_store = FAISS.from_documents(
    documents,
    embeddings
)



# Search

query = "How can I build LLM applications?"


results = vector_store.similarity_search(
    query,
    k=2
)



print("Search Results")
print("================")


for doc in results:

    print("\nContent:")
    print(doc.page_content)

    print("Metadata:")
    print(doc.metadata)