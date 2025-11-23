# 📊 Data Extraction & Orchestration Guide

## Overview
This document explains **EXACTLY** how real data flows from `risk_assessment_results.json` through the Watsonx Orchestrate agents and into the React dashboard.

---

## 🔄 Complete Data Flow

```
[News Scrapers] → [Risk Scorer Agent] → [Chart Generator Agent] → [Feed Poster Agent] → [Dashboard UI]
      ↓                    ↓                        ↓                       ↓                ↓
  JSON files      risk_assessment_       article{N}_1.png          Feed titles         User sees
  (raw news)      results.json          article{N}_2.png          & hashtags        everything
```

---

## 📂 Data Source: `risk_assessment_results.json`

### File Location
```
hackathon-IBM/agents/risk_agent/risk_assessment_results.json
```

### JSON Structure
```json
{
  "detailed_results": [
    {
      "source": "www.moneycontrol.com",
      "title": "Oracle slump sends Larry Ellison sliding down billionaire ranks",
      "url": "https://www.moneycontrol.com/news/business/companies/",
      "published_time": "2025-11-22T17:35:54.485693",
      "content_text": "Full article text here...",
      "graphs_images": ["https://...image.png"],
      "risk_tags_detected": ["profit", "ban", "fine", "lawsuit"],
      "sentiment": "neutral",
      "competitor_mentions": ["Samsung Electronics"],
      "risk_analysis": {
        "risk_score": 0.8,                              // 0.0 - 1.0 scale
        "sentiment_score": 0.0,                         // -1.0 to 1.0
        "sentiment_label": "neutral",                   // positive/neutral/negative
        "risk_category": ["regulatory", "financial"],   // Categories detected
        "matched_keywords": ["profit", "ban", "fine"],  // Risk keywords found
        "reasoning": "The tone is neutral and involves regulatory..."
      },
      "_analysis_metadata": {
        "article_index": 1,        // 🔑 KEY: Used to find charts
        "source_file": "finance_news.json",
        "analyzed_at": "2025-11-22"
      }
    },
    // ... 21 more articles
  ]
}
```

### Total Data
- **22 articles** analyzed
- **4,270 lines** of JSON
- Each article has complete risk analysis metadata

---

## 🎯 Data Extraction in Dashboard.js

### 1. Loading the JSON File

```javascript
// Dashboard.js - useEffect hook
useEffect(() => {
  fetch('/agents/risk_agent/risk_assessment_results.json')  // Fetch from public folder
    .then(res => res.json())
    .then(jsonData => {
      const articles = jsonData.detailed_results || [];  // Extract array
      console.log(`📊 Loaded ${articles.length} articles`);
      setData(articles);  // Store in React state
    })
    .catch(error => {
      console.error('❌ Error loading JSON:', error);
    });
}, []);
```

**What happens:**
- React fetches the JSON file from `/public/agents/risk_agent/`
- Extracts the `detailed_results[]` array (22 articles)
- Stores in `data` state variable
- Dashboard re-renders with real data

---

### 2. Extracting URL (Source Link)

```javascript
// ArticleCard.js component
const ArticleCard = ({ article }) => {
  // DIRECT EXTRACTION from JSON
  const sourceUrl = article.url;  
  // Example: "https://www.moneycontrol.com/news/business/companies/"
  
  const sourceName = article.source;  
  // Example: "www.moneycontrol.com"
  
  return (
    <div className="article-card">
      <a href={sourceUrl} target="_blank">
        {article.title}
        <ExternalLink />
      </a>
      <span>{sourceName}</span>
    </div>
  );
};
```

**Field Mapping:**
- `article.url` → Full article URL ✅
- `article.source` → Website name ✅

---

### 3. Extracting Risk Data

```javascript
// ArticleCard.js - Risk analysis extraction
const ArticleCard = ({ article }) => {
  // EXTRACT nested risk_analysis object
  const riskScore = article.risk_analysis?.risk_score || 0;  
  // Example: 0.8 (80% risk)
  
  const sentimentScore = article.risk_analysis?.sentiment_score || 0;  
  // Example: 0.0 (neutral)
  
  const sentimentLabel = article.risk_analysis?.sentiment_label || 'Unknown';  
  // Example: "neutral"
  
  const riskCategories = article.risk_analysis?.risk_category || [];  
  // Example: ["regulatory", "financial"]
  
  const matchedKeywords = article.risk_analysis?.matched_keywords || [];  
  // Example: ["profit", "ban", "fine", "lawsuit"]
  
  const reasoning = article.risk_analysis?.reasoning || '';
  // Example: "The tone is neutral and involves regulatory..."
  
  // Display risk score as percentage
  const riskPercentage = (riskScore * 100).toFixed(1);  // "80.0%"
  
  return (
    <div className="risk-badge">
      <h3>{riskPercentage}% Risk</h3>
      <p>Sentiment: {sentimentLabel}</p>
      <div>
        {riskCategories.map(cat => (
          <span className="category-tag">#{cat}</span>
        ))}
      </div>
    </div>
  );
};
```

