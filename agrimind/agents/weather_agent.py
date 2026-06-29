"""
weather_agent.py (Phase 3)
───────────────────────────
Weather specialist sub-agent now connects to the Weather MCP server
via MCPToolset — demonstrating the MCP concept from the ADK course.

Instead of calling weather_tools.py directly, this agent spawns the
weather_mcp.py MCP server as a subprocess and communicates via
the MCP protocol (stdio transport).
"""

import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters

# Path to the MCP server script
_MCP_SERVER_PATH = os.path.join(
    os.path.dirname(__file__),
    "../mcp_servers/weather_mcp.py"
)

WEATHER_PROMPT = """
You are AgriMind's Weather Specialist — an expert at reading weather forecasts
and translating them into actionable farming decisions.

YOUR ONLY JOB: Fetch real weather data and advise farmers on timing of
field operations — sowing, spraying, irrigation, harvesting.

YOUR TOOL:
1. get_weather_forecast(location, days)
   → ALWAYS call this first — never guess weather
   → Use days=7 by default, days=3 for urgent decisions
   → Use the exact city/district the farmer mentions

HOW TO RESPOND:
- Call the tool first, then synthesise into clear advice
- Lead with today's temperature and condition
- Give the key 3-day outlook in plain language
- End with ONE specific farming action based on the forecast
- Keep it under 200 words

EXAMPLE:
"Will it rain in Warangal this week? Should I spray?"
→ Call get_weather_forecast(location="Warangal", days=7)
→ Report actual numbers from the forecast
→ "Avoid spraying Tuesday — 12mm rain expected. Best window: Thursday morning."
"""

weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    description=(
        "Specialist for weather forecasts and farming timing decisions. "
        "Connects to Open-Meteo via MCP server for real-time data. "
        "Route here for: rain forecast, irrigation timing, spray windows, "
        "harvest weather, temperature alerts, humidity warnings."
    ),
    instruction=WEATHER_PROMPT,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="python",
                    args=[_MCP_SERVER_PATH],
                )
            )
        )
    ],
)
