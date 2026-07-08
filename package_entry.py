import sys
from pathlib import Path

from pacman.config import Parser
from pacman.engine import GameEngine
from pacman.errors import format_exception_error


def main() -> None:
    """Launch the packaged game with its bundled default config file."""
    try:
        base_dir = Path(
            getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
        )

        if len(sys.argv) == 1:
            sys.argv.append(str(base_dir / "config.json"))

        engine = GameEngine()
        parser = Parser()
        parser.parser_main(sys.argv)
        config = parser.__dict__
        engine.init_game(config)

    except Exception as e:
        print(format_exception_error(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
