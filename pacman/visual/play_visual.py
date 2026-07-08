import pygame
from pacman.assets import LoadedAssets
from pacman.core import GameState
from pacman.ui import Colors
from typing import Dict, Any

HUD_IMAGES_POS = {
    "score_board": (1632, 140),
    "score_board_gg": (941, 744),
    "lives_icon": (1632, 460),
    "level_icon": (1632, 623),
    "timer_icon": (1632, 802),
    "volume_bar": (159, 1163),
    "game_over": (811, 178),
    "good_job": (811, 178),
    "pause_button": (1970, 980),
    "sound_icon": (365, 1140)
}

HUD_LABEL_RECTS = {
    "lives": (1632, 512, 149, 44),
    "level": (1632, 684, 149, 44),
}

HUD_TEXT_POSITIONS = {
    "score": (1774, 323),
    "score_gg": (1083, 926),
    "your_final_score": (981, 704),
    "lives_label": (1663, 516),
    "lives_value": (1833, 492),
    "level_label": (1658, 686),
    "level_value": (1833, 683),
    "timer": (1833, 862),
    "loading": (780, 848),
}

NEXT_BUTTON = {
    "font_size": 24,
    "width": 120,
    "height": 50,
    "right_margin": 20,
    "top": 40,
}

MAZE_WALL_WIDTH = 5
PLAY_AREA_RADIUS = 50
HUD_LABEL_RADIUS = 8


