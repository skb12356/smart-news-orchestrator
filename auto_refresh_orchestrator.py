"""
Auto-refresh orchestrator that runs the pipeline every 30 minutes
Keeps the dashboard updated with fresh news analysis
"""

import time
import schedule
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from run_orchestrator import run_pipeline


def job():
    """Job to run the pipeline"""
    print(f"\n⏰ Scheduled run at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        run_pipeline()
    except Exception as e:
        print(f"❌ Pipeline error: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main scheduler loop"""
    print("=" * 60)
    print("🔄 Auto-Refresh Orchestrator Started")
    print("=" * 60)
    print("⏱️  Running pipeline every 30 minutes")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Run immediately on start
    print("\n🚀 Running initial pipeline...")
    job()
    
    # Schedule every 30 minutes
    schedule.every(30).minutes.do(job)
    
    # Keep running
    print("\n⏳ Waiting for next scheduled run in 30 minutes...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Orchestrator stopped by user")
        sys.exit(0)
