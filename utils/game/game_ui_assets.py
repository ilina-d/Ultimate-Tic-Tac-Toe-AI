import pygame
import os

# Dimensions
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

BOARD_WIDTH = BOARD_HEIGHT = 9
SQUARE_SIZE = 60

X_MARGIN = int((WINDOW_WIDTH - (BOARD_WIDTH * SQUARE_SIZE)) / 2)
Y_MARGIN = int((WINDOW_HEIGHT - (BOARD_HEIGHT * SQUARE_SIZE)) / 2)

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_OFF_WHITE = (200, 200, 200)
COLOR_LIGHT = (245, 245, 245)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (60, 60, 60)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_DARK_GRAY = (80, 80, 80)
COLOR_BLUE = (34, 161, 228)
COLOR_YELLOW = (242, 178, 20)

COLOR_DARK_BLUE = (22, 86, 119)
COLOR_DARK_YELLOW = (132, 100, 21)

BG_COLOR = COLOR_BLACK
BIG_LINE_COLOR = COLOR_OFF_WHITE
SMALL_LINE_COLOR = COLOR_GRAY

OPPOSITE_SIGN_COLORS = {'O': COLOR_YELLOW, 'X': COLOR_BLUE}
SIGN_COLORS = {'X': COLOR_YELLOW, 'O': COLOR_BLUE, 'T': SMALL_LINE_COLOR}


# Fix Assets Path
working_dir_path = os.getcwd().split('\\')[::-1]

if 'utils' not in os.listdir('.'):
    scope_counter = 1
    for _ in working_dir_path:
        if 'utils' in os.listdir('../' * scope_counter):
            break

        scope_counter += 1

    os.chdir('../' * scope_counter)


# Images:
x_img_small = pygame.image.load("utils/game/images/small_x.png")
x_img_big = pygame.image.load("utils/game/images/big_x.png")

o_img_small = pygame.image.load("utils/game/images/small_o.png")
o_img_big = pygame.image.load("utils/game/images/big_o.png")

title_image = pygame.image.load("utils/game/images/title/title.png")
title_image1 = pygame.image.load("utils/game/images/title/title1.png")
title_image2 = pygame.image.load("utils/game/images/title/title2.png")

choose_image = pygame.image.load("utils/game/images/choose_menu/choose.png")
choose_image_top_x = pygame.image.load("utils/game/images/choose_menu/top_x.png")
choose_image_top_o = pygame.image.load("utils/game/images/choose_menu/top_o.png")
choose_image_bottom_easy = pygame.image.load("utils/game/images/choose_menu/bottom_easy.png")
choose_image_bottom_normal = pygame.image.load("utils/game/images/choose_menu/bottom_normal.png")
choose_image_bottom_hard = pygame.image.load("utils/game/images/choose_menu/bottom_hard.png")
choose_image_top = pygame.image.load("utils/game/images/choose_menu/top.png")
choose_image_bottom = pygame.image.load("utils/game/images/choose_menu/bottom.png")

button_bar = pygame.image.load("utils/game/images/buttons/bar.png")
button_dark = pygame.image.load("utils/game/images/buttons/dark.png")
button_light = pygame.image.load("utils/game/images/buttons/light.png")
button_hint = pygame.image.load("utils/game/images/buttons/hint.png")
button_reset = pygame.image.load("utils/game/images/buttons/reset.png")
button_to_title = pygame.image.load("utils/game/images/buttons/to_title.png")
button_back = pygame.image.load("utils/game/images/buttons/back.png")

button_bar_hover = pygame.image.load("utils/game/images/buttons/bar_hover.png")
#button_dark_hover = pygame.image.load("utils/game/images/buttons/dark_hover.png")
#button_light_hover = pygame.image.load("utils/game/images/buttons/light_hover.png")
button_hint_hover = pygame.image.load("utils/game/images/buttons/hint_hover.png")
button_reset_hover = pygame.image.load("utils/game/images/buttons/reset_hover.png")
button_to_title_hover = pygame.image.load("utils/game/images/buttons/to_title_hover.png")
button_back_hover = pygame.image.load("utils/game/images/buttons/back_hover.png")

big_images = {'X': x_img_big, 'O': o_img_big}
small_images = {'X': x_img_small, 'O': o_img_small}

# Sounds
pygame.mixer.init()

click_sound = pygame.mixer.Sound('utils/game/sounds/zipclick.flac')

# Converters
rc_to_idx = (
        ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)),
        ((1, 4), (1, 5), (1, 6), (2, 4), (2, 5), (2, 6), (3, 4), (3, 5), (3, 6)),
        ((1, 7), (1, 8), (1, 9), (2, 7), (2, 8), (2, 9), (3, 7), (3, 8), (3, 9)),
        ((4, 1), (4, 2), (4, 3), (5, 1), (5, 2), (5, 3), (6, 1), (6, 2), (6, 3)),
        ((4, 4), (4, 5), (4, 6), (5, 4), (5, 5), (5, 6), (6, 4), (6, 5), (6, 6)),
        ((4, 7), (4, 8), (4, 9), (5, 7), (5, 8), (5, 9), (6, 7), (6, 8), (6, 9)),
        ((7, 1), (7, 2), (7, 3), (8, 1), (8, 2), (8, 3), (9, 1), (9, 2), (9, 3)),
        ((7, 4), (7, 5), (7, 6), (8, 4), (8, 5), (8, 6), (9, 4), (9, 5), (9, 6)),
        ((7, 7), (7, 8), (7, 9), (8, 7), (8, 8), (8, 9), (9, 7), (9, 8), (9, 9))
    )

idx_to_rc = (
        ((-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)),
        ((-1, -1), (0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)),
        ((-1, -1), (0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)),
        ((-1, -1), (0, 6), (0, 7), (0, 8), (1, 6), (1, 7), (1, 8), (2, 6), (2, 7), (2, 8)),
        ((-1, -1), (3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2)),
        ((-1, -1), (3, 3), (3, 4), (3, 5), (4, 3), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)),
        ((-1, -1), (3, 6), (3, 7), (3, 8), (4, 6), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8)),
        ((-1, -1), (6, 0), (6, 1), (6, 2), (7, 0), (7, 1), (7, 2), (8, 0), (8, 1), (8, 2)),
        ((-1, -1), (6, 3), (6, 4), (6, 5), (7, 3), (7, 4), (7, 5), (8, 3), (8, 4), (8, 5)),
        ((-1, -1), (6, 6), (6, 7), (6, 8), (7, 6), (7, 7), (7, 8), (8, 6), (8, 7), (8, 8))
    )
