# AgriMind 🌾

### Every Indian farmer deserves a team of experts. AgriMind puts four in their pocket.

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)](https://python.org)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-2.3.0-orange?style=flat-square)](https://google.github.io/adk-docs/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-green?style=flat-square&logo=google)](https://aistudio.google.com)
[![Tests](https://img.shields.io/badge/Tests-28%20passed-brightgreen?style=flat-square)](#testing)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)](LICENSE)
[![Track](https://img.shields.io/badge/Track-Agents%20for%20Good-teal?style=flat-square)](#)

> **Built for the Google Agent Development Kit Capstone · Agents for Good Track**

---

## The Problem

India has **600 million people** dependent on agriculture. The average smallholder farmer owns less than 2 hectares of land and makes every planting, spraying, and selling decision without any expert guidance.

| The gap | The consequence |
|---|---|
| No access to agronomists | 30–70% yield loss from unidentified pest outbreaks |
| No market intelligence | 20–40% income lost from selling at the wrong time |
| No weather-aware planning | Entire seasons lost to preventable waterlogging or drought |
| No knowledge of MSP | Farmers sell below the government's legal price floor |

The gap isn't intelligence — Indian farmers are extraordinarily skilled. The gap is **access to the right information at the right moment.**

AgriMind closes that gap.

---

## What AgriMind Does

A farmer types a question in plain English or Hindi. Within seconds they receive advice that would otherwise require consulting an agronomist, a meteorologist, a commodity trader, and a plant pathologist.

**One question. Four specialists. One clear answer.**

```
Farmer:   "My cotton leaves are curling and turning yellow. What is wrong?"

AgriMind: Your cotton has Cotton Leaf Curl Virus (CLCuV) — Medium confidence.
          This viral disease is common in Warangal and can cause complete crop failure.

          Management Steps:
          1. Variety Selection: Use CLCuV-resistant varieties (MNH-786 or VH-289)
          2. Vector Control: Spray Thiamethoxam 25 WG @ 0.5g/litre immediately
          3. Sanitation: Remove infected plants within 45 days to limit spread

          Verify before spending on pesticides. For severe outbreaks,
          contact your local Krishi Vigyan Kendra (KVK) immediately.
```

```
Farmer:   "What is the cotton MSP? Should I sell now?"

AgriMind: Cotton MSP: ₹7,121/quintal (government floor price — your legal minimum)
          Current market estimate: ₹8,545/quintal (+20% above MSP)
          Recommendation: SELL. Market trend is stable and off-peak season
          means stored stock fetches a premium right now.
```

```
Farmer:   "Will it rain in Warangal this week?"

AgriMind: Today: 25.1°C, moderate drizzle, high humidity.
          Forecast: Thunderstorms with 30mm+ rain July 3–5.
          Farming advice: Ensure field drainage is clear to prevent
          waterlogging. Watch for fungal diseases with high humidity.
```

---

## Architecture

AgriMind is a **three-tier multi-agent system** built on Google ADK 2.3.0.

```
┌─────────────────────────────────────────────────┐
│                   FARMER                        │
│         Asks in plain language                  │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│            AGRIMIND CORE                        │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │        Orchestrator Agent                │   │
│  │  Routes queries · Manages sessions       │   │
│  │  Owns long-term memory tools             │   │
│  └────┬──────────┬──────────┬──────────┬───┘   │
│       │          │          │          │        │
│  ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐  │
│  │ Soil & │ │Weather │ │Market  │ │Disease │  │
│  │ Crop   │ │Agent   │ │Agent   │ │Agent   │  │
│  │ Agent  │ │(MCP)   │ │(MCP)   │ │        │  │
│  └────────┘ └───┬────┘ └───┬────┘ └────────┘  │
└─────────────────┼──────────┼───────────────────┘
                  │          │
     ┌────────────▼─┐  ┌─────▼──────────┐
     │ Weather MCP  │  │  Market MCP    │
     │  Open-Meteo  │  │  MSP 2024-25   │
     │  (Real-time) │  │  + Seasonal    │
     └──────────────┘  └────────────────┘
```

### The Orchestrator

The root agent receives every farmer query, reads the intent, and uses ADK's `transfer_to_agent` to route to the right specialist. It owns all memory tools — saving and retrieving farmer profiles, logging every piece of advice given so the system never repeats itself.

### The 4 Specialist Sub-Agents

| Agent | Domain | Tools |
|---|---|---|
| **Soil & Crop Agent** | Crop selection, planting calendars, fertiliser advice | `get_crop_recommendation`, `get_soil_advice` |
| **Weather Agent** | Real-time forecasts, irrigation timing, spray windows | `get_weather_forecast` via **MCP** |
| **Market Agent** | MSP rates, commodity prices, sell/hold decisions | `get_commodity_price` via **MCP** |
| **Disease Agent** | Pest/disease identification, treatment protocols | `identify_pest_or_disease` |

---

## ADK Course Concepts — All 7 Demonstrated

### ✅ 1. Multi-Agent Systems

AgriMind uses a full orchestrator–specialist pattern. Every question is routed via ADK's `transfer_to_agent`. The Events panel in ADK Web UI shows this in real time:

```
agrimind_orchestrator → disease_agent  → identify_pest_or_disease  ✓
agrimind_orchestrator → weather_agent  → get_weather_forecast       ✓
agrimind_orchestrator → market_agent   → get_commodity_price        ✓
```

### ✅ 2. MCP Servers

Two custom MCP servers built with **FastMCP**:

- `weather_mcp.py` — wraps the Open-Meteo real-time weather API
- `market_mcp.py` — exposes CCEA MSP 2024-25 commodity price data

Weather Agent and Market Agent connect via `MCPToolset` + `StdioConnectionParams`, spawning MCP servers as subprocesses. Real-world MCP protocol, not simulated.

```python
weather_agent = Agent(
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="python",
                    args=["agrimind/mcp_servers/weather_mcp.py"],
                )
            )
        )
    ]
)
```

### ✅ 3. Agent Skills

Each sub-agent has a tightly scoped skill set — it knows its domain deeply and nothing outside it. The Soil Agent only handles agronomy. The Disease Agent only handles plant pathology. This mirrors how real expert teams work, and produces better answers than a flat-tool single agent.

### ✅ 4. Sessions & State Management

Every farmer gets an isolated session via `InMemorySessionService`. The orchestrator maintains full conversation context across turns — it remembers that Ravi Kumar mentioned cotton three messages ago.

```python
session_service = InMemorySessionService()
session = await session_service.create_session(
    app_name="agrimind",
    user_id=farmer_id
)
runner = Runner(
    agent=root_agent,
    app_name="agrimind",
    session_service=session_service
)
```

### ✅ 5. Long-Term Memory

Farmer profiles persist to disk as JSON files in `data/farm_profiles/`. This memory survives across sessions — when Ravi Kumar returns next week, AgriMind already knows his 5 acres of black soil in Warangal. Advice history is logged so the agent never contradicts past recommendations.

```json
{
  "farmer_name": "Ravi Kumar",
  "location": "Warangal",
  "soil_type": "black",
  "current_crops": ["cotton", "tur"],
  "query_history": [
    {
      "date": "2026-06-30",
      "topic": "disease",
      "advice": "Cotton Leaf Curl Virus detected..."
    }
  ]
}
```

### ✅ 6. Context Engineering

`context_manager.py` builds a compact farm profile string and injects it silently into every message before it reaches the agents. Agents are personalised from the very first word — no redundant memory calls, no "what's your farm like?" questions on every visit.

```
[FARMER CONTEXT — inject silently]
Name: Ravi Kumar | Location: Warangal | Soil: black soil
Farm: 5.0 acres | Crops: cotton, tur | Water: rainfed
Last: disease — My cotton leaves are curling...
```

### ✅ 7. Security Features

`guardrails.py` runs programmatically before every query reaches the agents:

- **Banned pesticide detection** — blocks 13 legally prohibited substances (endosulfan, monocrotophos, DDT, etc.) with a clear explanation of Indian law
- **Off-topic filtering** — keeps AgriMind focused on farming
- **Input sanitisation** — strips HTML/injection characters
- **Safety disclaimers** — appended automatically for any chemical advice

```
Farmer:   "Tell me about endosulfan dosage for cotton"

AgriMind: 'Endosulfan' is legally banned in India under the Insecticides Act.
          AgriMind cannot provide advice on prohibited substances.
          Safe alternatives for cotton pest control: [list follows]
```

---

## Data Sources

All data is real, public, and verifiable.

| Data | Source | Cost |
|---|---|---|
| Weather forecasts | [Open-Meteo API](https://open-meteo.com) (real-time, 7-day) | Free, no API key |
| MSP crop prices | [CCEA Government of India 2024-25](https://agricoop.nic.in) | Public data |
| Crop knowledge | [ICAR agronomic guidelines](https://icar.org.in) | Public data |
| Disease management | [NCIPM (National Centre for IPM)](https://ncipm.icar.gov.in) | Public data |

---

## Project Structure

```
agrimind/
├── agrimind/
│   ├── agent.py                    # Orchestrator agent
│   ├── agents/
│   │   ├── soil_crop_agent.py      # Crop & soil specialist
│   │   ├── weather_agent.py        # Weather specialist (MCPToolset)
│   │   ├── market_agent.py         # Market specialist (MCPToolset)
│   │   └── disease_agent.py        # Disease & pest specialist
│   ├── mcp_servers/
│   │   ├── weather_mcp.py          # FastMCP weather server (Open-Meteo)
│   │   └── market_mcp.py           # FastMCP market server (MSP data)
│   ├── memory/
│   │   ├── farm_memory.py          # Long-term memory (JSON persistence)
│   │   └── context_manager.py      # Context engineering — profile injection
│   ├── tools/
│   │   ├── weather_tools.py        # Open-Meteo integration
│   │   ├── market_tools.py         # MSP + commodity data
│   │   ├── crop_tools.py           # ICAR crop knowledge
│   │   └── disease_tools.py        # NCIPM pest/disease data
│   └── security/
│       └── guardrails.py           # Input validation & safety
├── main.py                         # Session runner (CLI interface)
├── test_agrimind.py                # 28-test verification suite
└── requirements.txt
```

---

## Setup & Installation

### Prerequisites

- Python 3.12+
- A [Gemini API key](https://aistudio.google.com/app/apikey) (free tier works)

### Install

```bash
git clone https://github.com/Anurag17050/agrimind
cd agrimind

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Mac / Linux
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Set your Gemini API key
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### Run

```bash
# Option 1 — ADK Web UI (recommended — shows Events panel with agent routing)
adk web agrimind/

# Option 2 — Terminal CLI
python main.py
```

With `adk web`, open [http://localhost:8000](http://localhost:8000) in your browser. You'll see a full chat interface with the Events panel on the left showing real-time agent routing.

---

## Testing

Run the full verification suite (no API calls required):

```bash
python test_agrimind.py
```

Expected output:

```
============================================================
AgriMind — Feature Verification Test
============================================================

[1] Multi-agent systems (ADK)
  ✅  Orchestrator agent loads
  ✅  4 sub-agents registered
  ✅  Orchestrator has memory tools

[2] MCP servers
  ✅  Weather agent uses MCPToolset
  ✅  Market agent uses MCPToolset
  ✅  Weather MCP server loads
  ✅  Market MCP server loads

[3] Agent skills
  ✅  Soil agent skill: get_crop_recommendation
  ✅  Soil agent skill: get_soil_advice
  ✅  Disease agent skill: identify_pest_or_disease

[4] Long-term memory
  ✅  Save farm profile to disk
  ✅  Retrieve profile from disk
  ✅  Log advice to history
  ✅  Retrieve recent advice

[5] Sessions & state management
  ✅  InMemorySessionService instantiates
  ✅  Runner instantiates with agent

[6] Context engineering
  ✅  Build compact farm context
  ✅  Inject context into message
  ✅  No context for unknown farmer

[7] Security features
  ✅  Valid farming query passes
  ✅  Banned pesticide blocked
  ✅  Off-topic query blocked
  ✅  Chemical query gets warning
  ✅  Too-short query blocked

[Bonus] Tools offline verification
  ✅  Market tool: cotton price (MSP=₹7,121)
  ✅  Crop tool: black soil kharif (3 crops)
  ✅  Soil tool: black soil advice (Regur / cotton soil)
  ✅  Disease tool: cotton leaf curl (Leaf Curl)

============================================================
  Results: 28 passed  |  0 failed
============================================================
```

---

## Example Conversations

Try these to explore the system — introduce yourself first so AgriMind can save your profile:

```
My name is Ravi Kumar, I farm in Warangal, Telangana.
5 acres of black soil, rainfed. Growing cotton and tur.
```

Then ask:

| Question | Agent invoked |
|---|---|
| "My cotton leaves are curling and turning yellow" | `disease_agent` |
| "Will it rain in Warangal this week?" | `weather_agent` → Weather MCP |
| "What is the cotton MSP? Should I sell now?" | `market_agent` → Market MCP |
| "What crop should I plant this kharif season?" | `soil_crop_agent` |
| "Tell me about endosulfan dosage" | ❌ Blocked by guardrails |

---

## Impact

| Scale | Number |
|---|---|
| Smallholder farmers in India | 150 million |
| Annual losses from pest/disease | ₹1.5 lakh crore |
| Annual losses from below-MSP sales | ₹40,000 crore |
| Average agronomist consultation fee | ₹500–2,000 |
| AgriMind consultation fee | ₹0 |

A cotton farmer who identifies Cotton Leaf Curl Virus 3 weeks earlier saves the entire crop. A wheat farmer in Punjab who knows the MSP is ₹2,275 doesn't sell at ₹2,200 to a middleman. A soybean farmer in Madhya Pradesh who switches to a resistant variety before yellow mosaic spreads avoids a catastrophic season.

These aren't hypothetical outcomes. They're the ordinary consequences of having expert knowledge versus not having it.

---

## Built With

| Component | Technology |
|---|---|
| Agent framework | [Google Agent Development Kit (ADK) 2.3.0](https://google.github.io/adk-docs/) |
| Language model | Gemini 2.5 Flash |
| MCP servers | [FastMCP](https://github.com/jlowin/fastmcp) |
| Weather data | [Open-Meteo API](https://open-meteo.com) |
| MSP data | CCEA Government of India 2024-25 |
| Language | Python 3.12 |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

*Built for the Google ADK Agents Capstone · Track: Agents for Good*
