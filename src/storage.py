"""
Storage Manager - Upload to GitHub Releases.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

import requests

from config.settings import GITHUB_REPO, GITHUB_TOKEN

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GitHubStorage:
    """Manage storage via GitHub Releases."""

    def __init__(self, repo: str = "van2703/bbc-podcast", token: str = GITHUB_TOKEN):
        self.repo = repo
        self.token = token
        self.api_url = f"https://api.github.com/repos/{repo}"
        self.headers = {
            "Authorization": f"Bearer {token}" if token else "",
            "Accept": "application/vnd.github+json",
        }

    def upload_episode(self, mp3_path: Path, title: str) -> Dict:
        """Upload MP3 to GitHub Release."""
        if not self.token:
            logger.warning("No GitHub token, saving locally")
            return {"url": str(mp3_path), "local": True}

        try:
            release = self._get_or_create_release()
            asset = self._upload_asset(release["id"], mp3_path)

            if asset:
                logger.info(f"Uploaded: {asset.get('browser_download_url')}")
                return {"url": asset.get("browser_download_url"), "id": asset.get("id")}

        except Exception as e:
            logger.warning(f"GitHub upload failed: {e}")

        return {"url": str(mp3_path), "local": True}

    def _get_or_create_release(self) -> Dict:
        """Get latest release or create new one."""
        response = requests.get(f"{self.api_url}/releases/latest", headers=self.headers)

        if response.status_code == 200:
            return response.json()

        if response.status_code == 404:
            tag = f"v{datetime.now().strftime('%Y%m%d')}"
            data = {
                "tag_name": tag,
                "name": f"Podcast {datetime.now().strftime('%Y-%m-%d')}",
                "draft": False,
                "prerelease": False,
            }

            response = requests.post(
                f"{self.api_url}/releases", headers=self.headers, json=data
            )

            if response.status_code in (201, 200):
                return response.json()

        raise Exception(f"Failed to get/create release: {response.status_code}")

    def _upload_asset(self, release_id: int, file_path: Path) -> Dict:
        """Upload file to release."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        response = requests.get(
            f"{self.api_url}/releases/{release_id}", headers=self.headers
        )
        upload_url = response.json().get("upload_url", "")
        upload_url = upload_url.replace("{?name,label}", "")

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "audio/mpeg")}

            response = requests.post(
                f"{upload_url}?name={file_path.name}",
                headers={"Authorization": self.headers.get("Authorization")},
                files=files,
            )

        if response.status_code in (201, 200):
            return response.json()

        logger.warning(f"Upload failed: {response.status_code} - {response.text}")
        return None

    def cleanup_old(self, days: int = 14) -> int:
        """Delete releases older than N days."""
        if not self.token:
            return 0

        try:
            response = requests.get(f"{self.api_url}/releases", headers=self.headers)
            releases = response.json()

            cutoff = datetime.now() - datetime.timedelta(days=days)

            deleted = 0
            for release in releases:
                import re

                match = re.search(r"v(\d{8})", release.get("tag_name", ""))
                if match:
                    date_str = match.group(1)
                    release_date = datetime.strptime(date_str, "%Y%m%d")

                    if release_date < cutoff:
                        requests.delete(
                            f"{self.api_url}/releases/{release['id']}",
                            headers=self.headers,
                        )
                        deleted += 1

            return deleted

        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
            return 0


def upload_episode(mp3_path: Path, title: str) -> Dict:
    """Simple function to upload episode."""
    storage = GitHubStorage()
    return storage.upload_episode(mp3_path, title)


if __name__ == "__main__":
    print("GitHub Storage module ready")
    print(f"Repo: {GITHUB_REPO}")
