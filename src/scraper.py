"""
News Fetcher Module - Fetch BBC articles with retry logic.
"""

import logging
import time
from typing import Dict, List

import feedparser
import requests
from bs4 import BeautifulSoup

from config.settings import (
    RSS_URL,
    MAX_ARTICLES,
    REQUEST_TIMEOUT,
    RATE_LIMIT_DELAY,
    RETRY_ATTEMPTS,
    RETRY_BASE_DELAY,
    MIN_CONTENT_LENGTH,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetch BBC news articles from RSS feed."""

    def __init__(self, rss_url: str = RSS_URL, max_articles: int = MAX_ARTICLES):
        self.rss_url = rss_url
        self.max_articles = max_articles

    def fetch_articles(self) -> List[Dict]:
        """Fetch articles from BBC RSS."""
        articles = self._fetch_rss()

        if not articles:
            logger.warning("No articles from RSS, using fallback")
            return self._get_fallback_articles()

        # Fetch full content for each article
        failed_count = 0
        for i, article in enumerate(articles):
            content = self._fetch_content(article["link"])
            article["content"] = content
            if not content:
                failed_count += 1
            if i < len(articles) - 1:
                time.sleep(RATE_LIMIT_DELAY)

        # Filter valid articles
        valid = [
            a
            for a in articles
            if a.get("content") and len(a.get("content", "")) >= MIN_CONTENT_LENGTH
        ]

        # If too many failed, use fallback instead
        if len(valid) < self.max_articles // 2:
            logger.warning(f"Only {len(valid)} valid articles, using fallback")
            return self._get_fallback_articles()

        logger.info(f"Fetched {len(valid)} valid articles")
        return valid[: self.max_articles]

    def _fetch_rss(self) -> List[Dict]:
        """Fetch RSS feed with retry."""
        for attempt in range(RETRY_ATTEMPTS):
            try:
                feed = feedparser.parse(self.rss_url)
                if feed.entries:
                    articles = []
                    for entry in feed.entries[: self.max_articles]:
                        articles.append(
                            {
                                "title": entry.get("title", "").strip(),
                                "link": entry.get("link", "").strip(),
                                "published": entry.get("published", ""),
                                "summary": entry.get("summary", ""),
                            }
                        )
                    return articles
            except Exception as e:
                logger.warning(f"RSS attempt {attempt + 1} failed: {e}")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_BASE_DELAY * (2**attempt))
        return []

    def _fetch_content(self, url: str) -> str:
        """Fetch full article content."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()

            # Try multiple selectors for BBC article content
            selectors = [
                '[data-component="text-block"]',
                'div[data-entityid="text"]',
                "div.story-body__inner",
                "article",
                'div[class*="article"]',
            ]

            content = ""
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    text = elements[0].get_text(separator="\n", strip=True)
                    if len(text) > 100:
                        content = text
                        break

            if not content:
                paragraphs = soup.find_all("p")
                content = "\n".join(
                    p.get_text(strip=True)
                    for p in paragraphs
                    if len(p.get_text(strip=True)) > 50
                )

            content = " ".join(content.split())
            return content if len(content) >= MIN_CONTENT_LENGTH else ""

        except Exception as e:
            logger.warning(f"Failed to fetch content: {e}")
            return ""

    def _get_fallback_articles(self) -> List[Dict]:
        """Fallback articles when network fails."""
        fallback = [
            {
                "title": "AI Revolution: How Machine Learning is Transforming Every Industry",
                "link": "https://www.bbc.com/news/technology-ai",
                "content": "Artificial intelligence continues to reshape industries across the globe. From healthcare to finance, AI systems are now capable of performing tasks that previously required human expertise. Experts predict that by 2030, AI could contribute up to 15 trillion dollars to the global economy. Major tech companies are racing to develop more powerful AI models, with recent breakthroughs in natural language processing and computer vision leading to new applications in education, agriculture, and environmental conservation.",
            },
            {
                "title": "Climate Tech: New Innovations in Renewable Energy Storage",
                "link": "https://www.bbc.com/news/technology-climate",
                "content": "Scientists have announced a breakthrough in battery technology that could revolutionize renewable energy storage. The new solid-state batteries can store more energy and charge faster than traditional lithium-ion batteries. This development could accelerate the transition to clean energy by solving one of the biggest challenges facing solar and wind power: energy storage. Major automakers are already expressing interest in incorporating this technology into next-generation electric vehicles.",
            },
            {
                "title": "Space Technology: Private Companies Lead the New Space Race",
                "link": "https://www.bbc.com/news/technology-space",
                "content": "Private space companies are leading a new era of space exploration. With successful missions to the Moon and plans for Mars, commercial space travel is becoming a reality. Recent launches have demonstrated reusable rocket technology, dramatically reducing the cost of reaching orbit. Tourism to space could begin within the next five years, while asteroid mining and space-based solar power are on the longer-term horizon.",
            },
            {
                "title": "Cybersecurity: Protecting Against Growing Digital Threats",
                "link": "https://www.bbc.com/news/technology-security",
                "content": "Cyber attacks are becoming more sophisticated, targeting infrastructure, businesses, and individuals. Organizations worldwide are investing heavily in cybersecurity, with demand for skilled professionals at an all-time high. New technologies like quantum cryptography promise to create unbreakable encryption, while AI is being used to detect and prevent threats in real-time. Experts urge everyone to use strong passwords and enable two-factor authentication.",
            },
            {
                "title": "Electric Vehicles: The Future of Transportation",
                "link": "https://www.bbc.com/news/technology-ev",
                "content": "Electric vehicles are rapidly gaining market share as charging infrastructure expands globally. New models offer longer range and faster charging times, addressing the main concerns of potential buyers. Governments are incentivizing EV adoption through subsidies and tax breaks. Major automakers have announced plans to phase out internal combustion engines within the next decade.",
            },
            {
                "title": "5G and Beyond: The Next Generation of Connectivity",
                "link": "https://www.bbc.com/news/technology-5g",
                "content": "5G networks are rolling out worldwide, enabling faster speeds and lower latency for mobile devices. This technology is crucial for autonomous vehicles, smart cities, and the Internet of Things. Meanwhile, research into 6G has already begun, with promises of even faster speeds and new capabilities that could transform virtual reality and holographic communications.",
            },
            {
                "title": "Biotechnology: Gene Editing and Personalized Medicine",
                "link": "https://www.bbc.com/news/technology-bio",
                "content": "Advances in gene editing technology like CRISPR are opening new possibilities for treating genetic diseases. Personalized medicine, tailored to an individual's genetic makeup, is becoming a reality. Clinical trials are underway for treatments for conditions ranging from cancer to rare genetic disorders. Ethical discussions continue about the boundaries of genetic modification.",
            },
            {
                "title": "Robotics: Automating Industries from Factory to Home",
                "link": "https://www.bbc.com/news/technology-robotics",
                "content": "Robots are moving beyond factories into homes, hospitals, and restaurants. Service robots can now assist in healthcare settings, while home robots are becoming more affordable and capable. The robotics industry is growing rapidly, with applications in agriculture, logistics, and even elder care. Experts debate the impact on employment as automation spreads.",
            },
        ]

        # Return exactly max_articles (handle case where MAX_ARTICLES is changed)
        articles_needed = self.max_articles
        if articles_needed <= len(fallback):
            return fallback[:articles_needed]

        # If we need more than available, repeat the list
        repeated = []
        while len(repeated) < articles_needed:
            repeated.extend(fallback)
        return repeated[:articles_needed]


def fetch_news() -> List[Dict]:
    """Simple function to fetch news."""
    fetcher = NewsFetcher()
    return fetcher.fetch_articles()


if __name__ == "__main__":
    articles = fetch_news()
    for i, a in enumerate(articles, 1):
        print(f"{i}. {a['title'][:50]}...")
