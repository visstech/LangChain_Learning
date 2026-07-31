# LangChain Learning Environment Setup Guide (Windows)

## 1. Create Project Folder

First create a dedicated folder for LangChain learning.

Example:

```powershell
C:
cd \ML

mkdir LangChain_Learning

cd LangChain_Learning
```

Project location:

```
C:\ML\LangChain_Learning
```

This folder will contain all LangChain examples and projects.

---

# 2. Create Python Virtual Environment

A virtual environment keeps LangChain packages isolated from other Python projects.

Inside:

```
C:\ML\LangChain_Learning
```

Run:

```powershell
python -m venv langchain_env
```

This creates:

```
LangChain_Learning
│
├── langchain_env
│   ├── Scripts
│   ├── Lib
│   └── Include
│
└── Project files
```

---

# 3. Activate Virtual Environment

Activate the environment:

```powershell
langchain_env\Scripts\activate
```

After activation, the terminal should show:

```
(langchain_env) PS C:\ML\LangChain_Learning>
```

The `(langchain_env)` confirms that the virtual environment is active.

---

# 4. Verify Python Environment

Check Python version:

```powershell
python --version
```

Example:

```
Python 3.12.4
```

Check which Python is running:

```powershell
Get-Command python
```

Expected:

```
Source:
C:\ML\LangChain_Learning\langchain_env\Scripts\python.exe
```

This confirms that the virtual environment Python is being used.

---

# 5. Install LangChain

Install LangChain:

```powershell
pip install langchain
```

LangChain provides the framework to build LLM applications.

---

# 6. Install Ollama Integration

Since we use local LLM models with Ollama:

```powershell
pip install langchain-ollama
```

This provides:

```python
from langchain_ollama import ChatOllama
```

connection to local models.

---

# 7. Install LangGraph

For future AI Agent workflows:

```powershell
pip install langgraph
```

LangGraph is used for:

* Stateful workflows
* AI agents
* Multi-step reasoning
* Multi-agent systems

---

# 8. Verify Installed Packages

Run:

```powershell
pip list
```

Expected packages:

```
langchain
langchain-ollama
langgraph
langsmith
pydantic
ollama
```

---

# 9. Install Cursor IDE

Cursor can be used to write and run LangChain code.

Steps:

1. Open Cursor.
2. Open folder:

```
C:\ML\LangChain_Learning
```

3. Open Terminal inside Cursor.

Activate environment:

```powershell
langchain_env\Scripts\activate
```

Terminal should show:

```
(langchain_env)
```

Now Cursor uses the LangChain environment.

---

# 10. Install Ollama

Install Ollama and verify:

```powershell
ollama --version
```

Check available models:

```powershell
ollama list
```

Example models:

```
llama3:latest
llama2:latest
phi3:latest
deepseek-r1:latest
gemma3:27b
```

---

# 11. Test ChatOllama Connection

Create:

```
test_ollama.py
```

Code:

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3:latest"
)

response = llm.invoke(
    "Explain Artificial Intelligence"
)

print(response.content)
```

Run:

```powershell
python test_ollama.py
```

If the AI response appears, the environment is working.

---

# 12. SSL Certificate Error Problem

During installation, we received:

```
SSLCertVerificationError:
certificate verify failed:
unable to get local issuer certificate
```

Problem:

Python could not verify the SSL certificate while connecting to PyPI.

Because of this:

```
pip install langchain
```

failed.

---

# 13. Check SSL Certificate Configuration

Run:

```powershell
python -c "import ssl; print(ssl.get_default_verify_paths())"
```

Output showed:

```
openssl_cafile:
C:\Program Files\Common Files\SSL\cert.pem
```

This confirmed Python SSL certificate configuration issue.

---

# 14. Install Certifi Certificate Package

Certifi provides trusted CA certificates.

Install:

```powershell
pip install certifi
```

Find certificate location:

```powershell
python -c "import certifi; print(certifi.where())"
```

Example:

```
C:\Users\<username>\AppData\Local\Programs\Python\Python312\Lib\site-packages\certifi\cacert.pem
```

---

# 15. Set SSL_CERT_FILE Environment Variable

Set Python to use certifi certificates:

PowerShell:

```powershell
setx SSL_CERT_FILE "C:\Users\<username>\AppData\Local\Programs\Python\Python312\Lib\site-packages\certifi\cacert.pem"
```

Example:

```powershell
setx SSL_CERT_FILE "C:\Users\visse\AppData\Local\Programs\Python\Python312\Lib\site-packages\certifi\cacert.pem"
```

After setting:

1. Close terminal.
2. Open a new Cursor terminal.
3. Activate environment again.

```powershell
langchain_env\Scripts\activate
```

Verify:

```powershell
echo $env:SSL_CERT_FILE
```

Expected:

```
C:\Users\visse\AppData\Local\Programs\Python\Python312\Lib\site-packages\certifi\cacert.pem
```

---

# 16. Final Environment Verification

Run:

```powershell
python --version
```

Example:

```
Python 3.12.4
```

Check environment:

```powershell
Get-Command python
```

Expected:

```
C:\ML\LangChain_Learning\langchain_env\Scripts\python.exe
```

Check packages:

```powershell
pip list
```

Check Ollama:

```powershell
ollama list
```

Everything is ready.

---

# Final Project Structure

```
C:\ML\LangChain_Learning

│
├── langchain_env
│
├── 01-Basics
│   ├── 01_chatollama.py
│   ├── 02_json_parser.py
│   ├── 03_pydantic_parser.py
│   ├── 04_chat_prompt.py
│   ├── 05_runnable_lambda.py
│
├── README.md
│
└── Notes
    └── LangChain_Learning_Notes.md
```

---

# Current Working Stack

Python:

```
Python 3.12.4
```

Environment:

```
langchain_env
```

LLM:

```
Ollama + Llama3
```

Frameworks:

```
LangChain
LangGraph
LangChain-Ollama
```

IDE:

```
Cursor
```

