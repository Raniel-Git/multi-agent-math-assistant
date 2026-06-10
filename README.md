# Multi-Agent Chatbot

## Overview

This project is a simple multi-agent chatbot application built with Streamlit.

The purpose of the project is to demonstrate the fundamental concepts used in modern AI agent systems, including:

* Agent orchestration
* Tool usage
* Memory management
* Context awareness
* Prompt engineering
* Guardrails

The chatbot performs mathematical operations through specialized agents and dedicated tools while maintaining conversational context across multiple interactions.

---

## Architecture

The application follows a modular architecture where each component has a clear responsibility.

```text
User
 │
 ▼
Streamlit Interface
 │
 ▼
Math Parser
 │
 ▼
Orchestrator
 ├─────────────► Mathematical Agent
 │                     │
 │                     ▼
 │                 Math Tools
 │
 ▼
Writer Agent
 │
 ▼
Memory
 │
 ▼
Response
```

---

## Project Structure

```text
multi-agent-chatbot/
├── app.py
├── agents/
│   ├── mathematical_agent.py
│   └── writer_agent.py
├── tools/
│   └── math_tools.py
├── orchestration/
│   └── orchestrator.py
├── memory/
│   └── session_memory.py
├── prompts/
│   ├── mathematical_prompt.py
│   └── writer_prompt.py
├── utils/
│   ├── language_detector.py
│   └── math_parser.py
├── tests/
└── requirements.txt
```

---

## Agent Responsibilities

### Mathematical Agent

Responsible for:

* Executing calculations
* Using tools as the source of truth
* Avoiding direct mathematical reasoning
* Returning structured results

Supported operations:

* Addition
* Subtraction
* Multiplication
* Division

---

### Writer Agent

Responsible for:

* Generating user-friendly responses
* Formatting outputs
* Adapting responses to the user's language
* Improving readability

---

## Tool Architecture

The project uses dedicated mathematical tools.

Available tools:

* add()
* subtract()
* multiply()
* divide()

All calculations are performed through tools instead of direct agent reasoning.

This ensures deterministic and reliable mathematical results.

---

## Memory Implementation

Conversation memory is implemented through SessionMemory.

Responsibilities:

* Store user messages
* Store assistant messages
* Store the latest mathematical result
* Provide context for follow-up requests

Example:

User:

```text
5 + 4
```

Assistant:

```text
9
```

User:

```text
subtract 2
```

Assistant:

```text
7
```

The second operation uses the previous result stored in memory.

---

## Context Awareness

The chatbot supports follow-up requests.

Examples:

```text
5 + 4
subtract 2
multiply by 3
divide by 7
```

The system automatically uses previous results when required.

---

## Language Detection

The application detects the user's language.

Supported languages:

* English
* Portuguese

Examples:

English:

```text
subtract 2
```

Response:

```text
The result is 7.
```

Portuguese:

```text
subtrair 2
```

Response:

```text
O resultado é 7.
```

---

## Guardrails

Basic guardrails were implemented.

Examples:

Division by zero:

```text
10 / 0
```

Response:

```text
Division by zero is not allowed.
```

Unsupported requests:

```text
Who is Neymar?
```

Response:

```text
No supported mathematical operation was found.
```

---

## Testing

The project includes automated tests covering:

* Mathematical tools
* Mathematical agent
* Writer agent
* Memory
* Parser
* Orchestrator
* Language detector
* Prompts

Coverage results:

* Business modules: 98%
* All tests passing

---

## Framework Choice

### Streamlit

Chosen because:

* Fast development
* Simple user interface
* Easy local execution
* Excellent for prototypes and demonstrations

---

## How to Run

Activate the virtual environment:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

---

## Learning Objectives

This project was created to provide practical experience with:

* AI agents
* Tool calling
* Agent collaboration
* Memory
* Context management
* Prompt engineering
* Guardrails
* Software architecture
* Automated testing

These concepts serve as the foundation for future AI projects and more advanced agent-based systems.
