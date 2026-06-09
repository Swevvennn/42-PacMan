import json
import os
from typing import Any

MAX_ENTRIES = 10
MAX_NAME_LEN = 10


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

    The local JSON;
    """

    def __init__(self, filepath: str) -> None:
        """Initialise the manager and load entries from disk.

        Args:
            filepath: Local JSON file path.
        """
        self.filepath = filepath
        self.entries: list[dict[str, Any]] = []
        self.entries = self.load()

    def load(self) -> list[dict[str, Any]]:
        """Read the local file"""
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

    def save(self) -> None:
        """Write the current entries back to the local file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)
        except OSError as e:
            print(f"highscore: cannot save local file ({e})")

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
