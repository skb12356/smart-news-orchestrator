# IBM Watsonx Orchestrate Deployment Package

This package contains all files needed to deploy the News Analysis Pipeline to IBM Watsonx Orchestrate.

## 📦 Package Contents

### 1. Agent Configuration Files (YAML)
```
agents/
├── risk-scorer-agent.yaml          ✅ Risk assessment agent
├── chart-generator-agent.yaml      ✅ Chart generation agent
└── feed-poster-agent.yaml          ✅ Social media feed agent
```

### 2. Tool Implementation Files (Python)
```
tools/
├── risk_scorer_tool.py             ✅ 4 @tool functions
├── chart_generator_tool.py         ✅ 5 @tool functions
└── feed_poster_tool.py             ✅ 4 @tool functions
```

### 3. Supporting Engine Files (Python)
```
tools/
├── risk_scorer.py                  ✅ Risk analysis engine
├── chart_generator.py              ✅ Chart generation engine
└── feed_poster.py                  ✅ Feed creation engine
```

### 4. Knowledge Base
```
knowledge/
└── company.json                     ✅ Company profile (Apple Inc.)
```

### 5. Flow Configuration
```
orchestrate_flow_config.json         ✅ Pre-configured flow
```

### 6. Documentation
```
WATSONX_ORCHESTRATE_DEPLOYMENT.md    ✅ Complete deployment guide
README.md                            ✅ Project overview
```

### 7. Verification Tools
```
verify_tools.py                      ✅ Tool verification script
flow_diagram.py                      ✅ Visual flow diagram
```

---

## 🚀 Quick Deployment Steps

### Step 1: Verify Tools
```bash
python verify_tools.py
```
Expected output: **13 tools detected** (4 + 5 + 4)

### Step 2: View Flow Diagram
```bash
python flow_diagram.py
```
Shows complete visual flow of the pipeline

### Step 3: Access IBM Watsonx Orchestrate
- URL: https://www.ibm.com/watsonx/orchestrate
- Login with IBM Cloud credentials
- Navigate to **Agent Builder**

### Step 4: Upload Agents (One by One)

#### Agent 1: Risk Scorer
1. **Create Agent** → **Upload YAML**
2. Upload: `agents/risk-scorer-agent.yaml`
3. **Register Tools** → Upload: `tools/risk_scorer_tool.py`
4. Upload supporting file: `tools/risk_scorer.py`
5. **Deploy Agent**

#### Agent 2: Chart Generator
1. **Create Agent** → **Upload YAML**
2. Upload: `agents/chart-generator-agent.yaml`
3. **Register Tools** → Upload: `tools/chart_generator_tool.py`
4. Upload supporting file: `tools/chart_generator.py`
5. **Deploy Agent**

#### Agent 3: Feed Poster
1. **Create Agent** → **Upload YAML**
2. Upload: `agents/feed-poster-agent.yaml`
3. **Register Tools** → Upload: `tools/feed_poster_tool.py`
4. Upload supporting file: `tools/feed_poster.py`
5. **Deploy Agent**

### Step 5: Create Flow

#### Option A: Import Pre-configured Flow
1. **Flows** → **Import Flow**
2. Upload: `orchestrate_flow_config.json`
3. Review and adjust if needed
4. **Deploy Flow**

#### Option B: Manual Flow Creation
1. **Flows** → **Create New Flow**
2. Name: "News Analysis Pipeline"
3. Add nodes in sequence:
   - Input → Risk Scorer → Filter → Chart Generator & Feed Poster → Output
4. Connect nodes following `orchestrate_flow_config.json`
5. **Deploy Flow**

### Step 6: Test the Flow
1. **Test Flow** → Upload sample JSON
2. Verify all agents execute correctly
3. Check outputs:
   - ✅ Risk assessment results
   - ✅ Generated charts
   - ✅ Social media feed

---

## 📁 File Upload Checklist

### For Risk Scorer Agent:
- [ ] `agents/risk-scorer-agent.yaml` (Agent config)
- [ ] `tools/risk_scorer_tool.py` (Tool decorators)
- [ ] `tools/risk_scorer.py` (Core engine)
- [ ] `knowledge/company.json` (Knowledge base)

