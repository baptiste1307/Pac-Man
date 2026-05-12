from pathlib import Path
from typing import Any
import random


def check_int_key(key: str,
                  config: dict[str, Any],
                  config_file_path: Path,
                  value: int) -> None:

    if value > 10000:
        config[key] = 10000
        print(
            f"{config_file_path}: incorrect value '{value}'"
            f"for '{key}' (max 10_000) => Automatically updated value:"
            f" {config[key]}.\n")

    elif value <= 0:
        config[key] *= -1
        print(
            f"{config_file_path}: incorrect value '{value}'"
            f"for '{key}' (min 1) => Automatically updated value: "
            f"{config[key]}.\n")


def check_str_key(key: str,
                  config: dict[str, Any],
                  config_file_path: Path,
                  default_config_keys: dict[str, Any]) -> None:

    splitted = config[key].strip().split('.')
    if len(splitted) != 2 or splitted[-1] != "json":
        config[key] = default_config_keys[key]["default"]
        print(
            f"{config_file_path}: incorrect JSON file name for '{key}'"
            f" => Automatically updated value: "
            f"'{default_config_keys[key]['default']}.'\n")


def check_levels_key(config: dict[str, Any],
                     config_file_path: Path,
                     default_size: int,
                     default_seed: int) -> None:

    for index, level in enumerate(config["levels"]):
        # each level is a dict that should contain height, weight
        # and seed keys. Other keys are ignored

        # Part 1: checking missing keys
        # case 1: width missing -> width = height
        if "height" in level and "width" not in level:
            level["width"] = level["height"]
            print(
                f"{config_file_path}: width missing for "
                f"level {index + 1} => "
                f"Automatically updated value: {level['width']}.\n")

        # case 2: height missing -> height = width
        elif "width" in level and "height" not in level:
            level["height"] = level["width"]
            print(
                f"{config_file_path}: height missing for "
                f"level {index + 1} => "
                f"Automatically updated value: {level['height']}.\n")

        # case 3: both missing -> width & height = default_size
        elif ("height" not in level and "width" not in level):
            level["height"] = default_size
            level["width"] = default_size
            print(
                f"{config_file_path}: incorrect height or width for"
                f" level {index + 1} => "
                f"Automatically updated value: {level['width']}.\n")

        # case 4: missing or invalid seed -> set to random int
        if ("seed" not in level
                or level["seed"] <= 0
                or level["seed"] > 1000000):
            # level 1 = default seed
            if index == 0:
                level["seed"] = default_seed
            else:
                level["seed"] = random.randint(1, 1_000_000)
            print(
                f"{config_file_path}: seed incorrect or missing for"
                f" level {index + 1} =>"
                f" Randomly generated value: {level['seed']}.\n")

        # Part 2: checking key values
        max_size = 20  # (for performance)
        min_size = 10
        original_height = level["height"]
        original_width = level["width"]

        # case 1: below min size -> set value to min_size
        if level["height"] < min_size:
            level["height"] = min_size
        if level["width"] < min_size:
            level["width"] = min_size

        # case 2: over max size -> set value to max_size
        if level["height"] > max_size:
            config["levels"][index]["height"] = max_size
        if level["width"] > max_size:
            config["levels"][index]["width"] = max_size

        # case 3: height * width < 180 -> increase the smallest one
        if (level["height"] * level["width"]) < 169:
            while (level["height"] * level["width"]) < 169:
                if level["height"] <= level["width"]:
                    level["height"] += 1
                else:
                    level["width"] += 1

        # case 4: height * width > 400 -> decrease the biggest one
        if (level["height"] * level["width"]) > 400:
            while (level["height"] * level["width"]) > 400:
                if level["height"] >= level["width"]:
                    level["height"] -= 1
                else:
                    level["width"] -= 1

        # log clear error messages if a value has changed
        if level["height"] != original_height:
            print(
                f"{config_file_path}: height for level {index + 1}"
                f" corrected from {original_height} to"
                f" {level['height']}.\n"
            )
        if level["width"] != original_width:
            print(
                f"{config_file_path}: width for level {index + 1}"
                f" corrected from {original_width} to"
                f" {level['width']}.\n"
            )

    # Part 3: less than 10 levels provided -> generate default ones
    if index < 10:
        index += 1
        while index != 10:
            config["levels"].append({
                "height": default_size,
                "width": default_size,
                "seed": random.randint(1, 1_000_000)
                })
            print(f"{config_file_path}: level {index + 1} details"
                  " missing. => Default level created.\n")
            index += 1


def check_missing_mandatory_key(default_config_keys: dict[str, Any],
                                config: dict[str, Any],
                                default_size: int,
                                config_file_path: Path) -> None:

    for key, value in default_config_keys.items():
        if value["count"] <= 0:
            # si une des clés mandatory n'est pas dans config
            if key == "levels":
                config["levels"] = []
                index = 0
                while index != 10:
                    multiplier = 1.2 ** (index // 3)
                    config["levels"].append({
                        "height": int(default_size * multiplier),
                        "width": int(default_size * multiplier),
                        "seed": random.randint(1, 1_000_000)
                        })
                    print(f"{config_file_path}: level {index + 1} details"
                          " missing. => Default level created.\n")
                    index += 1
            else:
                config[key] = value["default"]
                # on l'ajoute et on lui donne sa valeur par defaut
                print(
                    f"{config_file_path}: key '{key}' missing. "
                    f"=> Updated with default value {value['default']}.\n")
