"""
Example Usage of Risk Scorer Agent
Demonstrates various ways to use the risk scoring system
"""

import json
from pathlib import Path

print("=" * 80)
print("RISK SCORER AGENT - USAGE EXAMPLES")
print("=" * 80)

# Example 1: Analyze a Single Article
print("\n1. SINGLE ARTICLE ANALYSIS")
print("-" * 80)

from tools.risk_scorer import RiskScorer, load_company_knowledge

knowledge = load_company_knowledge("knowledge/company.json")
scorer = RiskScorer(knowledge)

article = {
    "article_text": """
    Apple Inc. announced today that it will delay the launch of its new 
    iPhone model due to ongoing supply chain issues. The company cited 
    chip shortages and manufacturing delays as primary factors. Analysts 
    predict this could impact Q4 revenue by up to 10%.
    """,
    "source": "TechNews Daily",
    "published_time": "2025-11-22",
    "title": "Apple Delays iPhone Launch"
}

result = scorer.analyze_article(article)
print(json.dumps(result, indent=2))

# Example 2: Batch Process All News Files
print("\n\n2. BATCH PROCESSING ALL NEWS")
print("-" * 80)

from agents.risk_scorer_agent import RiskScorerAgent

agent = RiskScorerAgent(
    "knowledge/company.json",
    "agents/finance_scrapper/data"
)

summary = agent.run("agents/risk_agent/risk_assessment_results.json")

print(f"\nProcessed {summary['total_articles_analyzed']} articles")
print(f"Average Risk Score: {summary['average_risk_score']}")
print(f"High Risk Articles: {summary['high_risk_articles_count']}")

# Example 3: Get High Risk Alerts
print("\n\n3. HIGH RISK ALERTS (Risk Score >= 0.7)")
print("-" * 80)

high_risk_articles = [
    article for article in summary['top_high_risk_articles'][:5]
]

for i, article in enumerate(high_risk_articles, 1):
    print(f"\n{i}. {article['title'][:70]}...")
    print(f"   Risk Score: {article['risk_score']}")
    print(f"   Categories: {', '.join(article['risk_category'])}")
    print(f"   Sentiment: {article['sentiment']}")

# Example 4: Category-Specific Analysis
print("\n\n4. RISK BREAKDOWN BY CATEGORY")
print("-" * 80)

categories = summary['risk_category_distribution']
for category, count in categories.items():
    if count > 0:
        print(f"{category.capitalize():15} : {count:3} articles")

# Example 5: Sentiment Distribution
print("\n\n5. SENTIMENT DISTRIBUTION")
print("-" * 80)

sentiments = summary['sentiment_distribution']
total = sum(sentiments.values())

for sentiment, count in sentiments.items():
    percentage = (count / total * 100) if total > 0 else 0
    bar = "█" * int(percentage / 2)
    print(f"{sentiment.capitalize():10} : {bar} {count} ({percentage:.1f}%)")

# Example 6: Using as IBM Orchestrate Tool
print("\n\n6. IBM ORCHESTRATE TOOL USAGE")
print("-" * 80)
print("""
# In your IBM Orchestrate workflow:

from tools.risk_scorer_tool import risk_scorer, analyze_all_news, get_high_risk_alerts

# Analyze single article
result = risk_scorer(
    article_text="Apple faces lawsuit...",
    source="Reuters",
    published_time="2025-11-22",
    article_title="Apple Legal Issues"
)

# Get all high risk alerts
alerts = get_high_risk_alerts(risk_threshold=0.7)

# Analyze all news
summary = analyze_all_news()
""")

# Example 7: Custom Risk Threshold Analysis
print("\n\n7. CUSTOM RISK THRESHOLD ANALYSIS")
print("-" * 80)

# Reload results
with open("agents/risk_agent/risk_assessment_results.json", 'r') as f:
    full_results = json.load(f)

thresholds = [0.3, 0.5, 0.7, 0.9]
for threshold in thresholds:
    count = sum(
        1 for r in full_results['detailed_results']
        if r['risk_score'] >= threshold
    )
    print(f"Risk >= {threshold}: {count:3} articles")

# Example 8: Monitoring Specific Risk Categories
print("\n\n8. MONITORING SPECIFIC CATEGORIES")
print("-" * 80)

target_categories = ['regulatory', 'sensitive']
filtered_articles = [
    r for r in full_results['detailed_results']
    if any(cat in r['risk_category'] for cat in target_categories)
]

print(f"\nFound {len(filtered_articles)} articles with regulatory or sensitive risks:")
for article in filtered_articles[:3]:
    print(f"\n• {article['article_title'][:60]}...")
    print(f"  Risk Score: {article['risk_score']}")
    print(f"  Categories: {', '.join(article['risk_category'])}")
    print(f"  Reasoning: {article['reasoning'][:80]}...")

print("\n" + "=" * 80)
print("END OF EXAMPLES")
print("=" * 80)
