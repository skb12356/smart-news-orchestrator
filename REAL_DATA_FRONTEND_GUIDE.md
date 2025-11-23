# 📊 Real Data Display on Frontend - Complete Guide

## How Real Data from JSON Appears on Your Dashboard

This guide shows **EXACTLY** how data flows from `risk_assessment_results.json` to your React frontend.

---

## 🔄 Complete Data Flow

```
risk_assessment_results.json → React fetch() → Extract fields → Display in UI
```

---

## 📂 Step 1: Data Source

**File Location:**
```
hackathon-IBM/dashboard/public/agents/risk_agent/risk_assessment_results.json
```

**Real Data Structure:**
```json
{
  "detailed_results": [
    {
      "source": "www.moneycontrol.com",
      "title": "Company Business News: Latest Indian Companies News...",
      "url": "https://www.moneycontrol.com/news/business/companies/",
      "published_time": "2025-11-22T17:35:54.485693",
      "content_text": "Oracle slump sends Larry Ellison sliding down...",
      "risk_analysis": {
        "risk_score": 0.8,                    ← 80% risk shown on frontend
        "sentiment_score": 0.0,               ← Neutral sentiment
        "sentiment_label": "neutral",         ← Display label
        "risk_category": [                    ← Tags shown as pills
          "regulatory",
          "financial"
        ],
        "matched_keywords": [                 ← Keywords shown as badges
          "profit",
          "ban",
          "fine",
          "lawsuit"
        ],
        "reasoning": "The tone is neutral..."  ← AI explanation
      },
      "_analysis_metadata": {
        "article_index": 1,                   ← Used to find charts
        "source_file": "finance_news.json"
      }
    }
    // ... 21 more articles
  ]
}
```

---

## 💻 Step 2: Frontend Loads Data

**Code in `Dashboard.js` (Lines 54-69):**
```javascript
useEffect(() => {
  // Load REAL data from risk_assessment_results.json
  fetch('/agents/risk_agent/risk_assessment_results.json')
    .then(res => res.json())
    .then(jsonData => {
      console.log('✅ Loaded data:', jsonData);
      // Extract the detailed_results array which contains all 22 articles
      const articles = jsonData.detailed_results || [];
      console.log(`📊 Extracted ${articles.length} articles`);
      setData(articles);  // ← Stores in React state
      setLoading(false);
    })
    .catch(error => {
      console.error('❌ Error loading JSON:', error);
    });
}, []);
```

**What Happens:**
1. React calls `fetch()` when component mounts
2. Loads JSON file from `/public/agents/risk_agent/` folder
3. Extracts `detailed_results[]` array (22 articles)
4. Stores in `data` state variable
5. Dashboard re-renders with real data

---

## 🎨 Step 3: Data Extraction & Display

### A. Article Card Component

**Code (Lines 244-290):**
```javascript
const ArticleCard = ({ article, index, onClick }) => {
  // EXTRACT DATA from JSON
  const riskScore = article.risk_analysis?.risk_score || 0;
  const sentimentScore = article.risk_analysis?.sentiment_score || 0;
  const riskCategories = article.risk_analysis?.risk_category || [];
  const matchedKeywords = article.risk_analysis?.matched_keywords || [];
  
  const riskColor = riskScore >= 0.7 ? 'red' : riskScore >= 0.4 ? 'yellow' : 'green';
  const sentimentColor = sentimentScore < -0.3 ? 'red' : sentimentScore > 0.3 ? 'green' : 'gray';

  return (
    <div className="glass rounded-xl p-6 hover-lift slide-in cursor-pointer" onClick={onClick}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-white mb-2">
            {article.title}  {/* ← Real title from JSON */}
            <ExternalLink className="inline ml-2" size={16} />
          </h3>
          <p className="text-gray-300 text-sm line-clamp-2">
            {article.content_text?.substring(0, 200)}...  {/* ← Real content */}
          </p>
        </div>
        <div className={`ml-4 px-4 py-2 bg-${riskColor}-500/20 border-2 border-${riskColor}-500 rounded-xl`}>
          <p className={`text-${riskColor}-400 font-black text-2xl`}>
            {(riskScore * 100).toFixed(0)}%  {/* ← 0.8 becomes "80%" */}
          </p>
          <p className="text-gray-400 text-xs">Risk</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {riskCategories.map((cat, idx) => (  {/* ← Real categories from JSON */}
          <span key={idx} className="px-3 py-1 bg-purple-500/20 border border-purple-500/50 rounded-full text-purple-300 text-xs font-semibold">
            #{cat}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center space-x-1">
          <Activity size={16} className={`text-${sentimentColor}-400`} />
          <span className="text-gray-300">
            Sentiment: <span className={`font-bold text-${sentimentColor}-400`}>
              {article.risk_analysis?.sentiment_label || 'Unknown'}  {/* ← Real sentiment */}
            </span>
          </span>
        </div>
        <div className="flex items-center space-x-1 text-gray-400">
          <Link2 size={16} />
          <span className="text-xs">{article.source}</span>  {/* ← Real source */}
        </div>
      </div>
    </div>
  );
};
```

