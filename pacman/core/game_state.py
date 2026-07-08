from typing import Any
from dataclasses import dataclass
from .statistics import Statistics
from .pacman_state import PacmanStateMixin
from .ghost_state import GhostStateMixin
from .level import Level
from .score_storage import get_score_path
from pathlib import Path
import json


@dataclass(kw_only=True)
class GameState(PacmanStateMixin, GhostStateMixin):
    """Central runtime state shared by the engine and visual layers."""

    config: dict[str, Any]
    game: Any
    status: str = "pause"
    current_level_index: int = 0
    animation_timer: int = 0
    animation_delay: int = 80
    level_timer: int = 0
    cheat: bool = False

    def __post_init__(self) -> None:
        self.statistics = Statistics(config=self.config)
        self.score_file = get_score_path(
            self.config.get("highscore_filename", "scores.json")
        )
        self.reset_level()

    def get_level(self) -> Level:
        """
        Get the level of the game.

        Return:
            Level: Level instance containing level information.
        """
        level = self.config["levels"][self.current_level_index]
        return Level(
            width=level["width"],
            height=level["height"],
            seed=level.get("seed", 0),
            game=self.game,
            index=self.current_level_index
        )

    def reset_stats(self) -> None:
        """
        Reset the statistics of the game when switching for the cheat mode.
        """
        if self.cheat is True:
            self.statistics.lives = 9999
            self.statistics.level_max_time = 9999

        else:
            self.statistics.lives = 3
            self.statistics.level_max_time = self.config["level_max_time"]

        self.statistics.time_left = self.statistics.level_max_time

    def is_last_level(self) -> bool:
        """
        Check if it's the last level of the game.
        """
        return self.current_level_index >= len(self.config["levels"]) - 1

    def complete_level(self) -> None:
        """
        Check if player complete the last level and win the game.
        """
        if self.is_last_level():
            self.status = "game_won"
            return

        self.current_level_index += 1
        self.reset_level()

    def find_42_pattern_cells(self) -> list[tuple[int, int]]:
        """
        Draw the 42 pattern in maze when possible.

        Returns:
            a list of cells where 42 patterns should be drawn.
        """
        return [
            (x, y)
            for y, row in enumerate(self.current_maze)
            for x, _ in enumerate(row)
            # if cell is fully closed
            if self.current_maze[y][x] == 15
        ]

    def reset_level(self) -> None:
        """
        Reset level.
        """
        self.status = "pause"

        self.level = self.get_level()
        self.current_maze = self.level.maze.maze
        self.fourty_two_cells = self.find_42_pattern_cells()

        self.update_level_layout()
        self.reset_pacman_state()

        if self.cheat is False:
            self.statistics.lives = 3
            self.statistics.level_max_time = self.config["level_max_time"]
            self.statistics.time_left = self.statistics.level_max_time

        self.reset_ghosts_states()

        self.level_timer = 0
        self.statistics.time_left = self.statistics.level_max_time

    def update_level_layout(self) -> None:
        """
        Update level layout.
        """
        self.level.cell_size = self.level._find_cell_size(
            self.level.width,
            self.level.height,
        )

        cell_size = self.level.cell_size

        self.wall_thickness = max(1, int(0.30 * cell_size))

        self.maze_width_pixel = self.level.width * cell_size

        self.maze_height_pixel = self.level.height * cell_size

        self.MAZE_OFFSET_X = self.game.black_rectangle_start[0] + (
            (self.game.black_rectangle_width - self.maze_width_pixel) // 2
        )
        self.MAZE_OFFSET_Y = self.game.black_rectangle_start[1] + (
            (self.game.black_rectangle_height - self.maze_height_pixel) // 2
        )

        last_row = self.level.height - 1
        last_col = self.level.width - 1

        self.maze_corners_coords = [
            (0, 0),
            (last_col, 0),
            (0, last_row),
            (last_col, last_row),
        ]

    def refresh_layout(self) -> None:
        """
        Refresh level layout when necessary.
        """
        self.update_level_layout()
        self.set_pacman_start_position()

    def load_scores(
        self, file_name: str | Path | None = None
    ) -> list[dict[str, Any]]:
        """
        Load saved scores, returning an empty list on missing/bad files.

        Args:
            file_name: the file_name of scores.json.

        Returns:
            a list of dictionary containing name and score of players.
        """
        path = self.score_file if file_name is None else get_score_path(
            file_name
        )
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                with open(path, "w") as f:
                    json.dump([], f)
                return []
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def save_new_score(
        self,
        name: str,
        score: int,
        file_name: str | Path | None = None,
    ) -> None:
        """
        Save a new score and keep only the top 10 entries.

        Args:
            name: player name
            score: player score
            file_name: the score json file where the score will be saved.
        """
        path = self.score_file if file_name is None else get_score_path(
            file_name
        )
        scores_list = self.load_scores(path)
        scores_list.append({"name": name, "score": score})
        sorted_list = sorted(
            scores_list, key=lambda x: x["score"], reverse=True
        )
        top_scores = sorted_list[:10]
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(top_scores, f, indent=4)

    def is_top_10(
        self, score: int, file_name: str | Path | None = None
    ) -> bool:
        """
        Return whether a score belongs in the current top 10 list.

        Args:
            score: player final score
            file_name: the score json file ready to be loaded.
        """
        scores_json = self.load_scores(file_name)
        score_list = [d["score"] for d in scores_json]
        score_list += [score]
        score_list.sort(reverse=True)
        if score_list.index(score) <= 9:
            return True
        return False
