import sys
from src.utils.config_loader import load_config
from src.engine import GameController

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config_file.json>")
        sys.exit(1)

    config_file = sys.argv[1]
    config = load_config(config_file)

    game = GameController(config)
    game.run()

if __name__ == "__main__":
    main()