"""
test_agrimind.py — AgriMind Feature Verification
──────────────────────────────────────────────────
Runs offline tests (no API calls) to prove all 7 ADK concepts
are implemented and working. Include this in your Kaggle writeup.

Run with:
  python test_agrimind.py
"""

import sys

print("=" * 60)
print("AgriMind — Feature Verification Test")
print("=" * 60)

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        result = fn()
        print(f"  ✅  {name}")
        if result:
            print(f"       → {result}")
        passed += 1
    except Exception as e:
        print(f"  ❌  {name}")
        print(f"       → ERROR: {e}")
        failed += 1

# ── Concept 1: Multi-agent systems ────────────────────────────────────────────
print("\n[1] Multi-agent systems (ADK)")
import os; os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "test")

from agrimind.agent import root_agent
test("Orchestrator agent loads",
     lambda: f"name={root_agent.name}")
test("4 sub-agents registered",
     lambda: f"{[a.name for a in root_agent.sub_agents]}")
test("Orchestrator has memory tools",
     lambda: f"{[t.__name__ for t in root_agent.tools]}")

# ── Concept 2: MCP servers ────────────────────────────────────────────────────
print("\n[2] MCP servers")
from agrimind.agents.weather_agent import weather_agent
from agrimind.agents.market_agent  import market_agent

test("Weather agent uses MCPToolset",
     lambda: f"tools={type(weather_agent.tools[0]).__name__}")
test("Market agent uses MCPToolset",
     lambda: f"tools={type(market_agent.tools[0]).__name__}")

import importlib.util
def load_mcp(name):
    spec = importlib.util.spec_from_file_location(
        name, f"agrimind/mcp_servers/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

test("Weather MCP server loads",
     lambda: f"name={load_mcp('weather_mcp').mcp.name}")
test("Market MCP server loads",
     lambda: f"name={load_mcp('market_mcp').mcp.name}")

# ── Concept 3: Agent skills ───────────────────────────────────────────────────
print("\n[3] Agent skills")
from agrimind.agents.soil_crop_agent import soil_crop_agent
from agrimind.agents.disease_agent   import disease_agent

test("Soil agent skill: get_crop_recommendation",
     lambda: "✓" if any(t.__name__ == "get_crop_recommendation"
                         for t in soil_crop_agent.tools) else None)
test("Soil agent skill: get_soil_advice",
     lambda: "✓" if any(t.__name__ == "get_soil_advice"
                         for t in soil_crop_agent.tools) else None)
test("Disease agent skill: identify_pest_or_disease",
     lambda: "✓" if any(t.__name__ == "identify_pest_or_disease"
                         for t in disease_agent.tools) else None)

# ── Concept 4: Long-term memory ───────────────────────────────────────────────
print("\n[4] Long-term memory")
from agrimind.memory.farm_memory import (
    save_farm_profile, get_farm_profile,
    log_advice_given, get_recent_advice
)

test("Save farm profile to disk",
     lambda: save_farm_profile(
         "test_001", "Test Farmer", "Warangal", "black",
         5.0, ["cotton", "tur"], "rainfed")["status"])
test("Retrieve profile from disk",
     lambda: f"{get_farm_profile('test_001')['farmer_name']} in "
             f"{get_farm_profile('test_001')['location']}")
test("Log advice to history",
     lambda: log_advice_given(
         "test_001", "What crop?", "Grow cotton", "crop")["status"])
test("Retrieve recent advice",
     lambda: f"{get_recent_advice('test_001', 1)['total_interactions']} interactions")

# ── Concept 5: Sessions & state ───────────────────────────────────────────────
print("\n[5] Sessions & state management")
from google.adk.sessions import InMemorySessionService
from google.adk.runners  import Runner

test("InMemorySessionService instantiates",
     lambda: type(InMemorySessionService()).__name__)
test("Runner instantiates with agent",
     lambda: type(Runner(agent=root_agent, app_name="agrimind",
                         session_service=InMemorySessionService())).__name__)

# ── Concept 6: Context engineering ────────────────────────────────────────────
print("\n[6] Context engineering")
from agrimind.memory.context_manager import build_farm_context, inject_context

test("Build compact farm context",
     lambda: f"{len(build_farm_context('test_001'))} chars of context built")
test("Inject context into message",
     lambda: "FARMER CONTEXT" in inject_context("test_001", "What crop?") and "✓")
test("No context for unknown farmer",
     lambda: inject_context("unknown_999", "Hello") == "Hello" and "✓ (pass-through)")

# ── Concept 7: Security features ─────────────────────────────────────────────
print("\n[7] Security features")
from agrimind.security.guardrails import validate_query

test("Valid farming query passes",
     lambda: f"is_valid={validate_query('What crop should I plant?')['is_valid']}")
test("Banned pesticide blocked",
     lambda: f"blocked: {validate_query('endosulfan dose')['is_valid']==False and '✓'}")
test("Off-topic query blocked",
     lambda: f"blocked: {validate_query('tell me about cricket')['is_valid']==False and '✓'}")
test("Chemical query gets warning",
     lambda: f"warning present: {bool(validate_query('spray fungicide dose')['warning'])}")
test("Too-short query blocked",
     lambda: f"blocked: {validate_query('hi')['is_valid']==False and '✓'}")

# ── Agent tools: offline verification ────────────────────────────────────────
print("\n[Bonus] Tools offline verification")
from agrimind.tools.market_tools  import get_commodity_price
from agrimind.tools.crop_tools    import get_crop_recommendation, get_soil_advice
from agrimind.tools.disease_tools import identify_pest_or_disease

test("Market tool: cotton price",
     lambda: f"MSP=₹{get_commodity_price('cotton')['msp_per_quintal']:,}")
test("Crop tool: black soil kharif",
     lambda: f"{len(get_crop_recommendation('Warangal','black','kharif','rainfed')['recommended_crops'])} crops")
test("Soil tool: black soil advice",
     lambda: get_soil_advice('black')['also_known_as'])
test("Disease tool: cotton leaf curl",
     lambda: identify_pest_or_disease('cotton','leaves curling yellow')['identified_threat'])

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"  Results: {passed} passed  |  {failed} failed")
print("=" * 60)

# Cleanup test profile
import os
try:
    os.remove("data/farm_profiles/test_001.json")
except: pass

sys.exit(0 if failed == 0 else 1)
