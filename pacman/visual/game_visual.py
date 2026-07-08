import sys
import pygame
from dataclasses import dataclass
from pacman.ui import Button, Colors
from .menu_visual import MenuVisualMixin
from .maze_visual import MazeVisualMixin
from .play_visual import PlayVisualMixin
from .visual_base import VisualBaseMixin

DESIGN_SIZE = (2160, 1280)
INITIAL_WINDOW_SCALE = 0.7
PLAY_AREA_FILL_RATIO = 0.9

IMAGE_SIZES = {
    "white_frame": (1433, 871),
    "pacman_img": (1393, 929),
    "instruc_img": (170, 115),
    "type_name_img": (507, 221),
    "score_img": (436, 436),
    "score_board": (278, 278),
    "lives_icon": (149, 149),
    "level_icon": (149, 149),
    "timer_icon": (149, 149),
    "volume_bar": (228, 25),
    "volume_knob": (53, 53),
    "game_over": (537, 537),
    "loading_pacman": (53, 53),
    "pause_button": (70, 70),
    "sound_icon": (112, 75),
}

BUTTON_SPECS = {
    "start_button": (277, 86, 941, 721, "Start", (982, 726), 8),
    "instruction_button": (
        240,
        58,
        609,
        902,
        "Instruction",
        (626, 908),
        4,
    ),
    "score_button": (240, 58, 960, 902, "High Score", (988, 908), 4),
    "exit_button": (240, 58, 1311, 902, "Exit", (1390, 908), 4),
    "go_back_button": (160, 58, 1512, 912, "Go Back", (1523, 918), 2),
    "play_back_button": (170, 58, 1632, 1076, "Go Back", (1650, 1082), 2),
    "load_back_button": (240, 58, 960, 972, "Go Back", (1000, 978), 4),
    "next_level_button": (
        216,
        58,
        1832,
        1076,
        "Next Level",
        (1847, 1082),
        2,
    ),
    "cheat_mode_disabled_button": (
        330,
        58,
        1632,
        990,
        "Cheat mode: OFF",
        (1648, 996),
        2,
    ),
    "cheat_mode_enabled_button": (
        320,
        58,
        1632,
        990,
        "Cheat mode: ON",
        (1648, 996),
        2,
    ),
}

FONT_SIZES = {
    "start_font": 64,
    "button_font": 36,
    "text_font": 24,
    "title_font": 48,
    "t_font": 32,
}

PLAY_AREA = {
    "start": (125, 140),
    "size": (1429, 1000),
}


