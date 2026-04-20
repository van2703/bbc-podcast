"""
Database Manager - Supabase with SQLite fallback.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import supabase
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

from config.settings import (
    DATABASE_PATH,
    USE_SUPABASE,
    SUPABASE_URL,
    SUPABASE_KEY,
    PROJECT_ROOT,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SQLiteDB:
    """SQLite fallback database."""

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

        logger.info(f"SQLite: Episode added {episode_id}")
        return episode_id

    def get_episodes(self, limit: int = 50) -> List[Dict]:
        """Get all episodes, newest first."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM episodes ORDER BY created_at DESC LIMIT ?", (limit,)
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row["id"],
                "title": row["title"],
                "summary": row["summary"],
                "audio_url": row["audio_url"],
                "duration": row["duration"],
                "created_at": row["created_at"],
                "source_links": json.loads(row["source_links"] or "[]"),
            }
            for row in rows
        ]

    def get_episode(self, episode_id: int) -> Optional[Dict]:
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
        """Get logs."""
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
            {"level": r["level"], "message": r["message"], "created_at": r["created_at"]}
            for r in rows
        ]


class SupabaseDB:
    """Supabase database wrapper."""

    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.client = supabase.create_client(url, key)
        logger.info("Supabase client initialized")

    def add_episode(self, data: Dict) -> int:
        """Add episode to Supabase."""
        payload = {
            "title": data.get("title", ""),
            "summary": data.get("summary", ""),
            "script": data.get("script", ""),
            "audio_url": data.get("audio_url", ""),
            "source_links": json.dumps(data.get("source_links", [])),
            "duration": data.get("duration", 0),
        }

        response = self.client.table("episodes").insert(payload).execute()

        if response.data:
            episode_id = response.data[0].get("id", 0)
            logger.info(f"Supabase: Episode added {episode_id}")
            return episode_id

        logger.warning("Supabase insert returned no data")
        return 0

    def get_episodes(self, limit: int = 50) -> List[Dict]:
        """Get all episodes from Supabase."""
        response = (
            self.client.table("episodes")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        episodes = []
        for row in response.data:
            episodes.append(
                {
                    "id": row.get("id"),
                    "title": row.get("title"),
                    "summary": row.get("summary"),
                    "audio_url": row.get("audio_url"),
                    "duration": row.get("duration"),
                    "created_at": row.get("created_at"),
                    "source_links": json.loads(row.get("source_links", "[]")),
                }
            )

        return episodes

    def get_episode(self, episode_id: int) -> Optional[Dict]:
        """Get single episode from Supabase."""
        response = (
            self.client.table("episodes")
            .select("*")
            .eq("id", episode_id)
            .execute()
        )

        if not response.data:
            return None

        row = response.data[0]
        return {
            "id": row.get("id"),
            "title": row.get("title"),
            "summary": row.get("summary"),
            "script": row.get("script"),
            "audio_url": row.get("audio_url"),
            "source_links": json.loads(row.get("source_links", "[]")),
            "duration": row.get("duration"),
            "created_at": row.get("created_at"),
        }

    def delete_episode(self, episode_id: int) -> bool:
        """Delete episode from Supabase."""
        response = (
            self.client.table("episodes")
            .delete()
            .eq("id", episode_id)
            .execute()
        )

        return len(response.data) > 0 if response.data else False

    def add_log(self, level: str, message: str):
        """Add log entry (logs table may not exist in Supabase)."""
        logger.info(f"Log: [{level}] {message}")

    def get_logs(self, limit: int = 100, level: str = None) -> List[Dict]:
        """Get logs (not implemented for Supabase)."""
        return []


class Database:
    """Unified database interface with Supabase + SQLite fallback."""

    def __init__(self):
        self.use_supabase = False
        self.db: Optional[SupabaseDB | SQLiteDB] = None

        if USE_SUPABASE and SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_KEY:
            try:
                self.db = SupabaseDB(SUPABASE_URL, SUPABASE_KEY)
                self.use_supabase = True
                logger.info("Using Supabase database")
            except Exception as e:
                logger.warning(f"Supabase connection failed: {e}, using SQLite fallback")
                self._init_sqlite()
        else:
            logger.info("Using SQLite database (fallback)")
            self._init_sqlite()

    def _init_sqlite(self):
        """Initialize SQLite fallback."""
        self.db = SQLiteDB()
        self.use_supabase = False

    def add_episode(self, data: Dict) -> int:
        """Add episode."""
        if self.db:
            return self.db.add_episode(data)
        return 0

    def get_episodes(self, limit: int = 50) -> List[Dict]:
        """Get all episodes."""
        if self.db:
            return self.db.get_episodes(limit)
        return []

    def get_episode(self, episode_id: int) -> Optional[Dict]:
        """Get single episode."""
        if self.db:
            return self.db.get_episode(episode_id)
        return None

    def delete_episode(self, episode_id: int) -> bool:
        """Delete episode."""
        if self.db:
            return self.db.delete_episode(episode_id)
        return False

    def add_log(self, level: str, message: str):
        """Add log entry."""
        if self.db:
            self.db.add_log(level, message)

    def get_logs(self, limit: int = 100, level: str = None) -> List[Dict]:
        """Get logs."""
        if self.db:
            return self.db.get_logs(limit, level)
        return []


_db: Optional[Database] = None


def get_database() -> Database:
    """Get database instance (singleton)."""
    global _db
    if _db is None:
        _db = Database()
    return _db


if __name__ == "__main__":
    db = get_database()
    episodes = db.get_episodes()
    print(f"Total episodes: {len(episodes)}")
    print(f"Using Supabase: {db.use_supabase}")