"""
IBM Watsonx Orchestrate Tool: Feed Poster
@tool decorated functions for creating social media feed posts from risk assessments.
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from pathlib import Path
import sys
import json

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(parent_dir))

from feed_poster import FeedPoster


@tool
def create_feed_post_from_article(
    article_json: str,
    creative_title: str = "",
    creative_content: str = "",
    title_style: str = "engaging"
) -> str:
    """
    Create a single engaging feed post from an article with LLM-generated creative content.
    
    Args:
        article_json: JSON string of article data from risk assessment
        creative_title: LLM-generated creative, attention-grabbing title
        creative_content: LLM-generated engaging content summary
        title_style: Style if auto-generating (engaging, urgent, informative, clickbait)
    
    Returns:
        JSON string with complete feed post data
    
    Example:
        article = '{"title": "Market Crash", "risk_analysis": {...}}'
        title = "🚨 ALERT: Markets Tumble as Investors Panic - What You Need to Know!"
        content = "Breaking: Major market downturn shakes investor confidence..."
        result = create_feed_post_from_article(article, title, content)
    """
    poster = FeedPoster()
    
    # Parse article
    article = json.loads(article_json)
    
    # Create post with LLM-provided content
    post = poster.create_feed_post(
        article,
        title_style=title_style,
        custom_title=creative_title if creative_title else None,
        custom_content=creative_content if creative_content else None
    )
    
    return json.dumps(post, indent=2, ensure_ascii=False)


@tool
def generate_complete_feed(
    assessment_file_path: str,
    max_posts: int = 10,
    min_risk_score: float = 0.3
) -> str:
    """
    Generate complete social media feed from risk assessment results.
    Processes all articles and creates prioritized feed posts.
    
    Args:
        assessment_file_path: Path to risk_assessment_results.json
        max_posts: Maximum number of posts to generate
        min_risk_score: Minimum risk score threshold (0.0 to 1.0)
    
    Returns:
        JSON string with feed metadata and all posts
    
    Example:
        path = "agents/risk_agent/risk_assessment_results.json"
        result = generate_complete_feed(path, max_posts=15, min_risk_score=0.4)
    """
    poster = FeedPoster()
    feed_data = poster.generate_feed_from_assessment(
        assessment_file_path,
        max_posts=max_posts,
        min_risk_score=min_risk_score
    )
    
    return json.dumps(feed_data, indent=2, ensure_ascii=False)


@tool
def analyze_article_for_feed(
    article_json: str
) -> str:
    """
    Analyze an article and return suggestions for creating an engaging feed post.
    Provides insights for LLM to generate creative titles and content.
    
    Args:
        article_json: JSON string of article data
    
    Returns:
        JSON string with analysis and suggestions
    
    Example:
        article = '{"title": "Tech IPO Success", "risk_analysis": {...}}'
        suggestions = analyze_article_for_feed(article)
    """
    article = json.loads(article_json)
    poster = FeedPoster()
    
    risk_analysis = article.get('risk_analysis', {})
    
    analysis = {
        "article_summary": {
            "original_title": article.get('title', ''),
            "source": article.get('source', ''),
            "risk_score": risk_analysis.get('risk_score', 0),
            "sentiment": risk_analysis.get('sentiment_label', 'neutral'),
            "risk_categories": risk_analysis.get('risk_category', [])
        },
        "content_suggestions": {
            "key_insights": poster._extract_key_insights(article),
            "recommended_hashtags": poster._generate_hashtags(article),
            "target_audience": poster._determine_target_audience(article),
            "posting_urgency": poster._suggest_posting_time(article),
            "priority_level": poster._determine_feed_priority(article)
        },
        "creative_guidance": {
            "tone": "urgent" if risk_analysis.get('risk_score', 0) >= 0.7 else "informative",
            "emphasis": "high risk" if risk_analysis.get('risk_score', 0) >= 0.7 else "moderate risk",
            "suggested_emoji": "🚨" if risk_analysis.get('risk_score', 0) >= 0.7 else "📊",
            "content_angle": f"Focus on {', '.join(risk_analysis.get('risk_category', [])[:2])} risks"
        },
        "media_selection": {
            "primary_image": poster._select_primary_image(article),
            "has_images": len(article.get('graphs_images', [])) > 0,
            "has_tables": len(article.get('relevant_tables', [])) > 0
        }
    }
    
    return json.dumps(analysis, indent=2, ensure_ascii=False)


@tool
def get_feed_statistics(
    feed_json: str
) -> str:
    """
    Get statistics and insights from generated feed data.
    
    Args:
        feed_json: JSON string of feed data
    
    Returns:
        JSON string with feed statistics
    
    Example:
        feed = '{"posts": [...], "summary": {...}}'
        stats = get_feed_statistics(feed)
    """
    feed_data = json.loads(feed_json)
    posts = feed_data.get('posts', [])
    
    # Calculate statistics
    sentiment_dist = {}
    category_dist = {}
    priority_dist = {'high': 0, 'medium': 0, 'low': 0}
    
    for post in posts:
        # Sentiment distribution
        sentiment = post.get('risk_metadata', {}).get('sentiment', 'neutral')
        sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1
        
        # Category distribution
        categories = post.get('risk_metadata', {}).get('risk_category', [])
        for cat in categories:
            category_dist[cat] = category_dist.get(cat, 0) + 1
        
        # Priority distribution
        priority = post.get('risk_metadata', {}).get('priority', 'low')
        priority_dist[priority] = priority_dist.get(priority, 0) + 1
    
    stats = {
        "total_posts": len(posts),
        "sentiment_distribution": sentiment_dist,
        "risk_category_distribution": category_dist,
        "priority_distribution": priority_dist,
        "average_risk_score": sum(
            p.get('risk_metadata', {}).get('risk_score', 0) for p in posts
        ) / len(posts) if posts else 0,
        "posts_with_images": sum(
            1 for p in posts if p.get('primary_image')
        )
    }
    
    return json.dumps(stats, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Test the tools
    print("Testing Feed Poster Tools\n")
    
    # Check if risk assessment exists
    assessment_path = Path(__file__).parent.parent / "agents" / "risk_agent" / "risk_assessment_results.json"
    
    if assessment_path.exists():
        print("=== Test: Generate Complete Feed ===")
        result = generate_complete_feed(str(assessment_path), max_posts=5, min_risk_score=0.4)
        feed_data = json.loads(result)
        print(f"Generated {feed_data.get('feed_metadata', {}).get('total_posts', 0)} posts")
        print(f"High priority: {feed_data.get('summary', {}).get('high_priority_posts', 0)}")
        print("\n✅ Tool tests complete!")
    else:
        print("⚠️ Risk assessment results not found. Run risk_scorer_agent.py first.")
