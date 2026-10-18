# Agentic AI Task Executor

A beginner-friendly Python agent that reads a user instruction, **chooses a task with a rule-based router**, runs it, and prints the result. Written in plain Python (no LangChain / CrewAI / Groq).

| Task | Handled by |
|---|---|
| Text summarization | Gemini |
| Translation to Hindi | Gemini |
| Sentiment (Positive / Negative / Neutral) | Gemini |
| Current weather | Open-Meteo API (no key needed) |
| General questions | Gemini |

## Folder structure

```text
agentic-task-executor/
├── .env                 your real API key (never commit)
├── .env.example         template showing which variables exist
├── .gitignore           keeps .env and .venv out of Git
├── requirements.txt     google-genai, python-dotenv, requests
├── README.md
├── main.py              entry point
└── agent/
    ├── __init__.py      marks the folder as a package
    ├── llm.py           the only file that talks to Gemini
    ├── decision.py      rule-based router: message -> task
    ├── tasks.py         the five tasks, with validation and error handling
    ├── tools.py         get_weather(city) using Open-Meteo
    └── executor.py      the interactive loop
```

Import direction (no circular imports): `main -> executor -> decision, tasks`; `tasks -> decision, llm, tools`.

## Architecture and workflow

```text
User Input -> Task Decision -> Task Execution -> Gemini LLM or Weather Tool -> Result Processing -> Response
              (decision.py)    (tasks.py)        (llm.py / tools.py)          (tasks.py)            (executor.py)
```

**Honest description:** task selection is a *rule-based router* (regular expressions in `decision.py`). Gemini is used only to perform language tasks *after* the router has decided. The LLM does **not** choose tools, so this is not autonomous LLM tool calling.

## Setup (Windows PowerShell, from the project folder)

```powershell
# 1. Create a virtual environment (Python 3.11 or 3.12)
python -m venv .venv

# 2. Activate it (if blocked, run once: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned)
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the key: get one at https://aistudio.google.com/apikey
notepad .env        # make the line read: GOOGLE_API_KEY=your_real_key   (no quotes, no spaces)

# 5. Run
python main.py
# or, equivalently, from the project root:
python -m agent.executor

# 6. Leave the virtual environment when finished
deactivate
```

### Changing the Gemini model
Google retires models regularly. The default is `gemini-3.1-flash-lite` with `gemini-flash-latest` as an automatic fallback on HTTP 404. To use another model, add this line to `.env` (no code change needed):

```text
GEMINI_MODEL=model-name-from-https://ai.google.dev/gemini-api/docs/models
```

## Testing and collecting evidence

Run `python main.py`, type each input, and copy the console output (screenshot or text) into your report. Fill the last column yourself with what you actually observed.

| # | Input | Expected behaviour | How to verify | Actual result |
|---|---|---|---|---|
| 1 | `Summarize this: Artificial intelligence helps automate repetitive tasks.` | `[Task selected: summarize]`, then a 1-3 sentence summary | Summary is shorter and keeps the meaning | |
| 2 | `Translate hello, how are you? to Hindi` | `translate`; Devanagari text (e.g. नमस्ते, आप कैसे हैं?) | Compare with Google Translate | |
| 3 | `Analyze sentiment: I love this product!` | `sentiment`; `Sentiment: Positive` | Label matches the text | |
| 4 | `Analyze sentiment: This is the worst service I have ever had.` | `Sentiment: Negative` | Label matches the text | |
| 5 | `Analyze sentiment: The package arrived on Tuesday.` | `Sentiment: Neutral` | Label matches the text | |
| 6 | `What is the temperature in Pune today?` | `weather`; location "Pune, Maharashtra, India", temperature in °C, humidity %, wind km/h | Compare with a weather website (small differences are normal) | |
| 7 | `What is an AI agent?` | `general`; a clear explanation from Gemini | Answer is accurate and readable | |
| 8 | `What is the weather today?` | `weather`; asks for a city instead of crashing | Message says it could not tell which city | |
| 9 | `weather in Xyzzyq` | Friendly "could not find a city" message | No traceback | |
| 10 | `Summarize this:` | Asks for text to summarize | No API call is made | |
| 11 | `What is the temperature of boiling water?` | `general` (not weather) | Shows the router avoids broad keywords | |
| 12 | Temporarily set a wrong key in `.env`, ask `What is an AI agent?` | Friendly "API key rejected" message; app keeps running | Restore the key afterwards | |

Router-only check (no API key or internet needed): the `[Task selected: ...]` line is printed before execution, so tests 1-11 verify routing even when Gemini is unavailable.

## Report outline

1. **Title and abstract**: one-paragraph summary of what was built and tested.
2. **Problem statement**: repetitive text and information tasks need separate tools; a single interface that picks the right one saves effort.
3. **Objectives**: five tasks; secure key handling; graceful errors; no agent frameworks.
4. **Existing vs proposed system**: separate websites/apps per task vs one command-line agent.
5. **System architecture**: the file structure and import diagram above.
6. **Agent workflow**: the pipeline diagram above.
7. **Tools and technologies**: Python, google-genai, python-dotenv, requests, Open-Meteo, Cursor IDE.
8. **Implementation**: one subsection per file (router patterns, Gemini wrapper, weather tool, loop).
9. **Test cases and actual results**: the table above, filled with your real observations and screenshots.
10. **Limitations**: keyword/regex routing misses unusual phrasing; Hindi is the only target language; no memory between turns; single-city geocoding picks the top match; Gemini output can vary between runs; needs internet and a key.
11. **Future improvements**: LLM-based routing via function calling, more languages, conversation memory, automated unit tests, a web UI.
12. **Conclusion**.
13. **Individual contribution and reflection**: what you wrote, debugged and learned (be specific; mention bugs you found).

### Rule-based router vs LLM-driven tool-calling agent

| | This project (rule-based router) | LLM-driven tool-calling agent |
|---|---|---|
| Who picks the task? | Your regular expressions | The LLM, given tool descriptions |
| Flexibility | Only phrasings you anticipated | Understands new phrasing |
| Predictability / cost | Deterministic, free, fast | Can vary; costs an extra model call |
| Multi-step plans | No | Yes (can call several tools in sequence) |
| Failure mode | Wrong or missing rule | Wrong tool or invented arguments |

## Troubleshooting

| Problem | Fix |
|---|---|
| `GOOGLE_API_KEY is missing` | Edit `.env` (not `.env.example`), set a real key, restart. Run from the project folder so `.env` is found. |
| `404 NOT_FOUND` / "model not found" | The model was retired or renamed. Pick a current name from the Gemini models page and set `GEMINI_MODEL` in `.env`. |
| `429` quota error | Free-tier limit reached; wait and retry. |
| `ModuleNotFoundError: google` / `dotenv` / `requests` | Activate the venv (`.\.venv\Scripts\Activate.ps1`) then `pip install -r requirements.txt`. |
| `ModuleNotFoundError: agent` | You are in the wrong folder. `cd` into `agentic-task-executor` and run `python main.py`. |
| Activation blocked by PowerShell | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again. |
| Hindi shows as `????` | Use Windows Terminal or Cursor's terminal; `main.py` already sets UTF-8 output. |
| Weather says it cannot connect | Check internet or firewall; Open-Meteo needs no key. |
| Installed the old `google-generativeai` | Not used here. Run `pip uninstall google-generativeai` and install `google-genai` only. |
#   a g e n t i c - a i - r e p o - f l e x i  
 