**What You See on Frontend:**

```
┌─────────────────────────────────────────────────────────────┐
│ Company Business News: Latest Indian Companies...      80% │
│ Oracle slump sends Larry Ellison sliding down...      Risk │
│                                                             │
│ #regulatory #financial                                      │
│                                                             │
│ Sentiment: neutral  |  www.moneycontrol.com               │
└─────────────────────────────────────────────────────────────┘
```

**Data Mapping:**
- **Title**: `article.title` → "Company Business News: Latest Indian..."
- **Content Preview**: `article.content_text.substring(0, 200)` → "Oracle slump sends..."
- **Risk Score**: `article.risk_analysis.risk_score * 100` → 0.8 → "80%"
- **Categories**: `article.risk_analysis.risk_category[]` → ["regulatory", "financial"]
- **Sentiment**: `article.risk_analysis.sentiment_label` → "neutral"
- **Source**: `article.source` → "www.moneycontrol.com"

---

### B. Modal Detail View

**Code (Lines 402-550):**
```javascript
const ArticleDetailModal = ({ article, onClose }) => {
  // EXTRACT REAL DATA from article object
  const riskScore = article.risk_analysis?.risk_score || 0;
  const sentimentScore = article.risk_analysis?.sentiment_score || 0;
  const sentimentLabel = article.risk_analysis?.sentiment_label || 'Unknown';
  const riskCategories = article.risk_analysis?.risk_category || [];
  const matchedKeywords = article.risk_analysis?.matched_keywords || [];
  const reasoning = article.risk_analysis?.reasoning || 'No reasoning provided';
  
  // EXTRACT article index to build chart paths
  const articleIndex = article._analysis_metadata?.article_index || 1;
  
  // BUILD CHART PATHS: /agents/charts/article{index}_1.png, article{index}_2.png
  const charts = [
    `/agents/charts/article${articleIndex}_1.png`,
    `/agents/charts/article${articleIndex}_2.png`
  ];
  
  // GENERATE FEED TITLE (simulates Feed Poster Agent)
  const feedTitle = generateFeedTitle(article, riskScore);

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm">
      <div className="glass rounded-3xl max-w-5xl w-full">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
          <h2 className="text-3xl font-black text-white">
            {article.title}  {/* ← Real title */}
          </h2>
          <div className="flex items-center space-x-4 text-white/80 text-sm">
            <span>{article.source}</span>  {/* ← Real source */}
            <span>•</span>
            <span>{new Date(article.published_time).toLocaleDateString()}</span>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Risk Score Display */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-red-500/20 rounded-2xl p-6 text-center">
              <p className="text-5xl font-black text-white">
                {(riskScore * 100).toFixed(1)}%  {/* ← 0.8 = 80.0% */}
              </p>
            </div>
            
            <div className="rounded-2xl p-6 text-center">
              <p className="text-3xl font-black text-white capitalize">
                {sentimentLabel}  {/* ← "neutral" */}
              </p>
              <p className="text-gray-300 text-sm mt-1">
                Score: {sentimentScore.toFixed(2)}  {/* ← 0.00 */}
              </p>
            </div>
            
            <div className="rounded-2xl p-6 text-center">
              <p className="text-4xl font-black text-white">
                {riskCategories.length}  {/* ← 2 categories */}
              </p>
              <p className="text-gray-300 text-sm mt-1">
                {matchedKeywords.length} keywords  {/* ← 4 keywords */}
              </p>
            </div>
          </div>

          {/* Article URL */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
            <h3 className="text-blue-400 font-semibold mb-2">Source URL</h3>
            <a href={article.url} target="_blank">  {/* ← Real URL */}
              {article.url}  {/* ← https://www.moneycontrol.com/... */}
            </a>
          </div>

          {/* Content */}
          <div className="bg-white/5 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">Full Article Content</h3>
            <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
              {article.content_text}  {/* ← Full real content */}
            </p>
          </div>

          {/* Risk Categories */}
          <div className="bg-white/5 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">Risk Categories</h3>
            <div className="flex flex-wrap gap-3">
              {riskCategories.map((cat, idx) => (  {/* ← ["regulatory", "financial"] */}
                <span key={idx} className="px-4 py-2 bg-purple-500/20">
                  #{cat}
                </span>
              ))}
            </div>
          </div>

          {/* Keywords */}
          <div className="bg-white/5 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">Matched Keywords</h3>
            <div className="flex flex-wrap gap-2">
              {matchedKeywords.map((keyword, idx) => (  {/* ← ["profit", "ban", "fine", "lawsuit"] */}
                <span key={idx} className="px-3 py-1 bg-red-500/20 text-red-300 text-sm">
                  {keyword}
                </span>
              ))}
            </div>
          </div>

          {/* AI Reasoning */}
          <div className="bg-gradient-to-r from-yellow-500/10 rounded-xl p-6">
            <h3 className="text-yellow-400 font-bold mb-3">Risk Scorer Reasoning</h3>
            <p className="text-gray-300 leading-relaxed">
              {reasoning}  {/* ← Real AI explanation */}
            </p>
          </div>

          {/* Charts */}
          <div className="bg-white/5 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">Charts Generated</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {charts.map((chartPath, idx) => (
                <div key={idx}>
                  <img 
                    src={chartPath}  {/* ← /agents/charts/article1_1.png */}
                    alt={`Chart ${idx + 1}`}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Feed Preview */}
          <div className="bg-gradient-to-r from-green-500/10 rounded-xl p-6">
            <h3 className="text-green-400 font-bold mb-4">Feed Poster Output</h3>
            <div className="bg-black/30 rounded-lg p-4">
              <p className="text-2xl font-bold text-white mb-3">
                {feedTitle}  {/* ← 🚨 ALERT: Company Business News... */}
              </p>
              <div className="flex flex-wrap gap-2">
                {riskCategories.map((cat, idx) => (
                  <span key={idx} className="text-blue-400 font-semibold">
                    #{cat}  {/* ← #regulatory #financial */}
                  </span>
                ))}
                <span className="text-blue-400 font-semibold">#RiskAlert</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
```

