import requests
from bs4 import BeautifulSoup
from readability import Document
import pandas as pd
import json
import uuid
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Any
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# -------------------------------------------------------
# LOAD COMPANY KNOWLEDGE BASE
# -------------------------------------------------------
with open("../../knowledge/company.json", "r") as f:
    KB = json.load(f)

COMPANY_NAME = KB["company"]["name"]
STOCK_SYMBOL = KB["company"]["stock_symbol"]
INDUSTRY = KB["company"]["industry"]
COMPETITORS = [c["name"] for c in KB["competitors"]]
COMPETITOR_SYMBOLS = [c["stock_symbol"] for c in KB["competitors"]]
RISK_KEYWORDS = sum(KB["risk_keywords"].values(), [])
PRODUCT_TERMS = sum(KB["product_keywords"].values(), [])
SENSITIVE_TOPICS = KB["sensitive_topics"]

# -------------------------------------------------------
# TIME WINDOW: LAST 20 HOURS
# -------------------------------------------------------
TIME_WINDOW_HOURS = 20
CUTOFF_TIME = datetime.now() - timedelta(hours=TIME_WINDOW_HOURS)

# -------------------------------------------------------
# CURATED BUSINESS NEWS SOURCES (ACCESSIBLE ALTERNATIVES)
# Note: LinkedIn requires authentication, using accessible tech business sources
# -------------------------------------------------------
LINKEDIN_SOURCES = {
    "business_insider": "https://www.businessinsider.com/tech",
    "cnet_news": "https://www.cnet.com/news/",
    "zdnet_tech": "https://www.zdnet.com/topic/apple/",
    "ars_technica": "https://arstechnica.com/gadgets/"
}

# -------------------------------------------------------
# HELPER – CLEAN TEXT
# -------------------------------------------------------
def clean_text(text: str) -> str:
    """Remove extra whitespace and clean text"""
    return re.sub(r"\s+", " ", text).strip()

# -------------------------------------------------------
# HELPER – EXTRACT PUBLISHED TIME
# -------------------------------------------------------
def extract_publish_time(soup: BeautifulSoup, url: str) -> str:
    """Extract published time from article"""
    time_patterns = [
        {"tag": "time", "attr": "datetime"},
        {"tag": "meta", "attr": "content", "property": "article:published_time"},
        {"tag": "span", "class": "timestamp"},
        {"tag": "div", "class": "publish-date"}
    ]
    
    for pattern in time_patterns:
        if "property" in pattern:
            elem = soup.find("meta", property=pattern["property"])
        elif "class" in pattern:
            elem = soup.find(pattern["tag"], class_=pattern["class"])
        else:
            elem = soup.find(pattern["tag"])
            
        if elem and pattern["attr"] in elem.attrs:
            return elem[pattern["attr"]]
        elif elem:
            return elem.get_text(strip=True)
    
    return datetime.now().isoformat()

# -------------------------------------------------------
# HELPER – CHECK IF ARTICLE IS WITHIN TIME WINDOW
# -------------------------------------------------------
def is_within_time_window(publish_time_str: str) -> bool:
    """Check if article was published within last 10 hours"""
    try:
        # Try multiple datetime formats
        formats = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d %b %Y, %I:%M %p",
            "%B %d, %Y %I:%M %p"
        ]
        
        publish_time = None
        for fmt in formats:
            try:
                publish_time = datetime.strptime(publish_time_str.split('+')[0].strip(), fmt)
                break
            except:
                continue
        
        if not publish_time:
            return True
            
        return publish_time >= CUTOFF_TIME
    except:
        return True

