from dataclasses import dataclass
from typing import Any
from .shortest_path import find_shortest_path


@dataclass
class GhostState:
    """Store one ghost's grid position, pixel target, status, and speed."""

    state: Any
    name: str
    status: str = "normal"
    pixel_x: int = 0
    pixel_y: int = 0
    pixel_target_x: int = 0
    pixel_target_y: int = 0
    vulnerable_timer: int = 0
    vulnerable_max_time: int = 10
    before_respawn_timer: int = 0
    time_to_respawn: int = 10
    start_x: int | None = None
    start_y: int | None = None
    mode: str | None = None

    def __post_init__(self) -> None:
        self.set_attributes()
        self.set_speed()

        self.pixel_x = (
            self.state.MAZE_OFFSET_X
            + (self.grid_x * self.state.level.cell_size)
            + self.state.wall_thickness
        )
        self.pixel_y = (
            self.state.MAZE_OFFSET_Y
            + (self.grid_y * self.state.level.cell_size)
            + self.state.wall_thickness
        )

        self.pixel_target_x = self.pixel_x
        self.pixel_target_y = self.pixel_y

        self.start_x = self.grid_x
        self.start_y = self.grid_y

        if self.asset_name == "orange_ghost":
            # "chase" or "scatter"
            self.mode = "chase"

    def set_speed(self) -> None:
        """
        Set ghost speed depending on levels and pacman spped.
        """
        cell_count = self.state.level.width * self.state.level.height

        if cell_count <= 100:
            speed = self.state.pacman_speed * 0.6
        elif cell_count > 100 and cell_count <= 170:
            speed = self.state.pacman_speed * 0.8
        elif cell_count > 170:
            speed = self.state.pacman_speed

        self.state.normal_ghost_speed = speed
        self.state.vulnerable_ghost_speed = speed * 0.6
        self.speed = speed

    def set_attributes(self) -> None:
        """
        Information on different attributes(ghosts).
        """
        last_col, last_row = (
            self.state.level.width - 1,
            self.state.level.height - 1,
        )

        if self.name == "blinky":
            self.asset_name = "red_ghost"
            self.direction = "right"
            self.grid_x = 0
            self.grid_y = 0
        if self.name == "pinky":
            self.asset_name = "pink_ghost"
            self.direction = "left"
            self.grid_x = last_col
            self.grid_y = 0
        if self.name == "inky":
            self.asset_name = "blue_ghost"
            self.direction = "right"
            self.grid_x = 0
            self.grid_y = last_row
        if self.name == "clyde":
            self.asset_name = "orange_ghost"
            self.direction = "left"
            self.grid_x = last_col
            self.grid_y = last_row


