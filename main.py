"""
BBC News Podcast Pipeline - Main orchestrator.

Usage:
    python main.py           # Run once
    python main.py --serve   # Start scheduler
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from config.settings import MAX_ARTICLES, GITHUB_REPO

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_pipeline():
    """Run the complete podcast pipeline."""
    logger.info("=" * 50)
    logger.info("Starting BBC News Podcast Pipeline")
    logger.info("=" * 50)

    start_time = datetime.now()

    try:
        # Step 1: Fetch newsarticles
        logger.info("Step 1: Fetching BBC news...")
        from src.scraper import NewsFetcher

        fetcher = NewsFetcher()
        articles = fetcher.fetch_articles()

        if not articles:
            logger.error("No articles fetched, aborting")
            return False

        logger.info(f"Fetched {len(articles)} articles")
        for i, a in enumerate(articles, 1):
            logger.info(f"  {i}. {a['title'][:50]}...")

        # Step 2: Generate script
        logger.info("Step 2: Generating script...")
        from src.script_gen import ScriptGenerator

        generator = ScriptGenerator()
        script_data = generator.generate_script(articles)

        script = script_data.get("script", "")
        title = script_data.get(
            "title", f"Podcast {datetime.now().strftime('%Y-%m-%d')}"
        )
        summary = script_data.get("summary", "")

        logger.info(f"Script generated: {len(script)} chars")
        logger.info(f"Title: {title}")

        # Step 3: Convert to speech
        logger.info("Step 3: Converting to audio...")
        from src.tts_gen import TTSEngine

        tts = TTSEngine()
        audio_data = tts.text_to_speech(script)

        audio_path = audio_data.get("file", "")
        duration = audio_data.get("duration", 0)

        logger.info(f"Audio generated: {audio_path}")
        logger.info(f"Duration: {duration // 60}m {duration % 60}s")

        # Step 4: Upload to GitHub
        logger.info("Step 4: Uploading to GitHub...")
        from src.storage import GitHubStorage

        storage = GitHubStorage()
        upload_data = storage.upload_episode(Path(audio_path), title)

        audio_url = upload_data.get("url", audio_path)

        logger.info(f"Uploaded: {audio_url}")

        # Step 5: Save to database
        logger.info("Step 5: Saving to database...")
        from src.database import get_database

        db = get_database()

        episode_id = db.add_episode(
            {
                "title": title,
                "summary": summary,
                "script": script,
                "audio_url": audio_url,
                "source_links": [a["link"] for a in articles[:3]],
                "duration": duration,
            }
        )

        logger.info(f"Saved episode ID: {episode_id}")

        # Complete
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("=" * 50)
        logger.info(f"Pipeline completed in {elapsed:.1f}s")
        logger.info(f"Episode: {title}")
        logger.info("=" * 50)

        return True

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="BBC News Podcast Pipeline")
    parser.add_argument("--serve", action="store_true", help="Run as scheduler")
    args = parser.parse_args()

    if args.serve:
        logger.info("Starting scheduler mode...")
        from src.scheduler import start_scheduler

        start_scheduler(run_pipeline)
    else:
        success = run_pipeline()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
