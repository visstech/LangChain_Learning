"""
tools.py
--------
The tool the agent can call to search the uploaded document.

Same pattern as the bank agent project: the tool doesn't take a
"which document" parameter the agent could fill in wrong — it always
searches whatever CURRENT_VECTORSTORE currently is, which app.py
sets right after a file is uploaded and processed.
"""

from langchain_core.tools import tool

CURRENT_VECTORSTORE = None


@tool
def search_document(query: str) -> str:
    """Search the uploaded document for content relevant to the query.
    Use this whenever the user asks something that could be answered
    or explained using the material they uploaded.

    Args:
        query: what to search for in the document.
    """
    if CURRENT_VECTORSTORE is None:
        return "No document has been uploaded yet."

    results = CURRENT_VECTORSTORE.similarity_search(query, k=4)

    if not results:
        return "No relevant content found in the document for that query."

    # Combine the top matching chunks into one block of context,
    # noting which page each came from where available.
    chunks = []
    for doc in results:
        page = doc.metadata.get("page")
        label = f"(page {page + 1})" if page is not None else ""
        chunks.append(f"{label} {doc.page_content}")

    return "\n\n---\n\n".join(chunks)
