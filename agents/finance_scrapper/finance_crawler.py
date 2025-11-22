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
# TIME WINDOW: LAST 10 HOURS
# -------------------------------------------------------
TIME_WINDOW_HOURS = 10
CUTOFF_TIME = datetime.now() - timedelta(hours=TIME_WINDOW_HOURS)

# -------------------------------------------------------
# CURATED FINANCIAL NEWS SOURCES
# -------------------------------------------------------
FINANCE_SOURCES = [
    "https://www.moneycontrol.com/news/business/",
    "https://www.livemint.com/market",
    "https://economictimes.indiatimes.com/markets",
    "https://www.bloomberg.com/markets",
    "https://www.reuters.com/markets/"
]

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
    """Check if article was published within last 10 hours"""
    try:
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
# HELPER – CHECK RELEVANCE TO COMPANY
# -------------------------------------------------------
def is_relevant_to_company(text, title):
    """Check if article is relevant to company"""
    combined_text = (title + " " + text).lower()
    
    # Check company name
    if COMPANY_NAME.lower() in combined_text or STOCK_SYMBOL.lower() in combined_text:
        return True, f"Direct mention of {COMPANY_NAME}"
    
    # Check competitors
    competitors_found = [c for c in COMPETITORS if c.lower() in combined_text]
    if competitors_found:
        return True, f"Competitor mentions: {', '.join(competitors_found)}"
    
    # Check industry
    if INDUSTRY.lower() in combined_text:
        return True, f"Industry mention: {INDUSTRY}"
    
    # Check product terms (at least 2 matches for relevance)
    product_matches = [p for p in PRODUCT_TERMS if p.lower() in combined_text]
    if len(product_matches) >= 2:
        return True, f"Product-related: {', '.join(product_matches[:3])}"
    
    # Check risk terms with company context
    risk_matches = [r for r in RISK_KEYWORDS if r.lower() in combined_text]
    if risk_matches and (COMPANY_NAME.lower() in combined_text or any(c.lower() in combined_text for c in COMPETITORS)):
        return True, f"Risk keywords with company context: {', '.join(risk_matches[:3])}"
    
    return False, "No direct relevance to company"

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
            tables_json.append(df.to_dict(orient="records"))
        except:
            pass

    return tables_json

# -------------------------------------------------------
# HELPER – EXTRACT IMAGES
# -------------------------------------------------------
def extract_images(soup: BeautifulSoup) -> List[str]:
    """Extract high-quality images from article (max 3)"""
    images = []
    
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        
        # Skip small images, icons, logos
        width = img.get("width", "")
        height = img.get("height", "")
        
        if width and height:
            try:
                if int(width) < 200 or int(height) < 150:
                    continue
            except:
                pass
        
        # Skip ads, tracking pixels, logos
        if any(skip in src.lower() for skip in ["logo", "icon", "avatar", "ads", "banner", "pixel", "tracking"]):
            continue
        
        images.append(src)
        
        if len(images) >= 3:  # Max 3 images
            break
    
    return images

# -------------------------------------------------------
# HELPER – EXTRACT NUMBERS FROM TEXT
# -------------------------------------------------------
def extract_numbers(text: str) -> Dict[str, List[str]]:
    """Extract financial numbers, percentages, revenues, profits from text"""
    numbers = {
        "revenues": [],
        "profit_loss": [],
        "percent_changes": [],
        "stock_price": []
    }
    
    # Revenue patterns
    revenue_patterns = [
        r"revenue[s]?\s+(?:of\s+)?[\$₹]?\s*([\d,\.]+)\s*(?:million|billion|crore|lakh)?",
        r"sales\s+(?:of\s+)?[\$₹]?\s*([\d,\.]+)\s*(?:million|billion|crore|lakh)?"
    ]
    
    # Profit/loss patterns
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
    
    # Factor in risk terms and sensitive topics
    neg_count += len(analysis.get("risk_tags_detected", [])) + len(analysis.get("sensitive_hits", []))
    
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
# HELPER – DETERMINE RELEVANCE
# -------------------------------------------------------
def is_relevant(analysis: Dict, text: str) -> tuple[bool, str]:
    """Determine if article is relevant to company - STRICT filter for company/competitors only"""
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
    
    # Check for industry mentions
    if INDUSTRY.lower() in text.lower():
        reasons.append(f"Industry mention: {INDUSTRY}")
    
    # STRICT: Must have company OR competitor mention to be considered relevant
    is_relevant_article = analysis["company_match"] or len(analysis["competitor_mentions"]) > 0
    reason_str = " | ".join(reasons) if reasons else "No direct relevance found"
    
    return is_relevant_article, reason_str