**Field Mapping:**
- `article.risk_analysis.risk_score` → 0.0-1.0 → Convert to % ✅
- `article.risk_analysis.sentiment_score` → -1.0 to 1.0 ✅
- `article.risk_analysis.sentiment_label` → "positive"/"neutral"/"negative" ✅
- `article.risk_analysis.risk_category[]` → Array of categories ✅
- `article.risk_analysis.matched_keywords[]` → Array of keywords ✅
- `article.risk_analysis.reasoning` → AI explanation text ✅

---

### 4. Extracting Charts (Generated by Chart Generator Agent)

```javascript
// ArticleDetailModal.js - Chart path construction
const ArticleDetailModal = ({ article }) => {
  // STEP 1: Extract article index from metadata
  const articleIndex = article._analysis_metadata?.article_index || 1;
  // Example: 1, 2, 3, etc.
  
  // STEP 2: Construct chart file paths using template
  const charts = [
    `/agents/charts/article${articleIndex}_1.png`,
    `/agents/charts/article${articleIndex}_2.png`
  ];
  // Example: ["/agents/charts/article1_1.png", "/agents/charts/article1_2.png"]
  
  return (
    <div className="charts-section">
      <h3>Charts Generated by Chart Generator Agent</h3>
      {charts.map((chartPath, idx) => (
        <img 
          src={chartPath} 
          alt={`Chart ${idx + 1} for article ${articleIndex}`}
          onError={(e) => {
            // Fallback if image doesn't exist
            e.target.style.display = 'none';
          }}
        />
      ))}
      <p>💡 Charts based on article_index: {articleIndex}</p>
    </div>
  );
};
```

**Chart Naming Convention:**
- Article 1: `article1_1.png`, `article1_2.png`
- Article 2: `article2_1.png`, `article2_2.png`
- Article N: `article{N}_1.png`, `article{N}_2.png`

**Files in `/agents/charts/`:**
```
article1_1.png  ← Risk chart for article 1
article1_2.png  ← Sentiment chart for article 1
article2_1.png  ← Risk chart for article 2
...
```

**Field Mapping:**
- `article._analysis_metadata.article_index` → 1, 2, 3... ✅
- Construct path: `/agents/charts/article{index}_{1|2}.png` ✅

---

### 5. Generating Feed Titles (Simulates Feed Poster Agent)

```javascript
// Dashboard.js - Feed title generation
const generateFeedTitle = (article, riskScore) => {
  // RULE 1: Select emoji based on risk level
  const emoji = riskScore >= 0.7 ? '🚨' :   // High risk (70%+)
                riskScore >= 0.4 ? '⚠️' :   // Medium risk (40-70%)
                '📊';                        // Low risk (<40%)
  
  // RULE 2: Select prefix text
  const prefix = riskScore >= 0.7 ? 'ALERT' :    // High risk
                 riskScore >= 0.4 ? 'UPDATE' :   // Medium risk
                 'INFO';                         // Low risk
  
  // RULE 3: Combine with article title
  return `${emoji} ${prefix}: ${article.title}`;
};

// Example Usage:
const article1 = { title: "Oracle slump...", risk_analysis: { risk_score: 0.8 } };
const feedTitle = generateFeedTitle(article1, 0.8);
// Result: "🚨 ALERT: Oracle slump sends Larry Ellison sliding down billionaire ranks"
```

**Feed Title Rules:**
| Risk Score | Emoji | Prefix | Example |
|-----------|-------|--------|---------|
| ≥ 0.7 (70%+) | 🚨 | ALERT | 🚨 ALERT: Oracle shares fall |
| 0.4 - 0.7 | ⚠️ | UPDATE | ⚠️ UPDATE: Market volatility rises |
| < 0.4 | 📊 | INFO | 📊 INFO: Quarterly earnings report |

