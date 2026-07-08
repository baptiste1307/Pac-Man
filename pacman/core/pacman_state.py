from dataclasses import dataclass


@dataclass
class PacmanStateMixin:
    """Manage Pac-Man position, target cell, and pacgum placement."""

    # Speeds are expressed in cells per second. The engine converts this to
    # pixels each frame using the current cell size and delta time.
    pacman_speed: float = 3
    pacman_direction: str | None = None
    pacman_wanted_direction: str | None = None
    pacman_current_frame: int = 1

    def update_target_position(self) -> None:
        """
        Update the target position.
        """
        self.target_x = (
            self.MAZE_OFFSET_X
            + self.pacman_grid_x * self.level.cell_size
            + self.wall_thickness
        )

        self.target_y = (
            self.MAZE_OFFSET_Y
            + self.pacman_grid_y * self.level.cell_size
            + self.wall_thickness
        )

    def find_start_coords(self) -> tuple[int, int]:
        """
        Find pacman's start coordinate (outside of 42 pattern).

        Returns:
            tuple[int, int]: where pacman starts.
        """
        x = self.level.width // 2
        y = self.level.height // 2
        if (x, y) not in self.fourty_two_cells:
            return (x, y)

        while (x, y) in self.fourty_two_cells:
            x -= 1

        return (x, y)

    def reset_pacman_state(self) -> None:
        """
        Reset pacman in its start position.
        """
        self.pacman_direction = None
        self.pacman_wanted_direction = None
        pacman_start_coords = self.find_start_coords()

        self.pacman_grid_x = pacman_start_coords[0]
        self.pacman_grid_y = pacman_start_coords[1]

        self.pacman_x = (
            self.MAZE_OFFSET_X
            + self.pacman_grid_x * self.level.cell_size
            + self.wall_thickness
        )
        self.pacman_y = (
            self.MAZE_OFFSET_Y
            + self.pacman_grid_y * self.level.cell_size
            + self.wall_thickness
        )

        pacman_start = (self.pacman_grid_x, self.pacman_grid_y)
        self.init_pacgums(pacman_start)

        self.target_x = self.pacman_x
        self.target_y = self.pacman_y
        self.pacman_current_frame = 1

    def init_pacgums(self, pacman_start: tuple[int, int]) -> None:
        """
        Set the number of pacgums on the map.

        Args:
            pacman_start: pacman start's coordinate.
        """
        self.pacgums = set()
        self.super_pacgums = set()
        for y, row in enumerate(self.current_maze):
            for x, _ in enumerate(row):
                if (x, y) not in self.fourty_two_cells and (
                    x,
                    y,
                ) != pacman_start:
                    # if len(self.pacgums) <= 1:
                    if (x, y) in self.maze_corners_coords:
                        self.super_pacgums.add((x, y))
                    else:
                        self.pacgums.add((x, y))

    def set_pacman_start_position(self) -> None:
        """
        Put pacman in its calculated start position.
        """
        self.pacman_direction = None
        self.pacman_wanted_direction = None
        pacman_start_coords = self.find_start_coords()

        self.pacman_grid_x = pacman_start_coords[0]
        self.pacman_grid_y = pacman_start_coords[1]

        self.pacman_x = (
            self.MAZE_OFFSET_X
            + self.pacman_grid_x * self.level.cell_size
            + self.wall_thickness
        )
        self.pacman_y = (
            self.MAZE_OFFSET_Y
            + self.pacman_grid_y * self.level.cell_size
            + self.wall_thickness
        )
        self.target_x = self.pacman_x
        self.target_y = self.pacman_y
        self.pacman_current_frame = 1
