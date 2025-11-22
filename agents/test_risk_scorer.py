"""
Test script for Risk Scorer Agent
Demonstrates the usage and validates the functionality
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from risk_scorer import RiskScorer, load_company_knowledge


def test_single_article():
    """Test risk scoring on a single example article"""
    print("=" * 80)
    print("TEST 1: Single Article Analysis")
    print("=" * 80)
    
    # Load company knowledge
    knowledge_path = Path(__file__).parent.parent / "knowledge" / "company.json"
    knowledge = load_company_knowledge(str(knowledge_path))
    
    # Create scorer
    scorer = RiskScorer(knowledge)
    
    # Test article 1: Negative operational risk
    article1 = {
        "article_text": """
        Apple Inc. announced significant delays in iPhone production due to 
        ongoing chip shortage issues affecting its manufacturing facilities 
        in Asia. The company faces supply chain disruptions that could impact 
        Q4 revenue projections. Analysts are concerned about potential 
        market share losses to competitors like Samsung.
        """,
        "source": "Reuters",
        "published_time": "2025-11-20",
        "title": "Apple Faces Production Delays Due to Chip Shortage"
    }
    
    result1 = scorer.analyze_article(article1)
    print("\nArticle: Apple production delays")
    print(json.dumps(result1, indent=2))
    
    # Validate result
    assert result1['sentiment_label'] == 'negative', "Should be negative sentiment"
    assert result1['risk_score'] > 0.5, "Should have moderate-high risk score"
    assert 'operational' in result1['risk_category'], "Should detect operational risk"
    print("✓ Test 1 passed: Negative operational risk detected correctly")
    
    print("\n" + "=" * 80)
    print("TEST 2: Positive Financial News")
    print("=" * 80)
    
    # Test article 2: Positive financial news
    article2 = {
        "article_text": """
        Apple reported strong earnings growth in Q3, beating analyst 
        expectations with record iPhone sales. Revenue surged 15% year-over-year, 
        driven by robust demand for new products. The company announced plans 
        for expansion and innovation in AI services.
        """,
        "source": "Bloomberg",
        "published_time": "2025-11-21",
        "title": "Apple Beats Earnings Expectations"
    }
    
    result2 = scorer.analyze_article(article2)
    print("\nArticle: Apple earnings beat")
    print(json.dumps(result2, indent=2))
    
    # Validate result
    assert result2['sentiment_label'] == 'positive', "Should be positive sentiment"
    assert result2['risk_score'] <= 0.6, "Should have low-moderate risk score (positive news still has financial keywords)"
    print("✓ Test 2 passed: Positive financial news handled correctly")
    
    print("\n" + "=" * 80)
    print("TEST 3: Regulatory Risk")
    print("=" * 80)
    
    # Test article 3: Regulatory risk
    article3 = {
        "article_text": """
        Apple faces antitrust lawsuit from EU regulators over App Store 
        practices. The company could face fines up to $10 billion if found 
        in violation of competition laws. This follows similar regulatory 
        scrutiny in the United States and Asia.
        """,
        "source": "Financial Times",
        "published_time": "2025-11-22",
        "title": "Apple Faces EU Antitrust Lawsuit"
    }
    
    result3 = scorer.analyze_article(article3)
    print("\nArticle: EU antitrust lawsuit")
    print(json.dumps(result3, indent=2))
    
    # Validate result
    assert 'regulatory' in result3['risk_category'], "Should detect regulatory risk"
    assert 'antitrust' in result3['matched_keywords'], "Should match antitrust keyword"
    assert result3['risk_score'] > 0.6, "Should have high risk score"
    print("✓ Test 3 passed: Regulatory risk detected correctly")
    
    print("\n" + "=" * 80)
    print("TEST 4: Sensitive Topic (Data Breach)")
    print("=" * 80)
    
    # Test article 4: Sensitive topic
    article4 = {
        "article_text": """
        Apple disclosed a data breach affecting millions of iCloud users. 
        The cyber attack compromised user privacy data, raising concerns 
        about the company's security measures. Regulators are investigating 
        the incident.
        """,
        "source": "TechCrunch",
        "published_time": "2025-11-22",
        "title": "Apple iCloud Data Breach"
    }
    
    result4 = scorer.analyze_article(article4)
    print("\nArticle: Data breach")
    print(json.dumps(result4, indent=2))
    
    # Validate result
    assert 'sensitive' in result4['risk_category'], "Should detect sensitive topic"
    assert result4['risk_score'] > 0.7, "Should have very high risk score"
    print("✓ Test 4 passed: Sensitive topic detected correctly")
    
    print("\n" + "=" * 80)
    print("All Tests Passed! ✓")
    print("=" * 80)


def test_batch_processing():
    """Test batch processing of news files"""
    print("\n" + "=" * 80)
    print("TEST 5: Batch Processing")
    print("=" * 80)
    
    from risk_scorer_agent import RiskScorerAgent
    
    # Initialize agent
    knowledge_path = Path(__file__).parent.parent / "knowledge" / "company.json"
    data_dir = Path(__file__).parent / "finance_scrapper" / "data"
    
    agent = RiskScorerAgent(str(knowledge_path), str(data_dir))
    
    # Process all news
    print("\nProcessing all news files...")
    results = agent.process_all_news()
    
    print(f"\nTotal articles processed: {len(results)}")
    
    # Generate summary
    summary = agent.generate_summary_report()
    
    print("\nSummary Statistics:")
    print(f"  Sentiment Distribution: {summary['sentiment_distribution']}")
    print(f"  Risk Category Distribution: {summary['risk_category_distribution']}")
    print(f"  Average Risk Score: {summary['average_risk_score']}")
    print(f"  High Risk Articles: {summary['high_risk_articles_count']}")
    
    # Validate
    assert len(results) > 0, "Should process at least some articles"
    assert summary['total_articles_analyzed'] == len(results), "Counts should match"
    print("\n✓ Test 5 passed: Batch processing works correctly")


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "=" * 80)
    print("TEST 6: Edge Cases")
    print("=" * 80)
    
    knowledge_path = Path(__file__).parent.parent / "knowledge" / "company.json"
    knowledge = load_company_knowledge(str(knowledge_path))
    scorer = RiskScorer(knowledge)
    
    # Empty article
    empty_article = {
        "article_text": "",
        "source": "Test",
        "published_time": "2025-11-22"
    }
    
    result = scorer.analyze_article(empty_article)
    print("\nEmpty article result:")
    print(json.dumps(result, indent=2))
    assert result['sentiment_label'] == 'neutral', "Empty should be neutral"
    assert result['risk_score'] == 0.0, "Empty should have zero risk"
    print("✓ Empty article handled correctly")
    
    # Very short article
    short_article = {
        "article_text": "Apple stock up.",
        "source": "Test",
        "published_time": "2025-11-22"
    }
    
    result = scorer.analyze_article(short_article)
    print("\nShort article result:")
    print(json.dumps(result, indent=2))
    assert result['risk_score'] >= 0.0, "Should return valid risk score"
    print("✓ Short article handled correctly")
    
    print("\n✓ Test 6 passed: Edge cases handled correctly")


if __name__ == "__main__":
    try:
        test_single_article()
        test_batch_processing()
        test_edge_cases()
        
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY! ✓✓✓")
        print("=" * 80)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
