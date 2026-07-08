#! /usr/bin/env python3

import pygame
from pacman.core import GameState
from pacman.visual import GameVisual
from .engine_utils import EngineUtils
from typing import Any


class GameEngine:
    """Coordinate events, game updates, and rendering."""

    def __init__(self) -> None:
        self.dragging = False

    def handle_events(
        self, game: GameVisual, state: GameState, utils: EngineUtils
    ) -> str:
        """
        Handle pygame events - user interaction.

        Args:
            game: the rendering of the game - GameVisual.
            state: current game state - GameState.
            utils: utility functions for the game - EngineUtils.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if state.status != "pause":
                        state.status = "pause"
                    else:
                        state.status = "play"

                if event.key == pygame.K_c:
                    state.cheat = not state.cheat
                    state.reset_stats()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if state.cheat is True:
                    if pygame.Rect(game.next_level_button.rect).collidepoint(
                        mouse_pos
                    ):
                        if state.current_level_index + 1 >= len(
                            state.config["levels"]
                        ):
                            state.status = "game_won"
                        else:
                            utils.next_level(state)

                if pygame.Rect(game.play_back_button.rect).collidepoint(
                    mouse_pos
                ):
                    return "menu"

                if game.get_pause_button_rect().collidepoint(mouse_pos):
                    if state.status != "pause":
                        state.status = "pause"
                    else:
                        state.status = "play"

                if pygame.Rect(
                    game.cheat_mode_enabled_button.rect
                ).collidepoint(mouse_pos) or pygame.Rect(
                    game.cheat_mode_disabled_button.rect
                ).collidepoint(
                    mouse_pos
                ):
                    state.cheat = not state.cheat
                    state.reset_stats()

                if game.track_rect.collidepoint(mouse_pos):
                    self.dragging = True

            if event.type == pygame.VIDEORESIZE:
                game.resize(event.w, event.h)
                state.refresh_layout()

            if event.type == pygame.MOUSEMOTION and self.dragging:
                mx = event.pos[0]
                left = game.x(game.knob_x_left)
                right = game.x(game.knob_x_right)
                if mx <= right and mx >= left:
                    game.volume = 1 - (right - mx) / (right - left)
                    pygame.mixer.music.set_volume(game.volume)
                    game.knob_x = game.knob_x_left + game.volume * (
                        game.knob_x_right - game.knob_x_left
                    )

            if event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False

        return "play"

    def render(
        self,
        game: GameVisual,
        state: GameState,
    ) -> None:
        """
        Rendering the game on the screen.

        Args:
            game: the rendering of the game - GameVisual.
            state: current game state - GameState.
        """

        game.draw_maze(state)
        game.draw_pacman(state)
        game.draw_pacgums(state)
        game.draw_ghosts(state)
        if state.status == "game_over":
            game.draw_game_over(state)
        game.present()

    def init_game(self, config: dict[str, Any]) -> None:
        """
        The engine of the game.

        Args:
            config: the parsed game configuration.
        """
        game = GameVisual()

        pygame.init()
        pygame.display.set_caption("Pac-Man")

        utils = EngineUtils()
        clock = pygame.time.Clock()
        app_running = True

        while app_running:
            game.main_menu()
            state = GameState(config=config, game=game)

            game_running = True
            while game_running:
                # time since previous frame (in ms)
                dt = clock.tick(60)
                event_result = self.handle_events(game, state, utils)

                if event_result == "quit":
                    app_running = False
                    game_running = False
                    continue

                if event_result == "menu":
                    game_running = False
                    continue

                if state.status != "game_over" and state.status != "game_won":
                    if state.status != "pause":
                        state.level_timer += dt

                    # when 1 sec passed
                    if state.level_timer >= 1000:
                        state.level_timer = 0
                        state.statistics.time_left -= 1

                        for ghost in state.ghosts:
                            if ghost.status == "vulnerable":
                                ghost.vulnerable_timer += 1

                                if (
                                    ghost.vulnerable_timer
                                    >= ghost.vulnerable_max_time
                                ):
                                    ghost.status = "normal"
                                    ghost.speed = state.normal_ghost_speed
                                    ghost.vulnerable_timer = 0

                            elif ghost.status == "eaten":
                                ghost.before_respawn_timer += 1

                                if (
                                    ghost.before_respawn_timer
                                    >= ghost.time_to_respawn
                                ):
                                    # this ghost respawns in his corner
                                    state.reset_ghosts_states(ghost=ghost)

                        if state.statistics.time_left <= 0:
                            # lose a life
                            state.statistics.lives -= 1
                            # reset timer
                            state.statistics.time_left = (
                                state.statistics.level_max_time
                            )
                            # reset the same level if pacman still have lives
                            if state.statistics.lives > 0:
                                state.reset_level()
                            # if lives <= 0: handle game over
                            elif state.statistics.lives <= 0:
                                state.status = "game_over"

                    utils.update_animation(state, dt)
                    utils.update_wanted_direction(state)
                    utils.update_pacman_target(state)
                    utils.move_pacman(state, dt)
                    utils.eat_touched_pacgums(state)
                    utils.move_ghosts(state, dt)
                    utils.check_ghost_collisions(state)
                # if game over or game_won
                else:
                    # only for game over: play specific sound
                    if state.status == "game_over":
                        self.render(game, state)
                        game.game_over_sound.play()
                        pygame.time.wait(3000)

                    # for game_over AND game_won: enter name and display scores
                    if state.is_top_10(state.statistics.score):
                        name_result = game.ask_player_name(state)
                        # close app
                        if name_result == "quit":
                            app_running = False
                            game_running = False
                            continue
                        # go back to menu but dont close app
                        if name_result == "menu":
                            game_running = False
                            continue

                        # Else display top scores list
                        score_result = game.show_score_list(state.score_file)
                        if score_result == "quit":
                            app_running = False
                        game_running = False
                        continue

                game.draw_play(state)
                self.render(game, state)

        pygame.quit()
