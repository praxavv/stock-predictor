import feedparser
from typing import List, Dict
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time

class NewsScraper:
    def __init__(self):
        self.feeds = {
            "US/World": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US",
            "India": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
        }

    def clean_html(self, text: str) -> str:
        if not text:
            return ""
        return re.sub('<[^<]+?>', '', text)

    def fetch_single_feed(self, category: str, url: str) -> List[Dict[str, str]]:
        try:
            feed = feedparser.parse(url)
            items = []
            # Extreme reduction: only top 3 items for speed
            for entry in feed.entries[:3]:
                items.append({
                    "title": entry.title,
                    "summary": self.clean_html(entry.get("summary", entry.get("description", ""))),
                    "link": entry.link,
                    "source": category,
                    "published": entry.get("published", "")
                })
            return items
        except Exception as e:
            print(f"Error fetching {category}: {e}")
            return []

    def fetch_news(self) -> List[Dict[str, str]]:
        all_news = []
        
        with ThreadPoolExecutor(max_workers=len(self.feeds)) as executor:
            futures = [executor.submit(self.fetch_single_feed, cat, url) for cat, url in self.feeds.items()]
            for future in futures:
                all_news.extend(future.result())
        
        return all_news

def get_latest_news() -> List[Dict[str, str]]:
    scraper = NewsScraper()
    return scraper.fetch_news()
