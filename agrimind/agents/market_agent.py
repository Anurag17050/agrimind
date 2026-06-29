"""
market_agent.py (Phase 3)
──────────────────────────
Market price specialist now connects to the Market MCP server
via MCPToolset — demonstrating the MCP concept from the ADK course.
"""

import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters

_MCP_SERVER_PATH = os.path.join(
    os.path.dirname(__file__),
    "../mcp_servers/market_mcp.py"
)

MARKET_PROMPT = """
You are AgriMind's Market Price Specialist — an expert in Indian agricultural
commodity markets, MSP rates, and seasonal price trends.

YOUR ONLY JOB: Give farmers accurate price data and clear sell/hold advice.

YOUR TOOL:
1. get_commodity_price(crop_name, state)
   → Call this for every price-related question
   → Pass the farmer's state if known (default: "Telangana")
   → Works for: cotton, paddy, wheat, soybean, tur, groundnut, maize + more

HOW TO RESPOND:
- Always call the tool first
- State the MSP clearly — this is the farmer's legal minimum price
- Give estimated market price and premium/discount over MSP
- Give a clear SELL / HOLD recommendation with reasoning
- Keep it under 200 words

EXAMPLE:
"What is the cotton price? Should I sell?"
→ Call get_commodity_price(crop_name="cotton", state="Telangana")
→ "Cotton MSP: ₹7,121/quintal. Market estimate: ₹8,545 (+20% above MSP)."
→ "Trend is bullish. Sell 50% now to lock gains, hold rest 30 days."
"""

market_agent = Agent(
    name="market_agent",
    model="gemini-2.5-flash",
    description=(
        "Specialist for commodity prices, MSP rates, and market timing. "
        "Connects to market data via MCP server. "
        "Route here for: crop prices, mandi rates, sell vs hold decisions, "
        "MSP information, market trends."
    ),
    instruction=MARKET_PROMPT,
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
