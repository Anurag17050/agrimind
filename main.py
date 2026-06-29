"""
main.py — AgriMind Session Runner (Phase 4)
────────────────────────────────────────────
Demonstrates all 7 ADK course concepts in one clean runner:

  ✅ Multi-agent systems    — orchestrator routes to 4 sub-agents
  ✅ MCP servers            — weather + market via MCPToolset
  ✅ Agent skills           — each sub-agent has focused tools
  ✅ Sessions & state       — InMemorySessionService per farmer
  ✅ Long-term memory       — farm profiles persisted to disk
  ✅ Context engineering    — farm profile injected every turn
  ✅ Security features      — guardrails validate every query
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise EnvironmentError(
        "\n❌  GOOGLE_API_KEY not found in .env file.\n"
        "Get your key at: https://aistudio.google.com/app/apikey\n"
    )

from google.adk.runners  import Runner
from google.adk.sessions import InMemorySessionService
from google.genai        import types

from agrimind.agent                   import root_agent
from agrimind.memory.context_manager  import inject_context
from agrimind.security.guardrails     import validate_query, add_safety_footer

# ── Session setup ─────────────────────────────────────────────────────────────
APP_NAME        = "agrimind"
session_service = InMemorySessionService()


async def run_session(farmer_id: str = "demo_farmer") -> None:
    """Run an interactive AgriMind session with full context + security."""

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=farmer_id,
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    print("\n" + "═" * 60)
    print("🌾  AgriMind — AI Agricultural Advisor")
    print("    Powered by Google ADK + Gemini")
    print("═" * 60)
    print("Ask about crops, weather, pests, soil, or market prices.")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            raw_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! Good luck with your harvest. 🌾")
            break

        if raw_input.lower() in ("quit", "exit", "bye"):
            print("\nGoodbye! 🌾")
            break

        if not raw_input:
            continue

        # ── Security: validate every query before sending to agent ────────────
        validation = validate_query(raw_input)

        if not validation["is_valid"]:
            print(f"\nAgriMind: {validation['block_reason']}\n")
            continue

        if validation["warning"]:
            print(f"\n⚠️  {validation['warning']}")

        # ── Context engineering: inject farm profile into the message ─────────
        enriched_message = inject_context(farmer_id, validation["clean_query"])

        content = types.Content(
            role="user",
            parts=[types.Part(text=enriched_message)],
        )

        print("\nAgriMind: ", end="", flush=True)

        async for event in runner.run_async(
            user_id=farmer_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    print(event.content.parts[0].text)
                break

        print()


def main():
    asyncio.run(run_session())


if __name__ == "__main__":
    main()
