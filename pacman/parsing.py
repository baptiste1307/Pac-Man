from pathlib import Path
from typing import Any
from .parsing_utils import (check_levels_key,
                            check_int_key,
                            check_str_key,
                            check_missing_mandatory_key)
import json
import argparse
import sys


def parse_input(args: list[str]) -> argparse.Namespace:
    if len(args) != 2:
        raise ValueError("There should be exactly 2 arguments.")

    # elif "/" not in args[0] and args[0] != "pac-man.py":
    #    raise ValueError("Incorrect program file. It should be 'pac-man.py', "
    #                      "or a path to this file.")

    # elif "/" in args[0] and args[0].split("/")[-1] != "pac-man.py":
    #    raise ValueError("Incorrect program file. It should be 'pac-man.py', "
    #                      "or a path to this file.")
    # ==> useless to verifiy name "pac-man.py"

    elif ".json" not in args[1]:
        raise ValueError("Config file should be a JSON.")

    try:
        parser = argparse.ArgumentParser(
            prog="python3 pac-man.py",
            description="Launch a pac-man game",
        )
        parser.add_argument(
            "config_file",
            help="Path to the configuration file of the game",
        )
        return parser.parse_args()

    except (TypeError, SystemExit):
        print("Error: invalid arguments.")
        sys.exit(1)


def load_json_with_comments(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"JSON file not found: {path}.")
    try:
        with open(path, 'r') as file:
            lines = []
            for line in file:
                # not "in file.read()" -> one chr at a time
                if (line.lstrip().startswith('#')
                        or line.lstrip().startswith("//")):
                    continue
                lines.append(line)
        config = json.loads("\n".join(lines))
        if not isinstance(config, dict):
            # in case load_json raises no error even if the file contains
            # not dict
            print(f"Error: {path}: root JSON value must be an object.")
            sys.exit(1)
        return config
    # json.loads() raises errors if invalid Json
    # so catching them here
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}.")
        sys.exit(1)
    except OSError as e:
        # system cannot open/read/write this file, even if it exists
        print(f"Error: cannot read file {path}: {e}", file=sys.stderr)
        sys.exit(1)


def check_json(config_file_path: Path,
               config: dict[str, Any]) -> None:

    default_size = 13
    default_seed = 42
    default_config_keys = {
        "highscore_filename": {"count": 0, "default": "scores.json"},
        "levels": {"count": 0, "default": [{
            "height": default_size,
            "width": default_size
            }]
        },
        "lives": {"count": 0, "default": 3},
        "pacgum": {"count": 0, "default": 42},
        "points_per_pacgum": {"count": 0, "default": 10},
        "points_per_super_pacgum": {"count": 0, "default": 50},
        "points_per_ghost": {"count": 0, "default": 200},
        "level_max_time": {"count": 0, "default": 90},
    }

    for key, value in config.items():
        if key not in default_config_keys:
            continue

        if key in default_config_keys:
            if key == "levels" and len(value) <= 0:
                continue
            default_config_keys[key]["count"] = (
                default_config_keys[key].get("count", 0) + 1)

        if isinstance(value, int):
            check_int_key(key, config, config_file_path, value)

        if isinstance(value, str):
            check_str_key(key, config, config_file_path, default_config_keys)

        elif key == "levels":
            if len(config["levels"]) <= 0:
                continue
            check_levels_key(config,
                             config_file_path,
                             default_size,
                             default_seed)

    # checks if a mandatory key from default_config_keys is missing in config
    check_missing_mandatory_key(default_config_keys,
                                config,
                                default_size,
                                config_file_path)
