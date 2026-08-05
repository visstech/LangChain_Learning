# Chapter 9 - Tools & AI Agents

## Overview

This chapter explains how to build AI Agents using LangChain Tools and local LLMs with Ollama.

An AI Agent combines:

- LLM reasoning
- External tools
- Decision making
- Action execution

---

# Architecture
User
|
v
LLM (Qwen2.5)
|
v
Tool Selection
|
v
Execute Tool
|
v
Tool Result
|
v
LLM Final Response


---

# Lessons

## 01_first_tool.py

### Concepts

- LangChain Tool
- @tool decorator
- Tool description
- Manual tool execution


Example:

```python
multiply_numbers.invoke(
{
"a":25,
"b":10
}
)

Output:

250
02_multiple_tools.py

Created multiple tools:

add_numbers
multiply_numbers
divide_numbers

The Agent receives a toolbox of available actions.

03_tool_calling.py

Connected Qwen2.5 with tools.

Used:

llm.bind_tools(tools)

The LLM generates structured tool calls.

Example:

{
"name":"multiply_numbers",
"args":{
"a":25,
"b":10
}
}
04_first_agent.py

Built the complete Agent loop.

Flow:

User asks question
LLM decides tool
Tool executes
Result returned to LLM
Final answer generated

Example:

Question:

What is 25 multiplied by 10?

Agent:

Select multiply_numbers

Execute:

25 * 10

Result:

250

Final:

The result of multiplying 25 by 10 is 250.
Technologies Used
Python
LangChain
LangChain Core
LangChain Ollama
Ollama
Qwen2.5