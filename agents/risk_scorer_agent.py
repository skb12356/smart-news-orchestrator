"""
Risk Scorer Agent for IBM Orchestrate ADK
Main agent file that processes news articles and assigns risk scores
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add tools directory to path
tools_dir = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

from risk_scorer import RiskScorer, load_company_knowledge, load_news_articles


class RiskScorerAgent:
    """
    Risk Scorer Agent that processes news articles from multiple sources
    and generates comprehensive risk assessments
    """
    
    def __init__(self, knowledge_path: str, data_dir: str):
        """
        Initialize the Risk Scorer Agent
        
        Args:
            knowledge_path: Path to company.json knowledge file
            data_dir: Directory containing news JSON files
        """
        self.knowledge_path = knowledge_path
        self.data_dir = Path(data_dir)
        
        # Load company knowledge
        self.company_knowledge = load_company_knowledge(knowledge_path)
        
        # Initialize risk scorer
        self.scorer = RiskScorer(self.company_knowledge)
        
        # Track processed articles
        self.processed_count = 0
        self.skipped_count = 0
        self.results = []
    
    def process_news_file(self, news_file_path: str) -> List[Dict[str, Any]]:
        """
        Process all articles from a single news file
        
        Args:
            news_file_path: Path to news JSON file
            
        Returns:
            List of risk assessment results
        """
        print(f"Processing: {news_file_path}")
        
        try:
            articles = load_news_articles(news_file_path)
            file_results = []
            
            for idx, article in enumerate(articles, 1):
                try:
                    # Analyze article
                    result = self.scorer.analyze_article(article)
                    
                    # Skip if marked as skipped (e.g., Access Denied pages)
                    if result.get('skipped'):
                        self.skipped_count += 1
                        continue
                    
                    # Add minimal metadata (article already has all its original fields)
                    result['_analysis_metadata'] = {
                        "article_index": idx,
                        "source_file": Path(news_file_path).name,
                        "analyzed_at": "2025-11-22"
                    }
                    
                    file_results.append(result)
                    self.processed_count += 1
                    
                except Exception as e:
                    print(f"Error processing article {idx}: {str(e)}")
                    continue
            
            return file_results
            
        except Exception as e:
            print(f"Error reading file {news_file_path}: {str(e)}")
            return []
    
    def process_all_news(self) -> List[Dict[str, Any]]:
        """
        Process all news files in the data directory
        
        Returns:
            List of all risk assessment results
        """
        all_results = []
        
        # Find all JSON files in data directory
        news_files = [
            self.data_dir / "finance_news.json",
            self.data_dir / "market_news.json",
            self.data_dir / "industry_news.json",
            self.data_dir / "linkedin_news.json"
        ]
        
        for news_file in news_files:
            if news_file.exists():
                results = self.process_news_file(str(news_file))
                all_results.extend(results)
            else:
                print(f"File not found: {news_file}")
        
        self.results = all_results
        return all_results
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of all risk assessments
        
        Returns:
            Summary statistics and insights
        """
        if not self.results:
            return {
                "error": "No results to summarize",
                "total_articles": 0
            }
        
        # Calculate statistics
        total_articles = len(self.results)
        
        # Sentiment distribution
        sentiment_counts = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }
        
        # Risk category distribution
        risk_category_counts = {
            "financial": 0,
            "operational": 0,
            "competitive": 0,
            "regulatory": 0,
            "sensitive": 0
        }
        
        # Risk score statistics
        risk_scores = []
        high_risk_articles = []
        
        for result in self.results:
            # Get risk analysis data
            risk_analysis = result.get('risk_analysis', {})
            
            # Sentiment
            sentiment_label = risk_analysis.get('sentiment_label', 'neutral')
            if sentiment_label in sentiment_counts:
                sentiment_counts[sentiment_label] += 1
            
            # Risk categories
            for category in risk_analysis.get('risk_category', []):
                if category in risk_category_counts:
                    risk_category_counts[category] += 1
            
            # Risk scores
            risk_score = risk_analysis.get('risk_score', 0)
            risk_scores.append(risk_score)
            
            # High risk articles (score >= 0.7)
            if risk_score >= 0.7:
                high_risk_articles.append({
                    "title": result.get('title', 'No title'),
                    "risk_score": risk_score,
                    "risk_category": risk_analysis.get('risk_category', []),
                    "sentiment": sentiment_label,
                    "source": result.get('source', 'unknown')
                })
        
        # Calculate average risk score
        avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        # Sort high risk articles by score
        high_risk_articles.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return {
            "total_articles_analyzed": total_articles,
            "sentiment_distribution": sentiment_counts,
            "risk_category_distribution": risk_category_counts,
            "average_risk_score": round(avg_risk_score, 2),
            "high_risk_articles_count": len(high_risk_articles),
            "top_high_risk_articles": high_risk_articles[:10],
            "company_name": self.company_knowledge.get('company', {}).get('name', 'Unknown')
        }
    
    def save_results(self, output_path: str):
        """
        Save all risk assessment results to a JSON file
        
        Args:
            output_path: Path to save results
        """
        output_data = {
            "company": self.company_knowledge.get('company', {}),
            "analysis_metadata": {
                "total_articles": len(self.results),
                "data_sources": ["finance_news", "market_news", "industry_news", "linkedin_news"]
            },
            "summary": self.generate_summary_report(),
            "detailed_results": self.results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to: {output_path}")
    
    def run(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the complete risk scoring workflow
        
        Args:
            output_path: Optional path to save results
            
        Returns:
            Summary report
        """
        print("=" * 80)
        print("Risk Scorer Agent - Starting Analysis")
        print("=" * 80)
        print(f"Company: {self.company_knowledge.get('company', {}).get('name', 'Unknown')}")
        print(f"Data Directory: {self.data_dir}")
        print()
        
        # Process all news
        self.process_all_news()
        
        # Generate summary
        summary = self.generate_summary_report()
        
        print("=" * 80)
        print("Analysis Complete")
        print("=" * 80)
        print(f"Total Articles Analyzed: {summary.get('total_articles_analyzed', 0)}")
        print(f"Skipped Articles: {self.skipped_count}")
        print(f"Average Risk Score: {summary.get('average_risk_score', 0)}")
        print(f"High Risk Articles: {summary.get('high_risk_articles_count', 0)}")
        print()
        
        # Save results if output path provided
        if output_path:
            self.save_results(output_path)
        
        return summary


def main():
    """Main entry point for the Risk Scorer Agent"""
    
    # Default paths
    current_dir = Path(__file__).parent
    knowledge_path = current_dir.parent / "knowledge" / "company.json"
    data_dir = current_dir / "finance_scrapper" / "data"
    output_path = current_dir / "risk_agent" / "risk_assessment_results.json"
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(exist_ok=True)
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        knowledge_path = sys.argv[1]
    if len(sys.argv) > 2:
        data_dir = Path(sys.argv[2])
    if len(sys.argv) > 3:
        output_path = sys.argv[3]
    
    # Initialize and run agent
    agent = RiskScorerAgent(str(knowledge_path), str(data_dir))
    summary = agent.run(str(output_path))
    
    # Print summary report
    print("\nSummary Report:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
