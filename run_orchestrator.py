"""
Integration script to connect the orchestrator with the dashboard
Runs the risk analysis pipeline and updates the dashboard data
"""

import json
import shutil
from pathlib import Path
import sys

# Add the agents directory to path
agents_dir = Path(__file__).parent / "agents"
sys.path.insert(0, str(agents_dir))

from risk_scorer_agent import RiskScorerAgent


def run_pipeline():
    """
    Run the complete news analysis pipeline:
    1. Load scraped news from finance_scrapper/data/
    2. Run risk scorer agent
    3. Copy results to dashboard
    4. Generate charts
    """
    
    print("=" * 60)
    print("🚀 Starting News Analysis Pipeline")
    print("=" * 60)
    
    # Paths
    workspace = Path(__file__).parent
    knowledge_path = workspace / "knowledge" / "company.json"
    data_dir = workspace / "agents" / "finance_scrapper" / "data"
    output_path = workspace / "agents" / "risk_agent" / "risk_assessment_results.json"
    dashboard_output = workspace / "dashboard" / "public" / "agents" / "risk_agent" / "risk_assessment_results.json"
    charts_dir = workspace / "dashboard" / "public" / "agents" / "charts"
    
    # Step 1: Check if news data exists
    print("\n📰 Step 1: Checking for news data...")
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        print("Please run the finance scraper first!")
        return False
    
    news_files = list(data_dir.glob("*.json"))
    if not news_files:
        print(f"❌ No news files found in {data_dir}")
        print("Please run the finance scraper first!")
        return False
    
    print(f"✅ Found {len(news_files)} news files:")
    for f in news_files:
        print(f"   - {f.name}")
    
    # Step 2: Run Risk Scorer Agent
    print("\n🎯 Step 2: Running Risk Scorer Agent...")
    try:
        agent = RiskScorerAgent(
            knowledge_path=str(knowledge_path),
            data_dir=str(data_dir)
        )
        
        # Process all news
        results = agent.process_all_news()
        
        # Generate summary
        summary = agent.generate_summary_report()
        
        # Save results
        output_data = {
            "company": agent.company_knowledge.get('company', agent.company_knowledge),
            "analysis_metadata": {
                "total_articles": len(results),
                "data_sources": ["finance_news", "market_news", "industry_news", "linkedin_news"]
            },
            "summary": summary,
            "detailed_results": results
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Processed {agent.processed_count} articles")
        print(f"   Skipped: {agent.skipped_count}")
        print(f"   Output: {output_path}")
        
    except Exception as e:
        print(f"❌ Error running risk scorer: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Copy to dashboard
    print("\n📋 Step 3: Copying results to dashboard...")
    try:
        dashboard_output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output_path, dashboard_output)
        print(f"✅ Copied to: {dashboard_output}")
    except Exception as e:
        print(f"❌ Error copying to dashboard: {str(e)}")
        return False
    
    # Step 4: Generate charts
    print("\n📊 Step 4: Generating charts...")
    try:
        import subprocess
        charts_script = charts_dir / "generate_all_charts.py"
        
        if charts_script.exists():
            result = subprocess.run(
                [sys.executable, str(charts_script)],
                capture_output=True,
                text=True,
                cwd=str(charts_dir)
            )
            
            if result.returncode == 0:
                print("✅ Charts generated successfully")
                print(result.stdout)
            else:
                print(f"⚠️ Chart generation had issues:")
                print(result.stderr)
        else:
            print(f"⚠️ Chart generation script not found: {charts_script}")
    
    except Exception as e:
        print(f"⚠️ Error generating charts: {str(e)}")
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("✅ Pipeline Completed Successfully!")
    print("=" * 60)
    print(f"\n📊 Analysis Summary:")
    print(f"   Total articles: {summary['total_articles_analyzed']}")
    print(f"   High risk: {summary.get('high_risk_articles_count', 0)}")
    print(f"   Average risk: {summary.get('average_risk_score', 0):.2f}")
    print(f"\n🎯 Sentiment Distribution:")
    for sentiment, count in summary.get('sentiment_distribution', {}).items():
        print(f"   {sentiment.capitalize()}: {count}")
    
    print(f"\n📁 Output Files:")
    print(f"   Risk Analysis: {output_path}")
    print(f"   Dashboard Data: {dashboard_output}")
    print(f"   Charts: {charts_dir}")
    
    print(f"\n🌐 Dashboard: http://localhost:3000")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
