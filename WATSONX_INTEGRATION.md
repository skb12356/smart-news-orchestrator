# 🤖 IBM Watsonx Integration Guide

## How Watsonx is Linked to Your Project

Your project uses **IBM Watsonx Orchestrate** to power the AI agents and coordinate their interactions. Here's exactly how it's integrated:

---

## 🔗 Integration Points

### 1. **Watsonx LLM Powers All Agents**

Every agent uses Watsonx's LLama model:

```yaml
# In orchestrator-agent.yaml, risk-scorer-agent.yaml, etc.
llm: watsonx/meta-llama/llama-3-2-90b-vision-instruct
```

**What this means:**
- All AI reasoning is powered by Watsonx's LLama 3.2 90B Vision model
- This model analyzes news articles, generates risk scores, and creates social posts

---

### 2. **Watsonx Orchestrate Coordinates Agent-to-Agent Calling**

The `orchestrator-agent.yaml` uses Watsonx's `orchestrate://` protocol:

```yaml
tools:
  - name: call_risk_scorer
    description: Invokes the Risk Scorer Agent to analyze article risk
    tool_choice: orchestrate://agents/risk_scorer  # ← Watsonx protocol
    parameters:
      article_content: string
      article_title: string
      article_url: string
  
  - name: call_chart_generator  
    description: Invokes the Chart Generator Agent to create visualizations
    tool_choice: orchestrate://agents/chart_generator_agent  # ← Watsonx protocol
    parameters:
      risk_data: object
      chart_types: array
  
  - name: call_feed_poster
    description: Invokes the Feed Poster Agent to create social media content
    tool_choice: orchestrate://agents/feed_poster_agent  # ← Watsonx protocol
    parameters:
      article_data: object
      risk_analysis: object
      chart_paths: array
```

**What this does:**
- Watsonx Orchestrate manages agent-to-agent communication
- Agents invoke each other automatically using the `orchestrate://` protocol
- Creates a seamless pipeline: Risk Scorer → Chart Generator → Feed Poster

---

### 3. **Watsonx ADK Tools Integration**

Your tools use IBM Watsonx Orchestrate's SDK:

```python
# tools/risk_scorer_tool.py
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool  # ← Watsonx decorator
def risk_scorer(
    article_text: str,
    source: str = "unknown",
    published_time: str = "unknown",
    article_title: str = "No title"
) -> Dict[str, Any]:
    """
    Analyze a news article and return a comprehensive risk assessment.
    """
    # ... analysis logic ...
```

**What this does:**
- Decorates Python functions as Watsonx-compatible tools
- Makes them callable by Watsonx agents
- Enables seamless integration with Watsonx Orchestrate workflows

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     IBM WATSONX ORCHESTRATE                     │
│                  (Coordination & LLM Engine)                    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Powers all agents with LLama 3.2 90B
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
┌───────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Risk Scorer Agent │  │ Chart Generator  │  │ Feed Poster      │
│                   │  │ Agent            │  │ Agent            │
├───────────────────┤  ├──────────────────┤  ├──────────────────┤
│ LLM: watsonx/     │  │ LLM: watsonx/    │  │ LLM: watsonx/    │
│ llama-3-2-90b     │  │ llama-3-2-90b    │  │ llama-3-2-90b    │
├───────────────────┤  ├──────────────────┤  ├──────────────────┤
│ Tools:            │  │ Tools:           │  │ Tools:           │
│ - risk_scorer     │  │ - chart_creator  │  │ - feed_generator │
│ - analyze_news    │  │ - visualizer     │  │ - post_creator   │
└───────────────────┘  └──────────────────┘  └──────────────────┘
        │                       │                      │
        └───────────────────────┴──────────────────────┘
                                │
                                │ orchestrate:// protocol
                                │
                                ▼
                ┌────────────────────────────────┐
                │ Orchestrator Agent             │
                │ (Master Coordinator)           │
                ├────────────────────────────────┤
                │ Calls agents in sequence:      │
                │ 1. Risk Scorer                 │
                │ 2. Chart Generator             │
                │ 3. Feed Poster                 │
                └────────────────────────────────┘
                                │
                                ▼
                ┌────────────────────────────────┐
                │ Complete Analysis Package      │
                │ - Risk scores                  │
                │ - Charts (PNG files)           │
                │ - Social media posts           │
                └────────────────────────────────┘
                                │
                                ▼
                ┌────────────────────────────────┐
                │ React Dashboard                │
                │ (Displays results to user)     │
                └────────────────────────────────┘
```

---

## 📁 Files Using Watsonx

### Agent Configuration Files (YAML):
1. **`agents/orchestrator-agent.yaml`**
   - Uses `llm: watsonx/meta-llama/llama-3-2-90b-vision-instruct`
   - Calls other agents via `orchestrate://` protocol

2. **`agents/risk-scorer-agent.yaml`**
   - Uses Watsonx LLM for risk analysis
   - Defines tools that Watsonx can call

3. **`agents/chart-generator-agent.yaml`**
   - Uses Watsonx LLM for chart generation decisions

4. **`agents/feed-poster-agent.yaml`**
   - Uses Watsonx LLM for social media post generation

### Python Integration:
1. **`tools/risk_scorer_tool.py`**
   ```python
   from ibm_watsonx_orchestrate.agent_builder.tools import tool
   
   @tool  # Makes function callable by Watsonx
   def risk_scorer(...):
       # Analysis logic
   ```

