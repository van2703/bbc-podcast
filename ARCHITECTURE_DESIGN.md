# BBC News AI Podcast - Architecture Design

**Version:** 3.0 (Simplified) | **Date:** April 2026

---

## 1. System Overview

The system follows a modular pipeline architecture:

```
Scheduler (cron)
    │
    ▼
main.py (orchestrator)
    │
    ├── scraper.py     → Fetch BBC articles
    ├── script_gen.py   → AI write script
    ├── tts_gen.py     → Text to speech
    ├── storage.py      → Upload to GitHub
    │
    └── database.py    → Store metadata
    │
    ▼
web/app.py (Streamlit)
```

---

## 2. Module Specifications

### 2.1 scraper.py (News Fetcher)

```python
class NewsFetcher:
    def fetch_articles() -> List[Dict]
        # Fetch 8 articles from BBC RSS
        # Returns: [{"title": str, "link": str, "content": str}]
```

### 2.2 script_gen.py (AI Script Generator)

```python
class ScriptGenerator:
    def generate_script(articles: List[Dict]) -> Dict
        # Input: list of article dicts
        # Output: {"script": str, "sentiment": str}
        # Uses OpenRouter API (GPT-4)
```

### 2.3 tts_gen.py (Text-to-Speech)

```python
class TTSEngine:
    def text_to_speech(script: str, output_path: Path) -> Dict
        # Convert script to MP3
        # Uses Edge-TTS (free voices)
        # Output: {"file": Path, "duration": float}
```

### 2.4 storage.py (GitHub Storage)

```python
class GitHubStorage:
    def upload_episode(mp3_path: Path, title: str) -> str
        # Upload to GitHub Releases
        # Returns: download URL
    
    def cleanup_old(days: int) -> int
        # Delete releases older than N days
```

### 2.5 database.py (Metadata Store)

```python
class Database:
    def add_episode(data: Dict) -> str
        # Save: title, script, audio_url, created_at
    
    def get_episodes(limit: int) -> List[Dict]
        # Get all episodes, newest first
```

### 2.6 scheduler.py (Daily Runner)

```python
class Scheduler:
    def start()
        # Run daily at 6:00 AM UTC+7
        # Uses APScheduler
```

### 2.7 web/app.py (Web Interface)

```python
# Pages:
# - / (home): episode list
# - Each episode: audio player + info
# - Admin: generate button
```

---

## 3. Folder Structure

```
bbc-podcast-ai/
├── config/
│   └── settings.py
├── src/
│   ├── scraper.py
│   ├── script_gen.py
│   ├── tts_gen.py
│   ├── storage.py
│   ├── database.py
│   └── scheduler.py
├── web/
│   └── app.py
├── data/
│   └── database.db
├── audio/
│   └── episodes/
├── main.py
└── requirements.txt
```

---

## 4. Configuration

All settings in `config/settings.py`:

```python
# BBC RSS
RSS_URL = "http://feeds.bbci.co.uk/news/technology/rss.xml"
MAX_ARTICLES = 8

# Schedule (UTC+7 = 23:00 UTC)
SCHEDULE_HOUR = 6
SCHEDULE_MINUTE = 0

# GitHub
GITHUB_REPO = "owner/repo"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# AI
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
```

---

## 5. External Services

| Service | Purpose | Cost |
|--------|---------|------|
| OpenRouter | AI script + voice | ~$5/month |
| GitHub | Storage + Pages | Free |
| Edge-TTS | Text-to-speech | Free |

---

## 6. Error Handling

- **BBC unreachable:** Use evergreen fallback articles
- **AI fails:** Retry 3x, then abort
- **TTS fails:** Retry 3x, then abort
- **GitHub upload fails:** Retry 3x, keep file locally

---

## 7. Security

- API keys in `.env` (never in git)
- Admin password for web admin features
- HTTPS on GitHub Pages