import pygame
from typing import Any, Tuple

from pacman.ui import Button, Colors

BUTTON_OUTER_RADIUS = 40
BUTTON_INNER_RADIUS = 30
BUTTON_HOVER_Y_OFFSET = 5


class VisualBaseMixin:
    """Shared responsive drawing helpers for visual mixins."""

    def x(self, value: int) -> int:
        """
        Adapt original x into relative x
        for responsive design.

        Args:
            value: reference x value.

        Returns:
            int: converted x value.
        """
        return int(self.screen_width * (value / self.design_width))

    def y(self, value: int) -> int:
        """
        Adapt original y into relative y
        for responsive design.

        Args:
            value: reference y value.

        Returns:
            int: converted y value.
        """
        return int(self.screen_height * (value / self.design_height))

    def pos(self, value: Tuple[int, int]) -> Tuple[int, int]:
        """
        Adapt original coordinate into relative coordinate
        for responsive design.

        Args:
            value: reference coordinate.

        Returns:
            int: converted coordinate.
        """
        return self.x(value[0]), self.y(value[1])

    def size(self, value: Tuple[int, int]) -> Tuple[int, int]:
        """
        Adapt original element size into relative size
        for responsive design.

        Args:
            value: reference size value.

        Returns:
            int: converted size value.
        """
        return self.x(value[0]), self.y(value[1])

    def rect(
        self, value: Tuple[int, int, int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Adapt original Rect into relative Rect
        for responsive design.

        Args:
            value: reference Rect value.

        Returns:
            int: converted Rect value.
        """
        return (
            self.x(value[0]),
            self.y(value[1]),
            self.x(value[2]),
            self.y(value[3]),
        )

    def radius(self, value: int) -> int:
        """
        Adapt original radius value into relative radius value
        for responsive design.

        Args:
            value: reference radius value.

        Returns:
            int: converted radius value.
        """
        return max(
            1,
            int(
                value
                * min(
                    self.screen_width / self.design_width,
                    self.screen_height / self.design_height,
                )
            ),
        )

    def present(self) -> None:
        """
        Update the pygage screen.
        """
        pygame.display.flip()

    def draw_button(self, button: Button, button_font: Any) -> None:
        """
        Function to draw button quickly on the page.

        Args:
            button: button instance containing all button information.
            button_font: button test font.
        """
        mouse = pygame.mouse.get_pos()
        stroke_rect = (
            button.rect_pos_x,
            button.rect_pos_y,
            button.rect_width,
            button.rect_height,
        )
        button_rect = (
            button.rect_pos_x + button.stroke_thickness,
            button.rect_pos_y + button.stroke_thickness,
            button.rect_width - 2 * button.stroke_thickness,
            button.rect_height - 2 * button.stroke_thickness,
        )
        shade_rect = (
            button.rect_pos_x,
            button.rect_pos_y + button.stroke_thickness,
            button.rect_width,
            button.rect_height,
        )

        hovered = pygame.Rect(stroke_rect).collidepoint(mouse)

        button_color = Colors.D_BLUE.value
        stroke_and_text_color = (
            Colors.CYAN.value if hovered else Colors.B_YELLOW.value
        )
        texto = button_font.render(button.text, True, stroke_and_text_color)

        if not hovered:
            pygame.draw.rect(
                self.screen,
                Colors.CYAN.value,
                shade_rect,
                border_radius=self.radius(BUTTON_OUTER_RADIUS),
            )
            pygame.draw.rect(
                self.screen,
                stroke_and_text_color,
                stroke_rect,
                border_radius=self.radius(BUTTON_OUTER_RADIUS),
            )

        elif hovered:
            pygame.draw.rect(
                self.screen,
                stroke_and_text_color,
                stroke_rect,
                border_radius=self.radius(BUTTON_OUTER_RADIUS),
            )

        pygame.draw.rect(
            self.screen,
            button_color,
            button_rect,
            border_radius=self.radius(BUTTON_INNER_RADIUS),
        )

        if hovered:
            self.screen.blit(
                texto,
                (
                    button.text_rect[0],
                    button.text_rect[1] + self.y(BUTTON_HOVER_Y_OFFSET),
                ),
            )
        elif not hovered:
            self.screen.blit(texto, button.text_rect)

    def draw_text(
        self,
        text: str,
        font: Any,
        color: Tuple[int, int, int],
        pos: Tuple[int, int],
        center: bool = False,
    ) -> None:
        """
        Draw text on the screen.

        Args:
            text: the text content to draw.
            font: the desired text font.
            color: the desired text color.
            pos: the position to draw the text.
            center: if the text is center-positioned (or topleft).
        """
        to_draw_text = font.render(text, True, color)
        scaled_pos = self.pos(pos)
        if center:
            rect = to_draw_text.get_rect(center=scaled_pos)
            self.screen.blit(to_draw_text, rect)
        else:
            self.screen.blit(to_draw_text, scaled_pos)
