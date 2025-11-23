"""
Risk Scorer Tool for IBM Orchestrate ADK
Analyzes news articles and assigns risk scores based on company knowledge
"""

import json
import re
from typing import Dict, List, Any, Optional


class RiskScorer:
    """
    Risk Scorer Tool that analyzes news articles against company knowledge
    and generates risk scores with sentiment analysis
    """
    
    def __init__(self, company_knowledge: Dict[str, Any]):
        """
        Initialize the Risk Scorer with company knowledge
        
        Args:
            company_knowledge: Dictionary containing company.json data
        """
        self.company = company_knowledge.get('company', {})
        self.risk_keywords = company_knowledge.get('risk_keywords', {})
        self.competitors = company_knowledge.get('competitors', [])
        self.product_keywords = company_knowledge.get('product_keywords', {})
        self.sensitive_topics = company_knowledge.get('sensitive_topics', [])
        self.stock_context = company_knowledge.get('stock_context', {})
        
        # Build flat keyword lists for matching
        self._build_keyword_indices()
    
    def _build_keyword_indices(self):
        """Build flattened keyword lists for efficient matching"""
        # Flatten all risk keywords into one list with category tags
        self.all_risk_keywords = {}
        for category, keywords in self.risk_keywords.items():
            for keyword in keywords:
                self.all_risk_keywords[keyword.lower()] = category
        
        # Flatten all product keywords
        self.all_product_keywords = []
        for category, keywords in self.product_keywords.items():
            self.all_product_keywords.extend([k.lower() for k in keywords])
        
        # Competitor names
        self.competitor_names = [c['name'].lower() for c in self.competitors]
        
        # Sensitive topics
        self.sensitive_keywords = [s.lower() for s in self.sensitive_topics]
    
    def _calculate_sentiment(self, text: str) -> tuple[str, float]:
        """
        Calculate sentiment label and score from text
        
        Args:
            text: Article text content
            
        Returns:
            Tuple of (sentiment_label, sentiment_score)
        """
        text_lower = text.lower()
        
        # Negative indicators
        negative_words = [
            'loss', 'fail', 'decline', 'drop', 'plunge', 'crash', 'down',
            'fell', 'slump', 'weak', 'poor', 'miss', 'delay', 'shortage',
            'risk', 'threat', 'concern', 'worry', 'problem', 'issue',
            'lawsuit', 'sue', 'fine', 'penalty', 'ban', 'violation',
            'breach', 'hack', 'attack', 'strike', 'layoff', 'cut'
        ]
        
        # Positive indicators
        positive_words = [
            'gain', 'rise', 'growth', 'increase', 'surge', 'jump', 'up',
            'beat', 'strong', 'robust', 'excellent', 'success', 'win',
            'profit', 'revenue', 'expansion', 'launch', 'innovation',
            'partnership', 'deal', 'agreement', 'boost', 'improve'
        ]
        
        # Neutral indicators
        neutral_words = [
            'stable', 'maintain', 'hold', 'steady', 'continue', 'remain'
        ]
        
        # Count occurrences
        neg_count = sum(1 for word in negative_words if word in text_lower)
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neutral_count = sum(1 for word in neutral_words if word in text_lower)
        
        total_count = neg_count + pos_count + neutral_count
        
        if total_count == 0:
            return "neutral", 0.0
        
        # Calculate raw score
        score = (pos_count - neg_count) / total_count
        
        # Determine label
        if score < -0.2:
            label = "negative"
        elif score > 0.2:
            label = "positive"
        else:
            label = "neutral"
        
        # Normalize score to -1 to +1 range
        normalized_score = max(-1.0, min(1.0, score))
        
        return label, normalized_score
    
    def _match_keywords(self, text: str) -> tuple[List[str], List[str]]:
        """
        Match keywords from company knowledge in the text
        
        Args:
            text: Article text content
            
        Returns:
            Tuple of (matched_keywords, risk_categories)
        """
        text_lower = text.lower()
        matched = []
        categories = set()
        
        # Match risk keywords
        for keyword, category in self.all_risk_keywords.items():
            if keyword in text_lower:
                matched.append(keyword)
                categories.add(category)
        
        # Match sensitive topics
        for keyword in self.sensitive_keywords:
            if keyword in text_lower:
                matched.append(keyword)
                categories.add("sensitive")
        
        # Match product keywords
        for keyword in self.all_product_keywords:
            if keyword in text_lower:
                matched.append(keyword)
        
        return matched, list(categories)
    
    def _calculate_risk_score(
        self,
        sentiment_score: float,
        matched_keywords: List[str],
        risk_categories: List[str]
    ) -> float:
        """
        Calculate risk score based on sentiment and keywords
        
        Formula:
        - Base score = abs(sentiment_score)
        - If negative sentiment → risk increases
        - If positive → risk reduces significantly
        - Add +0.1 for each matched risk keyword
        - Clamp to maximum of 1.0
        
        Args:
            sentiment_score: Sentiment score (-1 to +1)
            matched_keywords: List of matched keywords
            risk_categories: List of risk categories detected
            
        Returns:
            Risk score (0 to 1)
        """
        # If negative sentiment, increase risk
        if sentiment_score < 0:
            # Negative news = higher risk
            base_score = abs(sentiment_score) * 0.6
        elif sentiment_score > 0:
            # Positive sentiment reduces risk significantly
            base_score = abs(sentiment_score) * 0.1
        else:
            # Neutral
            base_score = 0.2
        
        # Add points for each matched keyword (capped)
        keyword_penalty = min(0.4, len(matched_keywords) * 0.1)
        risk_score = base_score + keyword_penalty
        
        # Add points for risk categories
        category_penalty = len(risk_categories) * 0.1
        risk_score += category_penalty
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, risk_score))
    
    def _generate_summary(self, text: str, max_sentences: int = 4) -> str:
        """
        Generate a clean 3-5 line summary of the article
        
        Args:
            text: Full article text
            max_sentences: Maximum number of sentences
            
        Returns:
            Summarized text
        """
        # Split into sentences (simple approach)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Take first few sentences
        summary_sentences = sentences[:max_sentences]
        summary = '. '.join(summary_sentences)
        
        # Ensure it ends with a period
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return summary[:500]  # Limit to 500 chars
    
    def _generate_reasoning(
        self,
        sentiment_label: str,
        risk_categories: List[str],
        matched_keywords: List[str]
    ) -> str:
        """
        Generate reasoning for the risk score
        
        Args:
            sentiment_label: Positive, neutral, or negative
            risk_categories: List of risk categories
            matched_keywords: List of matched keywords
            
        Returns:
            Reasoning text
        """
        parts = []
        
        # Sentiment
        parts.append(f"The tone is {sentiment_label}")
        
        # Categories
        if risk_categories:
            categories_str = ', '.join(risk_categories)
            parts.append(f"involves {categories_str} concerns")
        
        # Keywords
        if matched_keywords:
            top_keywords = matched_keywords[:3]
            keywords_str = ', '.join(top_keywords)
            parts.append(f"with keywords: {keywords_str}")
        
        reasoning = ' and '.join(parts) + '.'
        return reasoning[:250]  # Limit to 250 chars
    
    def analyze_article(
        self,
        article: Dict[str, Any],
        previous_risk_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single news article and return risk assessment
        
        Args:
            article: Dictionary containing article data with keys:
                    - content_text or article_text: main content
                    - source: source name
                    - published_time or published: publication time
                    - title (optional)
                    - risk_tags_detected (optional): pre-detected risk keywords
                    - sentiment (optional): pre-detected sentiment
                    - competitor_mentions (optional): detected competitors
            previous_risk_context: Optional previous risk context
            
        Returns:
            Dictionary with risk assessment following the output schema
        """
        # Extract article text
        article_text = article.get('content_text') or article.get('article_text', '')
        title = article.get('title', '')
        full_text = f"{title} {article_text}"
        
        # Skip "Access Denied" error pages
        if "Access Denied" in title or "access denied" in article_text.lower()[:100]:
            return {
                "summary": "Skipped: Access denied error page (not real content)",
                "sentiment_label": "neutral",
                "sentiment_score": 0.0,
                "risk_category": [],
                "risk_score": 0.0,
                "matched_keywords": [],
                "reasoning": "Article skipped - scraper encountered access denial",
                "skipped": True
            }
        
        if not full_text.strip():
            # Return neutral result if no content
            return {
                "summary": "No content available for analysis.",
                "sentiment_label": "neutral",
                "sentiment_score": 0.0,
                "risk_category": [],
                "risk_score": 0.0,
                "matched_keywords": [],
                "reasoning": "No content available for analysis."
            }
        
        # Calculate sentiment
        sentiment_label, sentiment_score = self._calculate_sentiment(full_text)
        
        # Use pre-detected sentiment from scraper if available
        if article.get('sentiment'):
            scraper_sentiment = article['sentiment'].lower()
            if scraper_sentiment in ['positive', 'neutral', 'negative']:
                sentiment_label = scraper_sentiment
                # Map label to score
                if scraper_sentiment == 'positive':
                    sentiment_score = 0.5
                elif scraper_sentiment == 'negative':
                    sentiment_score = -0.5
                else:
                    sentiment_score = 0.0
        
        # Match keywords
        matched_keywords, risk_categories = self._match_keywords(full_text)
        
        # Enhance with pre-detected risk tags from scraper
        if article.get('risk_tags_detected'):
            scraper_keywords = article['risk_tags_detected']
            # Add scraper keywords that aren't already matched
            for keyword in scraper_keywords:
                if keyword.lower() not in [k.lower() for k in matched_keywords]:
                    matched_keywords.append(keyword.lower())
                # Update categories based on scraper keywords
                for cat, keywords in self.risk_keywords.items():
                    if keyword.lower() in [k.lower() for k in keywords]:
                        if cat not in risk_categories:
                            risk_categories.append(cat)
        
        # Add competitor information
        if article.get('competitor_mentions'):
            for competitor in article['competitor_mentions']:
                if competitor.lower() not in [k.lower() for k in matched_keywords]:
                    matched_keywords.append(f"competitor: {competitor}")
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(
            sentiment_score,
            matched_keywords,
            risk_categories
        )
        
        # Generate summary
        summary = self._generate_summary(article_text or title)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            sentiment_label,
            risk_categories,
            matched_keywords
        )
        
        # Build enriched result - PRESERVE ALL original scraper data
        # Start with a copy of the original article to keep all fields
        result = {}
        
        # First, add ALL original fields from the article
        for key, value in article.items():
            # Skip internal fields that shouldn't be in output
            if key not in ['article_text']:  # Keep content_text but remove article_text alias
                result[key] = value
        
        # Now ADD (not replace) our risk analysis fields
        result['risk_analysis'] = {
            "summary": summary,
            "sentiment_label": sentiment_label,
            "sentiment_score": round(sentiment_score, 2),
            "risk_category": risk_categories,
            "risk_score": round(risk_score, 2),
            "matched_keywords": matched_keywords[:10],
            "reasoning": reasoning
        }
        
        return result


def load_company_knowledge(knowledge_path: str) -> Dict[str, Any]:
    """
    Load company knowledge from JSON file
    
    Args:
        knowledge_path: Path to company.json file
        
    Returns:
        Company knowledge dictionary
    """
    with open(knowledge_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_news_articles(news_path: str) -> List[Dict[str, Any]]:
    """
    Load news articles from JSON file
    
    Args:
        news_path: Path to news JSON file
        
    Returns:
        List of news articles
    """
    with open(news_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def score_article(
    article_text: str,
    company_knowledge_path: str,
    source: str = "unknown",
    published: str = "unknown"
) -> Dict[str, Any]:
    """
    Convenience function to score a single article
    
    Args:
        article_text: The article text content
        company_knowledge_path: Path to company.json
        source: Source of the article
        published: Publication time
        
    Returns:
        Risk assessment dictionary
    """
    knowledge = load_company_knowledge(company_knowledge_path)
    scorer = RiskScorer(knowledge)
    
    article = {
        "article_text": article_text,
        "source": source,
        "published": published
    }
    
    return scorer.analyze_article(article)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python risk_scorer.py <company_knowledge.json> <news_file.json>")
        sys.exit(1)
    
    knowledge_path = sys.argv[1]
    news_path = sys.argv[2]
    
    # Load data
    knowledge = load_company_knowledge(knowledge_path)
    articles = load_news_articles(news_path)
    
    # Create scorer
    scorer = RiskScorer(knowledge)
    
    # Analyze all articles
    results = []
    for article in articles[:5]:  # Process first 5 articles as example
        result = scorer.analyze_article(article)
        results.append(result)
        print(json.dumps(result, indent=2))
        print("-" * 80)