**Hashtag Generation:**
```javascript
// Add hashtags from risk categories
const hashtags = article.risk_analysis.risk_category.map(cat => `#${cat}`);
// Example: ["#regulatory", "#financial"]

hashtags.push('#RiskAlert');
hashtags.push('#WatsonxOrchestrate');
// Final: ["#regulatory", "#financial", "#RiskAlert", "#WatsonxOrchestrate"]
```

---

## 🤖 Watsonx Orchestrate Agent Flow

### How Agents Call Each Other

```yaml
# orchestrator-agent.yaml
name: orchestrator-agent
description: Master coordinator that orchestrates all agents

tools:
  - name: risk_scorer
    type: orchestrate://risk_scorer_agent
    inputs:
      article_text: string
      url: string
      source: string
    outputs:
      risk_score: number
      sentiment_label: string
      risk_category: array
      matched_keywords: array
  
  - name: chart_generator
    type: orchestrate://chart_generator_agent
    inputs:
      risk_score: number
      categories: array
      article_index: number
    outputs:
      chart_paths: array
  
  - name: feed_poster
    type: orchestrate://feed_poster_agent
    inputs:
      title: string
      risk_score: number
      categories: array
    outputs:
      feed_title: string
      hashtags: array
      urgency: string
```

### Agent Calling Sequence

```
1. User triggers orchestrator with article data
   Input: { title, content, url, source }

2. Orchestrator calls Risk Scorer Agent
   orchestrate://risk_scorer_agent
   ↓
   Returns: { risk_score: 0.8, sentiment: "neutral", categories: [...] }

3. Orchestrator calls Chart Generator Agent
   orchestrate://chart_generator_agent
   Input: { risk_score: 0.8, categories: [...], article_index: 1 }
   ↓
   Generates: article1_1.png, article1_2.png
   Returns: { charts: ["/agents/charts/article1_1.png", ...] }

4. Orchestrator calls Feed Poster Agent
   orchestrate://feed_poster_agent
   Input: { title: "...", risk_score: 0.8, categories: [...] }
   ↓
   Returns: { 
     feed_title: "🚨 ALERT: ...", 
     hashtags: ["#regulatory", "#financial", "#RiskAlert"],
     urgency: "immediate"
   }

5. Orchestrator combines all results
   Returns complete analysis to dashboard
```

---

## 📊 Complete Data Extraction Example

### Input (from JSON):
```json
{
  "source": "www.moneycontrol.com",
  "title": "Oracle slump sends Larry Ellison sliding down billionaire ranks",
  "url": "https://www.moneycontrol.com/news/business/companies/",
  "content_text": "Oracle shares fell 6.7% on Tuesday...",
  "risk_analysis": {
    "risk_score": 0.8,
    "sentiment_score": 0.0,
    "sentiment_label": "neutral",
    "risk_category": ["regulatory", "financial"],
    "matched_keywords": ["profit", "ban", "fine", "lawsuit"]
  },
  "_analysis_metadata": {
    "article_index": 1
  }
}
```

### Extracted Data (in Dashboard):

```javascript
// 1. URL EXTRACTION
const url = article.url;
// → "https://www.moneycontrol.com/news/business/companies/"

// 2. RISK SCORE
const riskScore = article.risk_analysis.risk_score;
// → 0.8 → Display as "80.0%"

// 3. SENTIMENT
const sentiment = article.risk_analysis.sentiment_label;
// → "neutral"

// 4. CATEGORIES
const categories = article.risk_analysis.risk_category;
// → ["regulatory", "financial"]

// 5. KEYWORDS
const keywords = article.risk_analysis.matched_keywords;
// → ["profit", "ban", "fine", "lawsuit"]

// 6. CHARTS
const articleIndex = article._analysis_metadata.article_index;  // 1
const charts = [
  `/agents/charts/article${articleIndex}_1.png`,  // article1_1.png
  `/agents/charts/article${articleIndex}_2.png`   // article1_2.png
];

// 7. FEED TITLE (generated)
const feedTitle = `🚨 ALERT: ${article.title}`;
// → "🚨 ALERT: Oracle slump sends Larry Ellison sliding down billionaire ranks"

