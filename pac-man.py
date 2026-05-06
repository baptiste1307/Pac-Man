import sys
import argparse
from pathlib import Path
from pacman.parsing import parse_input, load_json_with_comments, check_json


def main():
    try:
        args: argparse.Namespace = parse_input(sys.argv)
        config_file_path = Path(args.config_file)
        config = load_json_with_comments(config_file_path)
        check_json(config_file_path, config)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
