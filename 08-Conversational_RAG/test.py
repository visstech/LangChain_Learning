"""
====================================================================

File:
    03_conversational_rag.py

Topic:
    Modern Conversational RAG using LCEL
    LangChain 1.2.10

Purpose:
    Build a chatbot that can answer questions from documents
    and maintain conversation context.

Concepts Covered:

    1. Document Loading
    2. Text Splitting
    3. Embeddings
    4. FAISS Vector Database
    5. Retriever
    6. RunnableParallel
    7. RunnablePassthrough
    8. ChatPromptTemplate
    9. ChatOllama
    10. StrOutputParser
    11. Conversation Memory


Architecture:

                    User Question

                          |
                          |
                          v

              +----------------------+
              | RunnableParallel     |
              +----------------------+

                  |              |

                  |              |
                  v              v

             Retriever    RunnablePassthrough

                  |              |

                  v              v

             Context       Question


                  |
                  |
                  v

          ChatPromptTemplate

                  |
                  |
                  v

             ChatOllama

                  |
                  |
                  v

          StrOutputParser

                  |
                  |
                  v

              Final Answer


====================================================================
"""


# ============================================================
# Imports
# ============================================================

from langchain_community.document_loaders import TextLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS

from langchain_ollama import (
    OllamaEmbeddings,
    ChatOllama
)

from langchain_core.prompts import ChatPromptTemplate

from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough
)

from langchain_core.output_parsers import StrOutputParser


# ============================================================
# Step 1: Load Document
# ============================================================

"""
TextLoader reads our knowledge source.

Example:

sample_policy.txt

This is our private knowledge base.
"""

loader = TextLoader(
    "sample_policy.txt",
    encoding="utf-8"
)


documents = loader.load()


print("\nDocuments Loaded:")
print(len(documents))


# ============================================================
# Step 2: Split Documents into Chunks
# ============================================================

"""
Large documents cannot be directly sent to LLM.

We split them into smaller chunks.

chunk_size:
Maximum characters per chunk

chunk_overlap:
Common text between chunks to preserve context
"""


splitter = RecursiveCharacterTextSplitter(

    chunk_size=200,

    chunk_overlap=50

)


chunks = splitter.split_documents(
    documents
)


print("\nChunks Created:")
print(len(chunks))


# ============================================================
# Step 3: Create Embeddings
# ============================================================

"""
Embedding Model:

Converts text into numerical vectors.

Example:

"accident claim"

        |
        v

[0.23,0.76,0.11...]

FAISS compares these vectors.
"""


embeddings = OllamaEmbeddings(

    model="nomic-embed-text"

)


# ============================================================
# Step 4: Create FAISS Vector Database
# ============================================================


vector_store = FAISS.from_documents(

    chunks,

    embeddings

)


print("\nFAISS Database Created")


# ============================================================
# Step 5: Create Retriever
# ============================================================


"""
Retriever converts:

User Question

into:

Relevant Document Chunks
"""


retriever = vector_store.as_retriever(

    search_kwargs={
        "k": 2
    }

)



# ============================================================
# Step 6: Load LLM
# ============================================================


llm = ChatOllama(

    model="llama3:latest"

)



# ============================================================
# Step 7: Create Prompt
# ============================================================


prompt = ChatPromptTemplate.from_template(

"""
You are an insurance assistant.

Answer the question using only the context.

Context:

{context}


Question:

{question}

"""

)



# ============================================================
# Step 8: Output Parser
# ============================================================


parser = StrOutputParser()



# ============================================================
# Step 9: Create RAG LCEL Chain
# ============================================================


"""
RunnableParallel creates:

{
    context:
        Retrieved Documents,

    question:
        Original User Question
}


Then:

Dictionary
      |
      v
Prompt
      |
      v
LLM
      |
      v
Parser
"""


rag_chain = (

    RunnableParallel(

        context=retriever,

        question=RunnablePassthrough()

    )

    |

    prompt

    |

    llm

    |

    parser

)



# ============================================================
# Step 10: Ask Question
# ============================================================


question = (

    "How many days does a policyholder have "
    "to report an accident?"

)



response = rag_chain.invoke(
    question
)



print("\n============================")
print("Question")
print("============================")

print(question)



print("\n============================")
print("Answer")
print("============================")

print(response)