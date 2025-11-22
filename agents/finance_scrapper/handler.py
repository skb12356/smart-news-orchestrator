import json
from finance_crawler import crawl_sync_wrapper


def run(event, context=None):
    # event contains seeds, allowed_domains, max_pages, depth, timeout, save_json
    seeds = event.get("seeds", [])
    if isinstance(seeds, str):
        seeds = [seeds]
    allowed = event.get("allowed_domains", None)
    max_pages = int(event.get("max_pages", 50))
    depth = int(event.get("depth", 1))
    timeout = int(event.get("timeout", 180))

    results = crawl_sync_wrapper(seeds, allowed, max_pages, depth, timeout=timeout)

    # optionally write JSON file (no raw html files are produced)
    save_path = event.get("save_json")
    if save_path:
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump({"status": "ok", "items_count": len(results), "items": results}, f, indent=2)
        except Exception as e:
            return {"status": "error", "error": str(e)}

    return {"status": "ok", "items_count": len(results), "items": results}

if __name__ == "__main__":
    # quick local test: small run and save results to JSON
    seeds = ["https://www.moneycontrol.com/news/",]
    output = run({
        "seeds": seeds,
        "allowed_domains": None,
        "max_pages": 1,
        "depth": 0,
        "timeout": 30,
        "save_json": "finance_results.json"
    })
    print(json.dumps(output, indent=2)[:1500])
