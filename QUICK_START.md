# 🚀 Quick Start Guide

## Dashboard is Ready! Here's how to run it:

### 1️⃣ Start the Dashboard
```bash
cd dashboard
npm start
```

This will:
- Open `http://localhost:3000` in your browser
- Load all 22 articles from `risk_assessment_results.json`
- Display charts from `/agents/charts/`

### 2️⃣ What You'll See

**Main Dashboard:**
- 📊 4 Stats Cards: Total articles, High/Medium risk counts, Average risk score
- 🔍 Category Filter: Filter by financial, regulatory, competitive, etc.
- 📈 2 Charts: Risk distribution by category, Sentiment analysis
- 🤖 Orchestration Flow: Shows how agents call each other
- 📰 22 Article Cards: All news articles with risk scores

**Click Any Article to See:**
- ✅ **Source URL** - Extracted from `article.url`
- ✅ **Risk Score** - From `article.risk_analysis.risk_score` (e.g., 80%)
- ✅ **Sentiment** - From `article.risk_analysis.sentiment_label` (positive/neutral/negative)
- ✅ **Categories** - From `article.risk_analysis.risk_category[]` (e.g., ["regulatory", "financial"])
- ✅ **Keywords** - From `article.risk_analysis.matched_keywords[]` (e.g., ["profit", "ban", "fine"])
- ✅ **Full Content** - Complete article text
- ✅ **Charts** - Auto-loaded from `/agents/charts/article{N}_1.png`, `article{N}_2.png`
- ✅ **Feed Preview** - Generated title with emoji (🚨 ALERT, ⚠️ UPDATE, 📊 INFO) based on risk
- ✅ **Hashtags** - Generated from categories (#regulatory #financial #RiskAlert)

### 3️⃣ Data Extraction Explained

**How it works:**
```javascript
// 1. Load JSON
fetch('/agents/risk_agent/risk_assessment_results.json')
  .then(res => res.json())
  .then(data => {
    const articles = data.detailed_results;  // 22 articles
  });

// 2. Extract URL
const url = article.url;  // "https://www.moneycontrol.com/..."

// 3. Extract Risk Data
const riskScore = article.risk_analysis.risk_score;  // 0.8 → 80%
const sentiment = article.risk_analysis.sentiment_label;  // "neutral"
const categories = article.risk_analysis.risk_category;  // ["regulatory", "financial"]
const keywords = article.risk_analysis.matched_keywords;  // ["profit", "ban", "fine"]

// 4. Build Chart Paths
const index = article._analysis_metadata.article_index;  // 1
const charts = [
  `/agents/charts/article${index}_1.png`,  // article1_1.png
  `/agents/charts/article${index}_2.png`   // article1_2.png
];

// 5. Generate Feed Title
const emoji = riskScore >= 0.7 ? '🚨' : '⚠️';
const feedTitle = `${emoji} ALERT: ${article.title}`;
```

### 4️⃣ Files Created

**Dashboard Files:**
```
dashboard/
├── package.json              ✅ React dependencies (installed)
├── public/
│   ├── index.html           ✅ HTML with Tailwind CDN
│   └── agents/
│       ├── risk_agent/
│       │   └── risk_assessment_results.json  ✅ 22 articles (COPIED)
│       └── charts/
│           ├── article1_1.png  ✅ Charts (COPIED)
│           └── ...
└── src/
    ├── index.js             ✅ React entry point
    ├── index.css            ✅ Custom animations
    └── Dashboard.js         ✅ Main component with data extraction
```

**Documentation:**
```
├── DATA_EXTRACTION_GUIDE.md     ✅ Complete extraction explanation
├── DASHBOARD_ENHANCEMENTS.md    ✅ Feature documentation
└── AGENT_CALLING_SETUP.md       ✅ Orchestration guide
```

**Agent Config:**
```
agents/
└── orchestrator-agent.yaml      ✅ Master agent for calling other agents
```

### 5️⃣ Watsonx Orchestrate Setup (Optional)

To enable agent-to-agent calling in production:

```bash
# Deploy orchestrator agent
orchestrate agents import -f agents/orchestrator-agent.yaml

# Verify deployment
orchestrate agents list

# Test agent calling
orchestrate agents run orchestrator-agent --input '{"article": {...}}'
```

See `AGENT_CALLING_SETUP.md` for full setup instructions.

---

## 🎯 Summary

### ✅ What's Working:
1. **Dashboard UI** - React app with modern design (gradient backgrounds, glass morphism, animations)
2. **Data Loading** - Fetches real data from `risk_assessment_results.json`
3. **URL Extraction** - Shows source URL from `article.url`
4. **Risk Analysis** - Displays risk score, sentiment, categories, keywords from `article.risk_analysis`
5. **Charts** - Loads from `/agents/charts/article{index}_1.png` using `article._analysis_metadata.article_index`
6. **Feed Generation** - Creates social media posts with emojis and hashtags based on risk level
7. **Orchestration Visualization** - Shows how Risk Scorer → Chart Generator → Feed Poster agents work together

### 🎨 UI Features:
- 📊 Interactive stats cards with color-coded risk levels
- 🔍 Category filtering (all, financial, regulatory, competitive, etc.)
- 📈 Visual charts for risk distribution and sentiment analysis
- 🤖 Expandable orchestration flow diagram
- 📰 Article cards with hover effects and animations
- 🔎 Modal detail view with all agent outputs
- 📱 Responsive design for mobile/tablet/desktop

### 🔄 Agent Orchestration:
- **Risk Scorer Agent** - Analyzes content, assigns risk score & categories
- **Chart Generator Agent** - Creates visualizations (article{N}_1.png, article{N}_2.png)
- **Feed Poster Agent** - Generates social posts with hashtags and urgency level
- **Orchestrator Agent** - Coordinates all agents via `orchestrate://` protocol

---

## 📚 Read More:
- `DATA_EXTRACTION_GUIDE.md` - Detailed extraction examples
- `DASHBOARD_ENHANCEMENTS.md` - All dashboard features
- `AGENT_CALLING_SETUP.md` - Watsonx Orchestrate setup

---

**🎉 Everything is ready! Run `npm start` in the dashboard folder to see it live!**
