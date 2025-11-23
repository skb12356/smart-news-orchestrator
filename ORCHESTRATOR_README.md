# News Orchestrator Integration

This connects the LLM-powered risk analysis with the dashboard.

## How It Works

```
News Scrapers → Risk Scorer Agent (LLM) → Dashboard → Auto-refresh Charts
```

## Quick Start

### Option 1: Run Once
Analyze existing news and update dashboard:

```bash
python run_orchestrator.py
```

### Option 2: Auto-Refresh (Every 30 minutes)
Continuously monitor and update:

```bash
python auto_refresh_orchestrator.py
```

## What It Does

1. **Loads News** - Reads scraped articles from `agents/finance_scrapper/data/`
2. **LLM Analysis** - Uses Risk Scorer Agent to analyze:
   - Sentiment (positive/negative/neutral)
   - Risk score (0-100%)
   - Risk categories (financial, regulatory, etc.)
   - Entity extraction
3. **Updates Dashboard** - Copies results to `dashboard/public/agents/risk_agent/`
4. **Generates Charts** - Creates 44 visualization charts
5. **Refreshes UI** - Dashboard auto-reloads with new data

## Pipeline Output

```
agents/risk_agent/risk_assessment_results.json
  ↓
dashboard/public/agents/risk_agent/risk_assessment_results.json
  ↓
Dashboard displays at http://localhost:3000
```

## File Structure

```
hackathon-IBM/
├── agents/
│   ├── finance_scrapper/data/      # Input: Scraped news
│   └── risk_agent/                 # Output: Risk analysis
├── dashboard/
│   └── public/agents/
│       ├── risk_agent/             # Dashboard data
│       └── charts/                 # Generated charts
├── run_orchestrator.py             # Run once
└── auto_refresh_orchestrator.py    # Auto-refresh every 30 min
```

## Requirements

Make sure you have:
- News data in `agents/finance_scrapper/data/*.json`
- LLM API keys configured (for Risk Scorer Agent)
- Dashboard server running (`npm start`)

## Manual Steps

If you want to run each step manually:

```bash
# 1. Scrape news (if needed)
cd agents/finance_scrapper
python run_all_scrapers.py

# 2. Run risk analysis
cd ../..
python run_orchestrator.py

# 3. Start dashboard
cd dashboard
npm start
```

## Troubleshooting

**No news data found:**
- Run the scrapers first: `cd agents/finance_scrapper && python run_all_scrapers.py`

**Dashboard not updating:**
- Check the file exists: `dashboard/public/agents/risk_agent/risk_assessment_results.json`
- Refresh browser (Ctrl+R)

**Charts missing:**
- Charts are auto-generated during pipeline
- Manually generate: `cd dashboard/public/agents/charts && python generate_all_charts.py`