### For Chart Generator Agent:
- [ ] `agents/chart-generator-agent.yaml` (Agent config)
- [ ] `tools/chart_generator_tool.py` (Tool decorators)
- [ ] `tools/chart_generator.py` (Core engine)

### For Feed Poster Agent:
- [ ] `agents/feed-poster-agent.yaml` (Agent config)
- [ ] `tools/feed_poster_tool.py` (Tool decorators)
- [ ] `tools/feed_poster.py` (Core engine)

### For Flow:
- [ ] `orchestrate_flow_config.json` (Flow configuration)

---

## 🔧 Configuration Requirements

### IBM Cloud Setup
- Active IBM Cloud account
- Watsonx Orchestrate instance provisioned
- Access to Watsonx AI (for LLM)
- API credentials configured

### LLM Model Access
- Model: `watsonx/meta-llama/llama-3-2-90b-vision-instruct`
- Ensure model is available in your region
- Configure API access tokens

### Storage
- Cloud Object Storage (for charts and outputs)
- Or configure local storage paths

---

## 🎯 Expected Tool Count

After deployment, verify in Orchestrate UI:

```
✅ risk-scorer-agent
   ├── analyze_article_risk
   ├── batch_analyze_articles
   ├── filter_articles_by_risk
   └── get_risk_summary
   Total: 4 tools

✅ chart-generator-agent
   ├── create_line_chart
   ├── create_bar_chart
   ├── create_pie_chart
   ├── create_histogram
   └── auto_generate_chart
   Total: 5 tools

✅ feed-poster-agent
   ├── create_feed_post_from_article
   ├── generate_complete_feed
   ├── analyze_article_for_feed
   └── get_feed_statistics
   Total: 4 tools

TOTAL: 13 TOOLS
```

---

## 📊 Test Data

Use sample data from:
```
agents/finance_scrapper/data/
├── finance_news.json
├── market_news.json
├── industry_news.json
└── linkedin_news.json
```

---

## 🐛 Troubleshooting

### Tools not registering
- **Issue**: @tool decorator not recognized
- **Solution**: Ensure correct import:
  ```python
  from ibm_watsonx_orchestrate.agent_builder.tools import tool
  ```

### Agent deployment fails
- **Issue**: YAML syntax error
- **Solution**: Validate with:
  ```bash
  python -c "import yaml; yaml.safe_load(open('agents/risk-scorer-agent.yaml'))"
  ```

### LLM model not found
- **Issue**: Model not available in region
- **Solution**: Check model availability or switch to available model in YAML

### Flow execution timeout
- **Issue**: Pipeline takes too long
- **Solution**: Increase timeout in flow settings:
  ```json
  "settings": {
    "timeout": 600
  }
  ```

---

## 📚 Additional Resources

- [WATSONX_ORCHESTRATE_DEPLOYMENT.md](../WATSONX_ORCHESTRATE_DEPLOYMENT.md) - Complete deployment guide
- [README.md](../README.md) - Project overview
- [IBM Watsonx Orchestrate Docs](https://www.ibm.com/docs/en/watsonx/orchestrate)

---

## ✅ Deployment Verification

After deployment, test with this sequence:

1. **Upload test data** (sample news JSON)
2. **Run flow** and verify:
   - ✅ Risk scores calculated
   - ✅ Charts generated
   - ✅ Feed posts created
3. **Check outputs**:
   - ✅ risk_assessment_results.json
   - ✅ agents/charts/*.png
   - ✅ agents/feeds/feed.json
4. **Verify LLM creativity**:
   - ✅ Emoji-enhanced titles (🚨, 📊, ✅)
   - ✅ Engaging content
   - ✅ Strategic hashtags

---

## 🎉 Success Criteria

Your deployment is successful when:

- ✅ All 3 agents deployed
- ✅ All 13 tools registered
- ✅ Flow created and connected
- ✅ Test run completes successfully
- ✅ Outputs match expected format
- ✅ LLM generates creative content

---

**Ready to deploy? Follow this guide and you'll have a fully automated news analysis pipeline running in IBM Watsonx Orchestrate!** 🚀
