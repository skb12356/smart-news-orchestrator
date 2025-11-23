"""
Example: Using Chart Generator with Risk Scorer
Demonstrates how to visualize risk assessment data and article metadata.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from tools.chart_generator import ChartGenerator
from tools.risk_scorer import RiskScorer
import json

def example_1_visualize_risk_scores():
    """Example 1: Generate a bar chart of article risk scores."""
    print("\n=== Example 1: Risk Score Comparison ===")
    
    # Sample articles with risk scores
    articles_data = [
        {"Title": "Market Crash Alert", "Risk Score": 0.9},
        {"Title": "Stable Growth Report", "Risk Score": 0.3},
        {"Title": "Regulatory Warning", "Risk Score": 0.7},
        {"Title": "Product Launch Success", "Risk Score": 0.2},
        {"Title": "Lawsuit Filed", "Risk Score": 0.8}
    ]
    
    generator = ChartGenerator()
    result = generator.generate_chart(
        articles_data,
        "Risk Scores for Recent Articles",
        chart_type="bar"
    )
    
    print(f"Chart Type: {result['chart_type']}")
    print(f"File Path: {result['file_path']}")
    print(f"Description: {result['description']}")
    return result['file_path']


def example_2_sentiment_distribution():
    """Example 2: Pie chart of sentiment distribution."""
    print("\n=== Example 2: Sentiment Distribution ===")
    
    sentiment_data = [
        {"Sentiment": "Positive", "Count": 15},
        {"Sentiment": "Neutral", "Count": 42},
        {"Sentiment": "Negative", "Count": 28}
    ]
    
    generator = ChartGenerator()
    result = generator.generate_chart(
        sentiment_data,
        "Article Sentiment Distribution",
        chart_type="pie"
    )
    
    print(f"Chart saved to: {result['file_path']}")
    return result['file_path']


def example_3_risk_trend_over_time():
    """Example 3: Line chart showing risk trend."""
    print("\n=== Example 3: Risk Trend Over Time ===")
    
    trend_data = [
        {"Week": "Week 1", "Avg Risk": 0.45},
        {"Week": "Week 2", "Avg Risk": 0.52},
        {"Week": "Week 3", "Avg Risk": 0.48},
        {"Week": "Week 4", "Avg Risk": 0.65},
        {"Week": "Week 5", "Avg Risk": 0.71}
    ]
    
    generator = ChartGenerator()
    result = generator.generate_chart(
        trend_data,
        "Average Risk Score Trend",
        chart_type="line"
    )
    
    print(f"Chart saved to: {result['file_path']}")
    return result['file_path']


def example_4_category_distribution():
    """Example 4: Bar chart of risk categories."""
    print("\n=== Example 4: Risk Category Distribution ===")
    
    category_data = [
        {"Category": "Financial", "Count": 35},
        {"Category": "Operational", "Count": 12},
        {"Category": "Competitive", "Count": 8},
        {"Category": "Regulatory", "Count": 28},
        {"Category": "Sensitive", "Count": 5}
    ]
    
    generator = ChartGenerator()
    result = generator.generate_chart(
        category_data,
        "Risk Categories Detected in Articles",
        chart_type="bar"
    )
    
    print(f"Chart saved to: {result['file_path']}")
    return result['file_path']


def example_5_from_real_assessment():
    """Example 5: Generate charts from actual risk assessment results."""
    print("\n=== Example 5: Charts from Real Assessment Data ===")
    
    # Load actual risk assessment results
    results_path = Path(__file__).parent / "agents" / "risk_agent" / "risk_assessment_results.json"
    
    if not results_path.exists():
        print("⚠️ Risk assessment results not found. Run risk_scorer_agent.py first.")
        return None
    
    with open(results_path, 'r', encoding='utf-8') as f:
        assessment = json.load(f)
    
    # Extract summary data
    summary = assessment.get('summary', {})
    
    # Chart 1: Sentiment distribution
    sentiment_dist = summary.get('sentiment_distribution', {})
    sentiment_data = [
        {"Sentiment": k.capitalize(), "Count": v}
        for k, v in sentiment_dist.items()
    ]
    
    generator = ChartGenerator()
    
    if sentiment_data:
        result1 = generator.generate_chart(
            sentiment_data,
            "Sentiment Distribution from Risk Assessment",
            chart_type="pie"
        )
        print(f"✅ Sentiment chart: {result1['file_path']}")
    
    # Chart 2: Risk category distribution
    risk_dist = summary.get('risk_category_distribution', {})
    risk_data = [
        {"Category": k.capitalize(), "Count": v}
        for k, v in risk_dist.items() if v > 0
    ]
    
    if risk_data:
        result2 = generator.generate_chart(
            risk_data,
            "Risk Category Distribution",
            chart_type="bar"
        )
        print(f"✅ Risk category chart: {result2['file_path']}")
    
    # Chart 3: Top high-risk articles
    high_risk = summary.get('top_high_risk_articles', [])[:5]
    if high_risk:
        high_risk_data = [
            {"Article": article['title'][:30] + "...", "Risk": article['risk_score']}
            for article in high_risk
        ]
        result3 = generator.generate_chart(
            high_risk_data,
            "Top 5 High-Risk Articles",
            chart_type="bar"
        )
        print(f"✅ High-risk articles chart: {result3['file_path']}")
    
    print(f"\n📊 Total articles analyzed: {summary.get('total_articles_analyzed', 0)}")
    print(f"📈 Average risk score: {summary.get('average_risk_score', 0):.2f}")


def main():
    """Run all chart generation examples."""
    print("=" * 70)
    print("Chart Generator Examples - IBM Watsonx Orchestrate")
    print("=" * 70)
    
    # Run examples
    example_1_visualize_risk_scores()
    example_2_sentiment_distribution()
    example_3_risk_trend_over_time()
    example_4_category_distribution()
    example_5_from_real_assessment()
    
    print("\n" + "=" * 70)
    print("✅ All examples complete!")
    print("📁 Charts saved to: agents/charts/")
    print("=" * 70)


if __name__ == "__main__":
    main()