# -------------------------------------------------------
# HELPER – EXTRACT HTML TABLES
# -------------------------------------------------------
def extract_tables(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract financial tables from article"""
    html_tables = soup.find_all("table")
    tables_json = []

    for tbl in html_tables:
        try:
            df = pd.read_html(str(tbl))[0]
            
            # Convert column names to strings (in case they are tuples from multi-index)
            df.columns = [str(col) for col in df.columns]
            
            table_data = {
                "table_title": "",
                "headers": df.columns.tolist() if hasattr(df, 'columns') else [],
                "rows": df.to_dict(orient="records")
            }
            
            # Try to find table caption or title
            caption = tbl.find("caption")
            if caption:
                table_data["table_title"] = clean_text(caption.get_text())
            
            tables_json.append(table_data)
        except:
            pass

    return tables_json

# -------------------------------------------------------
# HELPER – EXTRACT IMAGES (MAX 3)
# -------------------------------------------------------
def extract_images(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract max 3 relevant images/graphs"""
    images = []
    
    for img in soup.find_all("img"):
        if len(images) >= 3:
            break
            
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        
        alt = img.get("alt", "")
        
        # Skip small images
        width = img.get("width", "")
        height = img.get("height", "")
        
        if width and height:
            try:
                if int(width) < 200 or int(height) < 150:
                    continue
            except:
                pass
        
        # Skip ads, logos, tracking pixels
        if any(skip in src.lower() for skip in ["logo", "icon", "avatar", "ads", "banner", "pixel", "1x1"]):
            continue
        
        images.append({
            "image_url": src,
            "image_alt": clean_text(alt)
        })
    
    return images[:3]

# -------------------------------------------------------
# HELPER – EXTRACT NUMERICAL DATA
# -------------------------------------------------------
def extract_numbers(text: str) -> Dict[str, List[str]]:
    """Extract financial numbers from text"""
    numbers = {
        "revenues": [],
        "profit_loss": [],
        "percent_changes": [],
        "market_share": [],
        "stock_price": []
    }
    
    # Revenue patterns
    revenue_patterns = [
        r"revenue[s]?\s+(?:of\s+)?[\$₹]?\s*([\d,\.]+)\s*(?:million|billion|crore|lakh)?",
        r"sales\s+(?:of\s+)?[\$₹]?\s*([\d,\.]+)\s*(?:million|billion|crore|lakh)?"
    ]
    
    # Profit/Loss patterns
    profit_patterns = [
        r"profit[s]?\s+(?:of\s+)?[\$₹]?\s*([\d,\.]+)\s*(?:million|billion|crore|lakh)?",
        r"loss(?:es)?\s+(?:of\s+)?[\$₹]?\s*([\d,\.]+)\s*(?:million|billion|crore|lakh)?"
    ]
    
    # Percentage change patterns
    percent_patterns = [
        r"([\d,\.]+)%\s*(?:increase|decrease|rise|fall|up|down|gain|loss)",
        r"(?:up|down|rise|fall)\s+([\d,\.]+)%"
    ]
    
    # Stock price patterns
    stock_patterns = [
        r"(?:trading|traded|price)\s+(?:at\s+)?[\$₹]?\s*([\d,\.]+)",
        r"[\$₹]\s*([\d,\.]+)\s+per\s+share"
    ]
    
    text_lower = text.lower()
    
    for pattern in revenue_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        # Convert tuples to strings if needed
        numbers["revenues"].extend([m if isinstance(m, str) else str(m[0]) if m else "" for m in matches])
    
    for pattern in profit_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        numbers["profit_loss"].extend([m if isinstance(m, str) else str(m[0]) if m else "" for m in matches])
    
    for pattern in percent_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        numbers["percent_changes"].extend([m if isinstance(m, str) else str(m[0]) if m else "" for m in matches])
    
    for pattern in stock_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        numbers["stock_price"].extend([m if isinstance(m, str) else str(m[0]) if m else "" for m in matches])
    
    # Remove empty strings
    for key in numbers:
        numbers[key] = [n for n in numbers[key] if n]
    
    return numbers

# -------------------------------------------------------
# HELPER – DETECT SENTIMENT
# -------------------------------------------------------
def detect_sentiment(text: str, analysis: Dict) -> str:
    """Analyze sentiment: positive, negative, or neutral"""
    text_lower = text.lower()
    
    positive_words = ["growth", "profit", "gain", "surge", "rise", "success", "innovation", "expansion", "strong", "bullish"]
    negative_words = ["loss", "decline", "fall", "crash", "concern", "risk", "issue", "problem", "weak", "bearish"]
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    # Factor in risk tags
    neg_count += len(analysis.get("risk_tags_detected", []))
    
    if pos_count > neg_count + 1:
        return "positive"
    elif neg_count > pos_count + 1:
        return "negative"
    else:
        return "neutral"

# -------------------------------------------------------
# HELPER – ANALYZE RELEVANCE
# -------------------------------------------------------
def analyze_relevance(text: str, title: str) -> Dict[str, Any]:
    """Analyze article relevance to company"""
    combined_text = (title + " " + text).lower()
    
    analysis = {
        "company_match": COMPANY_NAME.lower() in combined_text or STOCK_SYMBOL.lower() in combined_text,
        "competitor_mentions": [c for c in COMPETITORS if c.lower() in combined_text],
        "stock_mentions": [STOCK_SYMBOL] if STOCK_SYMBOL.lower() in combined_text else [],
        "risk_tags_detected": [w for w in RISK_KEYWORDS if w.lower() in combined_text],
        "product_terms": [p for p in PRODUCT_TERMS if p.lower() in combined_text],
        "sensitive_hits": [s for s in SENSITIVE_TOPICS if s.lower() in combined_text]
    }
    
    # Add competitor stock symbols
    for i, comp in enumerate(COMPETITORS):
        if comp.lower() in combined_text:
            symbol = COMPETITOR_SYMBOLS[i]
            if symbol not in analysis["stock_mentions"]:
                analysis["stock_mentions"].append(symbol)
    
    return analysis

# -------------------------------------------------------
# HELPER – DETERMINE RELEVANCE (STRICT FILTER)
# -------------------------------------------------------
def is_relevant(analysis: Dict, text: str) -> tuple[bool, str]:
    """Determine if article is relevant to company - STRICT filter"""
    reasons = []
    
    if analysis["company_match"]:
        reasons.append(f"Direct mention of {COMPANY_NAME}")
    
    if analysis["competitor_mentions"]:
        reasons.append(f"Competitor mentions: {', '.join(analysis['competitor_mentions'])}")
    
    if analysis["risk_tags_detected"]:
        reasons.append(f"Risk keywords: {', '.join(analysis['risk_tags_detected'][:3])}")
    
    if analysis["product_terms"]:
        reasons.append(f"Product-related: {', '.join(analysis['product_terms'][:3])}")
    
    if analysis["sensitive_hits"]:
        reasons.append(f"Sensitive topics: {', '.join(analysis['sensitive_hits'])}")
    
    # STRICT: Must have company OR competitor mention
    is_relevant_article = analysis["company_match"] or len(analysis["competitor_mentions"]) > 0
    reason_str = " | ".join(reasons) if reasons else "No direct relevance found"
    
    return is_relevant_article, reason_str

# -------------------------------------------------------
# MAIN ARTICLE SCRAPER
# -------------------------------------------------------
def scrape_article(url: str) -> Dict[str, Any]:
    """Scrape and analyze a single article with STRICT company/competitor filter"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        res = requests.get(url, timeout=8, headers=headers)
        res.raise_for_status()  # Raise error for bad status codes
        doc = Document(res.text)
        soup = BeautifulSoup(doc.summary(), "lxml")
        full_soup = BeautifulSoup(res.text, "lxml")

        title = clean_text(doc.short_title())
        content_text = clean_text(soup.get_text())
        published_time = extract_publish_time(full_soup, url)
        
        # Check time window
        if not is_within_time_window(published_time):
            return None

        tables = extract_tables(full_soup)
        images = extract_images(full_soup)
        
        # Analyze relevance
        analysis = analyze_relevance(content_text, title)
        is_rel, reason = is_relevant(analysis, content_text)
        
        # Extract numbers
        numbers = extract_numbers(content_text)
        
        # Detect sentiment
        sentiment = detect_sentiment(content_text, analysis)

        article_json = {
            "source": urlparse(url).netloc,
            "title": title,
            "url": url,
            "published_time": published_time,
            "content_text": content_text[:5000],  # Limit to 5000 chars
            "relevant_tables": tables,
            "graphs_images": images,
            "related_to_company": is_rel,
            "reason_for_relevance": reason,
            "risk_tags_detected": analysis["risk_tags_detected"],
            "sentiment": sentiment,
            "competitor_mentions": analysis["competitor_mentions"],
            "stock_mentions": analysis["stock_mentions"],
            "extracted_numbers": numbers
        }
        
        return article_json if is_rel else None
        
    except (requests.Timeout, requests.ConnectionError, requests.RequestException):
        # Skip silently for network errors
        return None
    except Exception:
        # Skip silently for parsing errors
        return None

# -------------------------------------------------------
# SOURCE SCRAPER
# -------------------------------------------------------
def linkedin_scraper(max_articles_per_source: int = 20) -> List[Dict[str, Any]]:
    """Scrape LinkedIn news from curated sources"""
    all_articles = []
    seen_urls = set()

    print("=" * 80)
    print(f"🚀 BUSINESS NEWS SCRAPER FOR {COMPANY_NAME}")
    print(f"📅 Time Window: Last {TIME_WINDOW_HOURS} hours")
    print(f"⚡ SOURCES: 4 accessible business/tech sites (Business Insider, CNET, ZDNet, Ars Technica)")
    print(f"🎯 Filter: STRICT - Only {COMPANY_NAME} and competitors")
    print("=" * 80)

    for source_name, source_url in LINKEDIN_SOURCES.items():
        print(f"\n🔍 Scraping: {source_name} ({source_url})")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            page = requests.get(source_url, timeout=10, headers=headers)
            soup = BeautifulSoup(page.text, "lxml")

            links = soup.find_all("a", href=True)
            articles_from_source = 0
            attempts = 0
            max_attempts = 30  # Only try 30 links per source to avoid hanging

            for a in links:
                if articles_from_source >= max_articles_per_source or attempts >= max_attempts:
                    break
                    
                href = a.get("href")
                if not href:
                    continue

                # Skip non-article links and social media
                if any(skip in href.lower() for skip in ["javascript", "#", "mailto:", "tel:", "twitter", "facebook", "linkedin", "instagram"]):
                    continue

                # Make absolute URL
                href = urljoin(source_url, href)

                # Skip if already seen or not http/https
                if href in seen_urls or not href.startswith(('http://', 'https://')):
                    continue

                seen_urls.add(href)
                attempts += 1

                # Scrape article
                article_data = scrape_article(href)
                
                if article_data:
                    all_articles.append(article_data)
                    articles_from_source += 1
                    print(f"    ✅ {article_data['title'][:60]}... | Sentiment: {article_data['sentiment']}")
                
                time.sleep(0.5)  # Respectful crawling

            print(f"✅ Found {articles_from_source} relevant articles from {source_name}")

        except Exception as e:
            print(f"❌ Error scraping {source_name}: {str(e)[:100]}")
            continue

    return all_articles

# -------------------------------------------------------
# SAVE TO JSON
# -------------------------------------------------------
def save_to_json(articles: List[Dict[str, Any]]):
    """Save articles to JSON file"""
    output_path = "data/linkedin_news.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {output_path}")

# -------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------
if __name__ == "__main__":
    start_time = time.time()
    
    # Scrape articles
    articles = linkedin_scraper(max_articles_per_source=15)
    
    # Save results
    if articles:
        save_to_json(articles)
    
    # Print summary
    print("\n" + "=" * 80)
    print("✅ BUSINESS NEWS SCRAPING COMPLETED!")
    print(f"📊 Total Articles: {len(articles)}")
    print(f"⏱️  Time Taken: {time.time() - start_time:.2f} seconds")
    
    if articles:
        sentiments = {}
        for article in articles:
            sent = article.get("sentiment", "unknown")
            sentiments[sent] = sentiments.get(sent, 0) + 1
        
        print(f"📈 Sentiment Distribution: {sentiments}")
        
        top_article = articles[0]
        print(f"🏆 Top Article: {top_article['title'][:60]}...")
        print(f"   Relevance: {top_article['reason_for_relevance'][:80]}...")
    
    print("=" * 80)
