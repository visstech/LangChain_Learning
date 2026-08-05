"""
===========================================================
Document Splitting with RecursiveCharacterTextSplitter
===========================================================

Purpose:

Split LangChain Document objects while preserving
metadata.

Important:

split_text()
    works with string

split_documents()
    works with Document objects


RAG Pipeline:

Document
    |
    v
Text Splitter
    |
    v
Document Chunks
    |
    v
Embeddings


===========================================================
"""


from langchain_core.documents import Document

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)


# Create Document object

document = Document(

    page_content="""
    LangChain is a framework for building applications
    powered by Large Language Models.

    It provides components for:
    
    - Prompt templates
    - Document loaders
    - Text splitters
    - Embeddings
    - Vector databases
    - Agents
    """,

    metadata={
        "source": "langchain_notes.txt",
        "page": 1
    }

)


print("Original Document")
print("-----------------")

print(document)


# Create splitter

splitter = RecursiveCharacterTextSplitter(

    chunk_size=100,

    chunk_overlap=20

)


# Split Document

chunks = splitter.split_documents(
    [document]
)


print("\nNumber of chunks:")
print(len(chunks))


# Display chunks

for index, chunk in enumerate(chunks, start=1):

    print("\n====================")
    print("Chunk:", index)

    print(chunk.page_content)

    print("\nMetadata:")
    print(chunk.metadata)