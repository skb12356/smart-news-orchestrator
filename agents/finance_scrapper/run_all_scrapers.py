"""
Parallel News Scraper Runner
Runs all 4 scrapers simultaneously for faster execution
"""

import subprocess
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import sys
import re

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# -------------------------------------------------------
# SCRAPER CONFIGURATIONS
# -------------------------------------------------------
SCRAPERS = [
    {
        "name": "Finance News",
        "script": "finance_crawler.py",
        "output": "data/finance_news.json"
    },
    {
        "name": "Market News",
        "script": "market_scraper.py",
        "output": "data/market_news.json"
    },
    {
        "name": "Industry News",
        "script": "industry_scraper.py",
        "output": "data/industry_news.json"
    },
    {
        "name": "Business News",
        "script": "linkedin_scraper.py",
        "output": "data/linkedin_news.json"
    }
]

# -------------------------------------------------------
# RUN SINGLE SCRAPER
# -------------------------------------------------------
def run_scraper(scraper_info):
    """Run a single scraper and return results"""
    name = scraper_info["name"]
    script = scraper_info["script"]
    
    print(f"🚀 Starting {name} scraper...")
    start_time = time.time()
    
    try:
        # Run the scraper script with real-time output
        process = subprocess.Popen(
            ["python", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )
        
        # Collect output while showing it in real-time
        output_lines = []
        for line in process.stdout:
            print(f"[{name}] {line.rstrip()}")
            output_lines.append(line)
        
        process.wait(timeout=300)
        output = ''.join(output_lines)
        elapsed = time.time() - start_time
        
        if process.returncode == 0:
            # Parse the output to get article count
            count_match = re.search(r'Total relevant articles: (\d+)', output)
            article_count = int(count_match.group(1)) if count_match else 0
            
            print(f"✅ {name} completed in {elapsed:.1f}s - Found {article_count} articles")
            return {
                "scraper": name,
                "status": "success",
                "articles": article_count,
                "time": elapsed,
                "output": output
            }
        else:
            print(f"❌ {name} failed with return code {process.returncode}")
            print(f"   Error: {output[:200]}")
            return {
                "scraper": name,
                "status": "failed",
                "articles": 0,
                "time": elapsed,
                "error": output,
                "stdout": output
            }
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  {name} timed out after 5 minutes")
        return {
            "scraper": name,
            "status": "timeout",
            "time": 300
        }
    except Exception as e:
        print(f"❌ {name} error: {str(e)[:100]}")
        return {
            "scraper": name,
            "status": "error",
            "error": str(e)
        }

# -------------------------------------------------------
# LOAD RESULTS SUMMARY
# -------------------------------------------------------
def load_scraper_results():
    """Load and summarize results from all scrapers"""
    summary = {
        "total_articles": 0,
        "by_scraper": {}
    }
    
    for scraper in SCRAPERS:
        try:
            with open(scraper["output"], "r", encoding="utf-8") as f:
                articles = json.load(f)
                count = len(articles) if isinstance(articles, list) else 0
                summary["total_articles"] += count
                summary["by_scraper"][scraper["name"]] = {
                    "count": count,
                    "file": scraper["output"]
                }
        except FileNotFoundError:
            summary["by_scraper"][scraper["name"]] = {
                "count": 0,
                "file": scraper["output"],
                "error": "File not found"
            }
        except Exception as e:
            summary["by_scraper"][scraper["name"]] = {
                "count": 0,
                "file": scraper["output"],
                "error": str(e)
            }
    
    return summary

# -------------------------------------------------------
# MAIN PARALLEL EXECUTION
# -------------------------------------------------------
def main():
    """Run all scrapers in parallel"""
    print("=" * 80)
    print("🔥 PARALLEL NEWS SCRAPER RUNNER")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Running {len(SCRAPERS)} scrapers in parallel")
    print("=" * 80)
    print()
    
    overall_start = time.time()
    results = []
    
    # Run all scrapers in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all scraper tasks
        future_to_scraper = {
            executor.submit(run_scraper, scraper): scraper 
            for scraper in SCRAPERS
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_scraper):
            scraper = future_to_scraper[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"❌ Exception for {scraper['name']}: {str(e)}")
                results.append({
                    "scraper": scraper["name"],
                    "status": "exception",
                    "error": str(e)
                })
    
    overall_time = time.time() - overall_start
    
    # Print summary
    print()
    print("=" * 80)
    print("📊 EXECUTION SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful
    
    print(f"\n✅ Successful: {successful}/{len(SCRAPERS)}")
    print(f"❌ Failed: {failed}/{len(SCRAPERS)}")
    print(f"⏱️  Total Time: {overall_time:.2f} seconds")
    
    print("\n📋 Individual Results:")
    for result in sorted(results, key=lambda x: x.get("time", 0)):
        status_emoji = "✅" if result["status"] == "success" else "❌"
        print(f"  {status_emoji} {result['scraper']}: {result['status']} ({result.get('time', 0):.2f}s)")
    
    # Load and display article counts
    print("\n" + "=" * 80)
    print("📰 ARTICLES COLLECTED")
    print("=" * 80)
    
    summary = load_scraper_results()
    
    for scraper_name, info in summary["by_scraper"].items():
        if "error" in info:
            print(f"  ❌ {scraper_name}: {info['error']}")
        else:
            print(f"  📄 {scraper_name}: {info['count']} articles")
    
    print(f"\n🎯 TOTAL ARTICLES: {summary['total_articles']}")
    print("=" * 80)
    
    return results, summary

if __name__ == "__main__":
    try:
        results, summary = main()
        print("\n✅ All scrapers completed!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
