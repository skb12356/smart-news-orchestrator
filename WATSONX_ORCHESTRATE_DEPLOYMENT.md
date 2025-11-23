# IBM Watsonx Orchestrate Deployment Guide

Complete guide to deploy and connect the News Analysis Pipeline in IBM Watsonx Orchestrate.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Agent & Tool Structure](#agent--tool-structure)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Flow Connection in Orchestrate UI](#flow-connection-in-orchestrate-ui)
5. [Testing the Flow](#testing-the-flow)
6. [UI Dashboard (Next Phase)](#ui-dashboard-next-phase)

---

## 🔧 Prerequisites

### Required Access
- IBM Watsonx Orchestrate account
- Access to Watsonx AI for LLM (meta-llama/llama-3-2-90b-vision-instruct)
- IBM Cloud account with API credentials

### Required Files (All Ready!)
```
hackathon-IBM/
├── agents/
│   ├── risk-scorer-agent.yaml          ✅ Ready
│   ├── chart-generator-agent.yaml      ✅ Ready
│   └── feed-poster-agent.yaml          ✅ Ready
├── tools/
│   ├── risk_scorer_tool.py             ✅ Ready (4 @tool functions)
│   ├── chart_generator_tool.py         ✅ Ready (5 @tool functions)
│   └── feed_poster_tool.py             ✅ Ready (4 @tool functions)
└── knowledge/
    └── company.json                     ✅ Ready
```

---

## 🎯 Agent & Tool Structure

### **Agent 1: Risk Scorer**
**File**: `agents/risk-scorer-agent.yaml`
**Purpose**: Analyzes news articles and assigns risk scores

**Tools** (from `tools/risk_scorer_tool.py`):
1. ✅ `analyze_article_risk` - Analyze single article
2. ✅ `batch_analyze_articles` - Process multiple articles
3. ✅ `filter_articles_by_risk` - Filter by risk threshold
4. ✅ `get_risk_summary` - Generate statistics

### **Agent 2: Chart Generator**
**File**: `agents/chart-generator-agent.yaml`
**Purpose**: Creates visualizations from tabular data

**Tools** (from `tools/chart_generator_tool.py`):
1. ✅ `create_line_chart` - Time series charts
2. ✅ `create_bar_chart` - Categorical comparisons
3. ✅ `create_pie_chart` - Percentage breakdowns
4. ✅ `create_histogram` - Distribution analysis
5. ✅ `auto_generate_chart` - Auto-detect chart type

### **Agent 3: Feed Poster**
**File**: `agents/feed-poster-agent.yaml`
**Purpose**: Creates engaging social media posts

**Tools** (from `tools/feed_poster_tool.py`):
1. ✅ `create_feed_post_from_article` - Single post with LLM content
2. ✅ `generate_complete_feed` - Batch process all articles
3. ✅ `analyze_article_for_feed` - Get LLM guidance
4. ✅ `get_feed_statistics` - Feed analytics

---

## 🚀 Step-by-Step Deployment

### **Step 1: Prepare Tool Files**

Each tool file is already decorated with `@tool` decorator. Verify they're ready:

```python
# Example from risk_scorer_tool.py
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool
def analyze_article_risk(article_json: str) -> str:
    """
    Analyze a single news article for risk assessment.
    
    Args:
        article_json: JSON string containing article data
        
    Returns:
        JSON string with risk analysis
    """
    # Implementation
    pass
```

### **Step 2: Access IBM Watsonx Orchestrate**

1. Go to: https://www.ibm.com/watsonx/orchestrate
2. Log in with your IBM Cloud credentials
3. Navigate to **"Agent Builder"**

### **Step 3: Upload Agents**

#### Upload Agent 1: Risk Scorer

1. In Agent Builder, click **"Create Agent"** or **"Import Agent"**
2. Select **"Upload YAML"**
3. Upload: `agents/risk-scorer-agent.yaml`
4. The system will parse:
   ```yaml
   kind: native
   spec_version: v1
   name: risk-scorer-agent
   llm:
     model_id: watsonx/meta-llama/llama-3-2-90b-vision-instruct
   tools:
     - analyze_article_risk
     - batch_analyze_articles
     - filter_articles_by_risk
     - get_risk_summary
   ```

5. Click **"Register Tools"**
6. Upload: `tools/risk_scorer_tool.py`
7. System will auto-detect the 4 `@tool` decorated functions
8. Click **"Deploy Agent"**

#### Upload Agent 2: Chart Generator

1. Click **"Create Agent"** → **"Upload YAML"**
2. Upload: `agents/chart-generator-agent.yaml`
3. Register tools from: `tools/chart_generator_tool.py` (5 tools)
4. Click **"Deploy Agent"**

#### Upload Agent 3: Feed Poster

1. Click **"Create Agent"** → **"Upload YAML"**
2. Upload: `agents/feed-poster-agent.yaml`
3. Register tools from: `tools/feed_poster_tool.py` (4 tools)
4. Click **"Deploy Agent"**

### **Step 4: Verify Tool Registration**

In Orchestrate UI, you should see:

```
✅ risk-scorer-agent (4 tools)
   ├── analyze_article_risk
   ├── batch_analyze_articles
   ├── filter_articles_by_risk
   └── get_risk_summary

✅ chart-generator-agent (5 tools)
   ├── create_line_chart
   ├── create_bar_chart
   ├── create_pie_chart
   ├── create_histogram
   └── auto_generate_chart

✅ feed-poster-agent (4 tools)
   ├── create_feed_post_from_article
   ├── generate_complete_feed
   ├── analyze_article_for_feed
   └── get_feed_statistics
```

---

## 🔗 Flow Connection in Orchestrate UI

### **Visual Flow Diagram**

```
┌─────────────────────────────────────────────────────────────────┐
│                     NEWS ANALYSIS PIPELINE                       │
└─────────────────────────────────────────────────────────────────┘

INPUT: News JSON Files
   │
   ├─ finance_news.json
   ├─ market_news.json
   ├─ industry_news.json
   └─ linkedin_news.json
   │
   ▼
┌──────────────────────────────────────┐
│  STEP 1: RISK SCORER AGENT           │
│  Tool: batch_analyze_articles        │
│  Input: All news JSON files          │
│  Output: risk_assessment_results.json│
└──────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────┐
│  STEP 2: CHART GENERATOR AGENT       │
│  Tool: auto_generate_chart           │
│  Input: risk_assessment_results.json │
│  Output: article{id}_{num}.png files │
└──────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────┐
│  STEP 3: FEED POSTER AGENT           │
│  Tool: generate_complete_feed        │
│  Input: risk_assessment_results.json │
│  Output: feed.json                   │
└──────────────────────────────────────┘
   │
   ▼
OUTPUT: Social Media Feed
   │
   └─ feed.json (ready for posting!)
```

### **Creating the Flow in Orchestrate UI**

#### **Step 1: Create New Flow**

1. In Orchestrate, go to **"Flows"** → **"Create Flow"**
2. Name: **"News Analysis Pipeline"**
3. Description: **"Automated news risk analysis with chart generation and social media feed creation"**

#### **Step 2: Add Input Node**

1. Drag **"Input"** node to canvas
2. Configure:
   - **Input Type**: File Upload (JSON)
   - **Accept Multiple**: Yes (for all 4 news sources)
   - **Parameter Name**: `news_files`

#### **Step 3: Add Risk Scorer Node**

1. Drag **"Agent Action"** to canvas
2. Select **"risk-scorer-agent"**
3. Choose tool: **"batch_analyze_articles"**
4. Configure:
   ```json
   {
     "news_files_json": "{{input.news_files}}",
     "company_knowledge_json": "{{file.company.json}}",
     "min_risk_threshold": 0.0
   }
   ```
5. Output variable: `risk_assessment`

#### **Step 4: Add Chart Generator Node**

1. Drag **"Agent Action"** to canvas
2. Select **"chart-generator-agent"**
3. Choose tool: **"auto_generate_chart"**
4. Configure:
   ```json
   {
     "articles_with_tables": "{{risk_assessment}}",
     "output_directory": "agents/charts"
   }
   ```
5. Output variable: `generated_charts`

#### **Step 5: Add Feed Poster Node**

1. Drag **"Agent Action"** to canvas
2. Select **"feed-poster-agent"**
3. Choose tool: **"generate_complete_feed"**
4. Configure:
   ```json
   {
     "assessment_file_path": "{{risk_assessment}}",
     "max_posts": 20,
     "min_risk_score": 0.3
   }
   ```
5. Output variable: `social_feed`

#### **Step 6: Add Output Node**

1. Drag **"Output"** node to canvas
2. Configure:
   ```json
   {
     "risk_assessment": "{{risk_assessment}}",
     "charts_created": "{{generated_charts}}",
     "social_feed": "{{social_feed}}"
   }
   ```

#### **Step 7: Connect Nodes**

Connect in sequence:
```
[Input] → [Risk Scorer] → [Chart Generator] → [Feed Poster] → [Output]
```

#### **Step 8: Save and Deploy Flow**

1. Click **"Save Flow"**
2. Click **"Deploy"**
3. Enable: **"Auto-run on new data"**

---

## 🧪 Testing the Flow

### **Test 1: Single Article Test**

1. In Orchestrate UI, go to **"Test Flow"**
2. Upload a test JSON:
   ```json
   [
     {
       "title": "Apple Reports Q4 Earnings Miss",
       "content": "Apple Inc. reported disappointing Q4 results...",
       "url": "https://example.com/article",
       "graphs_images": ["https://example.com/chart.png"],
       "relevant_tables": [
         {"Q1": 100, "Q2": 95, "Q3": 90, "Q4": 85}
       ]
     }
   ]
   ```
3. Click **"Run Flow"**
4. Verify outputs:
   - ✅ Risk assessment with score
   - ✅ Chart generated (article1_1.png)
   - ✅ Feed post with creative title

### **Test 2: Full Pipeline Test**

1. Upload all 4 news JSON files from `agents/finance_scrapper/data/`
2. Run flow
3. Expected output:
   - **Risk Assessment**: ~15-20 analyzed articles
   - **Charts**: ~5-10 visualization files
   - **Feed**: ~15 social media posts with creative titles

### **Test 3: Verify LLM Creativity**

Check feed.json output for:
- ✅ Creative emoji-enhanced titles (🚨, 📊, ✅)
- ✅ Engaging 280-char content
- ✅ Relevant hashtags (#Finance, #MarketAlert)
- ✅ Target audience recommendations
- ✅ Posting urgency (immediate, scheduled)

---

## 🎨 Flow Configuration Options

### **Option 1: High-Risk Alerts Only**

For urgent monitoring, configure:
```json
{
  "min_risk_threshold": 0.7,
  "max_posts": 5,
  "priority_filter": "high"
}
```

### **Option 2: Comprehensive Analysis**

For full coverage:
```json
{
  "min_risk_threshold": 0.0,
  "max_posts": 50,
  "include_charts": true
}
```

### **Option 3: Social Media Focus**

For content generation:
```json
{
  "min_risk_threshold": 0.3,
  "max_posts": 20,
  "creative_mode": "maximum"
}
```

---

## 🖥️ UI Dashboard (Next Phase)

After connecting the flow in Orchestrate, we'll build a custom UI to showcase:

### **Dashboard Features**

1. **Real-time News Monitoring**
   - Live feed of analyzed articles
   - Risk score visualization
   - Sentiment trends

2. **Risk Alerts Dashboard**
   - High-risk alerts (0.7+)
   - Risk category breakdown
   - Keyword cloud

3. **Chart Gallery**
   - All generated visualizations
   - Interactive filtering
   - Download options

4. **Social Media Feed Preview**
   - Feed post previews
   - Engagement predictions
   - Scheduling calendar

5. **Analytics Overview**
   - Total articles processed
   - Average risk score
   - Top risk categories
   - Charts generated
   - Posts created

### **Tech Stack for UI**

```
Frontend: React.js + Tailwind CSS
Backend: Flask/FastAPI (Python)
Database: MongoDB (store results)
Visualization: Chart.js / D3.js
Deployment: IBM Cloud / Vercel
```

### **UI Mockup Structure**

```
┌─────────────────────────────────────────────────────────┐
│  🎯 Smart News Orchestrator Dashboard                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 OVERVIEW                                            │
│  ┌──────────┬──────────┬──────────┬──────────┐         │
│  │ Articles │ High Risk│  Charts  │  Posts   │         │
│  │   22     │    7     │    8     │   15     │         │
│  └──────────┴──────────┴──────────┴──────────┘         │
│                                                          │
│  🚨 HIGH RISK ALERTS                                    │
│  ┌─────────────────────────────────────────────┐       │
│  │ 🔴 Apple Earnings Miss - Risk: 0.85         │       │
│  │ ⚠️  Regulatory Investigation - Risk: 0.78    │       │
│  │ 💥 Supply Chain Disruption - Risk: 0.72     │       │
│  └─────────────────────────────────────────────┘       │
│                                                          │
│  📈 RISK TRENDS                                         │
│  [Line chart showing risk over time]                    │
│                                                          │
│  📱 SOCIAL MEDIA FEED                                   │
│  ┌─────────────────────────────────────────────┐       │
│  │ 🚨 ALERT: Apple Stock Plunges 8%...        │       │
│  │ [Chart Preview] [Hashtags] [Schedule]       │       │
│  └─────────────────────────────────────────────┘       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Deployment Checklist

### **Pre-Deployment**
- [ ] IBM Watsonx Orchestrate account active
- [ ] API credentials configured
- [ ] All YAML files validated
- [ ] All tool files have `@tool` decorators
- [ ] Company knowledge base (`company.json`) updated

### **Agent Deployment**
- [ ] Risk Scorer Agent deployed
- [ ] Chart Generator Agent deployed
- [ ] Feed Poster Agent deployed
- [ ] All 13 tools registered (4+5+4)

### **Flow Configuration**
- [ ] Flow created in Orchestrate UI
- [ ] All nodes connected
- [ ] Input/output configured
- [ ] Test run successful

### **Validation**
- [ ] Single article test passed
- [ ] Full pipeline test passed
- [ ] LLM creativity verified
- [ ] Charts generated correctly
- [ ] Feed posts look professional

---

## 🔧 Troubleshooting

### **Issue: Tools not found**

**Solution**: Ensure `@tool` decorator is imported correctly:
```python
from ibm_watsonx_orchestrate.agent_builder.tools import tool
```

### **Issue: Agent deployment fails**

**Solution**: Validate YAML syntax:
```bash
python -c "import yaml; yaml.safe_load(open('agents/risk-scorer-agent.yaml'))"
```

### **Issue: Flow execution timeout**

**Solution**: Increase timeout in flow settings or reduce batch size:
```json
{
  "max_posts": 10,
  "timeout": 300
}
```

### **Issue: LLM not generating creative content**

**Solution**: Check temperature setting in YAML:
```yaml
llm:
  parameters:
    temperature: 0.9  # For feed poster (creativity)
    temperature: 0.7  # For risk scorer (accuracy)
```

---

## 📚 Additional Resources

- [IBM Watsonx Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/orchestrate)
- [Agent Builder Guide](https://www.ibm.com/docs/en/watsonx/orchestrate/agent-builder)
- [Tool Development Guide](https://www.ibm.com/docs/en/watsonx/orchestrate/tools)
- [Flow Designer Guide](https://www.ibm.com/docs/en/watsonx/orchestrate/flows)

---

## 🎯 Next Steps

1. ✅ **Deploy Agents** - Upload all 3 agents to Watsonx Orchestrate
2. ✅ **Connect Flow** - Create and test the complete pipeline
3. ⏭️ **Build UI Dashboard** - Create interactive frontend
4. ⏭️ **Add Automation** - Schedule automatic runs
5. ⏭️ **Production Deploy** - Scale for production use

---

**Ready to deploy? Follow this guide step-by-step and your News Analysis Pipeline will be live in IBM Watsonx Orchestrate!** 🚀
