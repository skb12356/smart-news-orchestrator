# Quick Start Guide - IBM Watsonx Orchestrate

⚡ **FASTEST WAY TO DEPLOY YOUR NEWS ANALYSIS PIPELINE**

## 🎯 What You'll Deploy

**3 Intelligent Agents** working together:
1. 🎯 **Risk Scorer** - Analyzes news articles, assigns risk scores
2. 📊 **Chart Generator** - Creates professional visualizations
3. 📱 **Feed Poster** - Generates creative social media posts

**Total: 13 AI-powered tools** ready to use!

---

## ✅ Pre-Deployment Checklist (2 minutes)

Run this command to verify everything is ready:
```bash
python verify_tools.py
```

Expected output:
```
✅ risk_scorer_tool.py: 4 tools found
✅ chart_generator_tool.py: 5 tools found  
✅ feed_poster_tool.py: 4 tools found
🎉 Perfect! All 13 tools detected and ready!
```

View the flow diagram:
```bash
python flow_diagram.py
```

---

## 🚀 5-Step Deployment (15 minutes)

### Step 1: Login to Watsonx Orchestrate (2 min)
```
1. Go to: https://www.ibm.com/watsonx/orchestrate
2. Login with IBM Cloud credentials
3. Click: "Agent Builder"
```

### Step 2: Deploy Risk Scorer Agent (4 min)
```
1. Click: "Create Agent" → "Upload YAML"
2. Upload: agents/risk-scorer-agent.yaml
3. Click: "Register Tools"
4. Upload: tools/risk_scorer_tool.py
5. Upload: tools/risk_scorer.py (supporting file)
6. Click: "Deploy Agent"
```

✅ **Verify**: You should see **4 tools** registered

### Step 3: Deploy Chart Generator Agent (4 min)
```
1. Click: "Create Agent" → "Upload YAML"
2. Upload: agents/chart-generator-agent.yaml
3. Click: "Register Tools"
4. Upload: tools/chart_generator_tool.py
5. Upload: tools/chart_generator.py (supporting file)
6. Click: "Deploy Agent"
```

✅ **Verify**: You should see **5 tools** registered

### Step 4: Deploy Feed Poster Agent (4 min)
```
1. Click: "Create Agent" → "Upload YAML"
2. Upload: agents/feed-poster-agent.yaml
3. Click: "Register Tools"
4. Upload: tools/feed_poster_tool.py
5. Upload: tools/feed_poster.py (supporting file)
6. Click: "Deploy Agent"
```

✅ **Verify**: You should see **4 tools** registered

### Step 5: Create the Flow (1 min)
```
1. Click: "Flows" → "Import Flow"
2. Upload: orchestrate_flow_config.json
3. Review the flow diagram
4. Click: "Deploy Flow"
```

---

## 🧪 Test Your Pipeline (5 minutes)

### Quick Test
```
1. In Orchestrate UI: Click "Test Flow"
2. Upload: agents/finance_scrapper/data/finance_news.json
3. Click: "Run"
4. Wait ~30 seconds
```

### Expected Results ✅
```
✅ Risk Assessment: Articles analyzed with risk scores
✅ Charts Generated: article1_1.png, article2_1.png, etc.
✅ Social Feed Created: 15 posts with creative titles

Example Post:
🚨 ALERT: Apple Earnings Miss - Stock Plunges 8%!
Content: "Apple's Q4 revenue fell short by $2B..."
Hashtags: #Apple #TechStocks #EarningsMiss
```

---

## 📋 Files You Need (All Ready!)

### Agent Configs (YAML)
- ✅ `agents/risk-scorer-agent.yaml`
- ✅ `agents/chart-generator-agent.yaml`
- ✅ `agents/feed-poster-agent.yaml`

### Tool Files (Python with @tool decorators)
- ✅ `tools/risk_scorer_tool.py` (4 tools)
- ✅ `tools/chart_generator_tool.py` (5 tools)
- ✅ `tools/feed_poster_tool.py` (4 tools)

