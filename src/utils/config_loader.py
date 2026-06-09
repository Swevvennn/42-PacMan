import json
import os
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "highscore_filename": "highscores.json",
    "seed": 42,
    "lives": 3,
    "level_max_time": 90,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "level":    [
        {"width": 15, "height": 15},
        {"width": 16, "height": 16},
        {"width": 17, "height": 17},
        {"width": 18, "height": 18},
        {"width": 19, "height": 19},
        {"width": 20, "height": 20},
        {"width": 21, "height": 21},
        {"width": 22, "height": 22},
        {"width": 23, "height": 23},
        {"width": 24, "height": 24}
    ]
}


def _validate_level_list(value: Any) -> list[dict[str, int]] | None:
    """Validate a ``[{"width": int, "height": int}, ...]`` list.

    Args:
        value: The raw value to validate.

    Returns:
        The validated list, or ``None`` if the value is malformed.
    """
    if not isinstance(value, list) or not value:
        return None
    out: list[dict[str, int]] = []
    for item in value:
        if not isinstance(item, dict):
            return None
        w = item.get("width")
        h = item.get("height")
        if not isinstance(w, int) or not isinstance(h, int):
            return None
        if w < 5 or h < 5 or w > 60 or h > 60:
            return None
        out.append({"width": w, "height": h})
    return out


def _strip_comments(text: str) -> str:
    """Drop every line whose first non-blank character is ``#``."""
    out_lines: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        out_lines.append(line)
    return "\n".join(out_lines)


def load_config(filepath: str) -> dict[str, Any]:
    """Read a JSON-with-``#``-comments config, falling back to defaults.

    Args:
        filepath: Path to the configuration file.

    Returns:
        A dictionary with every default key, overridden by the user values
        whenever they are valid. Malformed values are silently kept at their
        default and a warning is printed.
    """
    config = DEFAULT_CONFIG.copy()
    config["level"] = list(DEFAULT_CONFIG["level"])

    if not filepath.lower().endswith(".json"):
        print(f"error: config file must end with .json (got {filepath!r}),"
              " using defaults")
        return config

    if not os.path.isfile(filepath):
        print(f"error: config file not found: {filepath}, using defaults")
        return config

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        print(f"error: cannot read {filepath} ({e}), using defaults")
        return config

    cleaned = _strip_comments(raw)
    if not cleaned.strip():
        print("warning: empty config file, using defaults")
        return config

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"warning: invalid JSON in config ({e}), using defaults")
        return config

    if not isinstance(parsed, dict):
        print("warning: config is not a JSON object, using defaults")
        return config

    for key, value in parsed.items():
        if key not in DEFAULT_CONFIG:
            print(f"warning: ignoring unknown config key '{key}'")
            continue
        if key == "level":
            validated = _validate_level_list(value)
            if validated is None:
                print("warning: invalid 'level' entry, keeping default")
                continue
            config["level"] = validated
            continue

        expected = type(DEFAULT_CONFIG[key])
        if isinstance(value, expected) and not isinstance(value, bool):
            if expected is int and value < 0:
                print(f"warning: '{key}' must be non-negative,\
 keeping default")
                continue
            config[key] = value
        else:
            print(f"warning: bad type for '{key}', keeping default")

    return config
