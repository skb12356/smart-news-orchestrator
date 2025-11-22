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
# CURATED INDUSTRY NEWS SOURCES (ACCESSIBLE HARDWARE/TECH)
# -------------------------------------------------------
INDUSTRY_SOURCES = {
    "gadgets360_tech": "https://www.gadgets360.com/tech/news",
    "theverge_tech": "https://www.theverge.com/tech",
    "zdnet_innovation": "https://www.zdnet.com/topic/innovation/",
    "cnet_tech": "https://www.cnet.com/tech/"
}

# -------------------------------------------------------
# NOTE: TIME WINDOW ALREADY DEFINED ABOVE
# -------------------------------------------------------
TIME_WINDOW_HOURS = 10
CUTOFF_TIME = datetime.now() - timedelta(hours=TIME_WINDOW_HOURS)

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
            return True  # Include if we can't parse the time
            
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
        
        src = img.get("src", "")
        alt = img.get("alt", "")
        
        if not src or src.startswith("data:"):
            continue
        
        # Make absolute URL
        if not src.startswith("http"):
            continue
        
        # Check image dimensions if available
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
def detect_sentiment(text: str, analysis: Dict[str, Any]) -> str:
    """Detect sentiment based on text and risk keywords"""
    text_lower = text.lower()
    
    positive_words = ["growth", "profit", "gain", "success", "innovation", "launch", "expansion", "achievement"]
    negative_words = ["loss", "decline", "fall", "crash", "lawsuit", "ban", "fine", "delay", "shortage"]
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    # Risk tags add to negative sentiment
    risk_count = len(analysis.get("risk_tags_detected", []))
    neg_count += risk_count
    
    if neg_count > pos_count:
        return "negative"
    elif pos_count > neg_count:
        return "positive"
    else:
        return "neutral"

# -------------------------------------------------------
# HELPER – ANALYZE RELEVANCE
# -------------------------------------------------------
def analyze_relevance(text: str, title: str) -> Dict[str, Any]:
    """Analyze relevance to company and competitors"""
    combined = f"{title} {text}".lower()
    
    # Check for company mention
    company_match = COMPANY_NAME.lower() in combined or STOCK_SYMBOL.lower() in combined
    
    # Check for competitor mentions
    competitor_mentions = [comp for comp in COMPETITORS if comp.lower() in combined]
    
    # Check for stock symbol mentions
    stock_mentions = [sym for sym in COMPETITOR_SYMBOLS if sym.lower() in combined]
    if STOCK_SYMBOL.lower() in combined:
        stock_mentions.append(STOCK_SYMBOL)
    
    # Check for risk keywords
    risk_tags_detected = [kw for kw in RISK_KEYWORDS if kw.lower() in combined]
    
    # Check for product mentions
    product_terms = [term for term in PRODUCT_TERMS if term.lower() in combined]
    
    # Check for sensitive topics
    sensitive_hits = [topic for topic in SENSITIVE_TOPICS if topic.lower() in combined]
    
    return {
        "company_match": company_match,
        "competitor_mentions": competitor_mentions,
        "stock_mentions": stock_mentions,
        "risk_tags_detected": risk_tags_detected,
        "product_terms": product_terms,
        "sensitive_hits": sensitive_hits
    }

# -------------------------------------------------------
# HELPER – CHECK IF ARTICLE IS RELEVANT (STRICT)
# -------------------------------------------------------
def is_relevant(analysis: Dict[str, Any], text: str) -> tuple[bool, str]:
    """STRICT: Only allow articles with company OR competitor mentions"""
    reasons = []
    
    if analysis["company_match"]:
        reasons.append(f"Company: {COMPANY_NAME}")
    
    if analysis["competitor_mentions"]:
        reasons.append(f"Competitor mentions: {', '.join(analysis['competitor_mentions'])}")
    
    if analysis["risk_tags_detected"]:
        reasons.append(f"Risk keywords: {', '.join(analysis['risk_tags_detected'][:3])}")
    
    if analysis["product_terms"]:
        reasons.append(f"Product-related: {', '.join(analysis['product_terms'][:2])}")
    
    # STRICT: Must have company match OR competitor mentions
    is_relevant_article = analysis["company_match"] or len(analysis["competitor_mentions"]) > 0
    
    return is_relevant_article, " | ".join(reasons) if reasons else "No clear relevance"

