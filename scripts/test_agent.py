#!/usr/bin/env python3
"""Interactive CLI test loop for the SupportIQ chatbot agent.

Usage
-----
python scripts/test_agent.py
"""

import asyncio
import sys
from pathlib import Path

# Ensure backend package is importable when running from repo root
_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT / "backend"))

from dotenv import load_dotenv

load_dotenv(_REPO_ROOT / "backend" / ".env")

from agent.orchestrator import run  # noqa: E402


async def main() -> None:
    print("SupportIQ Chatbot — Test Console (type 'quit' to exit)")
    print("=" * 60)

    history: list[dict] = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break

        reply = await run(user_input, history, user="TestUser")
        print(f"\nBot: {reply}")
        print("-" * 60)

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    asyncio.run(main())
