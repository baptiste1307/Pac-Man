from pathlib import Path
import json
import argparse
import sys
import random


def parse_input(args: list[str]) -> argparse.Namespace:
    if len(args) != 2:
        raise ValueError("There should be exactly 2 arguments.")

    # elif "/" not in args[0] and args[0] != "pac-man.py":
    #    raise ValueError("Incorrect program file. It should be 'pac-man.py', "
    #                      "or a path to this file.")

    # elif "/" in args[0] and args[0].split("/")[-1] != "pac-man.py":
    #    raise ValueError("Incorrect program file. It should be 'pac-man.py', "
    #                      "or a path to this file.")
    # ==> inutie de vérifier le nom pac-man.py

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


def load_json_with_comments(path: Path) -> dict:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"JSON file not found: {path}.")
    try:
        with open(path, 'r') as file:
            lines = []
            for line in file:
                # et pas "in file.read()" -> chr par chr
                if (line.lstrip().startswith('#')
                        or line.lstrip().startswith("//")):
                    continue
                lines.append(line)
        config = json.loads("\n".join(lines))
        if not isinstance(config, dict):
            # au cas ou load_json passe sans erreur alors que le fichier
            # ne contient pas de dict
            print(f"Error: {path}: root JSON value must be an object.")
            sys.exit(1)
        return config
    # json.loads() raise des erreurs si json invalide
    # donc je les catch ici
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}.")
        sys.exit(1)
    except OSError as e:
        # le système npp ouvrir/lire/écrire ce fichier, même s’il existe.
        print(f"Error: cannot read file {path}: {e}", file=sys.stderr)
        sys.exit(1)


def check_json(config_file_path: Path, config: dict) -> None:

    default_width = 21
    default_height = 21
    default_seed = 42
    default_config_keys = {
        "highscore_filename": {"count": 0, "default": "scores.json"},
        "levels": {"count": 0, "default": [{
            "height": default_height,
            "width": default_width
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

        if isinstance(value, str):
            splitted = config[key].strip().split('.')
            if len(splitted) != 2 or splitted[-1] != "json":
                config[key] = default_config_keys[key]["default"]
                print(
                    f"{config_file_path}: incorrect JSON file name for '{key}'"
                    f" => Automatically updated value: "
                    f"'{default_config_keys[key]["default"]}.'\n")

        elif key == "levels":
            if len(config["levels"]) <= 0:
                continue
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
                        f"Automatically updated value: {level["width"]}.\n")

                elif "width" in level and "height" not in level:
                    # pareil mais inversement
                    level["height"] = level["width"]
                    print(
                        f"{config_file_path}: height missing for "
                        f"level {index + 1} => "
                        f"Automatically updated value: {level["height"]}.\n")

                elif (("height" not in level and "width" not in level)
                        or level["height"] <= 0 or level["height"] >= 200
                        or level["width"] <= 0 or level["width"] >= 200):
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
                        f"Automatically updated value: {level["width"]}.\n")

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
                        f" Randomly generated value: {level["seed"]}.\n")

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
                    f"=> Updated with default value {value["default"]}.\n")

    # debug
    print("\n".join(f"{key}: {value}" for key, value in config.items()))
