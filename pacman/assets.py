import pygame

GHOSTS = {
    "vulnerable_ghost": "vulnerable",
    "red_ghost": "blinky",
    "orange_ghost": "clyde",
    "blue_ghost": "inky",
    "pink_ghost": "pinky",
}

ANIMATED_GHOST_FILES = {
    f"{name}_{direction}": {
        f"frame_{frame}": f"assets/ghosts/{folder}/{direction}/{frame}.png"
        for frame in range(1, 3)
    }
    for name, folder in GHOSTS.items()
    for direction in ("up", "down", "left", "right")
}

PACMAN_FILES = {
    f"pacman_{direction}": {
        "opened": f"assets/pacman-{direction}/1.png",
        "half_opened": f"assets/pacman-{direction}/2.png",
        "closed": f"assets/pacman-{direction}/3.png",
    }
    for direction in ("down", "left", "right", "up")
}

FILES = {
    **ANIMATED_GHOST_FILES,
    "pacgum": "assets/other/dot.png",
    "super_pacgum": "assets/other/super_pacgum.png",
    **PACMAN_FILES,
}


class LoadedAssets:
    """Load and cache scaled game entity assets."""

    def __init__(self) -> None:
        # load every asset
        for name, value in FILES.items():

            if isinstance(value, str):
                setattr(self, name, pygame.image.load(value).convert_alpha())

            elif isinstance(value, dict):
                loaded_dict = {}

                for sub_name, path in value.items():
                    loaded_dict[sub_name] = pygame.image.load(
                        path
                    ).convert_alpha()

                setattr(self, name, loaded_dict)

        self.scaled_assets: dict[
            tuple[str, int, int | None, str | None],
            pygame.Surface | list[pygame.Surface],
        ] = {}

    # rescale the corresponding asset to perfectly fit current maze, according
    # to its cell size
    def get_asset(
        self,
        name: str,
        cell_size: int,
        thickness: int | None = None,
        sub_name: str | None = None,
    ) -> pygame.Surface | list[pygame.Surface]:
        """Return a scaled asset matching the current maze cell size."""

        cache_key = (name, cell_size, thickness, sub_name)

        if cache_key in self.scaled_assets:
            return self.scaled_assets[cache_key]

        asset = getattr(self, name)

        if name == "pacgum":
            new_size = max(1, int(cell_size * 0.1))

        elif name == "super_pacgum":
            new_size = max(1, int(cell_size * 0.3))

        else:
            new_size = max(1, int(cell_size - thickness))

        # for pacgums only (small size)
        if isinstance(asset, pygame.Surface):
            scaled_asset = pygame.transform.scale(asset, (new_size, new_size))
            self.scaled_assets[cache_key] = scaled_asset
            return scaled_asset

        # for asset pacman that has sub-pathes
        elif isinstance(asset, dict):

            if sub_name is None:
                raise ValueError(f"Asset '{name}' requires a sub_name.")

            # return all assets (open, half-open and closed)
            elif sub_name == "all":
                return [
                    pygame.transform.scale(asset[p], (new_size, new_size))
                    for p in asset
                ]

            # return only one sub_path given by sub_name
            else:
                return pygame.transform.scale(
                    asset[sub_name], (new_size, new_size)
                )

        # if no "name" attribute
        raise TypeError(f"Unsupported asset type for '{name}'.")
