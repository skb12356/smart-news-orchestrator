# Smart News Orchestrator - IBM Watsonx Orchestrate

Risk assessment agent for analyzing financial news articles using IBM Watsonx Orchestrate.

## 📁 Project Structure

```
hackathon-IBM/
├── agents/                          # IBM Orchestrate Agents
│   ├── risk_scorer_agent.py        # Main risk scoring agent (batch processor)
│   ├── risk-scorer-agent.yaml      # Agent config for IBM Orchestrate
│   ├── example_usage.py            # Usage examples
│   ├── test_risk_scorer.py         # Unit tests
│   ├── test_llm_integration.py     # LLM integration tests
│   ├── risk_agent/                 # Output directory
│   │   └── risk_assessment_results.json
│   └── finance_scrapper/           # Data scrapers
│       ├── finance_crawler.py
│       ├── finance_scraper.py
│       ├── industry_scraper.py
│       ├── linkedin_scraper.py
│       ├── market_scraper.py
│       ├── run_all_scrapers.py     # Run all scrapers at once
│       └── data/                   # Scraped news data
│           ├── finance_news.json
│           ├── market_news.json
│           ├── industry_news.json
│           └── linkedin_news.json
│
├── tools/                          # Orchestrate Tools
│   ├── risk_scorer.py             # Core risk analysis engine
│   ├── risk_scorer_tool.py        # @tool decorated functions for Orchestrate
│   └── greetings.py               # Demo tool
│
├── knowledge/                      # Knowledge Base
│   └── company.json               # Company info (Apple Inc.)
│
└── req.txt                        # Python dependencies

```

## 🎯 What Each Component Does

### **Agents (`agents/`)**
Entry points for IBM Watsonx Orchestrate integration.

- **`risk_scorer_agent.py`**: Main orchestration script
  - Reads news data from `finance_scrapper/data/`
  - Analyzes each article using the risk scorer
  - Generates comprehensive risk assessment reports
  - Filters out "Access Denied" pages
  - Preserves ALL scraper metadata (graphs, tables, URLs, etc.)

- **`risk-scorer-agent.yaml`**: IBM Orchestrate configuration
  - Defines LLM model: `watsonx/meta-llama/llama-3-2-90b-vision-instruct`
  - Lists available tools
  - Contains agent instructions for risk analysis

- **`example_usage.py`**: Shows how to use the agent locally

- **`test_*.py`**: Test suites for validation

### **Tools (`tools/`)**
Reusable functions that agents can call.

- **`risk_scorer.py`**: Core analysis engine
  - `RiskScorer` class with sentiment analysis
  - Keyword matching against company knowledge base
  - Risk scoring algorithm (0-1 scale)
  - Risk categorization (financial, operational, competitive, regulatory, sensitive)

- **`risk_scorer_tool.py`**: IBM Orchestrate tool wrappers
  - `@tool` decorated functions callable by LLM
  - `risk_scorer()`: Analyze single article
  - `analyze_all_news()`: Batch process all news
  - `get_high_risk_alerts()`: Get high-risk articles

- **`greetings.py`**: Simple demo tool for testing Orchestrate

### **Data Scrapers (`agents/finance_scrapper/`)**
Web scrapers that collect news articles.

- **Individual scrapers**: `finance_scraper.py`, `market_scraper.py`, etc.
  - Scrape news from various financial sources
  - Extract metadata: graphs, tables, images, numbers
  - Detect risk tags, competitors, stock mentions

- **`run_all_scrapers.py`**: Execute all scrapers in sequence

- **`data/`**: Output directory with scraped JSON files

### **Knowledge Base (`knowledge/`)**
Reference data for analysis.

- **`company.json`**: Company profile (Apple Inc.)
  - Risk keywords (financial, operational, competitive, regulatory)
  - Competitor list
  - Product keywords
  - Sensitive topics

## 🚀 How to Use

### 1. Run Scrapers (Get Fresh Data)
```bash
cd agents/finance_scrapper
python run_all_scrapers.py
```

### 2. Run Risk Analysis
```bash
cd hackathon-IBM
python agents/risk_scorer_agent.py
```

Output saved to: `agents/risk_agent/risk_assessment_results.json`

### 3. Run Tests
```bash
python agents/test_risk_scorer.py
python agents/test_llm_integration.py
```

## 📊 Output Format

The risk assessment output includes:
- **All original scraper metadata** (preserved completely):
  - `url`, `graphs_images`, `relevant_tables`, `extracted_numbers`
  - `risk_tags_detected`, `competitor_mentions`, `stock_mentions`
  - `source`, `title`, `published_time`, `content_text`

- **Risk analysis** (added by agent):
  - `risk_analysis.risk_score` (0-1)
  - `risk_analysis.sentiment_score` (-1 to +1)
  - `risk_analysis.risk_category` (array)
  - `risk_analysis.matched_keywords` (array)
  - `risk_analysis.reasoning` (explanation)

## 🔗 IBM Watsonx Orchestrate Integration

This agent is designed for IBM Watsonx Orchestrate:
- **Hybrid architecture**: Algorithm-based for speed, LLM-orchestrated when deployed
- **Agent YAML**: `agents/risk-scorer-agent.yaml` configures the agent
- **Tools**: `@tool` decorated functions in `tools/risk_scorer_tool.py`
- **LLM Model**: `meta-llama/llama-3-2-90b-vision-instruct`

## 📝 Dependencies

See `req.txt` for Python package requirements.

## 🎯 Key Features

✅ Analyzes financial news for risk assessment  
✅ Preserves ALL original scraper metadata  
✅ Filters "Access Denied" error pages  
✅ Multi-category risk classification  
✅ Sentiment analysis (-1 to +1)  
✅ Keyword-based risk detection  
✅ Batch processing of multiple news sources  
✅ IBM Orchestrate ready with @tool decorators  
✅ Comprehensive test coverage  

---

**Ready for IBM Watsonx Orchestrate deployment** 🚀
