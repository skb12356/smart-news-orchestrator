# IBM Orchestra News Analysis Pipeline

Complete automated news analysis system for IBM Watsonx Orchestrate that processes scraped financial news articles, performs risk assessment, generates visualizations, and creates engaging social media posts.

## 🎯 System Overview

```
News Scrapers → Risk Assessment → Chart Generation → Feed Posting → Social Media
```

### Pipeline Components

1. **News Scrapers** - Collect financial news from multiple sources
2. **Risk Scorer Agent** - Analyzes articles and assigns risk scores (0.0-1.0)
3. **Chart Generator Agent** - Creates visualizations from tabular data
4. **Feed Poster Agent** - Generates engaging social media posts with creative titles

## 🚀 Quick Start

### Prerequisites

```bash
pip install matplotlib
```

### Run Complete Pipeline

```bash
# Run with default settings (all articles)
python run_complete_pipeline.py

# Filter by minimum risk score
python run_complete_pipeline.py --min-risk 0.5

# Limit number of social media posts
python run_complete_pipeline.py --max-posts 10

# Combine filters
python run_complete_pipeline.py --min-risk 0.6 --max-posts 20
```

## 📁 Directory Structure

```
hackathon-IBM/
├── agents/
│   ├── risk_scorer_agent.py          # Risk assessment orchestrator
│   ├── risk-scorer-agent.yaml        # Risk scorer LLM config
│   ├── chart-generator-agent.yaml    # Chart generator LLM config
│   ├── feed-poster-agent.yaml        # Feed poster LLM config
│   ├── charts/                       # Generated visualizations
│   │   ├── article1_1.png
│   │   ├── article1_2.png
│   │   └── ...
│   ├── feeds/                        # Generated social media feeds
│   │   └── feed.json
│   └── finance_scrapper/
│       └── data/                     # Scraped news articles
│           ├── finance_news.json
│           ├── market_news.json
│           ├── industry_news.json
│           └── linkedin_news.json
├── tools/
│   ├── risk_scorer.py                # Risk analysis engine
│   ├── risk_scorer_tool.py           # IBM Orchestrate tools
│   ├── chart_generator.py            # Chart generation engine
│   ├── chart_generator_tool.py       # IBM Orchestrate tools
│   ├── feed_poster.py                # Feed generation engine
│   └── feed_poster_tool.py           # IBM Orchestrate tools
├── knowledge/
│   └── company.json                  # Company knowledge base (Apple Inc.)
├── run_complete_pipeline.py          # Main orchestrator script
└── README.md                         # This file
```

## 🎨 Agent Details

### 1. Risk Scorer Agent

**Purpose**: Analyzes news articles and assigns risk scores based on sentiment, keywords, and company relevance.

**Key Features**:
- Sentiment analysis (-1.0 to +1.0)
- Risk scoring (0.0 to 1.0)
- Risk categorization (financial, operational, regulatory, competitive, market, reputational)
- Preserves ALL original scraper metadata

**Risk Thresholds**:
- **High Risk** (0.7-1.0): Immediate attention required
- **Medium Risk** (0.4-0.7): Monitor closely
- **Low Risk** (0.0-0.4): Informational

**Tools**:
- `analyze_article_risk` - Analyze single article
- `batch_analyze_articles` - Process multiple articles
- `filter_articles_by_risk` - Filter by risk threshold
- `get_risk_summary` - Generate risk statistics

### 2. Chart Generator Agent

**Purpose**: Creates professional visualizations from tabular data in articles.

**Key Features**:
- Auto-detects optimal chart type (line, bar, pie, histogram)
- Article-specific naming (`article1_1.png`, `article1_2.png`)
- 150 DPI professional quality
- Matplotlib-powered visualizations

**Chart Types**:
- **Line Chart**: Time series data, trends
- **Bar Chart**: Categorical comparisons
- **Pie Chart**: Percentage breakdowns
- **Histogram**: Distribution analysis

**Tools**:
- `create_line_chart` - Time series visualization
- `create_bar_chart` - Categorical comparison
- `create_pie_chart` - Percentage breakdown
- `create_histogram` - Distribution visualization
- `auto_generate_chart` - Automatic chart type detection

### 3. Feed Poster Agent

**Purpose**: Creates engaging social media posts from risk-assessed articles.

**Key Features**:
- Creative title generation with emoji prefixes (🚨, ⚠️, 📊, ✅)
- 280-character engaging content summaries
- Smart image selection
- Strategic hashtag generation
- Audience targeting
- Posting urgency recommendations

