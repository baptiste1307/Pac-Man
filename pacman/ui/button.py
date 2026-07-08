from typing import Any
from dataclasses import dataclass


@dataclass
class Button:
    """Store button geometry and text placement for pygame rendering."""

    rect_width: int
    rect_height: int
    rect_pos_x: int
    rect_pos_y: int
    text: str
    text_rect: Any
    stroke_thickness: int

    def __post_init__(self) -> None:

        self.rect = (
            self.rect_pos_x,
            self.rect_pos_y,
            self.rect_width,
            self.rect_height,
        )
