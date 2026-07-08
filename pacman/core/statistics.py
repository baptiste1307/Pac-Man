#! /usr/bin/env python3

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Statistics:
    """Keep score, lives, timer, and point values for the current game."""

    config: dict[str, Any]
    score: int = 0
    lives: int = 3

    def __post_init__(self) -> None:
        self.level_max_time = self.config["level_max_time"]
        self.time_left = self.level_max_time
        self.points_per_ghost = self.config["points_per_ghost"]
        self.points_per_pacgum = self.config["points_per_pacgum"]
        self.points_per_super_pacgum = self.config["points_per_super_pacgum"]
        self.scores_list: Dict[str, int] = {}
