# Smart News Orchestrator Dashboard

A stunning, animated dashboard to visualize risk analysis results from IBM Watsonx Orchestrate agents.

## Features

🎨 **Crazy Beautiful UI**
- Animated gradient backgrounds
- Glass morphism effects
- Neon glow animations
- Smooth hover transitions
- Floating elements

📊 **Category-Wise Risk Analysis**
- Financial Risk
- Operational Risk
- Regulatory Risk
- Competitive Risk
- Market Risk
- Reputational Risk

🔥 **Real-Time Intelligence**
- Live risk alerts
- High-risk article monitoring
- Sentiment analysis visualization
- Risk distribution charts
- Social media feed preview

## Installation

```bash
cd dashboard
npm install
```

## Running the Dashboard

```bash
npm start
```

The dashboard will open at `http://localhost:3000`

## Data Sources

The dashboard reads from:
- `/risk_assessment_results.json` - Main risk analysis data
- `/agents/feeds/feed.json` - Social media posts (optional)
- `/agents/charts/*.png` - Generated visualizations (optional)

## Mock Data

For demo purposes, the dashboard includes mock data that will be used if the JSON files are not found. Replace with real data from your Watsonx Orchestrate agents.

## Tech Stack

- **React 18.2** - UI framework
- **Tailwind CSS** - Styling via CDN
- **Lucide React** - Beautiful icons
- **Custom CSS Animations** - Gradient, float, pulse effects

## Color Coding

- 🔴 **Red (70-100%)** - High Risk
- 🟡 **Yellow (40-69%)** - Medium Risk  
- 🟢 **Green (0-39%)** - Low Risk

## Components

- **Dashboard** - Main container with stats and filters
- **StatsCard** - Animated metric cards
- **ArticleCard** - Individual article risk display
- **RiskDistributionChart** - Category breakdown visualization
- **SentimentChart** - Sentiment analysis bars
- **SocialFeedPreview** - Social media post cards

## Customization

Edit `src/Dashboard.js` to:
- Adjust risk thresholds
- Add new categories
- Customize colors
- Modify animations
- Change data sources

## Built With IBM Watsonx Orchestrate

This dashboard visualizes output from:
- **Risk Scorer Agent** - Analyzes news for risk
- **Chart Generator Agent** - Creates visualizations
- **Feed Poster Agent** - Generates social posts

All agents deployed via `orchestrate` CLI to IBM Watsonx Orchestrate.
