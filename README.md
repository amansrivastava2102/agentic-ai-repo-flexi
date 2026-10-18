# 🤖 Agentic AI Task Executor

A beginner-friendly Python project that reads a user's instruction, selects the appropriate task using a **rule-based router**, executes it, and displays the result.

Built with **Python, Google Gemini, and Open-Meteo** — without LangChain, CrewAI, or other agent frameworks.

## ✨ Features

| Feature | Description | Technology |
|---|---|---|
| 📝 Text Summarization | Summarizes text into 1–3 sentences | Gemini |
| 🌐 Hindi Translation | Translates text into Hindi | Gemini |
| 💬 Sentiment Analysis | Classifies text as Positive, Negative, or Neutral | Gemini |
| 🌤️ Weather Information | Retrieves current weather for a city | Open-Meteo API |
| 🧠 General Q&A | Answers general knowledge questions | Gemini |

### Why this project?

- **Simple architecture:** Easy to understand and extend.
- **Rule-based routing:** Uses regular expressions to identify the requested task.
- **Secure API key handling:** Loads credentials from environment variables.
- **Error handling:** Handles missing input, invalid cities, API errors, and unavailable services.
- **No agent frameworks:** Uses plain Python and lightweight libraries.
- **Free weather API:** Uses Open-Meteo without requiring an API key.

## 🏗️ Project Structure

```text
agentic-task-executor/
│
├── .env                 # API key (never commit)
├── .env.example         # Environment variable template
├── .gitignore           # Excludes secrets and virtual environments
├── requirements.txt     # Project dependencies
├── README.md            # Project documentation
├── main.py              # Application entry point
│
└── agent/
    ├── __init__.py      # Python package initializer
    ├── llm.py           # Gemini API integration
    ├── decision.py      # Rule-based task router
    ├── tasks.py         # Task execution and validation
    ├── tools.py         # Open-Meteo weather integration
    └── executor.py      # Interactive execution loop
```

## 🔄 Architecture & Workflow

```text
            ┌─────────────────┐
            │   User Input    │
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │  Task Decision  │
            │  decision.py    │
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │  Task Execution │
            │    tasks.py     │
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │ Gemini or Tool  │
            │ llm.py/tools.py │
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │ Result Processing│
            │    tasks.py     │
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │    Response     │
            │  executor.py    │
            └─────────────────┘
```

### 🧩 How It Works

1. The user enters a natural-language instruction.
2. The rule-based router in `decision.py` analyzes the input using regular expressions.
3. The router selects the appropriate task.
4. The task is executed through Gemini or the Open-Meteo API.
5. The application validates and processes the result.
6. The response is displayed in the terminal.

> **Important:** This project uses a rule-based router, not autonomous LLM tool calling. Gemini performs language tasks only after the router selects the task.

## 🛠️ Technologies Used

- **Python 3.11 or 3.12** — Core programming language
- **Google Gemini API** — Summarization, translation, sentiment analysis, and general Q&A
- **Open-Meteo API** — Weather information and geocoding
- **google-genai** — Official Google Gen AI Python SDK
- **python-dotenv** — Environment variable management
- **requests** — HTTP requests
- **Cursor IDE** — Development environment
- **Git & GitHub** — Version control and source code hosting

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.11 or 3.12
- Git
- A Google Gemini API key
- An internet connection

### Step 1: Clone the repository

```bash
git clone https://github.com/amansrivastava2102/agentic-ai-repo-flexi.git
cd agentic-ai-repo-flexi
```

If you already have the project on your computer, open a terminal in the project folder instead.

### Step 2: Create a virtual environment

```powershell
python -m venv .venv
```

### Step 3: Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the environment again.

### Step 4: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 5: Configure the API key

Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

Create or edit the `.env` file in the project root:

```env
GOOGLE_API_KEY=your_real_api_key
```

Do not add quotes or spaces around the equals sign.

Optional: configure the Gemini model:

```env
GEMINI_MODEL=gemini-3.1-flash-lite
```

The application can use `gemini-flash-latest` as a fallback for HTTP 404 model errors, provided the fallback is available to your API key.

### Step 6: Run the application

```powershell
python main.py
```

Alternatively:

```powershell
python -m agent.executor
```

### Step 7: Deactivate the virtual environment

```powershell
deactivate
```

## 💻 Usage Examples

Start the application and enter instructions such as the following:

| User Input | Expected Task |
|---|---|
| `Summarize this: Artificial intelligence automates repetitive tasks.` | Text summarization |
| `Translate hello, how are you? to Hindi` | Hindi translation |
| `Analyze sentiment: I love this product!` | Positive sentiment |
| `Analyze sentiment: This is the worst service ever.` | Negative sentiment |
| `Analyze sentiment: The package arrived on Tuesday.` | Neutral sentiment |
| `What is the temperature in Pune today?` | Current weather |
| `What is an AI agent?` | General question |
| `What is the weather today?` | Ask the user for a city |
| `Summarize this:` | Ask for text to summarize |
| `What is the temperature of boiling water?` | General question |

## 🧪 Testing & Validation

Use the following test cases to verify the application's behavior.

| # | Test Case | Expected Result |
|---|---|---|
| 1 | Summarization request | Short summary preserving the meaning |
| 2 | Hindi translation request | Hindi text in Devanagari script |
| 3 | Positive sentiment | Positive label |
| 4 | Negative sentiment | Negative label |
| 5 | Neutral sentiment | Neutral label |
| 6 | Weather in Pune | Temperature, humidity, and wind information |
| 7 | General knowledge question | Relevant answer from Gemini |
| 8 | Weather request without a city | Friendly prompt asking for a city |
| 9 | Invalid city name | Helpful error message without a traceback |
| 10 | Empty summarization input | Request for text to summarize |
| 11 | Boiling water temperature | Routed to general Q&A, not weather |
| 12 | Invalid Gemini API key | Friendly API error; application remains usable |

**Testing notes:**
- Verify that the router prints the selected task before execution.
- Compare translation and weather results with reliable reference sources.
- Record actual results from your own runs.
- Never claim a test passed unless you have verified it.

## 🔀 Rule-Based Router vs. LLM-Driven Agent

| Feature | This Project | LLM-Driven Tool-Calling Agent |
|---|---|---|
| Task selection | Regular expressions and rules | LLM selects tools based on descriptions |
| Flexibility | Depends on predefined patterns | Can interpret more varied instructions |
| Predictability | Generally deterministic routing | Tool selection may vary |
| Cost | No separate LLM call for routing | Usually requires an LLM call for tool selection |
| Multi-step planning | Not implemented | Can support multi-step tool execution |
| Failure modes | Missing or incorrect rules | Incorrect tool selection or arguments |

## 🔐 Security

- Store your API key in `.env`.
- Add `.env` and `.venv/` to `.gitignore`.
- Never commit real API keys, passwords, or other credentials.
- Keep `.env.example` limited to placeholder values.
- If a secret is accidentally pushed to GitHub, revoke or rotate it immediately.

Example `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
```

## ⚠️ Limitations

- Task selection depends on predefined keywords and regular expressions.
- Only Hindi translation is supported.
- The application does not retain conversation memory between turns.
- City geocoding may select an unintended location when names are ambiguous.
- Gemini responses may vary between runs.
- Language tasks require an internet connection and a valid API key.
- API quotas, rate limits, and model availability may affect execution.
- The application does not autonomously plan and execute multiple tools.

## 🚀 Future Improvements

- Implement LLM-based routing with function calling.
- Add support for more languages.
- Introduce conversation memory.
- Build a web interface using Streamlit or FastAPI.
- Add automated unit and integration tests.
- Support multiple weather providers and more data sources.
- Add structured logging and improved error reporting.
- Enable safe multi-step task execution.

## 📚 Learning Outcomes

This project demonstrates:

- Python modular programming and package structure
- Regular expressions and rule-based decision-making
- Integration with external APIs
- Environment variables and secure credential handling
- Input validation and exception handling
- Command-line application development
- Git and GitHub workflows
- The difference between rule-based automation and LLM-driven agents

## 📝 Report Outline

For academic documentation or project submission, use the following sections:

1. Title and abstract
2. Problem statement
3. Objectives
4. Existing system vs. proposed system
5. System architecture
6. Agent workflow
7. Tools and technologies
8. Implementation details
9. Test cases and actual results
10. Limitations
11. Future enhancements
12. Conclusion
13. Individual contribution and reflection

## 🎯 Conclusion

The **Agentic AI Task Executor** demonstrates how a simple Python application can route natural-language instructions to appropriate language-processing tasks and external tools.

By combining rule-based decision-making, Google Gemini, and the Open-Meteo API, the project provides a practical introduction to API integration, modular software design, and AI-assisted automation without relying on large agent frameworks.

It also provides a foundation for future development toward more flexible, LLM-driven agents with function calling, memory, and multi-step planning.

## 👨‍💻 Author

**Aman Srivastava**

GitHub: [@amansrivastava2102](https://github.com/amansrivastava2102)

---

⭐ If you find this project useful, consider giving the repository a star!
