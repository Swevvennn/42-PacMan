import sys
from typing import Any

from src.utils.config_loader import load_config


def main() -> None:
    """Parse the command line, load the config, hand control to the engine."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config_file.json>")
        sys.exit(1)

    config_file = sys.argv[1]
    config: dict[str, Any] = load_config(config_file)

    try:
        from src.engine import GameController
    except ImportError as e:
        print(f"error: cannot start the game ({e})")
        sys.exit(1)

    try:
        game = GameController(config)
        game.run()
    except KeyboardInterrupt:
        print("\ninterrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
