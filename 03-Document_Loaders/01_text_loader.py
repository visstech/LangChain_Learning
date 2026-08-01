"""
===========================================================
LangChain Document Loader
===========================================================

What is Document Loader?

Document Loader is used to load external data sources
into LangChain Document objects.

Sources:

- Text files
- PDF files
- Word files
- Websites
- Databases


Why do we need Document Loaders?

LLMs do not automatically know our private documents.

Example:

Company Policy PDF
        |
        v
Document Loader
        |
        v
LangChain Document
        |
        v
RAG Application


Document contains:

1. page_content
   Actual text

2. metadata
   Information about the source


===========================================================
"""


from langchain_community.document_loaders import TextLoader
import os

print('path is:',os.getcwd())

loader = TextLoader(
    "C:/ML/LangChain_Learning/03-Document_Loaders/sample.txt",
    encoding="utf-8"
)

documents = loader.load()

print(type(documents))

print(type(documents[0]))

print("-------------------")

print("CONTENT:")
print(documents[0].page_content)

print("-------------------")

print("METADATA:")
print(documents[0].metadata)