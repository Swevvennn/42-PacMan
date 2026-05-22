import json
import os
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "highscore_filename": "highscores.json",
    "level": [
        {"width": 15, "height": 15},
        {"width": 20, "height": 20}
    ],
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90
}

def load_config(filepath: str) -> Dict[str, Any]:
    config = DEFAULT_CONFIG.copy()

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        clean_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith("#"):
                clean_lines.append(line)

        json_str = "".join(clean_lines)

        if not json_str.strip():
            print("empty file, using defaults")
            return config

        parsed_config = json.loads(json_str)

        if not isinstance(parsed_config, dict):
            print("bad json, using defaults")
            return config

        for key, value in parsed_config.items():
            if key in config:
                expected_type = type(config[key])
                if isinstance(value, expected_type):
                    config[key] = value
                else:
                    print(f"bad type for {key}")
            else:
                print(f"unknown key {key}")

    except FileNotFoundError:
        print(f"file not found: {filepath}")
    except PermissionError:
        print(f"permission denied: {filepath}")
    except IsADirectoryError:
        print(f"is a directory: {filepath}")
    except json.JSONDecodeError as e:
        print(f"json error: {e}")
    except Exception as e:
        print(f"error: {e}")

    return config
