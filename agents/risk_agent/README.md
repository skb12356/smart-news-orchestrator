# Risk Scorer Agent

An intelligent agent for IBM Watsonx Orchestrate that analyzes news articles and assigns risk scores based on company knowledge, sentiment analysis, and keyword matching.

## Overview

The Risk Scorer Agent processes news articles from multiple sources (finance, market, industry, LinkedIn) and generates comprehensive risk assessments for a target company (Apple Inc. by default).

## Components

### 1. Core Risk Scorer (`tools/risk_scorer.py`)
- Main risk scoring engine
- Sentiment analysis
- Keyword matching against company knowledge
- Risk score calculation based on formula:
  ```
  Base score = abs(sentiment_score)
  If negative sentiment → risk increases
  If positive → risk reduces
  Add +0.1 for each matched risk keyword
  Clamp to maximum of 1.0
  ```

### 2. Risk Scorer Agent (`agents/risk_scorer_agent.py`)
- Orchestrates batch processing of news articles
- Generates summary reports
- Saves detailed results to JSON

### 3. IBM Orchestrate Tools (`tools/risk_scorer_tool.py`)
- **risk_scorer**: Analyze a single article
- **analyze_all_news**: Batch analyze all news from data directory
- **get_high_risk_alerts**: Get high-risk articles above threshold

### 4. Agent Configuration (`agents/risk-scorer-agent.yaml`)
- IBM Orchestrate ADK configuration
- Agent instructions and behavior
- LLM model configuration

## Output Format

Each article analysis returns:

```json
{
  "summary": "3-5 line distilled summary of the article",
  "sentiment_label": "positive|neutral|negative",
  "sentiment_score": 0.0,
  "risk_category": ["financial", "operational", "competitive", "regulatory", "sensitive"],
  "risk_score": 0.75,
  "matched_keywords": ["chip shortage", "production", "revenue"],
  "reasoning": "The tone is negative and involves operational concerns with keywords: chip shortage, production."
}
```

## Risk Categories

- **financial**: Revenue, profit, earnings, share price, market crash
- **operational**: Manufacturing delays, supply chain, factory accidents, chip shortages
- **competitive**: Competitor launches, price wars, market share changes
- **regulatory**: Bans, compliance issues, fines, lawsuits, antitrust
- **sensitive**: Data breaches, privacy issues, cyber attacks, employee strikes, layoffs

## Usage

### Standalone Execution

```bash
# Run the agent to analyze all news
cd hackathon-IBM/agents
python risk_scorer_agent.py

# Or specify custom paths
python risk_scorer_agent.py ../knowledge/company.json finance_scrapper/data output.json
```

### As IBM Orchestrate Tool

```python
from ibm_watsonx_orchestrate.agent_builder.tools import risk_scorer

# Analyze a single article
result = risk_scorer(
    article_text="Apple announces delay in iPhone production...",
    source="Reuters",
    published_time="2025-11-22",
    article_title="Apple Production Delays"
)

# Get all high-risk alerts
alerts = get_high_risk_alerts(risk_threshold=0.7)
```

### Command Line Tool

```bash
# Analyze specific news file
python tools/risk_scorer.py knowledge/company.json agents/finance_scrapper/data/finance_news.json
```

## Input Files

### Company Knowledge (`knowledge/company.json`)
Contains:
- Company information (name, industry, CEO, stock symbol)
- Risk keywords by category
- Competitors list
- Product keywords
- Sensitive topics
- Stock context

### News Data Files (`agents/finance_scrapper/data/`)
- `finance_news.json` - Financial news
- `market_news.json` - Market analysis
- `industry_news.json` - Industry trends
- `linkedin_news.json` - LinkedIn company news

## Output Files

### Risk Assessment Results (`agents/risk_agent/risk_assessment_results.json`)