**Title Formulas by Risk**:

**High Risk (0.7+)**:
- "🚨 ALERT: [Impact] - [What Investors Must Know]"
- "⚠️ BREAKING: [Company] Faces [Crisis]"

**Medium Risk (0.4-0.7)**:
- "📊 UPDATE: [Company] Reports [News]"
- "📈 TRENDING: [Topic] Raises [Concern]"

**Low Risk (0.0-0.4)**:
- "✅ INSIGHT: [Positive Development]"
- "💡 ANALYSIS: What [Event] Tells Us"

**Tools**:
- `create_feed_post_from_article` - Single post with LLM-generated content
- `generate_complete_feed` - Batch process all articles
- `analyze_article_for_feed` - Get LLM guidance for creative content
- `get_feed_statistics` - Feed analytics

## 🎯 What Each Component Does

### **Agents (`agents/`)**
Three-agent system for complete news analysis automation:

- **`risk_scorer_agent.py`**: Main orchestration script

- **`risk_scorer_agent.py`**: Risk assessment orchestrator that analyzes all scraped news
- **`risk-scorer-agent.yaml`**: LLM configuration for risk analysis
- **`chart-generator-agent.yaml`**: LLM configuration for chart generation  
- **`feed-poster-agent.yaml`**: LLM configuration for social media post creation

### **Tools (`tools/`)**
Reusable analysis engines and IBM Orchestrate tool wrappers:

- **`risk_scorer.py`** + **`risk_scorer_tool.py`**: Sentiment analysis, risk scoring, categorization
- **`chart_generator.py`** + **`chart_generator_tool.py`**: Auto-detects chart types, creates visualizations
- **`feed_poster.py`** + **`feed_poster_tool.py`**: Creative title generation, content writing, image selection

### **Data Scrapers (`agents/finance_scrapper/`)**
Web scrapers that collect news articles from financial sources.

### **Knowledge Base (`knowledge/`)**
- **`company.json`**: Company profile with risk keywords, competitors, products (Apple Inc.)

## 📊 Output Files

### risk_assessment_results.json

Risk analysis results with sentiment, risk score, and categories:

```json
[
  {
    "title": "Apple Reports Q4 Earnings",
    "content": "Apple Inc. reported quarterly earnings...",
    "url": "https://example.com/article",
    "graphs_images": ["https://example.com/image.jpg"],
    "relevant_tables": [{...}],
    "extracted_numbers": {...},
    "sentiment_score": -0.45,
    "risk_score": 0.75,
    "risk_categories": ["financial", "regulatory"],
    "matched_keywords": ["earnings miss", "revenue decline"]
  }
]
```

### feed.json

Social media posts with creative titles and engagement metadata:

```json
{
  "generated_at": "2024-01-15T10:30:00",
  "total_posts": 15,
  "posts": [
    {
      "post_id": "post_1",
      "title": "🚨 ALERT: Apple Earnings Miss - Stock Plunges 8%!",
      "content": "Apple's Q4 revenue fell short by $2B. iPhone sales down 12%...",
      "key_insights": ["Risk Score: 0.75 (High)", "Sentiment: Negative"],
      "primary_image": "https://example.com/image.jpg",
      "risk_metadata": {
        "risk_score": 0.75,
        "sentiment": "negative",
        "priority": "high"
      },
      "engagement_metadata": {
        "recommended_hashtags": ["#Apple", "#TechStocks", "#EarningsMiss"],
        "target_audience": "investors, traders, tech analysts",
        "best_posting_time": "immediate"
      }
    }
  ]
}
```

## 🛠️ Usage Examples

### Individual Agents

#### Risk Scorer Agent

```python
from tools.risk_scorer import RiskScorer
import json

with open('knowledge/company.json', 'r') as f:
    company_data = json.load(f)

scorer = RiskScorer(company_data)

with open('agents/finance_scrapper/data/finance_news.json', 'r') as f:
    articles = json.load(f)

analyzed = scorer.analyze_article(articles[0])
print(f"Risk Score: {analyzed['risk_score']:.2f}")
```

#### Chart Generator

```python
from tools.chart_generator import ChartGenerator

generator = ChartGenerator(output_dir='agents/charts')

chart_path = generator.generate_chart(
    data={'Q1': 100, 'Q2': 120, 'Q3': 90, 'Q4': 110},
    title='Quarterly Revenue',
    article_id=1,
    chart_number=1
)
# Saves as: agents/charts/article1_1.png
```

#### Feed Poster

