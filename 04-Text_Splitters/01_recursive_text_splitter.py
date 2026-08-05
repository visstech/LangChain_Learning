"""
===========================================================
RecursiveCharacterTextSplitter
===========================================================

What is RecursiveCharacterTextSplitter?

It splits large documents into smaller chunks while
trying to preserve natural boundaries such as paragraphs,
sentences, and words.

Why do we use it?

- LLMs have context limits.
- Large documents cannot be processed at once.
- Splitting improves retrieval performance.
- Chunk overlap preserves context.

Important Parameters:

chunk_size:
    Maximum size of each chunk.

chunk_overlap:
    Number of characters shared between adjacent chunks.

===========================================================
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

text = """
LangChain is an open-source framework for building applications powered by Large Language Models.
It provides components for prompts, document loading, text splitting, embeddings, vector stores,
retrievers, agents, and much more. RecursiveCharacterTextSplitter is one of the most commonly
used text splitters because it preserves context while creating manageable chunks.
"""

splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,
    chunk_overlap=10
)

chunks = splitter.split_text(text)

print(f"Number of chunks: {len(chunks)}")

for i, chunk in enumerate(chunks, start=1):
    print(f"\n----- Chunk {i} -----")
    print(chunk)