# -------------------------------------------------------
# MAIN ARTICLE SCRAPER
# -------------------------------------------------------
def scrape_article(url: str) -> Dict[str, Any]:
    """Scrape and analyze a single article - STRICT company/competitor filter"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        res = requests.get(url, timeout=15, headers=headers)
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
        
        # STRICT: Only include if relevant to company/competitors
        if not is_rel:
            return None
        
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
        
        return article_json
        
    except Exception as e:
        print(f"    ❌ Error scraping {url[:80]}: {str(e)[:50]}")
        return None

# -------------------------------------------------------
# SOURCE SCRAPER (FINANCE CATEGORY)
# -------------------------------------------------------
def finance_scraper(max_articles_per_source: int = 30) -> List[Dict[str, Any]]:
    """Scrape financial news from curated sources - ONLY company/competitor related"""
    all_articles = []
    seen_urls = set()

    for src in FINANCE_SOURCES:
        print(f"\n🔍 Scraping: {src}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            page = requests.get(src, timeout=15, headers=headers)
            soup = BeautifulSoup(page.text, "lxml")

            # all clickable links
            links = soup.find_all("a", href=True)
            articles_from_source = 0

            for a in links:
                if articles_from_source >= max_articles_per_source:
                    break
                    
                href = a.get("href")
                if not href: continue

                # skip ads, anchors, and javascript
                if any(skip in href.lower() for skip in ["javascript", "#", "mailto:", "tel:"]):
                    continue

                # absolute URL fix
                href = urljoin(src, href)
                
                # Skip duplicates
                if href in seen_urls:
                    continue
                    
                # Only process article-like URLs
                if not any(pattern in href for pattern in ["/news/", "/article/", "/story/", "/markets/", "/business/"]):
                    continue

                try:
                    article_data = scrape_article(href)
                    
                    # Article is None if not relevant or outside time window
                    if article_data:
                        all_articles.append(article_data)
                        seen_urls.add(href)
                        articles_from_source += 1
                        print(f"  ✅ {article_data['title'][:60]}... | {article_data['sentiment']}")
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    pass

            print(f"✅ Found {articles_from_source} relevant articles from {urlparse(src).netloc}")

        except Exception as e:
            print(f"❌ Failed to scrape {urlparse(src).netloc}: {str(e)[:50]}")
            pass

    return all_articles


# -------------------------------------------------------
# SAVE TO JSON
# -------------------------------------------------------
def save_to_json(articles: List[Dict[str, Any]], filename: str = "finance_news.json"):
    """Save scraped articles to JSON file"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved {len(articles)} articles to {filename}")

# -------------------------------------------------------
# RUN SCRAPER
# -------------------------------------------------------
if __name__ == "__main__":
    print("=" * 80)
    print(f"🚀 FINANCE NEWS CRAWLER FOR {COMPANY_NAME}")
    print(f"📅 Time Window: Last {TIME_WINDOW_HOURS} hours")
    print(f"🎯 Filter: ONLY {COMPANY_NAME} and competitors ({', '.join(COMPETITORS)})")
    print("=" * 80)
    
    start_time = time.time()
    data = finance_scraper(max_articles_per_source=20)
    
    # Save results
    save_to_json(data, "finance_news.json")
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print(f"✅ FINANCE NEWS SCRAPED SUCCESSFULLY!")
    print(f"📊 Total Relevant Articles: {len(data)}")
    print(f"⏱️  Time Taken: {elapsed:.2f} seconds")
    
    if data:
        print(f"\n📈 Sentiment Distribution:")
        sentiments = {"positive": 0, "neutral": 0, "negative": 0}
        for article in data:
            sentiments[article["sentiment"]] += 1
        for sentiment, count in sentiments.items():
            print(f"   {sentiment.capitalize()}: {count}")
        
        print(f"\n🏆 Top Article: {data[0]['title'][:70]}...")
        print(f"   Reason: {data[0]['reason_for_relevance'][:70]}...")
        print(f"   Sentiment: {data[0]['sentiment']}")
        print(f"   Stock Mentions: {', '.join(data[0]['stock_mentions']) if data[0]['stock_mentions'] else 'None'}")
    else:
        print(f"\n⚠️  No articles found for {COMPANY_NAME} or competitors in the last {TIME_WINDOW_HOURS} hours")
    
    print("=" * 80)
