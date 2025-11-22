# risk_scorer_tool.py
"""
Risk Scorer Tool for IBM Watsonx Orchestrate
Analyzes news articles and assigns risk scores based on company knowledge
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
import json
from pathlib import Path
from typing import Dict, Any, Optional


@tool
def risk_scorer(
    article_text: str,
    source: str = "unknown",
    published_time: str = "unknown",
    article_title: str = "No title"
) -> Dict[str, Any]:
    """
    Analyze a news article and return a comprehensive risk assessment.
    
    Args:
        article_text: The full text content of the news article
        source: The source of the article (e.g., "Reuters", "Bloomberg")
        published_time: When the article was published
        article_title: Title of the article
    
    Returns:
        Dictionary containing:
        - summary: 3-5 line distilled summary
        - sentiment_label: "positive", "neutral", or "negative"
        - sentiment_score: float between -1 and +1
        - risk_category: list of categories ["financial", "operational", "competitive", "regulatory", "sensitive"]
        - risk_score: float between 0 and 1
        - matched_keywords: list of keywords from company knowledge
        - reasoning: short explanation
    """
    
    # Import the RiskScorer class
    from risk_scorer import RiskScorer, load_company_knowledge
    
    # Load company knowledge
    # Adjust path based on your project structure
    current_dir = Path(__file__).parent.parent
    knowledge_path = current_dir / "knowledge" / "company.json"
    
    try:
        company_knowledge = load_company_knowledge(str(knowledge_path))
        scorer = RiskScorer(company_knowledge)
        
        # Create article object
        article = {
            "article_text": article_text,
            "content_text": article_text,
            "source": source,
            "published_time": published_time,
            "title": article_title
        }
        
        # Analyze the article
        result = scorer.analyze_article(article)
        
        return result
        
    except Exception as e:
        return {
            "summary": f"Error analyzing article: {str(e)}",
            "sentiment_label": "neutral",
            "sentiment_score": 0.0,
            "risk_category": [],
            "risk_score": 0.0,
            "matched_keywords": [],
            "reasoning": f"Analysis failed: {str(e)}"
        }


@tool
def analyze_all_news(data_directory: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze all news articles from the data directory and return a comprehensive report.
    
    Args:
        data_directory: Optional path to directory containing news JSON files.
                       If not provided, uses default location.
    
    Returns:
        Dictionary containing:
        - total_articles_analyzed: total number of articles processed
        - sentiment_distribution: count of positive/neutral/negative articles
        - risk_category_distribution: count by risk category
        - average_risk_score: mean risk score across all articles
        - high_risk_articles_count: number of articles with risk_score >= 0.7
        - top_high_risk_articles: list of top 10 highest risk articles
    """
    
    from risk_scorer_agent import RiskScorerAgent
    
    # Set default paths
    current_dir = Path(__file__).parent.parent
    knowledge_path = current_dir / "knowledge" / "company.json"
    
    if data_directory is None:
        data_dir = current_dir / "agents" / "finance_scrapper" / "data"
    else:
        data_dir = Path(data_directory)
    
    try:
        # Initialize agent
        agent = RiskScorerAgent(str(knowledge_path), str(data_dir))
        
        # Process all news
        agent.process_all_news()
        
        # Generate summary report
        summary = agent.generate_summary_report()
        
        return summary
        
    except Exception as e:
        return {
            "error": f"Failed to analyze news: {str(e)}",
            "total_articles_analyzed": 0
        }


@tool
def get_high_risk_alerts(
    risk_threshold: float = 0.7,
    data_directory: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get alerts for high-risk news articles above a specified threshold.
    
    Args:
        risk_threshold: Minimum risk score to include (default: 0.7)
        data_directory: Optional path to directory containing news JSON files
    
    Returns:
        Dictionary containing:
        - alert_count: number of high-risk articles found
        - threshold_used: the risk threshold applied
        - high_risk_articles: list of articles with details
    """
    
    from risk_scorer_agent import RiskScorerAgent
    
    # Set default paths
    current_dir = Path(__file__).parent.parent
    knowledge_path = current_dir / "knowledge" / "company.json"
    
    if data_directory is None:
        data_dir = current_dir / "agents" / "finance_scrapper" / "data"
    else:
        data_dir = Path(data_directory)
    
    try:
        # Initialize agent
        agent = RiskScorerAgent(str(knowledge_path), str(data_dir))
        
        # Process all news
        agent.process_all_news()
        
        # Filter high-risk articles
        high_risk = [
            {
                "title": r.get('article_title', 'No title'),
                "risk_score": r['risk_score'],
                "sentiment": r['sentiment_label'],
                "risk_category": r.get('risk_category', []),
                "source": r.get('original_source', 'unknown'),
                "reasoning": r.get('reasoning', '')
            }
            for r in agent.results
            if r['risk_score'] >= risk_threshold
        ]
        
        # Sort by risk score descending
        high_risk.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return {
            "alert_count": len(high_risk),
            "threshold_used": risk_threshold,
            "high_risk_articles": high_risk
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get alerts: {str(e)}",
            "alert_count": 0,
            "threshold_used": risk_threshold,
            "high_risk_articles": []
        }