@dataclass
class GhostStateMixin:
    """Create ghosts and update their pathfinding targets."""

    ghost_current_frame: int = 0

    def reset_ghosts_states(self, ghost: GhostState | None = None) -> None:
        """
        Reset ghosts when needed.

        Args:
            ghost: A ghost with its information such as speed and location.
        """
        # if only need to reset ONE ghost (given in param)
        if ghost and ghost.status == "eaten":
            new_ghost = GhostState(self, name=ghost.name)

            if ghost.name == "blinky":
                self.blinky = new_ghost
            elif ghost.name == "pinky":
                self.pinky = new_ghost
            elif ghost.name == "inky":
                self.inky = new_ghost
            elif ghost.name == "clyde":
                self.clyde = new_ghost

            self.ghosts = [self.blinky, self.pinky, self.clyde, self.inky]
            return

        # reset all ghosts states
        else:
            self.blinky = GhostState(self, "blinky")
            self.pinky = GhostState(self, "pinky")
            self.inky = GhostState(self, "inky")
            self.clyde = GhostState(self, "clyde")
            self.ghosts = [self.blinky, self.pinky, self.clyde, self.inky]

    def update_ghosts_targets(self) -> None:
        """
        How different ghosts are supposed to move in the game.
        """
        # Blinky est sur une case grille
        # Pac-Man est sur une case grille
        # On calcule le plus court chemin entre les deux
        # On prend seulement la prochaine case du chemin
        # On met cette case comme target de Blinky

        for ghost in self.ghosts:
            # if ghost is still moving to his target
            if (
                ghost.pixel_x != ghost.pixel_target_x
                or ghost.pixel_y != ghost.pixel_target_y
                or ghost.status == "eaten"
            ):
                continue

            start = (ghost.grid_x, ghost.grid_y)
            if ghost.status == "normal":
                if ghost == self.blinky:
                    # blinky's target is pacman
                    goal = (self.pacman_grid_x, self.pacman_grid_y)
                elif ghost == self.pinky:
                    # pinky's target is a few cells around pacman
                    goal = self.find_goal_near_pacman(self.pinky)
                elif ghost == self.clyde:
                    # clyde's target alternates between pacman (chase mode)
                    # and his starting point (scatter mode)
                    goal = self.find_clyde_goal()
                elif ghost == self.inky:
                    # inky's position is the opposite of blinky's one
                    goal = self.find_inky_goal()

            elif ghost.status == "vulnerable":
                goal = (ghost.start_x, ghost.start_y)

            path = find_shortest_path(self.current_maze, start, goal)

            if len(path) < 2:
                continue

            next_cell = path[1]

            ghost.grid_x, ghost.grid_y = next_cell
            ghost.pixel_target_x = (
                self.MAZE_OFFSET_X
                + ghost.grid_x * self.level.cell_size
                + self.wall_thickness
            )
            ghost.pixel_target_y = (
                self.MAZE_OFFSET_Y
                + ghost.grid_y * self.level.cell_size
                + self.wall_thickness
            )

    def find_goal_near_pacman(
        self, ghost: GhostState
    ) -> tuple[int, int]:
        """
        One ghost move mechanism. Find somewhere near the pacman and go.

        Args:
            ghost: The ghost that moves as such.

        Returns:
            tuple[int, int]: coordinate of pacman.
        """
        offset = 2

        if self.pacman_direction == "right":
            return (self.pacman_grid_x + offset, self.pacman_grid_y)
        if self.pacman_direction == "left":
            return (self.pacman_grid_x - offset, self.pacman_grid_y)
        if self.pacman_direction == "down":
            return (self.pacman_grid_x, self.pacman_grid_y + offset)
        if self.pacman_direction == "up":
            return (self.pacman_grid_x, self.pacman_grid_y - offset)

        return (self.pacman_grid_x, self.pacman_grid_y)

    def update_clyde_mode(self) -> None:
        """
        Update clye mode between chase and scatter
        """
        clyde_pos = (self.clyde.grid_x, self.clyde.grid_y)
        pacman_pos = (self.pacman_grid_x, self.pacman_grid_y)
        corner_pos = (self.clyde.start_x, self.clyde.start_y)

        distance_to_pacman = abs(clyde_pos[0] - pacman_pos[0]) + abs(
            clyde_pos[1] - pacman_pos[1]
        )

        if self.clyde.mode == "chase" and distance_to_pacman <= 2:
            self.clyde.mode = "scatter"

        elif self.clyde.mode == "scatter" and clyde_pos == corner_pos:
            self.clyde.mode = "chase"

    def find_clyde_goal(self) -> tuple[int | None, int | None]:
        """
        The movement of Clyde ghost.

        Returns:
            tuple[int, int]: coordinate of pacman.
        """
        self.update_clyde_mode()

        if self.clyde.mode == "scatter":
            return (self.clyde.start_x, self.clyde.start_y)

        return self.find_goal_near_pacman(self.clyde)

    def find_inky_goal(self) -> tuple[int, int]:
        """
        The movement of Inky ghost.

        Returns:
            tuple[int, int]: coordinate of pacman.
        """
        offset = 2

        ahead_x = self.pacman_grid_x
        ahead_y = self.pacman_grid_y

        if self.pacman_direction == "right":
            ahead_x += offset
        elif self.pacman_direction == "left":
            ahead_x -= offset
        elif self.pacman_direction == "down":
            ahead_y += offset
        elif self.pacman_direction == "up":
            ahead_y -= offset

        goal = (
            2 * ahead_x - self.blinky.grid_x,
            2 * ahead_y - self.blinky.grid_y,
        )

        return self.clamp_goal(goal)

    def clamp_goal(self, goal: tuple[int, int]) -> tuple[int, int]:
        """
        Clamp a ghost target so it stays inside the current maze.

        Args:
            goal: the destination coordinate of the move.

        Returns:
            tuple[int, int]: goal coordinate.
        """
        x, y = goal
        x = max(0, min(x, self.level.width - 1))
        y = max(0, min(y, self.level.height - 1))
        return (x, y)
