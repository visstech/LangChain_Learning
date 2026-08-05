"""
===========================================================
Basic Embeddings using Ollama
===========================================================

What are embeddings?

Embeddings convert text into numerical vectors.

Text
 |
 v
Embedding Model
 |
 v
Vector


Used for:

- Semantic Search
- RAG
- Similarity Matching
- Recommendation Systems


===========================================================
"""


from langchain_ollama import OllamaEmbeddings


embeddings = OllamaEmbeddings(

    model="nomic-embed-text"

)


text = "LangChain helps build AI applications"


vector = embeddings.embed_query(text)


print(type(vector))

print("Vector length:")
print(len(vector))


print("\nFirst 10 values:")
print(vector[:10])