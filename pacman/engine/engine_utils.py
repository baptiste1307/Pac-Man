import pygame
from pacman.core import GameState
from typing import Any


class EngineUtils:
    """Pure gameplay helpers used by the main engine loop."""

    def __init__(self) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.sound_eat = pygame.mixer.Sound("./sounds/sound_eat.mp3")
        self.sound_supergum = pygame.mixer.Sound("./sounds/supergum_eat.mp3")
        self.sound_eat.set_volume(0.4)

    def can_move(
        self,
        maze: list[list[int]],
        grid_x: int,
        grid_y: int,
        pacman_direction: str | None,
        state: GameState,
    ) -> bool:
        """
        If towards a certain direction is movable.

        Args:
            maze: the game maze, a list of walls.
            grid_x: x coordinate of the grid.
            grid_y: y coordinate of the grid.
            pacman_direction: where pacman wants to go.
            state: pacman's status.

        Returns:
            bool: if moving is now possible.
        """
        cell = maze[grid_y][grid_x]

        if state.status == "pause":
            return False

        if pacman_direction == "up":
            return not (cell & 1)
        if pacman_direction == "right":
            return not (cell & 2)
        if pacman_direction == "down":
            return not (cell & 4)
        if pacman_direction == "left":
            return not (cell & 8)

        return False

    def next_level(self, state: GameState) -> None:
        """
        set next level

        Args:
            state: the game state.
        """

        state.current_level_index += 1

        pacgums_points_count = (
            len(state.pacgums) * state.statistics.points_per_pacgum
        )
        super_pacgums_points_count = (
            len(state.super_pacgums) * state.statistics.points_per_super_pacgum
        )

        total_level_points = pacgums_points_count + super_pacgums_points_count

        state.statistics.score += total_level_points
        state.reset_level()

    def update_animation(self, state: GameState, dt: int) -> None:
        """
        animation of ghosts and pacman.

        Args:
            state: current game state.
            dt: delta_time for animation delay calculation.
        """
        if state.status != "play":
            return
        state.animation_timer += dt

        if state.animation_timer >= state.animation_delay:
            state.animation_timer = 0
            state.pacman_current_frame = (state.pacman_current_frame + 1) % 3
            state.ghost_current_frame = (state.ghost_current_frame + 1) % 2

    def update_wanted_direction(self, state: GameState) -> None:
        """
        next movement according to keybaord input.

        Args:
            state: current game state.
        """
        keys = pygame.key.get_pressed()

        is_arrow = 0

        if keys[pygame.K_LEFT]:
            state.pacman_wanted_direction = "left"
            is_arrow = 1
        elif keys[pygame.K_RIGHT]:
            state.pacman_wanted_direction = "right"
            is_arrow = 1

        elif keys[pygame.K_UP]:
            state.pacman_wanted_direction = "up"
            is_arrow = 1

        elif keys[pygame.K_DOWN]:
            state.pacman_wanted_direction = "down"
            is_arrow = 1

        if is_arrow == 1 and state.status == "pause":
            state.status = "play"

    def update_pacman_target(self, state: GameState) -> None:
        """
        Updates pacman's movement.

        Args:
            state: current game state.
        """
        if state.status != "play" or state.pacman_wanted_direction is None:
            return

        if (
            state.pacman_x != state.target_x
            or state.pacman_y != state.target_y
        ):
            return

        # if pacman can move in the direction the player want
        if self.can_move(
            state.current_maze,
            state.pacman_grid_x,
            state.pacman_grid_y,
            state.pacman_wanted_direction,
            state,
        ):
            # the "official" direction is now the wanted direction
            state.pacman_direction = state.pacman_wanted_direction

        elif not self.can_move(
            state.current_maze,
            state.pacman_grid_x,
            state.pacman_grid_y,
            state.pacman_direction,
            state,
        ):
            state.pacman_current_frame = 1
            return

        if state.pacman_direction == "up":
            state.pacman_grid_y -= 1
        elif state.pacman_direction == "right":
            state.pacman_grid_x += 1
        elif state.pacman_direction == "down":
            state.pacman_grid_y += 1
        elif state.pacman_direction == "left":
            state.pacman_grid_x -= 1

        state.update_target_position()

    def move_pacman(self, state: GameState, dt: int) -> None:
        """
        Move pacman.

        Args:
            state: current game state.
            dt: delta_time for converse of speed in pixels/second.
        """
        if state.status != "play":
            return

        # clock.tick() returns milliseconds since last frame.
        # Multiplying by dt_seconds converts a speed in pixels/second
        # into the exact distance to travel for this frame.
        dt_seconds = dt / 1000
        # state.pacman_speed(px/s) * cell_size(px) * dt_seconds (s) = px
        step = state.pacman_speed * state.level.cell_size * dt_seconds

        if state.pacman_x < state.target_x:
            state.pacman_x = min(
                state.pacman_x + step,
                state.target_x,
            )
        elif state.pacman_x > state.target_x:
            state.pacman_x = max(
                state.pacman_x - step,
                state.target_x,
            )

        if state.pacman_y < state.target_y:
            state.pacman_y = min(
                state.pacman_y + step,
                state.target_y,
            )
        elif state.pacman_y > state.target_y:
            state.pacman_y = max(
                state.pacman_y - step,
                state.target_y,
            )

    def eat_touched_pacgums(self, state: GameState) -> None:
        """
        when pacman touched/eated pacgum.

        Args:
            state: current game state.
        """
        pacman_size = state.level.cell_size - state.wall_thickness
        pacman_radius = pacman_size / 2
        pacman_center_x = state.pacman_x + pacman_radius
        pacman_center_y = state.pacman_y + pacman_radius
        eaten_pacgums = []

        # add two sets together
        pacgums_and_super_pacgums = state.pacgums | state.super_pacgums

        for x, y in pacgums_and_super_pacgums:
            pacgum_center_x = (
                state.MAZE_OFFSET_X
                + x * state.level.cell_size
                + state.wall_thickness
                + ((state.level.cell_size - state.wall_thickness) // 2)
            )
            pacgum_center_y = (
                state.MAZE_OFFSET_Y
                + y * state.level.cell_size
                + state.wall_thickness
                + ((state.level.cell_size - state.wall_thickness) // 2)
            )

            distance_x = pacgum_center_x - pacman_center_x
            distance_y = pacgum_center_y - pacman_center_y

            if distance_x**2 + distance_y**2 <= pacman_radius**2:
                eaten_pacgums.append((x, y))

        for pacgum in eaten_pacgums:
            if pacgum in state.pacgums:
                state.pacgums.remove(pacgum)
                state.statistics.score += state.statistics.points_per_pacgum
                self.sound_eat.play()
            elif pacgum in state.super_pacgums:
                state.super_pacgums.remove(pacgum)
                state.statistics.score += (
                    state.statistics.points_per_super_pacgum
                )
                self.sound_supergum.play()
                for ghost in state.ghosts:
                    if ghost.status == "normal":
                        ghost.status = "vulnerable"
                        ghost.speed = state.vulnerable_ghost_speed
                self.sound_eat.play()

    def check_ghost_collisions(self, state: GameState) -> None:
        """
        when pacgum touched the ghost.

        Args:
            state: current game state.
        """
        if state.status != "play":
            return

        entity_size = state.level.cell_size - state.wall_thickness

        pacman_rect = pygame.Rect(
            state.pacman_x,
            state.pacman_y,
            entity_size,
            entity_size,
        )

        for ghost in state.ghosts:
            if ghost.status == "eaten":
                continue

            ghost_rect = pygame.Rect(
                ghost.pixel_x + (entity_size // 2),
                ghost.pixel_y + (entity_size // 2),
                entity_size // 2,
                entity_size // 2,
            )

            if pacman_rect.colliderect(ghost_rect):
                self.handle_pacman_touch_ghost(state, ghost)
                return

    def handle_pacman_touch_ghost(self, state: GameState, ghost: Any) -> None:
        """
        handle events when pacman touched a ghost.

        Args:
            state: current game state.
        """
        # ghost killed by pacman
        if ghost.status == "vulnerable":
            ghost.status = "eaten"
            ghost.vulnerable_timer = 0
            ghost.before_respawn_timer = 0
            ghost.speed = state.normal_ghost_speed
            state.statistics.score += state.config["points_per_ghost"]
            return

        # pacman killed by ghost
        elif ghost.status == "normal":
            if state.cheat is False:
                state.statistics.lives -= 1
                state.set_pacman_start_position()
                state.reset_ghosts_states()
                state.status = "pause"

        if state.statistics.lives <= 0:
            state.status = "game_over"
            return

    def move_ghosts(self, state: GameState, dt: int) -> None:
        """
        Move ghosts.

        Args:
            state: current game state.
            dt: delta_time for converse of speed in pixels/second.
        """
        if state.status != "play" or not state.ghosts:
            return

        state.update_ghosts_targets()
        dt_seconds = dt / 1000

        for ghost in state.ghosts:
            if ghost.status == "eaten":
                continue

            # Each ghost has its own pixels/second speed. The frame distance
            # changes with dt, so a slower frame moves farther once,
            # not slower.
            step = ghost.speed * state.level.cell_size * dt_seconds

            if ghost.pixel_x != ghost.pixel_target_x:
                if ghost.pixel_x < ghost.pixel_target_x:
                    ghost.pixel_x = min(
                        ghost.pixel_x + step,
                        ghost.pixel_target_x,
                    )
                    ghost.direction = "right"

                elif ghost.pixel_x > ghost.pixel_target_x:
                    ghost.pixel_x = max(
                        ghost.pixel_x - step,
                        ghost.pixel_target_x,
                    )
                    ghost.direction = "left"

            elif ghost.pixel_y != ghost.pixel_target_y:

                if ghost.pixel_y < ghost.pixel_target_y:
                    ghost.pixel_y = min(
                        ghost.pixel_y + step,
                        ghost.pixel_target_y,
                    )
                    ghost.direction = "down"

                elif ghost.pixel_y > ghost.pixel_target_y:
                    ghost.pixel_y = max(
                        ghost.pixel_y - step,
                        ghost.pixel_target_y,
                    )
                    ghost.direction = "up"
