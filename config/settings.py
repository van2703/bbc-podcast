"""
Configuration settings for BBC News Podcast project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent

# RSS Feed
RSS_URL = "http://feeds.bbci.co.uk/news/technology/rss.xml"
MAX_ARTICLES = 8

# Schedule (UTC+7 timezone)
SCHEDULE_HOUR = 6
SCHEDULE_MINUTE = 0

# Request settings
REQUEST_TIMEOUT = 10
RATE_LIMIT_DELAY = 1
RETRY_ATTEMPTS = 3
RETRY_BASE_DELAY = 2
MIN_CONTENT_LENGTH = 100

# GitHub Configuration
GITHUB_REPO = os.getenv("GITHUB_REPO", "your-username/bbc-podcast")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# AI Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Database
DATABASE_PATH = PROJECT_ROOT / "data" / "database.db"

# Audio
AUDIO_OUTPUT_DIR = PROJECT_ROOT / "audio" / "episodes"

# Web
WEB_PORT = 8501
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Supabase
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() == "true"
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Ensure directories exist
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