@dataclass
class GameVisual(
    VisualBaseMixin,
    MenuVisualMixin,
    MazeVisualMixin,
    PlayVisualMixin,
):
    """Main pygame visual object composed from focused drawing mixins."""

    pygame.init()
    pygame.font.init()

    design_width = DESIGN_SIZE[0]
    design_height = DESIGN_SIZE[1]
    play_area_fill_ratio = PLAY_AREA_FILL_RATIO

    colors: type = Colors
    my_font: str = (
        "fonts/Bitcount_Prop_Double/BitcountPropDouble-VariableFont_"
        "CRSV,ELSH,ELXP,slnt,wght.ttf"
    )

    volume = 0.5
    knob_x_left = 146
    knob_x_right = 344
    knob_x = (knob_x_left + knob_x_right) // 2
    knob_y = 1147
    dragging = False
    game_over = False
    good_job_sound = pygame.mixer.Sound("./sounds/good_job.mp3")
    game_over_sound = pygame.mixer.Sound("./sounds/game_over.mp3")

    def __post_init__(self) -> None:
        info = pygame.display.Info()
        width = int(info.current_w * INITIAL_WINDOW_SCALE)
        height = int(info.current_h * INITIAL_WINDOW_SCALE)
        self.resize(width, height)
        self.assets = None
        self.sprites = None

    def fit_to_design_ratio(self, width: int, height: int) -> tuple[int, int]:
        """
        Adapt original coordinates into responsive design.

        Args:
            width: screen_width
            height: screen_height

        Returns:
            tuple[int, int]: converted relative coordinate.
        """
        width = max(1, width)
        height = max(1, height)
        design_ratio = self.design_width / self.design_height
        requested_ratio = width / height

        if requested_ratio > design_ratio:
            height = height
            width = int(height * design_ratio)
        else:
            width = width
            height = int(width / design_ratio)

        return max(1, width), max(1, height)

    def resize(self, width: int, height: int) -> None:
        """
        Resize the elements after the calculation of relative coordinates.

        Args:
            width: screen_width
            height: screen_height
        """
        self.screen_width, self.screen_height = self.fit_to_design_ratio(
            width, height
        )
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.RESIZABLE,
        )
        self.load_fonts()
        self.load_images()
        self.load_buttons()
        self.load_play_area()

    def font_size(self, value: int) -> int:
        """
        Adapt original font size into relative font size
        for responsive design.

        Args:
            value: reference font size value.

        Returns:
            int: converted font size value.
        """
        return max(1, self.y(value))

    def load_fonts(self) -> None:
        """
        Load personalized font.
        """
        for font_name, font_size in FONT_SIZES.items():
            setattr(
                self,
                font_name,
                pygame.font.Font(self.my_font, self.font_size(font_size)),
            )

    def load_images(self) -> None:
        """
        Load images for the game visual.
        """
        self.background_img = pygame.transform.scale(
            pygame.image.load("./img/background.jpeg").convert(),
            (self.screen_width, self.screen_height),
        )
        self.white_frame = pygame.transform.scale(
            pygame.image.load("./img/white frame.png").convert_alpha(),
            self.size(IMAGE_SIZES["white_frame"]),
        )
        self.pacman_img = pygame.transform.scale(
            pygame.image.load("./img/pac-man-title.png").convert_alpha(),
            self.size(IMAGE_SIZES["pacman_img"]),
        )
        self.instruc_img = pygame.transform.scale(
            pygame.image.load("./img/keyboard.png").convert_alpha(),
            self.size(IMAGE_SIZES["instruc_img"]),
        )
        self.type_name_img = pygame.transform.scale(
            pygame.image.load("./img/type_name_img.png").convert_alpha(),
            self.size(IMAGE_SIZES["type_name_img"]),
        )
        self.score_img = pygame.transform.scale(
            pygame.image.load("./img/score_img.png").convert_alpha(),
            self.size(IMAGE_SIZES["score_img"]),
        )
        self.score_board = pygame.transform.scale(
            pygame.image.load("./img/play/score_board.png").convert_alpha(),
            self.size(IMAGE_SIZES["score_board"]),
        )
        self.lives_icon = pygame.transform.scale(
            pygame.image.load("./img/play/lives.png").convert_alpha(),
            self.size(IMAGE_SIZES["lives_icon"]),
        )
        self.level_icon = pygame.transform.scale(
            pygame.image.load("./img/play/level-badge.png").convert_alpha(),
            self.size(IMAGE_SIZES["level_icon"]),
        )
        self.timer_icon = pygame.transform.scale(
            pygame.image.load("./img/play/time.png").convert_alpha(),
            self.size(IMAGE_SIZES["timer_icon"]),
        )
        self.volume_bar = pygame.transform.scale(
            pygame.image.load("./img/volume bar.png").convert_alpha(),
            self.size(IMAGE_SIZES["volume_bar"]),
        )
        self.volume_knob = pygame.transform.scale(
            pygame.image.load("./img/volume knob.png").convert_alpha(),
            self.size(IMAGE_SIZES["volume_knob"]),
        )
        self.pause_button = pygame.transform.scale(
            pygame.image.load("./img/play/pause_button.png").convert_alpha(),
            self.size(IMAGE_SIZES["pause_button"]),
        )
        self.resume_button = pygame.transform.scale(
            pygame.image.load("./img/play/resume_button.png").convert_alpha(),
            self.size(IMAGE_SIZES["pause_button"]),
        )

        self.sound_icon = pygame.transform.scale(
            pygame.image.load("./img/sound_icon.png").convert_alpha(),
            self.size(IMAGE_SIZES["sound_icon"]),
        )

        self.track_rect = pygame.Rect(
            self.x(self.knob_x_left),
            self.y(self.knob_y - 10),
            self.x(self.knob_x_right - self.knob_x_left),
            self.y(self.volume_knob.get_height() + 20),
        )

        self.game_over = pygame.transform.scale(
            pygame.image.load("./img/game_over .png").convert_alpha(),
            self.size(IMAGE_SIZES["game_over"]),
        )

        self.good_job = pygame.transform.scale(
            pygame.image.load("./img/good_job.png").convert_alpha(),
            self.size(IMAGE_SIZES["game_over"]),
        )

        self.loading_blinky1 = pygame.transform.scale(
            pygame.image.load(
                "./assets/ghosts/blinky/right/1.png"
            ).convert_alpha(),
            self.size(IMAGE_SIZES["loading_pacman"]),
        )
        self.loading_blinky2 = pygame.transform.scale(
            pygame.image.load(
                "./assets/ghosts/blinky/right/2.png"
            ).convert_alpha(),
            self.size(IMAGE_SIZES["loading_pacman"]),
        )
        self.loading_clyde1 = pygame.transform.scale(
            pygame.image.load(
                "./assets/ghosts/clyde/right/1.png"
            ).convert_alpha(),
            self.size(IMAGE_SIZES["loading_pacman"]),
        )
        self.loading_clyde2 = pygame.transform.scale(
            pygame.image.load(
                "./assets/ghosts/clyde/right/2.png"
            ).convert_alpha(),
            self.size(IMAGE_SIZES["loading_pacman"]),
        )
        self.loading_pinky1 = pygame.transform.scale(
            pygame.image.load(
                "./assets/ghosts/pinky/right/1.png"
            ).convert_alpha(),
            self.size(IMAGE_SIZES["loading_pacman"]),
        )
        self.loading_pinky2 = pygame.transform.scale(
            pygame.image.load(
                "./assets/ghosts/pinky/right/2.png"
            ).convert_alpha(),
            self.size(IMAGE_SIZES["loading_pacman"]),
        )
        self.loading_inky1 = pygame.transform.scale(
            pygame.image.load(
                "./assets/ghosts/inky/right/1.png"
            ).convert_alpha(),
            self.size(IMAGE_SIZES["loading_pacman"]),
        )
        self.loading_inky2 = pygame.transform.scale(
            pygame.image.load(
                "./assets/ghosts/inky/right/2.png"
            ).convert_alpha(),
            self.size(IMAGE_SIZES["loading_pacman"]),
        )

    def make_button(
        self,
        width: int,
        height: int,
        x: int,
        y: int,
        text: str,
        text_pos: tuple[int, int],
        stroke_thickness: int,
    ) -> Button:
        """
        Draw buttons in the game.

        Args:
            width: button width
            height: button height
            x: where to put button (x)
            y: where to put button (y)
            text: button text content.
            text_pos: text reference coordinate.
            stroke_thickness: desired stroke of the button.

        Returns:
            a button object.
        """
        return Button(
            self.x(width),
            self.y(height),
            self.x(x),
            self.y(y),
            text,
            self.pos(text_pos),
            self.x(stroke_thickness),
        )

    def load_buttons(self) -> None:
        """
        Load buttons
        """
        for button_name, button_spec in BUTTON_SPECS.items():
            setattr(self, button_name, self.make_button(*button_spec))

    def load_play_area(self) -> None:
        """
        Load play area.
        """
        self.black_rectangle_start = self.pos(PLAY_AREA["start"])
        self.black_rectangle_width = self.x(PLAY_AREA["size"][0])
        self.black_rectangle_height = self.y(PLAY_AREA["size"][1])

    def main_menu(self) -> None:
        """
        Handle pygame events outside of game engine such as clicking buttons.
        """
        page = "hero"

        pygame.mixer.music.load("./sounds/background.ogg")
        pygame.mixer.music.play(-1)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit(0)
                if event.type == pygame.VIDEORESIZE:
                    self.resize(event.w, event.h)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    event_pos = event.pos
                    if page == "hero":
                        if pygame.Rect(self.start_button.rect).collidepoint(
                            event_pos
                        ):
                            page = "play"
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load("./sounds/play_bgm.ogg")
                            pygame.mixer.music.set_volume(0.5)
                            pygame.mixer.music.play(-1)

                        if pygame.Rect(
                            self.instruction_button.rect
                        ).collidepoint(event_pos):
                            page = "instruction"
                        if pygame.Rect(self.score_button.rect).collidepoint(
                            event_pos
                        ):
                            page = "score"
                        if pygame.Rect(self.exit_button.rect).collidepoint(
                            event_pos
                        ):
                            sys.exit(0)
                    elif page == "instruction":
                        if pygame.Rect(self.go_back_button.rect).collidepoint(
                            event_pos
                        ):
                            page = "hero"
                    elif page == "score":
                        if pygame.Rect(self.go_back_button.rect).collidepoint(
                            event_pos
                        ):
                            page = "hero"
                    elif page == "play":
                        if self.game_over is True:
                            print("HERE RIGHT?")
                        if pygame.Rect(
                            self.play_back_button.rect
                        ).collidepoint(event_pos):
                            page = "hero"
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load("./sounds/background.ogg")
                            pygame.mixer.music.play(-1)
            if page == "hero":
                self.draw_hero()
            elif page == "instruction":
                self.draw_instruction()
            elif page == "type_name":
                self.draw_type_name()
            elif page == "score":
                self.draw_score_list()
            elif page == "play":
                return
            self.present()
        pygame.quit()


if __name__ == "__main__":
    v = GameVisual()
    # scores = {"huian": 300, "baptiste": 600, "allan": 200, "james": 500}
    v.main_menu()