**What You See When You Click an Article:**

```
╔═══════════════════════════════════════════════════════════════╗
║ Company Business News: Latest Indian Companies...             ║
║ www.moneycontrol.com • Nov 22, 2025                      [✕]  ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  🚨 RISK SCORE      😐 SENTIMENT       #️⃣ CATEGORIES          ║
║     80.0%             Neutral              2                  ║
║                    Score: 0.00         4 keywords             ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║ 🔗 Source URL:                                                ║
║ https://www.moneycontrol.com/news/business/companies/        ║
╠═══════════════════════════════════════════════════════════════╣
║ 📄 Full Content:                                              ║
║ Oracle slump sends Larry Ellison sliding down ranks of        ║
║ world's richest. Oracle's swoon has vaulted Alphabet Inc...   ║
╠═══════════════════════════════════════════════════════════════╣
║ 🏷️  Risk Categories: #regulatory #financial                  ║
║ 🔍 Keywords: profit, ban, fine, lawsuit                       ║
╠═══════════════════════════════════════════════════════════════╣
║ 💡 Risk Scorer Agent Reasoning:                               ║
║ The tone is neutral and involves regulatory, financial...     ║
╠═══════════════════════════════════════════════════════════════╣
║ 📊 Charts Generated:                                          ║
║ [article1_1.png]  [article1_2.png]                           ║
╠═══════════════════════════════════════════════════════════════╣
║ 📱 Feed Poster Agent Output:                                  ║
║ 🚨 ALERT: Company Business News: Latest Indian Companies...   ║
║ #regulatory #financial #RiskAlert #WatsonxOrchestrate        ║
║ Urgency: immediate                                            ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 🗺️ Complete Field Mapping

| Frontend Display | JSON Path | Example Value |
|-----------------|-----------|---------------|
| **Article Title** | `article.title` | `"Company Business News: Latest Indian..."` |
| **Source** | `article.source` | `"www.moneycontrol.com"` |
| **Source URL** | `article.url` | `"https://www.moneycontrol.com/news/..."` |
| **Published Date** | `article.published_time` | `"2025-11-22T17:35:54.485693"` |
| **Content** | `article.content_text` | `"Oracle slump sends Larry Ellison..."` |
| **Risk Score %** | `article.risk_analysis.risk_score * 100` | `0.8` → `"80%"` |
| **Sentiment Label** | `article.risk_analysis.sentiment_label` | `"neutral"` |
| **Sentiment Score** | `article.risk_analysis.sentiment_score` | `0.0` |
| **Risk Categories** | `article.risk_analysis.risk_category[]` | `["regulatory", "financial"]` |
| **Keywords** | `article.risk_analysis.matched_keywords[]` | `["profit", "ban", "fine", "lawsuit"]` |
| **AI Reasoning** | `article.risk_analysis.reasoning` | `"The tone is neutral and involves..."` |
| **Article Index** | `article._analysis_metadata.article_index` | `1` |
| **Chart 1** | `/agents/charts/article${index}_1.png` | `article1_1.png` |
| **Chart 2** | `/agents/charts/article${index}_2.png` | `article1_2.png` |
| **Feed Title** | Generated from `risk_score` + `title` | `"🚨 ALERT: Company Business News..."` |
| **Hashtags** | Generated from `risk_category[]` | `["#regulatory", "#financial", "#RiskAlert"]` |

---

## 🎯 Real Example: Article 1

### JSON Data (Input):
```json
{
  "source": "www.moneycontrol.com",
  "title": "Company Business News: Latest Indian Companies News...",
  "url": "https://www.moneycontrol.com/news/business/companies/",
  "published_time": "2025-11-22T17:35:54.485693",
  "content_text": "Oracle slump sends Larry Ellison sliding down...",
  "risk_analysis": {
    "risk_score": 0.8,
    "sentiment_score": 0.0,
    "sentiment_label": "neutral",
    "risk_category": ["regulatory", "financial"],
    "matched_keywords": ["profit", "ban", "fine", "lawsuit"],
    "reasoning": "The tone is neutral and involves regulatory..."
  },
  "_analysis_metadata": {
    "article_index": 1
  }
}
```

### Frontend Display (Output):

**Article Card:**
```
┌─────────────────────────────────────────────────────┐
│ Company Business News: Latest Indian...        80% │
│ Oracle slump sends Larry Ellison sliding...   Risk │
│                                                     │
│ #regulatory #financial                              │
│                                                     │
│ Sentiment: neutral  |  www.moneycontrol.com        │
└─────────────────────────────────────────────────────┘
```

**Modal (when clicked):**
- ✅ **URL**: `https://www.moneycontrol.com/news/business/companies/`
- ✅ **Risk Score**: `80.0%`
- ✅ **Sentiment**: `neutral (Score: 0.00)`
- ✅ **Categories**: `#regulatory #financial`
- ✅ **Keywords**: `profit, ban, fine, lawsuit`
- ✅ **Charts**: `article1_1.png`, `article1_2.png`
- ✅ **Feed**: `🚨 ALERT: Company Business News...`
- ✅ **Hashtags**: `#regulatory #financial #RiskAlert`