class PlayVisualMixin:
    """Draw the gameplay screen, HUD, entities, and overlays."""

    def draw_play(self, state: GameState) -> None:
        """
        Draw play page wit all the HUDS.

        Args:
            state: game state.
        """
        r_start_x, r_start_y = (
            self.black_rectangle_start[0],
            self.black_rectangle_start[1],
        )

        r_width, r_height = (
            self.black_rectangle_width,
            self.black_rectangle_height,
        )

        self.screen.blit(self.background_img, (0, 0))
        pygame.draw.rect(
            self.screen,
            Colors.BLACK.value,
            (r_start_x, r_start_y, r_width, r_height),
            border_radius=self.radius(PLAY_AREA_RADIUS),
        )
        self.screen.blit(
            self.score_board, self.pos(HUD_IMAGES_POS["score_board"])
        )

        self.draw_text(
            f"{state.statistics.score}",
            self.start_font,
            Colors.BLACK.value,
            HUD_TEXT_POSITIONS["score"],
            center=True,
        )

        self.screen.blit(
            self.lives_icon, self.pos(HUD_IMAGES_POS["lives_icon"])
        )
        pygame.draw.rect(
            self.screen,
            Colors.CYAN.value,
            self.rect(HUD_LABEL_RECTS["lives"]),
            border_radius=self.radius(HUD_LABEL_RADIUS),
        )
        self.draw_text(
            "LIVES",
            self.button_font,
            Colors.BLACK.value,
            HUD_TEXT_POSITIONS["lives_label"],
        )
        self.draw_text(
            f"{state.statistics.lives}",
            self.title_font,
            Colors.WHITE.value,
            HUD_TEXT_POSITIONS["lives_value"],
        )

        self.screen.blit(
            self.level_icon, self.pos(HUD_IMAGES_POS["level_icon"])
        )
        pygame.draw.rect(
            self.screen,
            Colors.CYAN.value,
            self.rect(HUD_LABEL_RECTS["level"]),
            border_radius=self.radius(HUD_LABEL_RADIUS),
        )
        self.draw_text(
            "LEVEL",
            self.button_font,
            Colors.BLACK.value,
            HUD_TEXT_POSITIONS["level_label"],
        )
        self.draw_text(
            f"{state.current_level_index + 1}",
            self.title_font,
            Colors.WHITE.value,
            HUD_TEXT_POSITIONS["level_value"],
        )

        self.screen.blit(
            self.timer_icon, self.pos(HUD_IMAGES_POS["timer_icon"])
        )
        self.draw_text(
            f"{state.statistics.time_left}",
            self.start_font,
            Colors.WHITE.value,
            HUD_TEXT_POSITIONS["timer"],
        )

        # play back button
        self.draw_button(self.play_back_button, self.button_font)

        # next level button
        if state.cheat is True:
            self.draw_button(self.next_level_button, self.button_font)

        # pause_button
        if state.status == "play":
            self.screen.blit(
                self.pause_button, self.pos(HUD_IMAGES_POS["pause_button"])
            )

        # resume button
        elif state.status == "pause":
            self.screen.blit(
                self.resume_button, self.pos(HUD_IMAGES_POS["pause_button"])
            )

        # cheat mode button
        if state.cheat is True:
            self.draw_button(self.cheat_mode_enabled_button, self.button_font)
        elif state.cheat is False:
            self.draw_button(self.cheat_mode_disabled_button, self.button_font)

        # volume bar
        self.screen.blit(
            self.volume_bar, self.pos(HUD_IMAGES_POS["volume_bar"])
        )
        self.screen.blit(
            self.volume_knob, (self.x(self.knob_x), self.y(self.knob_y))
        )

        # sound icon next to volume bar
        self.screen.blit(
            self.sound_icon, self.pos(HUD_IMAGES_POS["sound_icon"])
        )

    def get_pause_button_rect(self) -> pygame.Rect:
        """
        Draw play/pause button

        Returns:
            a pygame rect for pause button.
        """
        return self.pause_button.get_rect(
            topleft=self.pos(HUD_IMAGES_POS["pause_button"])
        )

    def draw_grid_asset(
        self,
        state: GameState,
        asset_name: str,
        grid_position: tuple[int, int],
        sub_name: str | None = None,
        frame_index: int | None = None,
    ) -> None:
        """
        Draw different assets in maze.

        Args:
            state: game state.
            asset_name: asset name.
            grid_position: grid coordinate.
            sub_name: asset sub name.
            frame_index: frame index.
        """
        cell_size = state.level.cell_size
        thickness = state.wall_thickness

        if self.assets is None:
            self.assets = LoadedAssets()

        asset = self.assets.get_asset(
            name=asset_name,
            cell_size=cell_size,
            sub_name=sub_name,
            thickness=thickness,
        )

        if isinstance(asset, list) and frame_index is not None:
            asset = asset[frame_index % len(asset)]
        elif isinstance(asset, list):
            raise ValueError(f"Animated asset '{asset_name}' needs a frame.")

        asset_rect = asset.get_rect()
        x, y = grid_position

        if "pacman" in asset_name or "ghost" in asset_name:
            self.screen.blit(asset, grid_position)

        else:
            asset_rect.center = (
                state.MAZE_OFFSET_X
                + (x * cell_size)
                + thickness
                + ((cell_size - thickness) // 2),
                state.MAZE_OFFSET_Y
                + (y * cell_size)
                + thickness
                + ((cell_size - thickness) // 2),
            )

            self.screen.blit(asset, asset_rect)

    def draw_pacman(self, state: GameState) -> None:
        """
        Draw pacman while playing.

        Args:
            state: game state.
        """
        direction = state.pacman_direction or "right"
        x = state.pacman_x
        y = state.pacman_y

        if direction == "up":
            asset = "pacman_up"
        elif direction == "down":
            asset = "pacman_down"
        elif direction == "right":
            asset = "pacman_right"
        elif direction == "left":
            asset = "pacman_left"

        self.draw_grid_asset(
            state, asset, (x, y), "all", state.pacman_current_frame
        )

    def draw_pacgums(self, state: GameState) -> None:
        """
        Draw pacgums and super pacgums while playing.

        Args:
            state: game state.
        """
        if len(state.pacgums) == 0 and len(state.super_pacgums) == 0:
            self.draw_good_job(state)
            state.complete_level()
            return

        for x, y in state.pacgums:
            self.draw_grid_asset(state, "pacgum", (x, y))

        for x, y in state.super_pacgums:
            self.draw_grid_asset(state, "super_pacgum", (x, y))

    def draw_ghosts(self, state: GameState) -> None:
        """Draw every visible ghost with its current status and direction."""
        for ghost in state.ghosts:
            if ghost.status == "eaten":
                continue
            asset_name = ghost.asset_name
            if ghost.status == "vulnerable":
                asset_name = "vulnerable_ghost"
            self.draw_grid_asset(
                state=state,
                asset_name=f"{asset_name}_{ghost.direction}",
                grid_position=(ghost.pixel_x, ghost.pixel_y),
                sub_name="all",
                frame_index=state.ghost_current_frame,
            )

    def draw_final_score(self, state: GameState) -> None:
        """
        Draw final score when game_over or good_job at level_10.

        Args:
            state: game state.
        """
        self.screen.blit(self.score_board,
                         self.pos(HUD_IMAGES_POS["score_board_gg"]))
        self.draw_text(
            "FINAL SCORE",
            self.button_font,
            Colors.WHITE.value,
            HUD_TEXT_POSITIONS["your_final_score"],
            center=False,
        )
        self.draw_text(
            f"{state.statistics.score}",
            self.start_font,
            Colors.D_BLUE.value,
            HUD_TEXT_POSITIONS["score_gg"],
            center=True,
        )

    def draw_game_over(self, state: GameState) -> None:
        """
        Draw game over image when game is over.

        Args:
            state: game state.
        """
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        game_over_rect = self.game_over.get_rect()
        game_over_rect.centerx = self.screen_width // 2
        game_over_rect.top = self.y(HUD_IMAGES_POS["game_over"][1])

        self.screen.blit(self.game_over, game_over_rect)
        self.draw_final_score(state)
        # self.draw_button(self.play_back_button, self.button_font)

    def draw_good_job(self, state: GameState) -> None:
        """
        Draw good job when a level has been completed.

        Args:
            state: game state.
        """
        self.good_job_sound.play()
        old_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(0.2)

        start_time = pygame.time.get_ticks()
        clock = pygame.time.Clock()
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        good_job_rect = self.good_job.get_rect()
        good_job_rect.centerx = self.screen_width // 2
        good_job_rect.top = self.y(HUD_IMAGES_POS["good_job"][1])

        scaled_loading_pos = self.pos(HUD_TEXT_POSITIONS["loading"])
        self.start_point = scaled_loading_pos[0]
        self.end_point = self.start_point + self.x(550)
        self.loading_speed = self.x(330)
        self.loading_height = scaled_loading_pos[1] - self.y(80)

        spacing_pixels = self.x(90)
        delay_step = int((spacing_pixels / self.loading_speed) * 1000)

        self.loading_ghosts = [
            {"name": "blinky", "x": self.start_point, "delay": 0},
            {"name": "clyde", "x": self.start_point, "delay": delay_step},
            {"name": "pinky", "x": self.start_point, "delay": delay_step * 2},
            {"name": "inky", "x": self.start_point, "delay": delay_step * 3},
        ]

        while pygame.time.get_ticks() - start_time < 300000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            self.screen.blit(overlay, (0, 0))
            self.screen.blit(self.good_job, good_job_rect)
            self.draw_button(self.play_back_button, self.button_font)

            if not state.is_last_level():
                self.draw_text(
                    "Loading your next level...",
                    self.title_font,
                    Colors.WHITE.value,
                    HUD_TEXT_POSITIONS["loading"],
                    center=False,
                )
                delta_time = clock.tick(60) / 1000
                current_elapsed = pygame.time.get_ticks() - start_time
                for ghost in self.loading_ghosts:
                    if current_elapsed >= ghost["delay"]:
                        ghost["x"] += self.loading_speed * delta_time
                        if ghost["x"] > self.end_point:
                            ghost["x"] = self.start_point
                        self.draw_loading_pacman(ghost=ghost)
            else:
                # draw score
                self.draw_final_score(state)
                clock.tick(60)
            pygame.display.flip()
        pygame.mixer.music.set_volume(old_volume)

    def draw_loading_pacman(self, ghost: Dict[str, Any]) -> None:
        """
        Draw loading bar with ghosts moving forward.

        Args:
            ghost: ghosts to be drawn.
        """
        if ghost["name"] == "blinky":
            image1 = self.loading_blinky1
            image2 = self.loading_blinky2
        elif ghost["name"] == "clyde":
            image1 = self.loading_clyde1
            image2 = self.loading_clyde2
        elif ghost["name"] == "pinky":
            image1 = self.loading_pinky1
            image2 = self.loading_pinky2
        elif ghost["name"] == "inky":
            image1 = self.loading_inky1
            image2 = self.loading_inky2

        if (pygame.time.get_ticks() // 150) % 2 == 0:
            self.screen.blit(image1, (ghost["x"], self.loading_height))
        else:
            self.screen.blit(image2, (ghost["x"], self.loading_height))