// 8. HASHTAGS (generated)
const hashtags = categories.map(c => `#${c}`).concat(['#RiskAlert']);
// → ["#regulatory", "#financial", "#RiskAlert"]
```

### Displayed in UI:

```
┌─────────────────────────────────────────────────────────┐
│ 🚨 ALERT: Oracle slump sends Larry Ellison...           │
├─────────────────────────────────────────────────────────┤
│ Risk Score: 80.0%  |  Sentiment: neutral                │
│                                                          │
│ Categories: #regulatory #financial                       │
│ Keywords: profit, ban, fine, lawsuit                     │
│                                                          │
│ 🔗 Source: https://www.moneycontrol.com/news/...        │
│                                                          │
│ [Chart 1: article1_1.png] [Chart 2: article1_2.png]     │
│                                                          │
│ Feed Preview:                                            │
│ 🚨 ALERT: Oracle slump sends Larry Ellison...           │
│ #regulatory #financial #RiskAlert #WatsonxOrchestrate   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 File Structure

```
hackathon-IBM/
├── agents/
│   ├── risk_agent/
│   │   └── risk_assessment_results.json  ← SOURCE DATA (22 articles)
│   ├── charts/
│   │   ├── article1_1.png  ← Generated charts
│   │   ├── article1_2.png
│   │   ├── article2_1.png
│   │   └── ...
│   └── orchestrator-agent.yaml  ← Agent calling config
│
├── dashboard/
│   ├── public/
│   │   └── agents/
│   │       ├── risk_agent/
│   │       │   └── risk_assessment_results.json  ← COPIED here for React
│   │       └── charts/
│   │           ├── article1_1.png  ← COPIED here
│   │           └── ...
│   └── src/
│       └── Dashboard.js  ← EXTRACTS and DISPLAYS data
│
└── DATA_EXTRACTION_GUIDE.md  ← This file
```

---

## ✅ Verification Checklist

- [x] **JSON file loaded**: Dashboard fetches `risk_assessment_results.json`
- [x] **22 articles extracted**: `jsonData.detailed_results[]` array
- [x] **URLs displayed**: `article.url` shown in modal
- [x] **Risk scores shown**: `article.risk_analysis.risk_score * 100`
- [x] **Sentiment extracted**: `article.risk_analysis.sentiment_label`
- [x] **Categories listed**: `article.risk_analysis.risk_category[]`
- [x] **Keywords shown**: `article.risk_analysis.matched_keywords[]`
- [x] **Charts loaded**: `/agents/charts/article{index}_1.png`
- [x] **Feed titles generated**: `🚨 ALERT: {title}` based on risk
- [x] **Hashtags created**: From categories + #RiskAlert

---

## 🚀 How to Run

1. **Start Dashboard:**
   ```bash
   cd dashboard
   npm start
   ```
   Opens at: `http://localhost:3000`

2. **Click any article** to see:
   - Full content
   - Source URL (extracted from `article.url`)
   - Risk score (from `article.risk_analysis.risk_score`)
   - Sentiment (from `article.risk_analysis.sentiment_label`)
   - Categories (from `article.risk_analysis.risk_category[]`)
   - Keywords (from `article.risk_analysis.matched_keywords[]`)
   - Charts (loaded from `/agents/charts/article{index}_1.png`)
   - Feed preview (generated title + hashtags)

3. **View Orchestration Flow**:
   - Click "How Watsonx Orchestrate Agents Work Together"
   - See agent-to-agent calling diagram
   - View data flow: Risk Scorer → Chart Generator → Feed Poster

---

## 🎯 Summary

**Question**: "How does actual info show on dashboard from risk_assessment.json?"

**Answer**:

1. **JSON Loading**: `fetch('/agents/risk_agent/risk_assessment_results.json')` loads all 22 articles
2. **Array Extraction**: `jsonData.detailed_results[]` extracts article array
3. **URL Extraction**: `article.url` → Direct link to news source
4. **Risk Extraction**: `article.risk_analysis.risk_score` → 0.8 → "80%"
5. **Sentiment Extraction**: `article.risk_analysis.sentiment_label` → "neutral"
6. **Category Extraction**: `article.risk_analysis.risk_category[]` → ["regulatory", "financial"]
7. **Keyword Extraction**: `article.risk_analysis.matched_keywords[]` → ["profit", "ban", "fine"]
8. **Chart Loading**: `article._analysis_metadata.article_index` → 1 → `/agents/charts/article1_1.png`
9. **Feed Generation**: `risk_score >= 0.7 → "🚨 ALERT: {title}"`
10. **Display**: All data shown in modal when clicking article card

**Orchestration**: Agents call each other via `orchestrate://` protocol defined in `orchestrator-agent.yaml`, passing data sequentially through the pipeline.

---

**🎉 All 22 articles are now live with real data extraction!**
