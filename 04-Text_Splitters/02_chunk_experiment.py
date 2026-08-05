"""
===========================================================
Chunk Size and Chunk Overlap Experiment
===========================================================

Purpose:

Understand how:

1. chunk_size
2. chunk_overlap

affect the number and content of chunks.

Formula:
Step size = chunk_size - chunk_overlap
Example:

chunk_size = 100
chunk_overlap = 20

Each new chunk moves:

100 - 20 = 80 characters

===========================================================
Important Observations:

1. Smaller chunk_size:
   - Creates more chunks
   - Improves retrieval precision
   - Increases embeddings and storage

2. Larger chunk_size:
   - Creates fewer chunks
   - Keeps more context
   - May include unrelated information

3. Larger chunk_overlap:
   - Preserves context
   - Creates more repeated content
   - Increases storage requirement


Production RAG usually balances:

chunk_size + chunk_overlap + document type

"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

text = """
Artificial Intelligence is transforming many industries.
Machine Learning helps computers learn from data.
Deep Learning uses neural networks to solve complex problems.
Natural Language Processing helps computers understand human language.
LangChain helps developers build applications using Large Language Models.
Retrieval Augmented Generation combines documents with LLMs.
"""

def text_spliter(chunk_size,chunk_overlap):

    print("======================================\n")
    print("chunk size:",chunk_size)
    print("chunk overlap size:",chunk_overlap)
    print("======================================")
    splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )

    chunk = splitter.split_text(text)
    print("Number of chunk is:",len(chunk))
    for index,chunk in enumerate(chunk,start=1):
        print('\nchunk index:',index)
        print(chunk)


# Experiment 1

text_spliter(
    chunk_size=100,
    chunk_overlap=0
)

# Experiment 2
text_spliter(
    chunk_size=50,
    chunk_overlap=10
)

# Experiment 3
text_spliter(
    chunk_size=200,
    chunk_overlap=50
)