### Engine Files (Core logic)
- ✅ `tools/risk_scorer.py`
- ✅ `tools/chart_generator.py`
- ✅ `tools/feed_poster.py`

### Flow Config
- ✅ `orchestrate_flow_config.json`

### Knowledge Base
- ✅ `knowledge/company.json`

---

## 🔗 Flow Connection (Auto-configured)

The flow is already configured in `orchestrate_flow_config.json`:

```
Input (News JSON)
    ↓
Risk Scorer Agent (analyze & score)
    ↓
Filter (min_risk: 0.3)
    ↓
    ├─→ Chart Generator (create visualizations)
    └─→ Feed Poster (generate posts)
    ↓
Output (Complete results)
```

---

## 💡 Usage Examples

### Scenario 1: Daily News Monitoring
```json
{
  "min_risk_threshold": 0.5,
  "max_posts": 10,
  "auto_run": true,
  "schedule": "daily at 9:00 AM"
}
```

### Scenario 2: High-Risk Alerts Only
```json
{
  "min_risk_threshold": 0.7,
  "max_posts": 5,
  "notification": "immediate"
}
```

### Scenario 3: Full Analysis
```json
{
  "min_risk_threshold": 0.0,
  "max_posts": 50,
  "include_charts": true,
  "include_analytics": true
}
```

---

## 🐛 Common Issues & Fixes

### Issue: "Tools not found"
**Fix**: Make sure you uploaded BOTH:
- Tool file (e.g., `risk_scorer_tool.py`)
- Engine file (e.g., `risk_scorer.py`)

### Issue: "Agent deployment failed"
**Fix**: Check YAML syntax:
```bash
python -c "import yaml; print(yaml.safe_load(open('agents/risk-scorer-agent.yaml')))"
```

### Issue: "LLM model not available"
**Fix**: Verify model access in your IBM Cloud region

### Issue: "Flow timeout"
**Fix**: Increase timeout in flow settings (default: 600s)

---

## 📊 What Happens After Deployment

### Automatic Processing:
```
1. News files uploaded → 22 articles
2. Risk Scorer analyzes → 15 high-risk found
3. Chart Generator creates → 8 visualizations
4. Feed Poster generates → 15 social posts
5. Output delivered → JSON + PNG files
```

### Example Output Structure:
```
risk_assessment_results.json    (15 analyzed articles)
agents/charts/
  ├── article1_1.png
  ├── article1_2.png
  ├── article2_1.png
  └── ...
agents/feeds/
  └── feed.json                 (15 social media posts)
```

---

## 🎨 Next Phase: UI Dashboard

After Orchestrate deployment, we'll build a dashboard with:

- 📊 Real-time risk monitoring
- 🚨 Alert notifications
- 📈 Trend visualization
- 📱 Social media preview
- 📉 Analytics reports

**Tech Stack**: React.js + Tailwind CSS + IBM Cloud

---

## ✅ Success Checklist

After deployment, verify:

- [ ] All 3 agents deployed in Orchestrate
- [ ] All 13 tools registered and active
- [ ] Flow created and connected
- [ ] Test run completed successfully
- [ ] Risk scores generated (0.0-1.0)
- [ ] Charts created (article{id}_{num}.png)
- [ ] Feed posts have creative titles with emojis
- [ ] Hashtags and metadata included

---

## 📞 Need Help?

1. **Detailed Guide**: See `WATSONX_ORCHESTRATE_DEPLOYMENT.md`
2. **Flow Diagram**: Run `python flow_diagram.py`
3. **Tool Verification**: Run `python verify_tools.py`
4. **Project Overview**: See `README.md`

---

## 🎉 You're Ready!

Everything is prepared and ready to deploy. Follow the 5 steps above and you'll have a fully automated, AI-powered news analysis pipeline running in **15 minutes**!

**Let's deploy! 🚀**
