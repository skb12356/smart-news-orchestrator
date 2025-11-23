# Agent-to-Agent Calling Setup for Watsonx Orchestrate

This guide explains how to set up agent-to-agent calling in IBM Watsonx Orchestrate, enabling your agents to automatically invoke each other.

## Overview

In Watsonx Orchestrate, agents can call other agents as tools, creating automated workflows:

```
News Article → Risk Scorer Agent → Chart Generator Agent → Feed Poster Agent → Complete Analysis
```

## Architecture

### Current Agent Setup

1. **Risk Scorer Agent** (`risk_scorer`)
   - Analyzes news articles for risk
   - Outputs: risk score, sentiment, categories
   - Tools: `analyze_all_news`, `get_high_risk_alerts`, `risk_scorer`

2. **Chart Generator Agent** (`chart_generator_agent`)
   - Creates visualizations from risk data
   - Outputs: PNG chart files
   - Tools: `create_trend_chart`, `create_comparison_chart`, etc.

3. **Feed Poster Agent** (`feed_poster_agent`)
   - Generates social media posts
   - Outputs: formatted posts with emojis and hashtags
   - Tools: `create_feed_post_from_article`, `generate_complete_feed`

4. **News Orchestrator Agent** (NEW - `orchestrator-agent.yaml`)
   - Master coordinator
   - Calls other agents in sequence
   - Combines all outputs

## Enabling Agent-to-Agent Calling

### Method 1: Using Tool Choice in Agent YAML

Agents can reference other agents as tools using the `orchestrate://` protocol:

```yaml
tools:
  - name: analyze_risk
    description: Call Risk Scorer Agent
    tool_choice: orchestrate://agents/risk_scorer
    parameters:
      article_content: string
```

### Method 2: LLM Instructions for Tool Invocation

Update agent instructions to explicitly call other agents:

```yaml
instructions: |
  When analyzing news:
  1. First, call the risk_scorer agent using its tools
  2. Then, pass results to chart_generator_agent
  3. Finally, call feed_poster_agent with all data
```

### Method 3: Skill Chaining (Recommended)

Watsonx Orchestrate supports skill chaining where agents automatically trigger based on output matching input schemas.

## Deployment Steps

### 1. Deploy Master Orchestrator Agent

```powershell
# Navigate to project
cd "c:\Users\saksh\OneDrive\Desktop\Projects\IBM-ORCHESTRA\hackathon-IBM"

# Activate environment
orchestrate env activate my-ai

# Import orchestrator agent
orchestrate agents import -f agents/orchestrator-agent.yaml
```

### 2. Update Existing Agents for Inter-Agent Communication

Modify the Risk Scorer agent to call Chart Generator upon completion:

```yaml
# agents/risk-scorer-agent.yaml
name: risk_scorer
description: Analyzes news articles and automatically triggers chart generation

instructions: |
  After analyzing risk:
  1. Calculate risk score and sentiment
  2. Automatically call chart_generator_agent with results
  3. Return combined output
  
post_processing:
  - agent: chart_generator_agent
    condition: risk_score > 0.4
    inputs:
      risk_data: ${output.risk_analysis}
```

### 3. Configure Chart Generator to Call Feed Poster

```yaml
# agents/chart-generator-agent.yaml
name: chart_generator_agent
description: Creates charts and triggers social media post generation

post_processing:
  - agent: feed_poster_agent
    inputs:
      article_data: ${input.article}
      risk_analysis: ${input.risk_data}
      chart_paths: ${output.charts}
```

### 4. Test Agent Chaining

```powershell
# Test with orchestrator
orchestrate agents invoke --agent orchestrator_agent --input '{
  "article": {
    "title": "Apple Q4 Earnings Miss",
    "content": "Apple reported earnings below expectations...",
    "url": "https://example.com/article",
    "source": "TechNews"
  }
}'
```

## Alternative: Using Flows

Watsonx Orchestrate also supports Flows for visual workflow orchestration:

### Create a Flow YAML

```yaml
# flows/news_analysis_flow.yaml
name: news_analysis_flow
description: Complete news analysis pipeline with agent chaining

steps:
  - id: risk_analysis
    agent: risk_scorer
    inputs:
      article: ${input.article}
    
  - id: chart_creation
    agent: chart_generator_agent
    inputs:
      risk_data: ${steps.risk_analysis.output}
      article: ${input.article}
    depends_on:
      - risk_analysis
  
  - id: social_post
    agent: feed_poster_agent
    inputs:
      article_data: ${input.article}
      risk_analysis: ${steps.risk_analysis.output}
      chart_paths: ${steps.chart_creation.output.charts}
    depends_on:
      - chart_creation

output:
  risk_analysis: ${steps.risk_analysis.output}
  charts: ${steps.chart_creation.output}
  social_post: ${steps.social_post.output}
```

### Deploy Flow

```powershell
orchestrate flows import -f flows/news_analysis_flow.yaml
```

## Verification

### Check Agent Connections

```powershell
# List all agents
orchestrate agents list

# Get agent details showing tool connections
orchestrate agents get --name orchestrator_agent --verbose
```

### Monitor Agent Calls

Enable verbose logging to see agent-to-agent calls:

```powershell
orchestrate config set logging.level debug
orchestrate agents invoke --agent orchestrator_agent --input-file test_article.json
```

## How Agent Calling Works in Production

1. **User/System submits article** → Orchestrator Agent
2. **Orchestrator calls Risk Scorer** → Analyzes risk (LLM: Llama 3.2 90B)
3. **Risk Scorer returns** → Risk score, sentiment, categories
4. **Orchestrator calls Chart Generator** → Creates visualizations
5. **Chart Generator returns** → PNG file paths
6. **Orchestrator calls Feed Poster** → Generates social content
7. **Feed Poster returns** → Social media post
8. **Orchestrator combines all** → Returns complete package

## Dashboard Integration

The dashboard shows this orchestration in the "How Watsonx Orchestrate Agents Work Together" section:

- **Visual flow diagram** showing agent connections
- **Step-by-step explanation** of agent calling sequence
- **Real-time status** of each agent in the pipeline
- **Article detail modal** showing outputs from each agent

## Benefits of Agent-to-Agent Calling

✅ **Fully Automated Pipeline** - No manual intervention needed
✅ **Intelligent Routing** - Agents call each other based on logic
✅ **Scalable Architecture** - Add new agents without changing workflow
✅ **LLM-Powered Decisions** - Each agent uses AI for its task
✅ **Error Handling** - Orchestrate manages failures and retries

## Next Steps

1. Deploy the orchestrator agent
2. Test agent chaining with sample articles
3. Monitor agent interactions in Watsonx Orchestrate UI
4. Adjust LLM parameters for optimal performance
5. Scale to production with batch processing

## Troubleshooting

### Agents Not Calling Each Other

- Verify agent names match exactly (use underscores, not hyphens)
- Check tool definitions include proper `tool_choice` or `agent` references
- Ensure output schema of one agent matches input schema of next
- Confirm all agents deployed successfully

### Performance Issues

- Adjust LLM temperature (lower = more deterministic)
- Use caching for frequently analyzed articles
- Consider parallel execution for independent agents
- Batch process multiple articles together

## Resources

- [IBM Watsonx Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [Agent Development Guide](https://www.ibm.com/docs/en/watsonx/watson-orchestrate/latest?topic=agents)
- [Orchestrate ADK CLI Reference](https://www.ibm.com/docs/en/watsonx/watson-orchestrate/latest?topic=cli)
