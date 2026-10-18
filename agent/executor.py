"""The interactive agent loop."""

from agent.decision import decide
from agent.tasks import run_task

WELCOME = """\
=== Agentic AI Task Executor ===
I can: summarize text, translate to Hindi, analyze sentiment,
report current weather, and answer general questions.

Examples:
  Summarize this: <text>
  Translate hello, how are you? to Hindi
  Analyze sentiment: I love this product!
  What is the temperature in Pune today?
  What is an AI agent?

Type 'exit' to quit.
"""


def process_request(user_input: str) -> str:
    """Decision -> execution -> result for ONE message (used by the loop)."""
    choice = decide(user_input)
    print("[Task selected: %s]" % choice.task)
    return run_task(choice)


def run_agent() -> None:
    print(WELCOME)
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            return

        try:
            result = process_request(user_input)
        except Exception as exc:  # last line of defence: never crash the loop
            result = "Unexpected error (%s). Please try again." % type(exc).__name__
        print("\nAgent: %s\n" % result)


if __name__ == "__main__":
    run_agent()
