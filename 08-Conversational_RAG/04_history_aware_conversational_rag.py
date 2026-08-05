"""
================================================================

Topic:
    History Aware Conversational RAG

LangChain Version:
    1.2.10

Purpose:

    Build a chatbot that:

    1. Understands previous conversation
    2. Rewrites follow-up questions
    3. Searches FAISS using standalone questions
    4. Generates answers using retrieved context


Architecture:


                 User Question

                       |
                       v

              Chat History Memory

                       |
                       v

             Question Rewriter LLM

                       |
                       v

            Standalone Question

                       |
                       v

                 FAISS Retriever

                       |
                       v

             Relevant Documents

                       |
                       v

              Answer Generation LLM

                       |
                       v

                  Final Answer

                       |
                       v

              Update Chat Memory


================================================================
"""


# ============================================================
# Imports
# ============================================================


from langchain_community.document_loaders import TextLoader


from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)


from langchain_community.vectorstores import FAISS


from langchain_ollama import (
    OllamaEmbeddings,
    ChatOllama
)


from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)


from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda
)


from langchain_core.output_parsers import (
    StrOutputParser
)


from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

# ============================================================
# Load Document
# ============================================================


loader = TextLoader(
    "C:/ML/LangChain_Learning/08-Conversational_RAG/sample_policy.txt",
    encoding="utf-8"
)


documents = loader.load()


print("\nDocuments Loaded:")
print(len(documents))

# ============================================================
# Text Splitting
# ============================================================


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
# Embeddings
# ============================================================


embeddings = OllamaEmbeddings(

    model="nomic-embed-text"

)



# ============================================================
# FAISS Vector Database
# ============================================================


vector_store = FAISS.from_documents(

    chunks,

    embeddings

)


print("\nFAISS Database Created")

# ============================================================
# Retriever
# ============================================================


retriever = vector_store.as_retriever(

    search_kwargs={
        "k": 2
    }

)

# ============================================================
# LLM
# ============================================================


llm = ChatOllama(

    model="llama3:latest"

)

# ============================================================
# Question Rewriter Prompt
# ============================================================
"""
====================================================

Question Rewriter

Purpose:

Convert follow-up questions into standalone questions.

Example:

History:

User:
What is motor insurance?

AI:
Motor insurance protects vehicles.


Question:

Does it cover accidents?


Rewritten:

Does motor insurance cover accidents?


The retriever can now search correctly.

====================================================
"""

contextualize_q_prompt = ChatPromptTemplate.from_messages(

    [

        (
            "system",

            """
Given a chat history and the latest user question,
rewrite the question so it can be understood
without the chat history.

Do NOT answer the question.
Only rewrite it.
"""
        ),


        MessagesPlaceholder(
            variable_name="chat_history"
        ),


        (
            "human",
            "{question}"
        )

    ]

)

# ============================================================
# Question Rewriter Chain
# ============================================================


question_rewriter = (

    contextualize_q_prompt

    |

    llm

    |

    StrOutputParser()

)

# ============================================================
# Format Documents
# ============================================================


def format_docs(docs):

    return "\n\n".join(

        doc.page_content

        for doc in docs

    )

# ============================================================
# History Aware Retriever
# ============================================================


history_aware_retriever = (

    question_rewriter

    |

    retriever

    |

    RunnableLambda(format_docs)

)

# ============================================================
# Answer Generation Prompt
# ============================================================


answer_prompt = ChatPromptTemplate.from_messages(

    [

        (
            "system",

            """
You are a helpful insurance assistant.

Answer the user's question using only the
provided context.

Rules:

1. Do not mention Document objects.
2. Do not mention metadata.
3. If information is not available in the context,
ONLY reply exactly:

"I could not find this information in the policy document."

Do not change this sentence.

Context:

{context}

"""
        ),


        MessagesPlaceholder(
            variable_name="chat_history"
        ),


        (
            "human",
            "{question}"
        )

    ]

)

# ============================================================
# Answer Generation Chain
# ============================================================


answer_chain = (

    answer_prompt

    |

    llm

    |

    StrOutputParser()

)

# ============================================================
# Complete Conversational RAG Chain
# ============================================================


rag_chain = (

    RunnableParallel(

        context=history_aware_retriever,

        question=RunnablePassthrough(),

        chat_history=lambda x: x["chat_history"]

    )

    |

    answer_chain

)


# ============================================================
# Conversation Memory
# ============================================================


chat_history = []


# ============================================================
# Interactive Chat
# ============================================================


while True:


    question = input(
        "\nAsk a Question (type 'exit' to quit): "
    )


    if question.lower() == "exit":

        print("\nGoodbye!")

        break



    response = rag_chain.invoke(

        {

            "question": question,

            "chat_history": chat_history

        }

    )



    print("\n============================")
    print("Answer")
    print("============================")

    print(response)



    # Store conversation

    chat_history.append(

        HumanMessage(
            content=question
        )

    )


    chat_history.append(

        AIMessage(
            content=response
        )

    )

"""
====================================================

Three Types of Memory in Conversational RAG

1. Knowledge Memory

Stored in:

FAISS Vector Database

Purpose:

Stores company documents,
PDFs,
Policies,
Manuals.


2. Conversation Memory

Stored in:

chat_history

Purpose:

Remembers previous user
and AI messages.


3. Reasoning Memory

Implemented by:

Question Rewriter

Purpose:

Converts follow-up questions into
standalone questions before retrieval.


Together these produce an intelligent
conversational assistant.

====================================================
"""
"""
====================================================

History Aware Conversational RAG

Complete Flow:


1. User asks question

2. Question Rewriter uses chat history
   to create standalone question

3. Retriever searches FAISS

4. Retrieved documents become context

5. Answer LLM receives:

       Context
       +
       Chat History
       +
       Question

6. Response is stored in memory


Components:

FAISS:
Knowledge Memory

chat_history:
Conversation Memory

Question Rewriter:
Reasoning Layer


====================================================
"""