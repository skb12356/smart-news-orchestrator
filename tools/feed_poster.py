"""
Feed Poster Tool for IBM Watsonx Orchestrate
Analyzes risk assessment articles and creates engaging social media feed posts.
Generates creative titles, content summaries, and selects images.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import random

class FeedPoster:
    """
    Analyzes articles from risk assessment and creates social media feed posts.
    LLM will use this to generate creative titles, content, and select images.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the feed poster.
        
        Args:
            output_dir: Directory to save feed.json (default: agents/feeds/)
        """
        if output_dir is None:
            base_path = Path(__file__).resolve().parents[1]
            output_dir = base_path / "agents" / "feeds"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_creative_title(self, article: Dict[str, Any], style: str = "engaging") -> str:
        """
        Generate a creative title based on article content and risk analysis.
        This is a fallback - LLM will generate better titles.
        
        Args:
            article: Article data with risk_analysis
            style: Title style (engaging, urgent, informative, clickbait)
        
        Returns:
            Creative title string
        """
        risk_analysis = article.get('risk_analysis', {})
        risk_score = risk_analysis.get('risk_score', 0)
        sentiment = risk_analysis.get('sentiment_label', 'neutral')
        categories = risk_analysis.get('risk_category', [])
        
        original_title = article.get('title', 'Breaking News')
        
        # Title prefixes based on risk and sentiment
        prefixes = {
            'high_risk': ['🚨 ALERT:', '⚠️ WARNING:', '🔴 URGENT:', '💥 BREAKING:'],
            'medium_risk': ['📊 UPDATE:', '📈 TRENDING:', '🎯 FOCUS:', '💼 BUSINESS:'],
            'low_risk': ['✅ INSIGHT:', '📰 NEWS:', '💡 ANALYSIS:', '🌟 SPOTLIGHT:']
        }
        
        # Determine risk level
        if risk_score >= 0.7:
            prefix_list = prefixes['high_risk']
        elif risk_score >= 0.4:
            prefix_list = prefixes['medium_risk']
        else:
            prefix_list = prefixes['low_risk']
        
        prefix = random.choice(prefix_list)
        
        # Style variations
        if style == "clickbait":
            templates = [
                f"{prefix} You Won't Believe What Happened with {original_title[:50]}!",
                f"{prefix} This Changes Everything: {original_title[:50]}",
                f"{prefix} What {original_title[:30]} Really Means for You"
            ]
            return random.choice(templates)
        elif style == "urgent":
            return f"{prefix} {original_title[:70]}"
        elif style == "informative":
            if categories:
                return f"{prefix} {categories[0].upper()} Risk - {original_title[:60]}"
            return f"{prefix} {original_title[:70]}"
        else:  # engaging
            return f"{prefix} {original_title[:70]}"
    
    def _extract_key_insights(self, article: Dict[str, Any], max_points: int = 3) -> List[str]:
        """
        Extract key insights from article content and risk analysis.
        
        Args:
            article: Article data
            max_points: Maximum number of key points
        
        Returns:
            List of key insight strings
        """
        risk_analysis = article.get('risk_analysis', {})
        insights = []
        
        # Insight 1: Risk level
        risk_score = risk_analysis.get('risk_score', 0)
        sentiment = risk_analysis.get('sentiment_label', 'neutral')
        if risk_score >= 0.7:
            insights.append(f"⚠️ High risk detected: {risk_score:.0%} risk score")
        elif risk_score >= 0.4:
            insights.append(f"📊 Moderate risk: {risk_score:.0%} risk score")
        else:
            insights.append(f"✅ Low risk: {risk_score:.0%} risk score")
        
        # Insight 2: Sentiment
        sentiment_emoji = {'positive': '📈', 'negative': '📉', 'neutral': '➡️'}
        emoji = sentiment_emoji.get(sentiment, '📰')
        insights.append(f"{emoji} Sentiment: {sentiment.upper()}")
        
        # Insight 3: Risk categories
        categories = risk_analysis.get('risk_category', [])
        if categories:
            cat_str = ', '.join(c.capitalize() for c in categories[:2])
            insights.append(f"🎯 Focus areas: {cat_str}")
        
        # Insight 4: Matched keywords
        keywords = risk_analysis.get('matched_keywords', [])
        if keywords and len(insights) < max_points:
            kw_str = ', '.join(keywords[:3])
            insights.append(f"🔑 Key topics: {kw_str}")
        
        return insights[:max_points]
    
    def _select_primary_image(self, article: Dict[str, Any]) -> Optional[str]:
        """
        Select the best primary image from article's graphs_images.
        
        Args:
            article: Article data with graphs_images
        
        Returns:
            Image URL or chart path
        """
        # Priority 1: Generated charts (if any)
        # Priority 2: Article images
        
        graphs_images = article.get('graphs_images', [])
        
        if graphs_images and isinstance(graphs_images, list):
            # Filter out tracking pixels and tiny images
            valid_images = [
                img for img in graphs_images
                if isinstance(img, str) and 
                not ('scorecardresearch' in img.lower() or 
                     'tracking' in img.lower() or
                     img.endswith('1x1.gif'))
            ]
            
            if valid_images:
                return valid_images[0]  # Return first valid image
        
        return None
    
    def _generate_content_summary(self, article: Dict[str, Any], max_length: int = 280) -> str:
        """
        Generate a concise content summary for the feed.
        
        Args:
            article: Article data
            max_length: Maximum character length
        
        Returns:
            Content summary string
        """
        risk_analysis = article.get('risk_analysis', {})
        summary = risk_analysis.get('summary', '')
        
        # If summary exists and is good length
        if summary and len(summary) <= max_length:
            return summary
        
        # Truncate if too long
        if summary:
            return summary[:max_length - 3] + "..."
        
        # Fallback to article content
        content = article.get('content_text', '')
        if content:
            return content[:max_length - 3] + "..."
        
        return "No summary available."
    
    def _determine_feed_priority(self, article: Dict[str, Any]) -> str:
        """
        Determine feed priority (high, medium, low) based on risk score.
        
        Args:
            article: Article data with risk_analysis
        
        Returns:
            Priority level string
        """
        risk_analysis = article.get('risk_analysis', {})
        risk_score = risk_analysis.get('risk_score', 0)
        
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def create_feed_post(self,
                        article: Dict[str, Any],
                        title_style: str = "engaging",
                        custom_title: str = None,
                        custom_content: str = None) -> Dict[str, Any]:
        """
        Create a single feed post from an article.
        
        Args:
            article: Article data from risk_assessment_results.json
            title_style: Style for auto-generated title
            custom_title: Override with custom title (LLM-generated)
            custom_content: Override with custom content (LLM-generated)
        
        Returns:
            Feed post dictionary
        """
        # Generate creative title (or use custom)
        title = custom_title if custom_title else self._generate_creative_title(article, title_style)
        
        # Generate content (or use custom)
        content = custom_content if custom_content else self._generate_content_summary(article)
        
        # Extract metadata
        risk_analysis = article.get('risk_analysis', {})
        
        feed_post = {
            "post_id": f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": title,
            "content": content,
            "key_insights": self._extract_key_insights(article),
            "source": article.get('source', 'unknown'),
            "source_url": article.get('url', ''),
            "published_time": article.get('published_time', ''),
            "primary_image": self._select_primary_image(article),
            "risk_metadata": {
                "risk_score": risk_analysis.get('risk_score', 0),
                "risk_category": risk_analysis.get('risk_category', []),
                "sentiment": risk_analysis.get('sentiment_label', 'neutral'),
                "priority": self._determine_feed_priority(article)
            },
            "engagement_metadata": {
                "recommended_hashtags": self._generate_hashtags(article),
                "target_audience": self._determine_target_audience(article),
                "best_posting_time": self._suggest_posting_time(article)
            },
            "created_at": datetime.now().isoformat()
        }
        
        return feed_post
    
    def _generate_hashtags(self, article: Dict[str, Any], max_tags: int = 5) -> List[str]:
        """Generate relevant hashtags based on article content."""
        risk_analysis = article.get('risk_analysis', {})
        categories = risk_analysis.get('risk_category', [])
        keywords = risk_analysis.get('matched_keywords', [])
        
        hashtags = set()
        
        # Add risk categories as hashtags
        for cat in categories:
            hashtags.add(f"#{cat.capitalize()}Risk")
        
        # Add general tags
        sentiment = risk_analysis.get('sentiment_label', '')
        if sentiment == 'negative':
            hashtags.add("#MarketAlert")
        elif sentiment == 'positive':
            hashtags.add("#MarketGrowth")
        
        # Add company/product tags from keywords
        for kw in keywords[:3]:
            if ':' not in kw:  # Skip "competitor: X" format
                clean_kw = kw.replace(' ', '').replace('-', '')
                hashtags.add(f"#{clean_kw}")
        
        # Add general finance tags
        hashtags.add("#Finance")
        hashtags.add("#MarketNews")
        
        return list(hashtags)[:max_tags]
    
    def _determine_target_audience(self, article: Dict[str, Any]) -> str:
        """Determine target audience based on content."""
        risk_analysis = article.get('risk_analysis', {})
        categories = risk_analysis.get('risk_category', [])
        
        if 'financial' in categories:
            return "investors, traders, financial analysts"
        elif 'regulatory' in categories:
            return "compliance officers, legal teams, executives"
        elif 'competitive' in categories:
            return "business strategists, market analysts, executives"
        elif 'operational' in categories:
            return "operations managers, supply chain professionals"
        else:
            return "general business audience, investors"
    
    def _suggest_posting_time(self, article: Dict[str, Any]) -> str:
        """Suggest optimal posting time based on content urgency."""
        risk_analysis = article.get('risk_analysis', {})
        risk_score = risk_analysis.get('risk_score', 0)
        
        if risk_score >= 0.7:
            return "immediate - high urgency"
        elif risk_score >= 0.4:
            return "within 2 hours - moderate urgency"
        else:
            return "next scheduled posting window - low urgency"
    
    def generate_feed_from_assessment(self,
                                     assessment_file: str,
                                     max_posts: int = 10,
                                     min_risk_score: float = 0.0,
                                     output_file: str = "feed.json") -> Dict[str, Any]:
        """
        Generate feed posts from risk assessment results.
        
        Args:
            assessment_file: Path to risk_assessment_results.json
            max_posts: Maximum number of posts to generate
            min_risk_score: Minimum risk score to include
            output_file: Output filename for feed.json
        
        Returns:
            Feed data dictionary
        """
        # Load assessment results
        assessment_path = Path(assessment_file)
        if not assessment_path.exists():
            return {
                "error": "Assessment file not found",
                "details": f"File {assessment_file} does not exist"
            }
        
        with open(assessment_path, 'r', encoding='utf-8') as f:
            assessment_data = json.load(f)
        
        articles = assessment_data.get('detailed_results', [])
        
        # Filter by risk score
        filtered_articles = [
            article for article in articles
            if article.get('risk_analysis', {}).get('risk_score', 0) >= min_risk_score
        ]
        
        # Sort by risk score (highest first)
        sorted_articles = sorted(
            filtered_articles,
            key=lambda x: x.get('risk_analysis', {}).get('risk_score', 0),
            reverse=True
        )
        
        # Generate feed posts
        feed_posts = []
        for idx, article in enumerate(sorted_articles[:max_posts], 1):
            post = self.create_feed_post(article)
            post['post_id'] = f"post_{idx}"
            feed_posts.append(post)
        
        # Create feed metadata
        feed_data = {
            "feed_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_posts": len(feed_posts),
                "source_file": str(assessment_file),
                "filters": {
                    "min_risk_score": min_risk_score,
                    "max_posts": max_posts
                }
            },
            "summary": {
                "high_priority_posts": sum(1 for p in feed_posts if p['risk_metadata']['priority'] == 'high'),
                "medium_priority_posts": sum(1 for p in feed_posts if p['risk_metadata']['priority'] == 'medium'),
                "low_priority_posts": sum(1 for p in feed_posts if p['risk_metadata']['priority'] == 'low'),
                "avg_risk_score": sum(p['risk_metadata']['risk_score'] for p in feed_posts) / len(feed_posts) if feed_posts else 0
            },
            "posts": feed_posts
        }
        
        # Save to file
        output_path = self.output_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(feed_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Feed generated successfully!")
        print(f"📁 Saved to: {output_path}")
        print(f"📊 Total posts: {len(feed_posts)}")
        print(f"🔴 High priority: {feed_data['summary']['high_priority_posts']}")
        print(f"🟡 Medium priority: {feed_data['summary']['medium_priority_posts']}")
        print(f"🟢 Low priority: {feed_data['summary']['low_priority_posts']}")
        
        return feed_data


def main():
    """Test the feed poster with sample data."""
    print("=" * 70)
    print("Feed Poster - Testing")
    print("=" * 70)
    
    poster = FeedPoster()
    
    # Check if risk assessment results exist
    assessment_path = Path(__file__).parent.parent / "agents" / "risk_agent" / "risk_assessment_results.json"
    
    if not assessment_path.exists():
        print("\n⚠️ Risk assessment results not found.")
        print("Run: python agents/risk_scorer_agent.py first")
        return
    
    # Generate feed from assessment
    feed_data = poster.generate_feed_from_assessment(
        str(assessment_path),
        max_posts=10,
        min_risk_score=0.3
    )
    
    # Display sample posts
    if feed_data.get('posts'):
        print("\n" + "=" * 70)
        print("Sample Feed Posts:")
        print("=" * 70)
        
        for post in feed_data['posts'][:3]:
            print(f"\n📰 {post['title']}")
            print(f"   Priority: {post['risk_metadata']['priority'].upper()}")
            print(f"   Risk Score: {post['risk_metadata']['risk_score']:.2f}")
            print(f"   Sentiment: {post['risk_metadata']['sentiment']}")
            print(f"   Content: {post['content'][:100]}...")
            print(f"   Hashtags: {', '.join(post['engagement_metadata']['recommended_hashtags'][:3])}")


if __name__ == "__main__":
    main()
