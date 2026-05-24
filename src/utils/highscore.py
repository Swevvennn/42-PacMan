import json
import os
from typing import Any

import requests


MAX_ENTRIES = 10
MAX_NAME_LEN = 10
GIST_API = "https://api.github.com/gists"
HTTP_TIMEOUT = 3.0


def _clean_name(raw: str) -> str:
    """Keep only alphanumerics and spaces, trim to ``MAX_NAME_LEN``."""
    cleaned = "".join(c for c in raw if c.isalnum() or c == " ").strip()
    if not cleaned:
        cleaned = "anon"
    return cleaned[:MAX_NAME_LEN]


def _normalise(entries: list[Any]) -> list[dict[str, Any]]:
    """Validate, sanitise, sort and cap a raw list of highscore entries."""
    out: list[dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        score = item.get("score")
        if not isinstance(name, str) or not isinstance(score, int):
            continue
        if score < 0:
            continue
        out.append({"name": _clean_name(name), "score": score})
    out.sort(key=lambda e: e["score"], reverse=True)
    return out[:MAX_ENTRIES]


class HighscoreManager:
    """Top-10 highscores persisted locally and on a shared public gist.

    The local JSON file is the offline fallback; the gist is the shared
    source. Every network call has a short timeout and silently falls back
    to local-only on error so the game never crashes when offline.
    """

    def __init__(self, filepath: str, gist_id: str = "",
                 gist_token: str = "") -> None:
        """Initialise the manager and load entries from disk and gist.

        Args:
            filepath: Local JSON file path.
            gist_id: Public gist identifier. Empty disables remote sync.
            gist_token: PAT with ``gist`` scope. Empty disables remote save
                but still allows remote read since the gist is public.
        """
        self.filepath = filepath
        self.gist_id = gist_id
        self.gist_token = gist_token
        self.entries: list[dict[str, Any]] = []
        self.load()

    def _headers(self) -> dict[str, str]:
        """Return GitHub API headers, with the auth header when present."""
        headers = {"Accept": "application/vnd.github+json"}
        if self.gist_token:
            headers["Authorization"] = f"Bearer {self.gist_token}"
        return headers

    def _load_local(self) -> list[dict[str, Any]]:
        """Read the local file, returning an empty list on any error."""
        if not os.path.isfile(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"highscore: cannot read local file ({e})")
            return []
        if not isinstance(data, list):
            return []
        return _normalise(data)

    def _load_remote(self) -> list[dict[str, Any]]:
        """Fetch the gist contents, returning an empty list on any error."""
        if not self.gist_id:
            return []
        try:
            resp = requests.get(
                f"{GIST_API}/{self.gist_id}",
                headers=self._headers(),
                timeout=HTTP_TIMEOUT,
            )
            resp.raise_for_status()
            payload = resp.json()
        except (requests.RequestException, ValueError) as e:
            print(f"highscore: cannot reach gist ({e})")
            return []
        files = payload.get("files", {})
        entry = files.get("highscores.json")
        if not isinstance(entry, dict):
            return []
        try:
            data = json.loads(entry.get("content", "[]"))
        except json.JSONDecodeError:
            return []
        if not isinstance(data, list):
            return []
        return _normalise(data)

    def load(self) -> None:
        """Merge local and remote entries into ``self.entries``."""
        merged = self._load_local() + self._load_remote()
        self.entries = _normalise(merged)

    def _save_local(self) -> None:
        """Write the current entries back to the local file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)
        except OSError as e:
            print(f"highscore: cannot save local file ({e})")

    def _save_remote(self) -> None:
        """Re-fetch the gist, merge to avoid stomping, then PATCH it."""
        if not self.gist_id or not self.gist_token:
            return
        remote = self._load_remote()
        merged = _normalise(self.entries + remote)
        self.entries = merged
        body = {
            "files": {
                "highscores.json": {
                    "content": json.dumps(merged, indent=2)
                }
            }
        }
        try:
            resp = requests.patch(
                f"{GIST_API}/{self.gist_id}",
                headers=self._headers(),
                json=body,
                timeout=HTTP_TIMEOUT,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"highscore: cannot push gist ({e})")

    def save(self) -> None:
        """Persist entries locally and try to sync them to the gist."""
        self._save_local()
        self._save_remote()

    def add(self, name: str, score: int) -> None:
        """Insert a new entry, keep the top 10 sorted by score.

        Args:
            name: Player name (sanitised before insertion).
            score: Non-negative integer score. Anything else is dropped.
        """
        if not isinstance(score, int) or score < 0:
            return
        self.entries.append({"name": _clean_name(name), "score": score})
        self.entries = _normalise(self.entries)

    def top(self) -> list[dict[str, Any]]:
        """Return the top entries, already sorted and capped at 10."""
        return list(self.entries)
