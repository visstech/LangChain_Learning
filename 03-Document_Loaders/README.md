# LangChain Document Loaders

## What is a Document Loader?

Document Loader is a LangChain component used to load external data sources into LangChain Document objects.

Supported sources:

- Text files
- PDF files
- Word documents
- CSV files
- Websites
- Databases


## LangChain Document Structure

A Document contains:

### page_content

Actual text content.

Example:

"LangChain helps developers build AI applications"


### metadata

Information about the source.

Example:

{
    "source": "sample.txt"
}


## TextLoader Example

Flow:

Text File
    |
    v
TextLoader
    |
    v
Document Object
    |
    v
RAG Pipeline


## Important Notes

loader.load() returns:

list[Document]

not a string.

Example:

[
 Document(
    page_content="...",
    metadata={}
 )
]

