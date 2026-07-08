import pygame

from pacman.core import GameState
from pacman.ui import Colors
from pacman.wall_sprites import Sprites


class MazeVisualMixin:
    """Draw the generated maze grid and its wall intersections."""

    def draw_wall(
        self,
        mask_value: int,
        x: int,
        y: int,
        cell_size: int,
        state: GameState,
        thickness: int,
    ) -> None:
        """Draw one maze-wall intersection from its neighbor mask."""
        if self.sprites is None:
            self.sprites = Sprites()

        sprite, (origin_x, origin_y) = self.sprites.get_sprite_by_mask(
            mask_value, cell_size, thickness
        )

        maze_x = state.MAZE_OFFSET_X + x * cell_size + thickness // 2
        maze_y = state.MAZE_OFFSET_Y + y * cell_size + thickness // 2

        intersection_x = maze_x - origin_x
        intersection_y = maze_y - origin_y

        self.screen.blit(sprite, (intersection_x, intersection_y))

    def get_mask_value(
        self, x: int, y: int, rows: int, cols: int, maze: list[list[int]]
    ) -> int:
        """Build the wall mask for one maze intersection."""
        top_left_cell = maze[y - 1][x - 1] if y > 0 and x > 0 else None
        top_right_cell = maze[y - 1][x] if y > 0 and x < cols else None
        bottom_left_cell = maze[y][x - 1] if y < rows and x > 0 else None
        bottom_right_cell = maze[y][x] if y < rows and x < cols else None

        mask = 0

        # if vertical up wall
        if (top_left_cell and top_left_cell & 2) or (
            top_right_cell and top_right_cell & 8
        ):
            mask |= 1

        # if vertical down wall
        if (bottom_left_cell and bottom_left_cell & 2) or (
            bottom_right_cell and bottom_right_cell & 8
        ):
            mask |= 4

        # if horizontal left wall
        if (top_left_cell and top_left_cell & 4) or (
            bottom_left_cell and bottom_left_cell & 1
        ):
            mask |= 8

        # if horizontal right wall
        if (top_right_cell and top_right_cell & 4) or (
            bottom_right_cell and bottom_right_cell & 1
        ):
            mask |= 2

        return mask

    def draw_maze(self, state: GameState) -> None:
        """Draw the full maze, including closed 42 cells and wall joints."""
        # 1,2,4,8 = N, E, S, W
        maze = state.current_maze
        cell_size = state.level.cell_size
        thickness = state.wall_thickness

        # go through each cell of the maze
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                px = state.MAZE_OFFSET_X + x * cell_size
                py = state.MAZE_OFFSET_Y + y * cell_size

                # if cell of 42 pattern, 4 walls, closed
                if cell == 15:
                    half = thickness // 2
                    pygame.draw.rect(
                        self.screen,
                        Colors.NEON_PINK.value,
                        (
                            px + half,
                            py + half,
                            cell_size - half,
                            cell_size - half,
                        ),
                    )

        rows = len(maze)
        cols = len(maze[0])
        intersections_count_x = cols + 1
        intersections_count_y = rows + 1

        # go through every intersection of the maze
        for y in range(0, intersections_count_y):
            for x in range(0, intersections_count_x):

                mask_value = self.get_mask_value(x, y, rows, cols, maze)

                # if mask_value == 0:
                #     continue

                self.draw_wall(mask_value, x, y, cell_size, state, thickness)
