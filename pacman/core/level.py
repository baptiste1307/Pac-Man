from dataclasses import dataclass, field
from mazegenerator.mazegenerator import MazeGenerator
from typing import Any


@dataclass
class Level:
    """Build one maze level and compute its responsive cell size."""

    width: int
    height: int
    seed: int
    game: Any
    index: int
    cell_size: int = field(default=0)
    maze: MazeGenerator = field(default=None)

    def __post_init__(self) -> None:
        self.cell_size = self._find_cell_size(self.width, self.height)
        # use seed only for first level
        if self.index != 0:
            self.seed = 0
        self.maze = MazeGenerator(
            size=(self.width, self.height),
            seed=self.seed,
        )

    def _find_cell_size(self, level_width: int, level_height: int) -> int:
        """
        Find the size of the maze according to the black block of the page.

        Args:
            level_width: the width of the maze of current level.
            level_height: the height of the maze of current level.

        Returns:
            int: the size of the maze cell.
        """

        rectangle_width, rectangle_height = (
            self.game.black_rectangle_width,
            self.game.black_rectangle_height,
        )
        fill_ratio = self.game.play_area_fill_ratio

        return int(
            min(
                (rectangle_height * fill_ratio) // level_height,
                (rectangle_width * fill_ratio) // level_width,
            )
        )
