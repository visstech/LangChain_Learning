"""
===========================================================
PDFLoader - LangChain Document Loader
===========================================================

What is PDFLoader?
------------------

PDFLoader is a LangChain component used to extract text
from PDF files and convert each page into a Document object.


Why do we need PDFLoader?
-------------------------

Most enterprise data exists in PDFs:

- Insurance documents
- Medical reports
- Research papers
- Manuals
- Contracts


PDFLoader converts:

PDF File
   |
   v
Document Objects


Document contains:

1. page_content
   Extracted text

2. metadata
   Source information and page number


Important:

One PDF page = One LangChain Document


Example:

10 page PDF

becomes:

[
 Document(page=1),
 Document(page=2),
 ...
 Document(page=10)
]


Real-world AI Usage:

PDF
 |
 v
PDFLoader
 |
 v
Text Splitter
 |
 v
Embeddings
 |
 v
Vector Database
 |
 v
RAG Question Answering


===========================================================
"""


from langchain_community.document_loaders import PyPDFLoader


loader = PyPDFLoader(
    "C:/ML/LangChain_Learning/03-Document_Loaders/master-your-mind-design-your-destiny.pdf"
    
)


documents = loader.load()


print("Number of documents:", len(documents))


print("\nFirst page content:")
print(documents[0].page_content)


print("\nMetadata:")
print(documents[5].metadata)