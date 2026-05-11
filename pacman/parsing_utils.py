import pygame
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
            f"{config_file_path}: incorrect value '{value}' "
            f"for '{key}' (max 10_000) => Automatically updated value:"
            f" {config[key]}.\n")

    elif value <= 0:
        config[key] *= -1
        print(
            f"{config_file_path}: incorrect value '{value}' "
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


def _find_max_level_size(cell_size: int) -> tuple[int, int]:

    pygame.init()
    info = pygame.display.Info()

    # gives the full computer screen size, then take
    # max 80% of it to prevent display bugs
    max_width = int(info.current_w * 0.8)
    max_height = int(info.current_h * 0.8)

    # Because 1 col = cell_size px
    max_cols, max_rows = max_width // cell_size, max_height // cell_size
    return (max_cols, max_rows)


def check_levels_key(config: dict[str, Any],
                     config_file_path: Path,
                     default_height: int,
                     default_width: int,
                     default_seed: int,
                     cell_size: int) -> None:

    max_cols, max_rows = _find_max_level_size(cell_size)

    for index, level in enumerate(config["levels"]):
        # chaque level est un dict censé contenir height, weight, seed
        # les autres clés sont ignorées

        multiplier = 1.2 ** (index // 3)
        if "height" in level and "width" not in level:
            # si height existe mais pas width et que sa valeur est
            # correcte, on donne à width la même valeur
            level["width"] = level["height"]
            print(
                f"{config_file_path}: width missing for "
                f"level {index + 1} => "
                f"Automatically updated value: {level['width']}.\n")

        elif "width" in level and "height" not in level:
            # pareil mais inversement
            level["height"] = level["width"]
            print(
                f"{config_file_path}: height missing for "
                f"level {index + 1} => "
                f"Automatically updated value: {level['height']}.\n")

        elif (("height" not in level and "width" not in level)
                or level["height"] <= 0
                or level["width"] <= 0):
            # si height/width ou les 2 n'existent pas on les créé
            # si leur valeur n'est pas correcte, on la remplace
            # dans tous les cas la nouvelle valeur sera calculée
            # en fonction du numero du tour: tour 1 à 3: 21.
            # tour 4 à 6: 25 (21 x 1,2), etc.
            level["height"] = int(default_height * multiplier)
            level["width"] = int(default_width * multiplier)
            print(
                f"{config_file_path}: incorrect height or width for"
                f" level {index + 1} => "
                f"Automatically updated value: {level['width']}.\n")

        if level["height"] > max_rows:
            config["levels"][index]["height"] = max_rows
        if level["width"] > max_cols:
            config["levels"][index]["width"] = max_cols

        if ("seed" not in level
                or level["seed"] <= 0
                or level["seed"] > 1000000):
            # si seed existe pas ou pas la bonne valeur
            if index == 0:
                level["seed"] = default_seed
            else:
                level["seed"] = random.randint(1, 1_000_000)
            print(
                f"{config_file_path}: seed incorrect or missing for"
                f" level {index + 1} =>"
                f" Randomly generated value: {level['seed']}.\n")

    if index < 10:
        index += 1
        while index != 10:
            multiplier = 1.2 ** (index // 3)
            config["levels"].append({
                "height": int(default_height * multiplier),
                "width": int(default_width * multiplier),
                "seed": random.randint(1, 1_000_000)
                })
            print(f"{config_file_path}: level {index + 1} details"
                  " missing. => Default level created.\n")
            index += 1


def check_missing_mandatory_key(default_config_keys: dict[str, Any],
                                config: dict[str, Any],
                                default_height: int,
                                default_width: int,
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
                        "height": int(default_height * multiplier),
                        "width": int(default_width * multiplier),
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