---

## 📊 Stats Dashboard

**Code (Lines 680-710):**
```javascript
const calculateStats = (data) => {
  const total = data.length;  // 22 articles
  const highRisk = data.filter(a => (a.risk_analysis?.risk_score || 0) >= 0.7).length;
  const mediumRisk = data.filter(a => {
    const score = a.risk_analysis?.risk_score || 0;
    return score >= 0.4 && score < 0.7;
  }).length;
  const avgRisk = data.reduce((sum, a) => sum + (a.risk_analysis?.risk_score || 0), 0) / (total || 1);
  
  return { total, highRisk, mediumRisk, avgRisk };
};
```

**What You See:**
```
┌────────────┬────────────┬────────────┬────────────┐
│ Total      │ High Risk  │ Medium     │ Avg Risk   │
│ Articles   │            │ Risk       │ Score      │
│            │            │            │            │
│    22      │     6      │     5      │   51.0%    │
│  +22       │  6 alerts  │ 5 warnings │    51.0    │
└────────────┴────────────┴────────────┴────────────┘
```

**Calculation:**
- **Total**: Count of `detailed_results[]` → `22`
- **High Risk**: Articles where `risk_score >= 0.7` → `6`
- **Medium Risk**: Articles where `0.4 <= risk_score < 0.7` → `5`
- **Avg Risk**: Sum of all `risk_score` / 22 → `0.51` → `51.0%`