```json
{
  "company": { ... },
  "analysis_metadata": {
    "total_articles": 150,
    "data_sources": ["finance_news", "market_news", "industry_news", "linkedin_news"]
  },
  "summary": {
    "total_articles_analyzed": 150,
    "sentiment_distribution": {
      "positive": 45,
      "neutral": 60,
      "negative": 45
    },
    "risk_category_distribution": {
      "financial": 30,
      "operational": 25,
      "competitive": 20,
      "regulatory": 15,
      "sensitive": 10
    },
    "average_risk_score": 0.42,
    "high_risk_articles_count": 15,
    "top_high_risk_articles": [...]
  },
  "detailed_results": [...]
}
```

## Key Features

1. **Multi-source Analysis**: Processes news from finance, market, industry, and LinkedIn sources
2. **Sentiment Analysis**: Evaluates article tone (positive/neutral/negative)
3. **Risk Categorization**: Classifies risks into 5 categories
4. **Keyword Matching**: Matches against company-specific risk keywords
5. **Risk Scoring**: Quantitative risk assessment (0-1 scale)
6. **Batch Processing**: Analyzes hundreds of articles efficiently
7. **Summary Reporting**: Aggregated insights and statistics
8. **High-Risk Alerts**: Identifies articles requiring immediate attention

## Algorithm Details

### Sentiment Calculation
- Analyzes negative/positive/neutral word occurrences
- Normalizes to -1 to +1 scale
- Negative: < -0.2
- Neutral: -0.2 to +0.2
- Positive: > +0.2

### Risk Score Formula
```python
base_score = abs(sentiment_score)
if sentiment_score < 0:
    risk_score = base_score
else:
    risk_score = base_score * 0.3

keyword_penalty = min(0.5, len(matched_keywords) * 0.1)
category_penalty = len(risk_categories) * 0.15

risk_score = min(1.0, risk_score + keyword_penalty + category_penalty)
```

## Dependencies

```
ibm_watsonx_orchestrate
```

## Configuration

Edit `knowledge/company.json` to customize:
- Target company
- Risk keywords
- Competitors
- Product keywords
- Sensitive topics

## Integration with IBM Orchestrate ADK

The agent is designed to work seamlessly with IBM Watsonx Orchestrate:

1. Tools are decorated with `@tool` decorator
2. YAML configuration follows ADK spec v1
3. LLM model: `watsonx/meta-llama/llama-3-2-90b-vision-instruct`
4. Compatible with Orchestrate workflows and agent collaboration

## Example Workflow

1. News scrapers collect articles → saved to `data/` directory
2. Risk Scorer Agent processes all articles
3. Generates risk assessments with scores and categories
4. Creates summary report with statistics
5. Identifies high-risk articles for alerts
6. Saves detailed results for further analysis

## Customization

### Adding New Risk Categories
Edit `knowledge/company.json`:
```json
"risk_keywords": {
  "new_category": ["keyword1", "keyword2", ...]
}
```

### Adjusting Risk Thresholds
Modify the risk score calculation in `tools/risk_scorer.py`:
```python
def _calculate_risk_score(self, sentiment_score, matched_keywords, risk_categories):
    # Adjust multipliers and penalties here
    keyword_penalty = len(matched_keywords) * 0.15  # Increase sensitivity
    category_penalty = len(risk_categories) * 0.20   # Increase category weight
```

### Changing Summary Length
In `tools/risk_scorer.py`:
```python
def _generate_summary(self, text, max_sentences=5):  # Increase from 4 to 5
```

## Troubleshooting

**Issue**: No articles processed
- Check that news JSON files exist in `data/` directory
- Verify file paths in agent configuration

**Issue**: Low risk scores for clearly risky articles
- Add more risk keywords to `company.json`
- Adjust risk score calculation weights

**Issue**: Import errors
- Ensure `tools/` directory is in Python path
- Check that all dependencies are installed

## Future Enhancements

- [ ] Real-time news monitoring
- [ ] Email/Slack alerts for high-risk articles
- [ ] Trend analysis over time
- [ ] Comparative analysis with competitors
- [ ] Integration with stock price movements
- [ ] Machine learning-based sentiment analysis
- [ ] Multi-language support
- [ ] Custom risk scoring models per industry

## License

Part of IBM-ORCHESTRA project

## Author

Created for IBM Orchestrate ADK hackathon
