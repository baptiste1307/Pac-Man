import sys
import argparse
from pathlib import Path
from mazegenerator.mazegenerator import MazeGenerator
from pacman.parsing import parse_input, load_json_with_comments, check_json
from pacman.visual import init_game


def main():
    try:
        sys.path.append(str(Path("build/wheel")))
        cell_size = 32
        args: argparse.Namespace = parse_input(sys.argv)
        config_file_path = Path(args.config_file)
        config = load_json_with_comments(config_file_path)
        check_json(config_file_path, config, cell_size)
        # debug
        print("\n".join(f"{key}: {value}" for key, value in config.items()))

        level_1 = MazeGenerator(
            size=(
                config["levels"][0]["width"],
                config["levels"][0]["height"],
            ))
        init_game(level_1, cell_size)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