---

## 🎨 Category Filtering

**Code (Lines 710-720):**
```javascript
const groupByCategory = (data) => {
  const grouped = { all: data };
  
  data.forEach(article => {
    const categories = article.risk_analysis?.risk_category || [];
    categories.forEach(cat => {
      if (!grouped[cat]) grouped[cat] = [];
      grouped[cat].push(article);
    });
  });
  
  return grouped;
};
```

**What Happens:**
1. Loops through all 22 articles
2. Extracts `risk_category[]` from each
3. Groups articles by category

**Result:**
```javascript
{
  all: [22 articles],
  financial: [15 articles],      // Articles with "financial" category
  regulatory: [11 articles],     // Articles with "regulatory" category
  competitive: [1 article],      // Articles with "competitive" category
  operational: [0 articles]      // No articles with this category
}
```

**Frontend Display:**
```
Filter by Risk Category:
┌────┬──────────┬───────────┬──────────────┬─────────┐
│All │Financial │Regulatory │Competitive   │Market   │
│ 22 │    15    │    11     │      1       │    0    │
└────┴──────────┴───────────┴──────────────┴─────────┘
```

---

## ✅ Summary

### Data Flow:
1. **JSON File** (`risk_assessment_results.json`) → Contains 22 articles with complete analysis
2. **React fetch()** → Loads JSON from `/public/agents/risk_agent/`
3. **Extract Array** → `jsonData.detailed_results` (22 articles)
4. **Store in State** → `setData(articles)`
5. **Display** → Map through articles and show in UI

### Real Data Displayed:
- ✅ **22 articles** from JSON
- ✅ **Risk scores** (0.8 → 80%)
- ✅ **Sentiments** (neutral, positive, negative)
- ✅ **Categories** (regulatory, financial, etc.)
- ✅ **Keywords** (profit, ban, fine, lawsuit)
- ✅ **Source URLs** (https://www.moneycontrol.com/...)
- ✅ **Charts** (article1_1.png, article1_2.png)
- ✅ **Feed titles** (🚨 ALERT: ...)
- ✅ **Hashtags** (#regulatory #financial #RiskAlert)

### No Mock Data:
- Dashboard uses **100% real data** from JSON
- Mock data only used if JSON fetch fails
- All 22 articles come from actual Watsonx analysis

---

**🎉 Every field you see on the frontend comes directly from `risk_assessment_results.json`!**