# -------------------------------------------------------
# ARTICLE SCRAPER
# -------------------------------------------------------
def scrape_article(url: str) -> Dict[str, Any]:
    """Scrape a single article and return structured data"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")
        
        # Use readability to extract main content
        doc = Document(response.text)
        title = clean_text(doc.title())
        
        # Get full article soup for content extraction
        full_soup = BeautifulSoup(doc.summary(), "lxml")
        content_text = clean_text(full_soup.get_text())
        
        # Extract published time
        published_time = extract_publish_time(soup, url)
        
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
        
    except Exception as e:
        print(f"    ❌ Error scraping {url[:80]}: {str(e)[:50]}")
        return None

# -------------------------------------------------------
# SOURCE SCRAPER
# -------------------------------------------------------
def industry_scraper(max_articles_per_source: int = 20) -> List[Dict[str, Any]]:
    """Scrape industry news from curated sources"""
    all_articles = []
    seen_urls = set()

    print("=" * 80)
    print(f"🚀 INDUSTRY NEWS SCRAPER FOR {COMPANY_NAME}")
    print(f"📅 Time Window: Last {TIME_WINDOW_HOURS} hours")
    print(f"⚡ SOURCES: 4 accessible tech sites (Gadgets360, The Verge, ZDNet, CNET)")
    print(f"🎯 Filter: STRICT - Only {COMPANY_NAME} and competitors")
    print("=" * 80)

    for source_name, source_url in INDUSTRY_SOURCES.items():
        print(f"\n🔍 Scraping: {source_name} ({source_url})")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            page = requests.get(source_url, timeout=15, headers=headers)
            soup = BeautifulSoup(page.text, "lxml")

            links = soup.find_all("a", href=True)
            articles_from_source = 0

            for a in links:
                if articles_from_source >= max_articles_per_source:
                    break
                    
                href = a.get("href")
                if not href:
                    continue

                # Skip non-article links
                if any(skip in href.lower() for skip in ["javascript", "#", "mailto:", "tel:"]):
                    continue

                # Make absolute URL
                href = urljoin(source_url, href)
                
                # Skip if already seen
                if href in seen_urls:
                    continue
                
                seen_urls.add(href)
                
                # Scrape the article
                article = scrape_article(href)
                
                if article:
                    all_articles.append(article)
                    articles_from_source += 1
                    print(f"    ✅ {article['title'][:60]}... | Sentiment: {article['sentiment']}")
                
                time.sleep(0.5)  # Be nice to servers

            print(f"✅ Found {articles_from_source} relevant articles from {source_name}")

        except Exception as e:
            print(f"❌ Error scraping {source_name}: {str(e)}")
            continue

    return all_articles

# -------------------------------------------------------
# SAVE TO JSON
# -------------------------------------------------------
def save_to_json(articles: List[Dict[str, Any]]):
    """Save articles to JSON file"""
    output_file = "data/industry_news.json"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved to: {output_file}")
    except Exception as e:
        print(f"\n❌ Error saving JSON: {e}")

# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
if __name__ == "__main__":
    start_time = time.time()
    
    articles = industry_scraper(max_articles_per_source=10)
    
    if articles:
        save_to_json(articles)
        
        print("\n" + "=" * 80)
        print("✅ INDUSTRY NEWS SCRAPING COMPLETED!")
        print(f"📊 Total Articles: {len(articles)}")
        print(f"⏱️  Time Taken: {time.time() - start_time:.2f} seconds")
        
        # Sentiment distribution
        sentiments = {}
        for article in articles:
            sentiment = article.get("sentiment", "neutral")
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        
        print(f"📈 Sentiment Distribution: {sentiments}")
        
        if articles:
            top = articles[0]
            print(f"🏆 Top Article: {top['title'][:60]}...")
            print(f"   Relevance: {top['reason_for_relevance'][:80]}...")
        
        print("=" * 80)
    else:
        print("\n⚠️  No relevant articles found in the time window.")
