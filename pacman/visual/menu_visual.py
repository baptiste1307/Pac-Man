import pygame
import sys
import json
from pathlib import Path
from typing import Any

from pacman.ui import Colors
from pacman.config.parsing import Parser
from pacman.core.score_storage import get_score_path

HERO_POSITIONS = {
    "pacman": (383, 0),
    "credit": (875, 1094),
}
LOADING_POSITION = (760, 875)

MENU_FRAME_POS = (365, 208)
MENU_PANEL_RECT = (401, 258, 1356, 778)
MENU_PANEL_RADIUS = 30

INSTRUCTION_POSITIONS = {
    "title": (461, 298),
    "intro": (700, 402),
    "time": (1400, 440),
    "move_text": (700, 534),
    "up_down": (1307, 534),
    "left_right": (700, 572),
    "maze_text": (950, 572),
    "points_text": (700, 666),
    "small_point": (1115 + 20, 666),
    "super_point": (1115 + 20, 704),
    "ghost_point": (1412 + 20, 780),
    "small_value": (1070, 666),
    "super_value": (1068, 704),
    "ghost_value": (1346, 780),
    "ending": (700, 874),
    "keyboard": (461, 503),
}

TYPE_NAME_POSITIONS = {
    "title": (779, 322),
    "subtitle": (681, 436),
    "line": (938, 531),
    "image": (828, 678),
}

SCORE_POSITIONS = {
    "title": (743, 348),
    "name": (743, 434),
    "score": (1069, 434),
    "image": (1208, 460),
}

SCORE_ROW_OFFSET = 55
SCORE_NAME_DASH_TOTAL = 17


