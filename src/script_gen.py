"""
AI Script Generator - Transform articles into podcast script.
"""

import json
import logging
from typing import Dict, List

import requests

from config.settings import OPENROUTER_API_KEY

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ScriptGenerator:
    """Generate podcast script from articles using AI."""

    def __init__(self, api_key: str = OPENROUTER_API_KEY):
        self.api_key = api_key
        self.model = "openai/gpt-4o"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def generate_script(self, articles: List[Dict]) -> Dict:
        """Generate podcast script from articles."""
        if not self.api_key:
            logger.warning("No API key, using fallback script")
            return self._fallback_script(articles)

        # Build article content
        content = self._build_article_content(articles)

        # Generate with AI
        result = self._call_ai(content)

        if result:
            return result
        return self._fallback_script(articles)

    def _build_article_content(self, articles: List[Dict]) -> str:
        """Build combined article text."""
        lines = []
        for i, article in enumerate(articles, 1):
            lines.append(f"\n--- Article {i} ---")
            lines.append(f"Title: {article.get('title', '')}")
            lines.append(f"Content: {article.get('content', '')[:1500]}")
        return "\n".join(lines)

    def _call_ai(self, content: str) -> Dict:
        """Call AI API to generate script."""
        prompt = f"""You are a professional podcast script writer. Transform these BBC news articles into an engaging 5-minute podcast script.

Articles:
{content}

Requirements:
1. Script length: ~750 words (5 minutes at 150 wpm)
2. Format: Single host (solo) delivering news
3. Include: Intro (greeting) → News stories → Outro
4. Cite sources: "According to BBC News..." after each story
5. Make it conversational and engaging
6. Output as JSON with keys: script, title, summary

Output JSON format:
{{
    "script": "Full podcast script...",
    "title": "BBC News Podcast - YYYY-MM-DD",
    "summary": "2-3 sentence summary of episode"
}}"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://bbc-podcast.local",
            "X-Title": "BBC News Podcast",
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional podcast script writer.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=data, timeout=60
            )
            response.raise_for_status()

            result = response.json()
            text = result["choices"][0]["message"]["content"]

            # Parse JSON from response
            if "{" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                json_str = text[start:end]
                return json.loads(json_str)

        except Exception as e:
            logger.warning(f"AI API call failed: {e}")

        return {}

    def _fallback_script(self, articles: List[Dict]) -> Dict:
        """Fallback script when AI fails."""
        from datetime import datetime

        article_titles = [a.get("title", "News")[:30] for a in articles[:3]]
        titles_str = ", ".join(article_titles)

        script = f"""Welcome to your daily BBC News podcast! I'm your host.

Today we're covering: {titles_str}

[News stories would be here in the full script]

That's all for today. Thanks for listening, and see you tomorrow!

---
Sources: BBC News Technology"""

        return {
            "script": script,
            "title": f"BBC News Podcast - {datetime.now().strftime('%Y-%m-%d')}",
            "summary": f"Daily news podcast covering {len(articles)} articles: {titles_str}",
        }


def generate_podcast_script(articles: List[Dict]) -> Dict:
    """Simple function to generate script."""
    generator = ScriptGenerator()
    return generator.generate_script(articles)


if __name__ == "__main__":
    test_articles = [
        {
            "title": "Test Article",
            "link": "http://example.com",
            "content": "This is test content for the article.",
        }
    ]
    result = generate_podcast_script(test_articles)
    print(f"Title: {result.get('title')}")
    print(f"Summary: {result.get('summary')}")
