"""
Complete News Analysis Pipeline Orchestrator

This script orchestrates the complete automated news analysis pipeline:
1. Risk Assessment - Analyzes scraped news articles and assigns risk scores
2. Chart Generation - Creates visualizations from tabular data
3. Feed Generation - Creates engaging social media posts

Usage:
    python run_complete_pipeline.py [--min-risk 0.5] [--max-posts 10]
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


class PipelineOrchestrator:
    """Orchestrates the complete news analysis pipeline"""
    
    def __init__(self, workspace_root: str = None):
        if workspace_root:
            self.workspace = Path(workspace_root)
        else:
            self.workspace = Path(__file__).parent
        
        # Define paths
        self.data_dir = self.workspace / "agents" / "finance_scrapper" / "data"
        self.knowledge_dir = self.workspace / "knowledge"
        self.charts_dir = self.workspace / "agents" / "charts"
        self.feeds_dir = self.workspace / "agents" / "feeds"
        self.agents_dir = self.workspace / "agents"
        
        # Create output directories
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        self.feeds_dir.mkdir(parents=True, exist_ok=True)
        
        # Define file paths
        self.company_json = self.knowledge_dir / "company.json"
        self.news_files = [
            self.data_dir / "finance_news.json",
            self.data_dir / "market_news.json",
            self.data_dir / "industry_news.json",
            self.data_dir / "linkedin_news.json"
        ]
        self.risk_assessment_file = self.workspace / "risk_assessment_results.json"
        self.feed_file = self.feeds_dir / "feed.json"
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def check_prerequisites(self) -> bool:
        """Check if all required files and directories exist"""
        self.log("Checking prerequisites...")
        
        # Check company knowledge base
        if not self.company_json.exists():
            self.log(f"ERROR: Company knowledge base not found: {self.company_json}", "ERROR")
            return False
        
        # Check news data files
        found_news = False
        for news_file in self.news_files:
            if news_file.exists():
                found_news = True
                self.log(f"Found news data: {news_file.name}")
        
        if not found_news:
            self.log("ERROR: No news data files found", "ERROR")
            return False
        
        # Check agents
        agents_to_check = [
            "risk_scorer_agent.py",
            "chart-generator-agent.yaml",
            "feed-poster-agent.yaml"
        ]
        
        for agent in agents_to_check:
            agent_path = self.agents_dir / agent
            if not agent_path.exists():
                self.log(f"WARNING: Agent not found: {agent}", "WARNING")
        
        self.log("Prerequisites check completed")
        return True
    
    def run_risk_assessment(self, min_risk: float = 0.0) -> bool:
        """
        Run the Risk Scorer Agent
        
        Args:
            min_risk: Minimum risk threshold for filtering articles
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.log("=" * 80)
        self.log("STEP 1: Running Risk Assessment Agent")
        self.log("=" * 80)
        
        try:
            # Import and run risk scorer
            sys.path.insert(0, str(self.workspace / "tools"))
            from risk_scorer import RiskScorer
            
            # Load company knowledge
            with open(self.company_json, 'r', encoding='utf-8') as f:
                company_data = json.load(f)
            
            # Initialize risk scorer
            scorer = RiskScorer(company_data)
            
            # Process all news files
            all_articles = []
            for news_file in self.news_files:
                if news_file.exists():
                    self.log(f"Processing: {news_file.name}")
                    with open(news_file, 'r', encoding='utf-8') as f:
                        articles = json.load(f)
                    
                    # Analyze each article
                    for article in articles:
                        analyzed = scorer.analyze_article(article)
                        all_articles.append(analyzed)
            
            # Filter by risk threshold
            filtered_articles = [a for a in all_articles if a.get('risk_score', 0) >= min_risk]
            
            self.log(f"Total articles analyzed: {len(all_articles)}")
            self.log(f"Articles above risk threshold ({min_risk}): {len(filtered_articles)}")
            
            # Sort by risk score (highest first)
            filtered_articles.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
            
            # Save results
            with open(self.risk_assessment_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_articles, f, indent=2, ensure_ascii=False)
            
            self.log(f"Risk assessment saved to: {self.risk_assessment_file}")
            self.log("✓ Risk Assessment completed successfully")
            return True
            
        except Exception as e:
            self.log(f"ERROR in risk assessment: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def run_chart_generation(self) -> bool:
        """
        Run the Chart Generator Agent
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.log("=" * 80)
        self.log("STEP 2: Running Chart Generation Agent")
        self.log("=" * 80)
        
        try:
            sys.path.insert(0, str(self.workspace / "tools"))
            from chart_generator import ChartGenerator
            
            # Load risk assessment results
            with open(self.risk_assessment_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            generator = ChartGenerator(output_dir=str(self.charts_dir))
            charts_created = 0
            
            # Process each article
            for idx, article in enumerate(articles, 1):
                # Check if article has tabular data
                tables = article.get('relevant_tables', [])
                extracted_numbers = article.get('extracted_numbers', {})
                
                if tables:
                    self.log(f"Article {idx}: Found {len(tables)} tables")
                    for table_idx, table in enumerate(tables, 1):
                        try:
                            chart_path = generator.generate_chart(
                                data=table,
                                title=f"Data from Article {idx}",
                                article_id=idx,
                                chart_number=table_idx
                            )
                            if chart_path:
                                charts_created += 1
                                self.log(f"  Created: {Path(chart_path).name}")
                        except Exception as e:
                            self.log(f"  Failed to create chart: {str(e)}", "WARNING")
                
                elif extracted_numbers and len(extracted_numbers) > 0:
                    self.log(f"Article {idx}: Found extracted numbers")
                    try:
                        chart_path = generator.generate_chart(
                            data=extracted_numbers,
                            title=f"Key Metrics from Article {idx}",
                            article_id=idx,
                            chart_number=1
                        )
                        if chart_path:
                            charts_created += 1
                            self.log(f"  Created: {Path(chart_path).name}")
                    except Exception as e:
                        self.log(f"  Failed to create chart: {str(e)}", "WARNING")
            
            self.log(f"Total charts created: {charts_created}")
            self.log("✓ Chart Generation completed successfully")
            return True
            
        except Exception as e:
            self.log(f"ERROR in chart generation: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def run_feed_generation(self, max_posts: int = None) -> bool:
        """
        Run the Feed Poster Agent
        
        Args:
            max_posts: Maximum number of posts to generate (None = all)
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.log("=" * 80)
        self.log("STEP 3: Running Feed Generation Agent")
        self.log("=" * 80)
        
        try:
            sys.path.insert(0, str(self.workspace / "tools"))
            from feed_poster import FeedPoster
            
            poster = FeedPoster(output_dir=str(self.feeds_dir))
            
            # Generate feed from risk assessment
            feed_data = poster.generate_feed_from_assessment(
                assessment_file_path=str(self.risk_assessment_file),
                max_posts=max_posts
            )
            
            if feed_data:
                feed = json.loads(feed_data)
                self.log(f"Generated {len(feed.get('posts', []))} social media posts")
                self.log(f"Feed saved to: {self.feed_file}")
                
                # Display summary
                for post in feed.get('posts', [])[:5]:  # Show first 5
                    self.log(f"\nPost: {post.get('title', 'Untitled')}")
                    self.log(f"  Risk: {post.get('risk_metadata', {}).get('risk_score', 0):.2f}")
                    self.log(f"  Priority: {post.get('risk_metadata', {}).get('priority', 'N/A')}")
                
                if len(feed.get('posts', [])) > 5:
                    self.log(f"\n... and {len(feed.get('posts', [])) - 5} more posts")
                
                self.log("✓ Feed Generation completed successfully")
                return True
            else:
                self.log("No feed data generated", "WARNING")
                return False
            
        except Exception as e:
            self.log(f"ERROR in feed generation: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def run_complete_pipeline(self, min_risk: float = 0.0, max_posts: int = None):
        """
        Run the complete pipeline
        
        Args:
            min_risk: Minimum risk threshold for filtering articles
            max_posts: Maximum number of social media posts to generate
        """
        self.log("=" * 80)
        self.log("COMPLETE NEWS ANALYSIS PIPELINE")
        self.log("=" * 80)
        self.log(f"Workspace: {self.workspace}")
        self.log(f"Min Risk Threshold: {min_risk}")
        self.log(f"Max Posts: {max_posts if max_posts else 'All'}")
        self.log("")
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.log("Prerequisites check failed. Aborting pipeline.", "ERROR")
            return False
        
        # Step 1: Risk Assessment
        if not self.run_risk_assessment(min_risk=min_risk):
            self.log("Risk assessment failed. Aborting pipeline.", "ERROR")
            return False
        
        # Step 2: Chart Generation
        if not self.run_chart_generation():
            self.log("Chart generation failed. Continuing anyway...", "WARNING")
        
        # Step 3: Feed Generation
        if not self.run_feed_generation(max_posts=max_posts):
            self.log("Feed generation failed. Aborting pipeline.", "ERROR")
            return False
        
        # Pipeline completed
        self.log("=" * 80)
        self.log("✓ PIPELINE COMPLETED SUCCESSFULLY")
        self.log("=" * 80)
        self.log(f"Risk Assessment: {self.risk_assessment_file}")
        self.log(f"Charts: {self.charts_dir}")
        self.log(f"Social Media Feed: {self.feed_file}")
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run the complete news analysis pipeline"
    )
    parser.add_argument(
        "--min-risk",
        type=float,
        default=0.0,
        help="Minimum risk threshold for filtering articles (0.0-1.0)"
    )
    parser.add_argument(
        "--max-posts",
        type=int,
        default=None,
        help="Maximum number of social media posts to generate"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=None,
        help="Path to workspace root directory"
    )
    
    args = parser.parse_args()
    
    # Validate min_risk
    if not 0 <= args.min_risk <= 1:
        print("ERROR: --min-risk must be between 0.0 and 1.0")
        sys.exit(1)
    
    # Run pipeline
    orchestrator = PipelineOrchestrator(workspace_root=args.workspace)
    success = orchestrator.run_complete_pipeline(
        min_risk=args.min_risk,
        max_posts=args.max_posts
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
