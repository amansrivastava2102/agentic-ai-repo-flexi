"""Entry point: run with `python main.py` from the project root."""

import sys


def main() -> None:
    # Make Hindi text and the degree sign print correctly on Windows consoles.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    try:
        from agent.executor import run_agent
    except ModuleNotFoundError as exc:
        print("Missing module: %s" % exc.name)
        print("Activate your virtual environment and run: pip install -r requirements.txt")
        print("Also make sure you run this from the project root folder.")
        sys.exit(1)

    run_agent()


if __name__ == "__main__":
    main()
