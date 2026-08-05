"""
===========================================================
Semantic Similarity Using Embeddings
===========================================================

Purpose:

Understand how embeddings compare meaning.

Process:

Sentence
   |
   v
Embedding Model
   |
   v
Vector
   |
   v
Cosine Similarity
   |
   v
Similarity Score


Similarity score:

Closer to 1
    |
    v
Very similar meaning


Closer to 0
    |
    v
Different meaning

Semantic Similarity:

Semantic similarity measures how close two texts are in meaning.

Steps:

1. Convert text into embeddings.
2. Compare vectors.
3. Higher similarity score means closer meaning.

Used in:

- RAG
- Search engines
- Recommendation systems
- Duplicate detection
- Document matching


Embedding model:
Text -> Vector

Vector Database:
Stores vectors and performs similarity search.

===========================================================

FAISS Vector Database
====================================================

Purpose:
Store and search embedding vectors efficiently.

Flow:

Documents
    |
    v
Embedding Model
    |
    v
Vectors
    |
    v
FAISS


During Search:

User Query
    |
    v
Query Embedding
    |
    v
Compare with stored vectors    |
    v
Return most similar documents
Important:
FAISS does NOT understand text.
FAISS understands vectors.
Similarity is based on mathematical comparison.
====================================================
"""


from langchain_ollama import OllamaEmbeddings

from sklearn.metrics.pairwise import cosine_similarity



# Create embedding model

embeddings = OllamaEmbeddings(

    model="nomic-embed-text"

)



sentence1 = (
    "LangChain helps developers build AI applications"
)


sentence2 = (
    "LangChain is used to create LLM based applications"
)


sentence3 = (
    "I like cooking delicious food"
)



# Create embeddings

vector1 = embeddings.embed_query(sentence1)

vector2 = embeddings.embed_query(sentence2)

vector3 = embeddings.embed_query(sentence3)



# Calculate similarity

similarity_1_2 = cosine_similarity(
    [vector1],
    [vector2]
)


similarity_1_3 = cosine_similarity(
    [vector1],
    [vector3]
)



print("Sentence 1:")
print(sentence1)


print("\nSentence 2:")
print(sentence2)


print("\nSimilarity between Sentence 1 and Sentence 2:")

print(similarity_1_2[0][0])



print("\nSentence 3:")
print(sentence3)


print("\nSimilarity between Sentence 1 and Sentence 3:")

print(similarity_1_3[0][0])