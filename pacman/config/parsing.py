from pathlib import Path
from typing import Any, List, Dict
from .parsing_utils import (
    check_levels_key,
    check_int_key,
    check_str_key,
    check_missing_mandatory_key,
)
from pacman.errors import format_current_error
import json
import argparse
import sys
from dataclasses import dataclass, field


@dataclass
class Parser:
    """Parse, validate, and normalize the JSON game configuration."""

    levels: List[Dict[str, Any]] = field(
        default_factory=lambda: [{"height": 13, "width": 13}]
    )

    highscore_filename: str = "scores.json"
    lives: int = 3
    pacgum: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    level_max_time: int = 900

    @staticmethod
    def parse_input(args: list[str]) -> argparse.Namespace:
        """
        Use argparse tool to introduce the command input arguments.

        Args:
            args: list of arguments.
        """
        if len(args) != 2:
            raise ValueError("There should be exactly 2 arguments.")

        # elif "/" not in args[0] and args[0] != "pac-man.py":
        #    raise ValueError("Incorrect program file.
        # It should be 'pac-man.py', "
        #                      "or a path to this file.")

        # elif "/" in args[0] and args[0].split("/")[-1] != "pac-man.py":
        #    raise ValueError("Incorrect program file.
        # It should be 'pac-man.py', "
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
            print(format_current_error("invalid arguments."))
            sys.exit(1)

    @staticmethod
    def load_json_with_comments(path: Path) -> dict[str, Any]:
        """
        Load config.json file and treat its commend lines.

        Args:
            path: the path string of the json file.
        """
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"JSON file not found: {path}.")
        try:
            with open(path, "r") as file:
                lines = []
                for line in file:
                    # not "in file.read()" -> one chr at a time
                    if line.lstrip().startswith(
                        "#"
                    ) or line.lstrip().startswith("//"):
                        continue
                    lines.append(line)
            config = json.loads("\n".join(lines))
            if not isinstance(config, dict):
                # in case load_json raises no error even if the file contains
                # not dict
                print(
                    format_current_error(
                        f"{path}: root JSON value must be an object."
                    )
                )
                sys.exit(1)
            return config
        # json.loads() raises errors if invalid Json
        # so catching them here
        except json.JSONDecodeError as e:
            print(format_current_error(f"invalid JSON in {path}: {e}."))
            sys.exit(1)
        except OSError as e:
            # system cannot open/read/write this file, even if it exists
            print(
                format_current_error(f"cannot read file {path}: {e}"),
                file=sys.stderr,
            )
            sys.exit(1)

    def check_json(
        self, config_file_path: Path, config: dict[str, Any]
    ) -> None:
        """
        Interprete various game parameters from config json file.

        Args:config_file_path: path string of the config.json file.
        config: A dictionary containing configuration keys and values.
        """

        default_size = 13
        default_seed = 42
        default_config_keys = {
            "highscore_filename": {"count": 0, "default": "scores.json"},
            "levels": {
                "count": 0,
                "default": [{"height": default_size, "width": default_size}],
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
                    default_config_keys[key].get("count", 0) + 1
                )

            if isinstance(value, int):
                check_int_key(key, config, config_file_path, value)

            if isinstance(value, str):
                check_str_key(
                    key, config, config_file_path, default_config_keys
                )

            elif key == "levels":
                if len(config["levels"]) <= 0:
                    continue
                check_levels_key(
                    config, config_file_path, default_size, default_seed
                )

        # checks if a mandatory key from default_config_keys is missing in
        # config
        check_missing_mandatory_key(
            default_config_keys, config, default_size, config_file_path
        )

        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def parser_main(self, args: list[str]) -> None:
        """
        Load and check command-line config and update parser fields.

        Args:
            the list of arguments
        """
        namespace = self.parse_input(args)
        path = Path(namespace.config_file)
        raw_data = self.load_json_with_comments(path)
        self.check_json(path, raw_data)

        # debug
        # print(
        # "\n".join(f"{key}: {value}" for key, value in raw_data.items()))