```python
from tools.feed_poster import FeedPoster

poster = FeedPoster(output_dir='agents/feeds')

feed_data = poster.generate_feed_from_assessment(
    assessment_file_path='risk_assessment_results.json',
    max_posts=10
)
print(json.dumps(json.loads(feed_data), indent=2))
```

## 🔧 Configuration

### Risk Scorer Configuration

Edit `tools/risk_scorer.py` to customize risk keywords by category:

```python
self.risk_keywords = {
    'financial': ['loss', 'decline', 'debt', 'bankruptcy'],
    'operational': ['disruption', 'recall', 'failure'],
    'regulatory': ['investigation', 'fine', 'lawsuit'],
    # ... add more
}
```

### Chart Generator Configuration

Edit `tools/chart_generator.py` for chart styling:

```python
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
```

### Feed Poster Configuration

Edit `tools/feed_poster.py` for emoji and content preferences:

```python
self.emoji_prefixes = {
    'high': ['🚨', '⚠️', '🔴', '💥'],
    'medium': ['📊', '📈', '🎯', '💼'],
    'low': ['✅', '📰', '💡', '🌟']
}
```

## 📈 Performance Metrics

From a typical run with 22 articles:

- **Risk Assessment**: 22 articles analyzed, 15 filtered (min_risk=0.5)
- **Chart Generation**: 8 charts created from tabular data
- **Feed Generation**: 15 social media posts created
- **Processing Times**: Risk ~2-3s, Charts ~1-2s each, Feed ~3-5s

## 🔍 Troubleshooting

### No charts generated
- Check if articles have `relevant_tables` or `extracted_numbers`
- Verify data format compatibility
- Check write permissions on `agents/charts/`

### Risk scores all zero
- Verify `company.json` has company name and keywords
- Check article `title` and `content` fields
- Review `risk_keywords` in `risk_scorer.py`

### Feed generation fails
- Ensure `risk_assessment_results.json` exists
- Check articles have required fields (title, content, risk_score)
- Verify `agents/feeds/` is writable

## 🤝 Integration with IBM Watsonx Orchestrate

### Deploying Agents

Each agent has a YAML configuration:

```yaml
kind: native
spec_version: v1
name: risk-scorer-agent
llm:
  model_id: watsonx/meta-llama/llama-3-2-90b-vision-instruct
  parameters:
    temperature: 0.7
tools:
  - analyze_article_risk
  - batch_analyze_articles
```

### Tool Registration

Tools decorated with `@tool` for IBM Orchestrate:

```python
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool
def analyze_article_risk(article_json: str) -> str:
    """Analyze article and return risk assessment"""
    pass
```

## 🎯 Key Features

✅ Three-agent automated pipeline (Risk → Charts → Feed)  
✅ LLM-generated creative social media titles  
✅ Intelligent chart type auto-detection  
✅ Article-specific naming (`article1_1.png`)  
✅ Complete metadata preservation  
✅ Sentiment & risk scoring  
✅ Professional visualizations (150 DPI)  
✅ Social media optimization (hashtags, audience, timing)  
✅ IBM Orchestrate ready with @tool decorators  
✅ Comprehensive test coverage  

## 📚 Additional Resources

- [IBM Watsonx Orchestrate Documentation](https://www.ibm.com/watsonx/orchestrate)
- [Matplotlib Documentation](https://matplotlib.org/stable/)
- [Python JSON Documentation](https://docs.python.org/3/library/json.html)

## 📄 License

IBM Orchestra Hackathon submission.

## 👥 Contributors

Built with Python 3.x, Matplotlib 3.10.0, IBM Watsonx Orchestrate ADK  
Model: watsonx/meta-llama/llama-3-2-90b-vision-instruct  
Architecture: Hybrid (Algorithm execution + LLM orchestration)
    {"Quarter": "Q1", "Revenue": 120},
    {"Quarter": "Q2", "Revenue": 140}
]

generator = ChartGenerator()

# Generate with article-specific naming
result = generator.generate_chart(
    data, 
    "Quarterly revenue",
    article_id="article1",  # Article identifier
    chart_number=1          # Chart number within article
)
# Returns: {"chart_type": "line", "file_path": ".../article1_1.png", ...}
```

**Naming Convention:**
- `article1_1.png` - First chart from article 1
- `article1_2.png` - Second chart from article 1
- `article2_1.png` - First chart from article 2
- Charts from same article are numbered sequentially

---

**Ready for IBM Watsonx Orchestrate deployment** 🚀