class MenuVisualMixin:
    """Draw and handle main menu, instructions, names, and scores."""

    def _handle_end_screen_event(
        self,
        event: pygame.event.Event,
        state: Any | None = None,
    ) -> str | None:
        """
        Handle end screen event such as click go back button.

        Args:
            event: pygame.event.
            state: different game states.

        Returns:
            either game state or none.
        """
        if event.type == pygame.QUIT:
            return "quit"

        if event.type == pygame.VIDEORESIZE:
            self.resize(event.w, event.h)
            if state is not None:
                state.refresh_layout()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(self.go_back_button.rect).collidepoint(event.pos):
                return "menu"

        return None

    def draw_hero(self) -> None:
        """
        Draw the hero page.
        """
        self.screen.blit(self.background_img, (0, 0))
        self.screen.blit(self.pacman_img, self.pos(HERO_POSITIONS["pacman"]))
        self.draw_button(self.start_button, self.start_font)
        self.draw_button(self.instruction_button, self.button_font)
        self.draw_button(self.score_button, self.button_font)
        self.draw_button(self.exit_button, self.button_font)
        self.draw_text(
            "A lovely project by bpasquer & hliu",
            self.text_font,
            Colors.B_YELLOW.value,
            HERO_POSITIONS["credit"],
        )

    def draw_instruction(self) -> None:
        """
        Draw instruction page.
        """
        p = Parser()
        p.parser_main(sys.argv)

        self.screen.blit(self.background_img, (0, 0))
        self.screen.blit(self.white_frame, self.pos(MENU_FRAME_POS))
        pygame.draw.rect(
            self.screen,
            Colors.WHITE.value,
            self.rect(MENU_PANEL_RECT),
            border_radius=self.radius(MENU_PANEL_RADIUS),
        )
        self.draw_text(
            "Instruction",
            self.title_font,
            Colors.D_BLUE.value,
            INSTRUCTION_POSITIONS["title"],
        )
        self.draw_text(
            "Try not to get eaten by aggressive ghosts.\nYou will be moved to "
            "next level if you last",
            self.t_font,
            Colors.D_BLUE.value,
            INSTRUCTION_POSITIONS["intro"],
        )
        self.draw_text(
            f"{p.level_max_time} seconds!",
            self.t_font,
            Colors.RED.value,
            INSTRUCTION_POSITIONS["time"],
        )
        self.draw_text(
            "Use the arrow keys to move Pac-Man ",
            self.t_font,
            Colors.D_BLUE.value,
            INSTRUCTION_POSITIONS["move_text"],
        )
        self.draw_text(
            "up, down",
            self.t_font,
            Colors.RED.value,
            INSTRUCTION_POSITIONS["up_down"],
        )
        self.draw_text(
            "left, and right ",
            self.t_font,
            Colors.RED.value,
            INSTRUCTION_POSITIONS["left_right"],
        )
        self.draw_text(
            "inside the mize.",
            self.t_font,
            Colors.D_BLUE.value,
            INSTRUCTION_POSITIONS["maze_text"],
        )
        self.draw_text(
            "Small dot (pac-gum) = \nBig dot (super-gum) = \nAfter eating "
            "super-gum, ghosts become vulnerable, \nIt's time to eat them up! "
            "Each ghost = ",
            self.t_font,
            Colors.D_BLUE.value,
            INSTRUCTION_POSITIONS["points_text"],
        )
        self.draw_text(
            "point,",
            self.t_font,
            Colors.D_BLUE.value,
            INSTRUCTION_POSITIONS["small_point"],
        )
        self.draw_text(
            "point,",
            self.t_font,
            Colors.D_BLUE.value,
            INSTRUCTION_POSITIONS["super_point"],
        )
        self.draw_text(
            "point,",
            self.t_font,
            Colors.D_BLUE.value,
            INSTRUCTION_POSITIONS["ghost_point"],
        )
        self.draw_text(
            f"{p.points_per_pacgum}",
            self.t_font,
            Colors.RED.value,
            INSTRUCTION_POSITIONS["small_value"],
        )
        self.draw_text(
            f"{p.points_per_super_pacgum}",
            self.t_font,
            Colors.RED.value,
            INSTRUCTION_POSITIONS["super_value"],
        )
        self.draw_text(
            f"{p.points_per_ghost}",
            self.t_font,
            Colors.RED.value,
            INSTRUCTION_POSITIONS["ghost_value"],
        )
        self.draw_text(
            "Try to survive and collect as many points!\nHave fun!!",
            self.t_font,
            Colors.D_BLUE.value,
            INSTRUCTION_POSITIONS["ending"],
        )

        self.screen.blit(
            self.instruc_img,
            self.pos(INSTRUCTION_POSITIONS["keyboard"]),
        )
        self.draw_button(self.go_back_button, self.button_font)

    def draw_type_name(self, current_name: str = "") -> None:
        """
        Draw type name page when player made to top 10.

        Args:
            current_name: input name from player.
        """
        self.screen.blit(self.background_img, (0, 0))
        self.screen.blit(self.white_frame, self.pos(MENU_FRAME_POS))
        pygame.draw.rect(
            self.screen,
            Colors.WHITE.value,
            self.rect(MENU_PANEL_RECT),
            border_radius=self.radius(MENU_PANEL_RADIUS),
        )
        self.draw_text(
            "Congratulations !!!",
            self.start_font,
            Colors.D_BLUE.value,
            TYPE_NAME_POSITIONS["title"],
        )
        self.draw_text(
            "Let us know what your name is...",
            self.title_font,
            Colors.D_BLUE.value,
            TYPE_NAME_POSITIONS["subtitle"],
        )
        display_name = current_name + "_" * (10 - len(current_name))
        self.draw_text(
            display_name,
            self.title_font,
            Colors.D_BLUE.value,
            TYPE_NAME_POSITIONS["line"],
        )
        self.screen.blit(
            self.type_name_img,
            self.pos(TYPE_NAME_POSITIONS["image"]),
        )
        self.draw_button(self.go_back_button, self.button_font)

    def ask_player_name(self, state: Any) -> str:
        """
        Ask player to type their name in type_name page.

        Args:
            state: game state.
        """
        current_name = ""
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)
            for event in pygame.event.get():
                common_result = self._handle_end_screen_event(event, state)
                if common_result is not None:
                    return common_result

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and current_name:
                        state.save_new_score(
                            name=current_name,
                            score=state.statistics.score,
                        )
                        return "score"

                    if event.key == pygame.K_BACKSPACE:
                        current_name = current_name[:-1]
                        continue

                    if len(current_name) < 10:
                        char = event.unicode
                        if char.isalnum() or char == " ":
                            current_name += char

            self.draw_type_name(current_name)
            self.present()

    def draw_score_list(
        self, file_name: str | Path = "scores.json"
    ) -> None:
        """
        Draw high score page according to score json file.

        Args:
            file_name: the score json file.
        """
        nb_dashes = {}
        try:
            path = get_score_path(file_name)
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                with open(path, "w") as f:
                    json.dump([], f)
            with open(path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = []
        sorted_scores = list(
            sorted(data, key=lambda x: x["score"], reverse=True)
        )
        self.screen.blit(self.background_img, (0, 0))
        self.screen.blit(self.white_frame, self.pos(MENU_FRAME_POS))
        pygame.draw.rect(
            self.screen,
            Colors.WHITE.value,
            self.rect(MENU_PANEL_RECT),
            border_radius=self.radius(MENU_PANEL_RADIUS),
        )
        self.draw_text(
            "Here are the best players...",
            self.title_font,
            Colors.D_BLUE.value,
            SCORE_POSITIONS["title"],
        )
        for d in sorted_scores:
            nb_dash = SCORE_NAME_DASH_TOTAL - len(d["name"])
            nb_dashes[d["name"]] = nb_dash
        i = 0
        for d in sorted_scores:
            row_y = SCORE_POSITIONS["name"][1] + SCORE_ROW_OFFSET * i
            self.draw_text(
                f"{d['name']} {'-' * nb_dashes[d['name']]}",
                self.button_font,
                Colors.D_BLUE.value,
                (SCORE_POSITIONS["name"][0], row_y),
            )
            self.draw_text(
                f"{d['score']}",
                self.button_font,
                Colors.D_BLUE.value,
                (SCORE_POSITIONS["score"][0], row_y),
            )
            i += 1
        self.screen.blit(self.score_img, self.pos(SCORE_POSITIONS["image"]))
        self.draw_button(self.go_back_button, self.button_font)

    def show_score_list(
        self, file_name: str | Path = "scores.json"
    ) -> str:
        """
        Show score list after player has typed their name.
        """
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)
            for event in pygame.event.get():
                common_result = self._handle_end_screen_event(event)
                if common_result is not None:
                    return common_result

            self.draw_score_list(file_name)
            self.present()