2. **`agents/risk_scorer_agent.py`**
   - Core logic that Watsonx agents invoke

---

## 🔄 Data Flow with Watsonx

```
1. News Article Input
   ↓
2. Watsonx Orchestrator Agent Receives Request
   ↓
3. Watsonx calls Risk Scorer Agent via orchestrate://agents/risk_scorer
   └─ Watsonx LLM analyzes article
   └─ Returns: risk_score, sentiment, categories
   ↓
4. Watsonx calls Chart Generator via orchestrate://agents/chart_generator
   └─ Watsonx LLM creates visualization config
   └─ Python creates PNG charts
   └─ Returns: chart file paths
   ↓
5. Watsonx calls Feed Poster via orchestrate://agents/feed_poster
   └─ Watsonx LLM generates social post
   └─ Returns: feed_title, hashtags, urgency
   ↓
6. Orchestrator combines all results
   └─ Returns complete analysis package
   ↓
7. Dashboard fetches and displays results
```

---

## 🚀 How to Deploy to Watsonx Orchestrate

### 1. Install Watsonx Orchestrate CLI

```bash
pip install ibm-watsonx-orchestrate
```

### 2. Configure Authentication

```bash
# Set up your Watsonx credentials
export WATSONX_API_KEY="your-api-key"
export WATSONX_PROJECT_ID="your-project-id"
```

### 3. Deploy Agents

```bash
cd hackathon-IBM

# Deploy orchestrator agent
orchestrate agents import -f agents/orchestrator-agent.yaml

# Deploy risk scorer agent
orchestrate agents import -f agents/risk-scorer-agent.yaml

# Deploy chart generator agent
orchestrate agents import -f agents/chart-generator-agent.yaml

# Deploy feed poster agent
orchestrate agents import -f agents/feed-poster-agent.yaml
```

### 4. Verify Deployment

```bash
# List all deployed agents
orchestrate agents list

# Get details of orchestrator
orchestrate agents get --name news_orchestrator_agent --verbose
```

### 5. Test Agent Calling

```bash
# Invoke orchestrator with test article
orchestrate agents invoke --agent news_orchestrator_agent --input '{
  "article": {
    "title": "Oracle Stock Falls After Earnings Miss",
    "content": "Oracle Corporation shares dropped 6.7% today after...",
    "url": "https://finance.yahoo.com/news/oracle-stock-falls",
    "source": "Yahoo Finance"
  }
}'
```

---

## 🔧 Current Status

### ✅ Already Configured:
- [x] Watsonx LLM model specified in all agent YAMLs
- [x] `orchestrate://` protocol configured for agent-to-agent calling
- [x] Orchestrator agent created with complete workflow
- [x] Python tools decorated with `@tool` for Watsonx compatibility
- [x] Agent instructions optimized for Watsonx LLama model

### 🔄 To Enable Production Deployment:
- [ ] Deploy agents to Watsonx Orchestrate cloud
- [ ] Configure authentication credentials
- [ ] Set up environment variables
- [ ] Test agent invocation via Watsonx CLI

---

## 💡 Key Watsonx Features Used

### 1. **Agent Builder**
- Defines agents with YAML configuration
- Specifies LLM model, instructions, tools

### 2. **Tool System**
- Python functions decorated with `@tool`
- Makes functions callable by Watsonx agents

### 3. **Agent-to-Agent Calling**
- `orchestrate://` protocol for cross-agent communication
- Sequential pipeline: Agent A → Agent B → Agent C

### 4. **LLM Engine**
- Uses Meta LLama 3.2 90B Vision model
- Powers all AI reasoning and generation

---

## 📊 What Watsonx Does in Your Project

| Component | Watsonx Role |
|-----------|-------------|
| **Risk Analysis** | Watsonx LLM analyzes article text and assigns risk scores |
| **Sentiment Detection** | Watsonx LLM determines positive/neutral/negative sentiment |
| **Category Classification** | Watsonx LLM classifies risk into financial/regulatory/etc. |
| **Keyword Matching** | Watsonx LLM matches article content to company knowledge |
| **Chart Generation** | Watsonx LLM decides what charts to create |
| **Social Post Creation** | Watsonx LLM generates feed titles, emojis, hashtags |
| **Agent Coordination** | Watsonx Orchestrate manages agent-to-agent calls |

---

## 🎯 Summary

**Watsonx Integration Points:**

1. **LLM Engine**: All agents use `watsonx/meta-llama/llama-3-2-90b-vision-instruct`
2. **Agent Orchestration**: `orchestrate://` protocol coordinates agent calls
3. **Tool System**: Python functions decorated with `@tool` from Watsonx SDK
4. **Workflow Management**: Orchestrator agent manages sequential agent invocation

**Current State:**
- ✅ Watsonx configured in all agent YAMLs
- ✅ Agent-to-agent calling setup with `orchestrate://`
- ✅ Dashboard simulates Watsonx outputs (fetches from JSON)
- 🔄 Ready to deploy to Watsonx Orchestrate cloud (optional)

**For Production Watsonx Deployment:**
- See `AGENT_CALLING_SETUP.md` for detailed deployment instructions
- Run `orchestrate agents import` commands to deploy
- Configure API keys and project IDs

---

**🤖 In short: Watsonx is the brain powering all AI agents and coordinating their interactions!**
