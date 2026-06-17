# 🤖 Multi-Agent Math Assistant

A multi-agent chatbot built with **Python**, **Streamlit**, **OpenAI**, and **Ollama**, capable of solving mathematical operations, understanding natural language, maintaining contextual memory, and handling conversational requests through specialized agents.

---

## 🚀 Features

### 🧠 Multi-Agent Architecture

The application is composed of specialized agents:

* **Intent Agent**

  * Interprets user intent.
  * Detects mathematical operations.
  * Handles contextual references.

* **Mathematical Agent**

  * Executes validated mathematical operations.
  * Uses deterministic tools instead of LLM calculations.

* **Writer Agent**

  * Generates friendly responses.
  * Supports multiple languages.

* **Conversation Agent**

  * Handles natural conversation.
  * Provides explanations and guidance when mathematical operations are not detected.

---

### 🧮 Mathematical Capabilities

Supports:

* Addition
* Subtraction
* Multiplication
* Division
* Parenthesized expressions
* Power operations
* Square roots
* Trigonometric functions
* Logarithmic functions
* Mathematical constants (`π`, `e`)
* Context-aware follow-up calculations

Examples:

```text
5 + 4

(5 + 4) * 3

sqrt(81)

raiz quadrada de 144

2 elevado a 10

sin(pi / 2)
```

### 💬 Contextual Memory

The assistant remembers previous results.

Example:

```text
User:
5 + 5

Assistant:
10

User:
Now multiply that by 3

Assistant:
30
```

### 🌎 Multi-Language Support

Supported languages:

* Portuguese 🇧🇷
* English 🇺🇸
* Spanish 🇪🇸

---

## 🛡️ Safety Features

* Division by zero protection
* Expression validation
* Safe AST-based evaluation
* Invalid mathematical input handling
* Context validation
* Prompt injection filtering

---

## 🏗️ Architecture

```text
User
  │
  ▼
Intent Agent
  │
  ▼
Expression Tool
  │
  ▼
Mathematical Agent
  │
  ▼
Writer Agent
  │
  ▼
Session Memory
```

---

## 🧰 Technologies

* Python 3.10+
* Streamlit
* OpenAI API
* Ollama
* AST Expression Evaluation
* Pytest
* Dotenv

---

## 📂 Project Structure

```text
multi-agent-math-assistant/

├── agents/
│   ├── conversation_agent.py
│   ├── intent_agent.py
│   ├── mathematical_agent.py
│   └── writer_agent.py
│
├── clients/
│   ├── openai_client.py
│   └── ollama_client.py
│
├── memory/
│   └── session_memory.py
│
├── tools/
│   ├── expression_tools.py
│   └── text_tools.py
│
├── utils/
│   ├── language_detector.py
│   ├── math_parser.py
│   ├── math_validator.py
│   └── parser_exceptions.py
│
├── tests/
│
├── app.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Raniel-Git/multi-agent-math-assistant.git
```

Enter the project:

```bash
cd multi-agent-math-assistant
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate:

Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
LLM_PROVIDER=openai
```

Run:

```bash
streamlit run app.py
```

---

## 📈 Future Improvements

* Image support
* Voice support
* Advanced symbolic mathematics
* Graph plotting
* Persistent memory
* RAG integration
* Multi-tool orchestration

---

## 👨‍💻 Developer

**Raniel Andrade**

LinkedIn:
https://www.linkedin.com/in/raniel-andrade-25a9ba2bb

GitHub:
https://github.com/Raniel-Git
