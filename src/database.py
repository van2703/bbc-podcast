"""
Database Manager - Store episode metadata.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from config.settings import DATABASE_PATH

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Database:
    """Store and retrieve episode metadata."""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create tables if not exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT,
                script TEXT,
                audio_url TEXT,
                source_links TEXT,
                sentiment TEXT,
                duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_episode(self, data: Dict) -> int:
        """Add episode to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO episodes (title, summary, script, audio_url, source_links, sentiment, duration) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                data.get("title", ""),
                data.get("summary", ""),
                data.get("script", ""),
                data.get("audio_url", ""),
                json.dumps(data.get("source_links", [])),
                data.get("sentiment", ""),
                data.get("duration", 0),
            ),
        )

        episode_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Episode added: {episode_id}")
        return episode_id

    def get_episodes(self, limit: int = 50) -> List[Dict]:
        """Get all episodes, newest first."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM episodes 
            ORDER BY created_at DESC 
            LIMIT ?
        """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        episodes = []
        for row in rows:
            episodes.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "summary": row["summary"],
                    "audio_url": row["audio_url"],
                    "duration": row["duration"],
                    "created_at": row["created_at"],
                    "source_links": json.loads(row["source_links"] or "[]"),
                }
            )

        return episodes

    def get_episode(self, episode_id: int) -> Dict:
        """Get single episode."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "id": row["id"],
            "title": row["title"],
            "summary": row["summary"],
            "script": row["script"],
            "audio_url": row["audio_url"],
            "source_links": json.loads(row["source_links"] or "[]"),
            "sentiment": row["sentiment"],
            "duration": row["duration"],
            "created_at": row["created_at"],
        }

    def delete_episode(self, episode_id: int) -> bool:
        """Delete episode."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    def add_log(self, level: str, message: str):
        """Add log entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (level, message) VALUES (?, ?)", (level, message)
        )
        conn.commit()
        conn.close()

    def get_logs(self, limit: int = 100, level: str = None) -> List[Dict]:
        """Get logs, optionally filtered by level."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if level:
            cursor.execute(
                "SELECT * FROM logs WHERE level = ? ORDER BY id DESC LIMIT ?",
                (level, limit),
            )
        else:
            cursor.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "level": r["level"],
                "message": r["message"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]


# Singleton instance
_db = None


def get_database() -> Database:
    """Get database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db


if __name__ == "__main__":
    db = get_database()
    episodes = db.get_episodes()
    print(f"Total episodes: {len(episodes)}")
