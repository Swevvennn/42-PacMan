import json
import os
from typing import Any


MAX_ENTRIES = 10
MAX_NAME_LEN = 10


def _clean_name(raw: str) -> str:
    """Keep only alphanumerics and spaces, trim to ``MAX_NAME_LEN``.

    Args:
        raw: The user-provided name.

    Returns:
        A sanitised name, never empty (``"anon"`` is used as fallback).
    """
    cleaned = "".join(c for c in raw if c.isalnum() or c == " ")
    cleaned = cleaned.strip()
    if not cleaned:
        cleaned = "anon"
    return cleaned[:MAX_NAME_LEN]


class HighscoreManager:
    """Persistent top-10 highscores backed by a JSON file."""

    def __init__(self, filepath: str) -> None:
        """Build the manager and load existing entries from ``filepath``."""
        self.filepath = filepath
        self.entries: list[dict[str, Any]] = []
        self.load()

    def load(self) -> None:
        """Read the file. Any error results in an empty list, no crash."""
        self.entries = []
        if not os.path.isfile(self.filepath):
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"highscore: could not read file ({e}), starting fresh")
            return

        if not isinstance(data, list):
            print("highscore: file is not a list, ignoring")
            return

        clean: list[dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            score = item.get("score")
            if not isinstance(name, str) or not isinstance(score, int):
                continue
            if score < 0:
                continue
            clean.append({"name": _clean_name(name), "score": score})

        clean.sort(key=lambda e: e["score"], reverse=True)
        self.entries = clean[:MAX_ENTRIES]

    def save(self) -> None:
        """Write the current entries back to disk."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)
        except OSError as e:
            print(f"highscore: could not save ({e})")

    def add(self, name: str, score: int) -> None:
        """Insert a new entry, keep the top 10, sort by score.

        Args:
            name: Player name (sanitised before insertion).
            score: Non-negative integer score. Anything else is dropped.
        """
        if not isinstance(score, int) or score < 0:
            return
        self.entries.append({"name": _clean_name(name), "score": score})
        self.entries.sort(key=lambda e: e["score"], reverse=True)
        self.entries = self.entries[:MAX_ENTRIES]

    def top(self) -> list[dict[str, Any]]:
        """Return the top entries, already sorted and capped at 10."""
        return list(self.entries)
