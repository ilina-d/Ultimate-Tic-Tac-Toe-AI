import pygame
import sys

from pygame.locals import *

from utils.players import Player, UserPlayer, RandomPlayer, MiniMaxPlayer
from utils.helpers import StateChecker, StateEvaluator, StateUpdater, GameEvaluator


import time

# TODO: change eval bar so theat it is animated :(

pygame.init()

# Dimensions
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

FPS = 120
FPS_CLOCK = pygame.time.Clock()

DISPLAY_SURF: pygame.Surface | None = None

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


StateChecker = StateChecker()
StateEvaluator = StateEvaluator()


class GameUI:
    """ Class representing the game state. """

    def __init__(self, player1: Player = UserPlayer(), player2: Player = UserPlayer(),
                 printing: bool = True, wait_after_move: int | str | None = 'input',
                 show_evaluation: bool = False, measure_thinking_time: bool = False,
                 opaque_on_board_completion: bool = True, light_theme: bool = False,
                 use_eval_bar: bool = False):
        """
        Create an instance of the Game class.

        Waiting Methods:
            - int | Number of milliseconds to wait.
            - "input" | Wait until input is given.
            - None | No waiting.

        Arguments:
             player1: The first player object.
             player2: The second player object.
             printing: Whether to print the board after each move.
             wait_after_move: The method for waiting after each move.
             show_evaluation: Whether to show the heuristic evaluation throughout the game.
                Printing needs to be turned on for this to work.
             measure_thinking_time: Whether to measure the time it takes for each player to make a move.
             opaque_on_board_completion: Whether to make the background of completed boards opaque.
             light_theme: Whether the UI will be dark or light theme.
             use_eval_bar: Whether to display the evaluation bar in the game UI.
        """

        global DISPLAY_SURF
        DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Ultimate Tic Tac Toe')

        global BG_COLOR, BIG_LINE_COLOR, SMALL_LINE_COLOR
        self.light_theme = light_theme
        if light_theme:
            BG_COLOR = COLOR_WHITE
            BIG_LINE_COLOR = COLOR_DARK_GRAY
            SMALL_LINE_COLOR = COLOR_LIGHT_GRAY

        self.state = None
        self.player1, self.player2 = player1, player2
        self.player1.set_sign('X'), self.player2.set_sign('O')
        self.prev_small_idx = None
        self.prev_move_made = None

        self.printing = printing
        self.show_evaluation = show_evaluation
        self.game_evaluator = GameEvaluator()

        self.measure_thinking_time = measure_thinking_time
        self.player1_thinking_times = []
        self.player2_thinking_times = []

        self.opaque_on_board_completion = opaque_on_board_completion
        self.use_eval_bar = use_eval_bar

        self.hinted_move = None
        self.reset = False
        self.selected_sign = None
        self.selected_difficulty = None

        def waiting(start_time: float = None):
            if wait_after_move is None:
                return
            if wait_after_move == 'input':
                input('... waiting for input ...')
                return
            if start_time:
                if time.time() - start_time <= wait_after_move:
                    pygame.time.wait(int(wait_after_move - (time.time() - start_time)))
                return
            else:
                pygame.time.wait(wait_after_move)
        self.wait_after_move = waiting

        self.reset_state()

        self.draw_board()


    def reset_state(self):
        """ Reset the current state to its starting form. """

        self.prev_small_idx = None
        self.state = (
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # Big board
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # Top-left small board
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # Top-middle small board
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # Top-right small board
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # Mid-left small board
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # ...
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},
        )


    def print_board(self):
        """ Prints the entire board. """

        s = self.state

        for i in (1, 4, 7):
            for j in (1, 4, 7):
                print(f'{s[i + 0]["display"][j]} {s[i + 0]["display"][j + 1]} {s[i + 0]["display"][j + 2]}  |  '
                      f'{s[i + 1]["display"][j]} {s[i + 1]["display"][j + 1]} {s[i + 1]["display"][j + 2]}  |  '
                      f'{s[i + 2]["display"][j]} {s[i + 2]["display"][j + 1]} {s[i + 2]["display"][j + 2]}')

            if i != 7:
                print('-------------------------')

        print('\n')

        for i in (1, 4, 7):
            print(f'{s[0]["display"][i]} | {s[0]["display"][i + 1]} | {s[0]["display"][i + 2]}')
            if i != 7:
                print('---------')

        print('\n')


    def make_move(self, sign: str, player: Player):
        """
        Make a move for a given sign.

        Arguments:
             sign: X or O.
             player: The player whose turn it is.
        """

        box_x, box_y = None, None
        big_idx, small_idx = None, None

        if isinstance(player, UserPlayer):
            waiting = True
            while waiting:
                self.check_for_quit()
                self.update_buttons()

                for event in pygame.event.get(pygame.MOUSEBUTTONUP):
                    click_sound.play()

                    self.check_for_button_click(event.pos, player)
                    if self.reset:
                        return

                    mouse_x, mouse_y = event.pos

                    box_x, box_y = self.get_box_at_pixel(mouse_x, mouse_y)

                    if box_x is not None and box_y is not None:
                        big_idx, small_idx = rc_to_idx[box_x][box_y]

                        if (big_idx, small_idx) not in player.get_current_legal_moves(self.prev_small_idx):
                            continue

                        waiting = False
                        break

        else:
            if self.measure_thinking_time:
                thinking_time_start = time.time()
                big_idx, small_idx = player.make_move(self.state, self.prev_small_idx)

                box_x, box_y = idx_to_rc[big_idx][small_idx]

                thinking_times = self.player1_thinking_times if sign == 'X' else self.player2_thinking_times
                thinking_times.append(time.time() - thinking_time_start)

            else:
                big_idx, small_idx = player.make_move(self.state, self.prev_small_idx)
                box_x, box_y = idx_to_rc[big_idx][small_idx]

        state, board_is_complete = StateUpdater.update_state(self.state, big_idx, small_idx, sign)

        # print(f"Drawing {sign} on box [{box_x}, {box_y}] and pos [{big_idx, small_idx}]")
        if self.hinted_move:
            self.cover_box(self.hinted_move[0], self.hinted_move[1])
            self.hinted_move = None
        self.draw_sign_on_box(box_x, box_y, sign)

        for i in set(i for i, _ in player.get_current_legal_moves(self.prev_small_idx)):
            self.draw_subgrid_at_board(i, SMALL_LINE_COLOR)

        self.state = state

        if self.state[0]['display'][big_idx] != '-':
            self.draw_sign_on_big_board(big_idx, self.state[0]['display'][big_idx])

        if self.state[0]['display'][small_idx] != '-':
            self.prev_small_idx = None
        else:
            self.prev_small_idx = small_idx

        self.prev_move_made = (big_idx, small_idx)

        player.update_legal_moves(big_idx, small_idx, board_is_complete=board_is_complete)


    def play(self):
        """ Start the game. """

        if not self.reset:
            self.show_title_screen()
        else:
            self.reset = False

        sign = 'X'
        player = self.player1
        move_start_time = None

        while not StateChecker.check_win(state = self.state, big_idx = 0):
            pygame.event.pump()
            self.check_for_quit()

            self.draw_buttons()
            self.update_buttons()

            already_evaluated = False
            if self.printing:
                self.print_board()
                print(f'{"X" if sign == "O" else "O"} made the move: {self.prev_move_made}')

                if self.measure_thinking_time:
                    if sign == 'O' and self.player1_thinking_times:
                        print(f'Time taken for move: {self.player1_thinking_times[-1]}')
                    elif sign == 'X' and self.player2_thinking_times:
                        print(f'Time taken for move: {self.player2_thinking_times[-1]}')

                if self.show_evaluation:
                    game_eval_score = self.game_evaluator.game_evaluation(self.state, self.prev_small_idx, player)
                    print(f'Game Evaluation  : '
                          f'{game_eval_score}')
                    already_evaluated = game_eval_score

            if not isinstance(player, UserPlayer):
                self.wait_after_move(move_start_time)

            move_start_time = time.time()
            self.make_move(sign, player)

            if self.reset:
                player = self.player1
                sign = 'X'
                move_start_time = None
                self.reset = False
                continue

            if self.use_eval_bar:
                self.update_eval_bar(player, already_evaluated)

            if self.prev_small_idx is not None:
                self.draw_subgrid_at_board(self.prev_small_idx, OPPOSITE_SIGN_COLORS[sign])
            else:
                for i in set(i for i, _ in player.get_current_legal_moves(self.prev_small_idx)):
                    self.draw_subgrid_at_board(i, OPPOSITE_SIGN_COLORS[sign])

            sign = 'O' if sign == 'X' else 'X'
            player = self.player2 if player == self.player1 else self.player1

            pygame.display.update()
            FPS_CLOCK.tick(FPS)

        winning_sign = StateChecker.check_win(self.state, big_idx = 0)

        if self.prev_small_idx is not None:
            self.draw_subgrid_at_board(self.prev_small_idx, SMALL_LINE_COLOR)
        else:
            for i in set(i for i, _ in player.get_current_legal_moves(self.prev_small_idx)):
                self.draw_subgrid_at_board(i, SMALL_LINE_COLOR)

        for i in range(3):
            self.draw_big_grid(SIGN_COLORS[winning_sign])
            pygame.time.wait(300)
            self.draw_big_grid(BIG_LINE_COLOR)
            pygame.time.wait(300)

        if self.printing:
            self.print_board()
            print(f'WINNER: {winning_sign}')

        # Wait to quit:
        wait_to_exit = True
        while wait_to_exit:
            self.check_for_quit()
            self.update_buttons()

            for event in pygame.event.get(MOUSEBUTTONUP):
                click_sound.play()
                self.check_for_button_click(event.pos, player)
                if self.reset:
                    self.play()


    def reset_players(self):
        self.player1 = UserPlayer()
        self.player1.set_sign('X')
        self.player2 = UserPlayer()
        self.player2.set_sign('O')

        player_to_alter = None

        if self.selected_difficulty == 'easy':
            player_to_alter = RandomPlayer()
        elif self.selected_difficulty == 'normal':
            player_to_alter = MiniMaxPlayer(target_depth=3)
        elif self.selected_difficulty == 'hard':
            player_to_alter = MiniMaxPlayer(target_depth='dynamic')

        if self.selected_sign == 'X':
            self.player2 = player_to_alter
            self.player2.set_sign('O')
        elif self.selected_sign == 'O':
            self.player1 = player_to_alter
            self.player1.set_sign('X')


    def show_title_screen(self):
        """ Displays the title and menu screens. """

        DISPLAY_SURF.blit(title_image, (0, 0))
        pygame.display.update()
        FPS_CLOCK.tick(FPS)

        on_main_menu = True
        while on_main_menu:
            one_player_rect = pygame.Rect(140, 510, 190, 40)
            two_player_rect = pygame.Rect(540, 510, 230, 40)
            # pygame.draw.rect(DISPLAY_SURF, COLOR_WHITE, one_player_rect)
            # pygame.draw.rect(DISPLAY_SURF, COLOR_WHITE, two_player_rect)

            self.check_for_quit()

            for event in pygame.event.get(pygame.MOUSEMOTION):
                mouse_x, mouse_y = event.pos
                if one_player_rect.collidepoint(mouse_x, mouse_y):
                    DISPLAY_SURF.blit(title_image1, (0, 0))
                elif two_player_rect.collidepoint(mouse_x, mouse_y):
                    DISPLAY_SURF.blit(title_image2, (0, 0))
                else:
                    DISPLAY_SURF.blit(title_image, (0, 0))

                pygame.display.update()
                FPS_CLOCK.tick(FPS)

            for event in pygame.event.get(MOUSEBUTTONUP):
                click_sound.play()

                mouse_x, mouse_y = event.pos
                if one_player_rect.collidepoint(mouse_x, mouse_y):
                    # user vs bot
                    on_choose_menu = True
                    selected_sign = None
                    selected_difficulty = None
                    DISPLAY_SURF.blit(choose_image, (0, 0))
                    DISPLAY_SURF.blit(button_back, (0, 0))
                    while on_choose_menu:
                        self.check_for_quit()

                        x_rect = pygame.Rect(295, 225, 90, 90)
                        o_rect = pygame.Rect(505, 225, 90, 90)

                        easy_rect = pygame.Rect(145, 510, 105, 45)
                        normal_rect = pygame.Rect(360, 510, 185, 45)
                        hard_rect = pygame.Rect(630, 510, 130, 45)

                        back_rect = pygame.Rect(0, 0, 60, 60)
                        # pygame.draw.rect(DISPLAY_SURF, COLOR_WHITE, easy_rect)
                        # pygame.draw.rect(DISPLAY_SURF, COLOR_WHITE, normal_rect)
                        # pygame.draw.rect(DISPLAY_SURF, COLOR_WHITE, harf_rect)
                        # pygame.draw.rect(DISPLAY_SURF, COLOR_WHITE, x_rect)
                        # pygame.draw.rect(DISPLAY_SURF, COLOR_WHITE, o_rect)

                        for event in pygame.event.get(MOUSEMOTION):
                            mouse_x, mouse_y = event.pos
                            if x_rect.collidepoint(mouse_x, mouse_y) and selected_sign is None:
                                DISPLAY_SURF.blit(choose_image_top_x, (0, 0))
                                pygame.draw.rect(DISPLAY_SURF, BG_COLOR, back_rect)
                                DISPLAY_SURF.blit(button_back, (0, 0))
                            elif o_rect.collidepoint(mouse_x, mouse_y) and selected_sign is None:
                                DISPLAY_SURF.blit(choose_image_top_o, (0, 0))
                                pygame.draw.rect(DISPLAY_SURF, BG_COLOR, back_rect)
                                DISPLAY_SURF.blit(button_back, (0, 0))
                            elif easy_rect.collidepoint(mouse_x, mouse_y) and selected_difficulty is None:
                                DISPLAY_SURF.blit(choose_image_bottom_easy, (0, 351))
                            elif normal_rect.collidepoint(mouse_x, mouse_y) and selected_difficulty is None:
                                DISPLAY_SURF.blit(choose_image_bottom_normal, (0, 351))
                            elif hard_rect.collidepoint(mouse_x, mouse_y) and selected_difficulty is None:
                                DISPLAY_SURF.blit(choose_image_bottom_hard, (0, 351))
                            else:
                                if selected_sign is None:
                                    DISPLAY_SURF.blit(choose_image_top, (0, 0))
                                    pygame.draw.rect(DISPLAY_SURF, BG_COLOR, back_rect)
                                    DISPLAY_SURF.blit(button_back, (0, 0))
                                if selected_difficulty is None:
                                    DISPLAY_SURF.blit(choose_image_bottom, (0, 351))

                                if back_rect.collidepoint(mouse_x, mouse_y):
                                    pygame.draw.rect(DISPLAY_SURF, BG_COLOR, back_rect)
                                    DISPLAY_SURF.blit(button_back_hover, (0, 0))
                                else:
                                    pygame.draw.rect(DISPLAY_SURF, BG_COLOR, back_rect)
                                    DISPLAY_SURF.blit(button_back, (0, 0))

                        for event in pygame.event.get(MOUSEBUTTONUP):
                            click_sound.play()

                            mouse_x, mouse_y = event.pos
                            if x_rect.collidepoint(mouse_x, mouse_y):
                                selected_sign = 'X'
                                DISPLAY_SURF.blit(choose_image_top_x, (0, 0))
                                pygame.draw.rect(DISPLAY_SURF, BG_COLOR, back_rect)
                                DISPLAY_SURF.blit(button_back, (0, 0))
                            elif o_rect.collidepoint(mouse_x, mouse_y):
                                selected_sign = 'O'
                                DISPLAY_SURF.blit(choose_image_top_o, (0, 0))
                                pygame.draw.rect(DISPLAY_SURF, BG_COLOR, back_rect)
                                DISPLAY_SURF.blit(button_back, (0, 0))
                            elif easy_rect.collidepoint(mouse_x, mouse_y):
                                selected_difficulty = 'easy'
                                DISPLAY_SURF.blit(choose_image_bottom_easy, (0, 351))
                            elif normal_rect.collidepoint(mouse_x, mouse_y):
                                selected_difficulty = 'normal'
                                DISPLAY_SURF.blit(choose_image_bottom_normal, (0, 351))
                            elif hard_rect.collidepoint(mouse_x, mouse_y):
                                selected_difficulty = 'hard'
                                DISPLAY_SURF.blit(choose_image_bottom_hard, (0, 351))
                            elif back_rect.collidepoint(mouse_x, mouse_y):
                                on_choose_menu = False
                                on_main_menu = True
                                DISPLAY_SURF.blit(title_image, (0, 0))
                                pygame.display.update()
                                FPS_CLOCK.tick(FPS)
                                break

                        pygame.display.update()
                        FPS_CLOCK.tick(FPS)

                        if selected_sign and selected_difficulty:
                            self.selected_sign = selected_sign
                            self.selected_difficulty = selected_difficulty

                            self.reset_players()

                            pygame.time.wait(100)
                            self.draw_board()
                            on_choose_menu = False
                            on_main_menu = False

                elif two_player_rect.collidepoint(mouse_x, mouse_y):
                    # user vs user
                    self.player1 = UserPlayer()
                    self.player1.set_sign('X')
                    self.player2 = UserPlayer()
                    self.player2.set_sign('O')

                    self.draw_board()
                    on_main_menu = False


    @staticmethod
    def draw_buttons():
        """ Displays the buttons on the game screen. """

        t, l = Y_MARGIN + 2 * SQUARE_SIZE, WINDOW_WIDTH - X_MARGIN + 1 * SQUARE_SIZE

        bg_rect = pygame.Rect(l, t, SQUARE_SIZE, 5 * SQUARE_SIZE)
        pygame.draw.rect(DISPLAY_SURF, BG_COLOR, bg_rect)

        DISPLAY_SURF.blit(button_hint, (l, t))
        # if self.light_theme:
        #     DISPLAY_SURF.blit(button_light, (l + SQUARE_SIZE, t + SQUARE_SIZE))
        # else:
        #     DISPLAY_SURF.blit(button_dark, (l, t + SQUARE_SIZE))
        DISPLAY_SURF.blit(button_bar, (l, t + 1 * SQUARE_SIZE))
        DISPLAY_SURF.blit(button_reset, (l, t + 3 * SQUARE_SIZE))
        DISPLAY_SURF.blit(button_to_title, (l, t + 4 * SQUARE_SIZE))

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


    def update_buttons(self):
        """ Updates the buttons on the game screen. """

        t, l = Y_MARGIN + 2 * SQUARE_SIZE, WINDOW_WIDTH - X_MARGIN + 1 * SQUARE_SIZE

        hint_rect = pygame.Rect(l, t, 60, 55)
        bar_rect = pygame.Rect(l, t + 1 * SQUARE_SIZE, 60, 55)

        reset_rect = pygame.Rect(l, t + 3 * SQUARE_SIZE, 60, 55)
        to_title_rect = pygame.Rect(l, t + 4 * SQUARE_SIZE, 60, 55)

        for event in pygame.event.get(MOUSEMOTION):
            mouse_x, mouse_y = event.pos
            if hint_rect.collidepoint(mouse_x, mouse_y):
                DISPLAY_SURF.blit(button_hint_hover, (l, t))
            elif bar_rect.collidepoint(mouse_x, mouse_y):
                DISPLAY_SURF.blit(button_bar_hover, (l, t + 1 * SQUARE_SIZE))
            elif reset_rect.collidepoint(mouse_x, mouse_y):
                DISPLAY_SURF.blit(button_reset_hover, (l, t + 3 * SQUARE_SIZE))
            elif to_title_rect.collidepoint(mouse_x, mouse_y):
                DISPLAY_SURF.blit(button_to_title_hover, (l, t + 4 * SQUARE_SIZE))
            else:
                self.draw_buttons()

            pygame.display.update()
            FPS_CLOCK.tick(FPS)


    def check_for_button_click(self, mouse_pos: tuple[int, int], player: Player):
        """ Checks weather a button was clicked and handles events accordingly.

        Arguments:
            mouse_pos: Position of the mouse click.
            player: Player whose turn it is.
        """

        t, l = Y_MARGIN + 2 * SQUARE_SIZE, WINDOW_WIDTH - X_MARGIN + 1 * SQUARE_SIZE

        hint_rect = pygame.Rect(l, t, 60, 55)
        bar_rect = pygame.Rect(l, t + 1 * SQUARE_SIZE, 60, 55)

        reset_rect = pygame.Rect(l, t + 3 * SQUARE_SIZE, 60, 55)
        to_title_rect = pygame.Rect(l, t + 4 * SQUARE_SIZE, 60, 55)

        if bar_rect.collidepoint(mouse_pos):
            self.use_eval_bar = False if self.use_eval_bar else True
            if self.use_eval_bar:
                game_eval_score = self.game_evaluator.game_evaluation(self.state, self.prev_small_idx, player)
                already_evaluated = game_eval_score or False
                self.update_eval_bar(player, already_evaluated)
            else:
                GameUI.hide_eval_bar()

        elif hint_rect.collidepoint(mouse_pos) and not StateChecker.check_win(self.state, big_idx = 0):
            b_idx, s_idx = self.game_evaluator.get_best_move(self.state, self.prev_small_idx, player)
            box_x, box_y = idx_to_rc[b_idx][s_idx]
            self.hinted_move = (box_x, box_y)
            self.draw_sign_on_box(box_x, box_y, player.sign)
            self.cover_box(box_x, box_y, transparent = True)

        elif reset_rect.collidepoint(mouse_pos):
            self.player1.reset_legal_moves()
            self.player2.reset_legal_moves()
            self.reset_players()
            self.reset_state()
            self.reset_board()
            self.reset = True

        elif to_title_rect.collidepoint(mouse_pos):
            self.player1.reset_legal_moves()
            self.player2.reset_legal_moves()
            self.reset_state()
            self.use_eval_bar = False
            self.selected_sign = None
            self.selected_difficulty = None
            self.play()

        pygame.display.update()
        FPS_CLOCK.tick(FPS)



    @staticmethod
    def hide_eval_bar():
        """ Hides the evaluation bar. """

        t, l = Y_MARGIN - 3, X_MARGIN - 100

        W = 16
        H = 546

        pygame.draw.rect(DISPLAY_SURF, BG_COLOR, (l, t, W, H))

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


    def update_eval_bar(self, player: Player, eval_score: int | bool = None):
        """
        Update the game evaluation bar.

        Arguments:
            player: The player object whose turn it is.
            eval_score: A precalculated evaluation score.
        """

        game_score = eval_score if eval_score \
            else self.game_evaluator.game_evaluation(self.state, self.prev_small_idx, player)
        yellow_h = int((game_score + 1000) / 2000 * 546)

        t, l = Y_MARGIN - 3, X_MARGIN - 100

        W = 16
        H = 546

        pygame.draw.rect(DISPLAY_SURF, COLOR_BLUE, (l, t, W, H))
        pygame.draw.rect(DISPLAY_SURF, COLOR_YELLOW, (l, t, W, yellow_h))

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


    def reset_board(self):
        """ Resets the board display. """

        self.draw_board()
        self.draw_buttons()


    @staticmethod
    def check_for_quit():
        """ Check for quit event. """

        for _ in pygame.event.get(QUIT):
            pygame.display.quit()
            pygame.quit()
            sys.exit()

        for event in pygame.event.get(KEYDOWN):
            if event.key == K_ESCAPE:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            pygame.event.post(event)


    @staticmethod
    def top_left_coords_of_box(box_x: int, box_y: int) -> tuple[int, int]:
        """
        Get the top left pixel coordinates of a box.

        Arguments:
            box_x: Box row index.
            box_y: Bow column index.

        Returns:
              The top left pixel coordinates of the box.
        """

        left = box_y * SQUARE_SIZE + X_MARGIN
        top = box_x * SQUARE_SIZE + Y_MARGIN
        return left, top


    @staticmethod
    def get_box_at_pixel(x: int, y: int) -> tuple[int, int] | tuple[None, None]:
        """
        Get the row and column of the box at the given pixel coordinates.

        Arguments:
            x: X-coordinate of pixel being checked.
            y: Y-coordinate of pixel being checked.

        Returns:
            The row and column of the box or None if not found.
        """

        for box_x in range(BOARD_WIDTH):
            for box_y in range(BOARD_HEIGHT):
                left, top = GameUI.top_left_coords_of_box(box_x, box_y)
                box_rect = pygame.Rect(left, top, SQUARE_SIZE, SQUARE_SIZE)

                if box_rect.collidepoint(x, y):
                    return box_x, box_y

        return None, None


    @staticmethod
    def draw_big_grid(color: tuple[int, int, int]):
        """
        Update the display surface by drawing the big grid of the game.

        Arguments:
            color: An RGB value of the grid color.
        """

        WIDTH = 6
        LENGTH = 9 * SQUARE_SIZE

        # Big grid:
        pygame.draw.rect(DISPLAY_SURF, color, (X_MARGIN + 3 * SQUARE_SIZE - 3, Y_MARGIN, WIDTH, LENGTH))
        pygame.draw.rect(DISPLAY_SURF, color, (X_MARGIN + 6 * SQUARE_SIZE - 3, Y_MARGIN, WIDTH, LENGTH))
        pygame.draw.rect(DISPLAY_SURF, color, (X_MARGIN, Y_MARGIN + 3 * SQUARE_SIZE - 3, LENGTH, WIDTH))
        pygame.draw.rect(DISPLAY_SURF, color, (X_MARGIN, Y_MARGIN + 6 * SQUARE_SIZE - 3, LENGTH, WIDTH))

        # Borders :
        pygame.draw.rect(DISPLAY_SURF, color, (X_MARGIN - 3, Y_MARGIN - 3, LENGTH + 6, LENGTH + 6), WIDTH)

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


    @staticmethod
    def draw_grid():
        """ Update the surface display by drawing all the small grids and the big grid. """

        # Sub-grids:
        SUB_WIDTH = 4
        SUB_LENGTH = 9 * SQUARE_SIZE

        for i in (1, 2, 4, 5, 7, 8):
            pygame.draw.rect(DISPLAY_SURF, SMALL_LINE_COLOR,
                             (X_MARGIN + i * SQUARE_SIZE - 2, Y_MARGIN, SUB_WIDTH, SUB_LENGTH))
            pygame.draw.rect(DISPLAY_SURF, SMALL_LINE_COLOR,
                             (X_MARGIN, Y_MARGIN + i * SQUARE_SIZE - 2, SUB_LENGTH, SUB_WIDTH))

        GameUI.draw_big_grid(BIG_LINE_COLOR)

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


    @staticmethod
    def draw_board():
        """ Update the surface display by drawing the background and the full game board. """

        DISPLAY_SURF.fill(BG_COLOR)

        GameUI.draw_grid()

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


    @staticmethod
    def cover_box(box_x: int, box_y: int, transparent: bool = False):
        """ Covers the box at the given position fully or transparently.

        Arguments:
            box_x: Box row index.
            box_y: Bow column index.
            transparent: Weather to cover the box fully or transparently.
        """

        l, t = GameUI.top_left_coords_of_box(box_x, box_y)

        if not transparent:
            pygame.draw.rect(DISPLAY_SURF, BG_COLOR, (l + 3, t + 3, SQUARE_SIZE - 6, SQUARE_SIZE - 6))
        else:
            s = pygame.Surface((SQUARE_SIZE - 6, SQUARE_SIZE - 6), pygame.SRCALPHA)
            s.fill((BG_COLOR[0], BG_COLOR[1], BG_COLOR[2], 200))
            DISPLAY_SURF.blit(s, (l + 3, t + 3))

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


    def draw_sign_on_box(self, box_x: int, box_y: int, sign: str):
        """
        Update the display surface by drawing the given sign at the specified box row and column.

        Arguments:
            box_x: Box row index.
            box_y: Bow column index.
            sign: The sign to draw, X or O.
        """

        if box_x is None or box_y is None:
            return

        l, t = GameUI.top_left_coords_of_box(box_x, box_y)

        DISPLAY_SURF.blit(small_images[sign], (l + 2 + 5, t + 2 + 5))

        if not self.hinted_move:
            pygame.display.update()
            FPS_CLOCK.tick(FPS)


    def draw_sign_on_big_board(self, big_idx: int, sign: str):
        """
        Update the display surface by drawing the given sign on the specified board
        or dimming the board if it's tied.

        Arguments:
            big_idx: Board index.
            sign: The sign: X, O, or T.
        """

        # print(f"Drawing big {sign} on board: {big_idx}")
        self.wait_after_move()

        box_x, box_y = idx_to_rc[big_idx][1]

        l, t = self.top_left_coords_of_box(box_x, box_y)

        if self.opaque_on_board_completion and sign != 'T':
            pygame.draw.rect(DISPLAY_SURF, BG_COLOR, (l + 3, t + 3, 3 * SQUARE_SIZE - 6, 3 * SQUARE_SIZE - 6))

        else:
            s = pygame.Surface((3 * SQUARE_SIZE - 6, 3 * SQUARE_SIZE - 6), pygame.SRCALPHA)
            s.fill((BG_COLOR[0], BG_COLOR[1], BG_COLOR[2], 200))
            DISPLAY_SURF.blit(s, (l + 3, t + 3))

        if sign != 'T':
            DISPLAY_SURF.blit(big_images[sign], (l + 3 + 10, t + 3 + 10))

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


    @staticmethod
    def draw_subgrid_at_board(big_idx: int, color: tuple[int, int, int]):
        """
        Update the display surface by changing the color of the board at big index.

        Arguments:
              big_idx: Board index.
              color: An RGB value of the grid color.
        """

        box_x, box_y = idx_to_rc[big_idx][1]
        l, t = GameUI.top_left_coords_of_box(box_x, box_y)

        SUB_WIDTH = 4
        SUB_LENGTH = SQUARE_SIZE * 3

        for i in (1, 2):
            pygame.draw.rect(DISPLAY_SURF, color, (l + i * SQUARE_SIZE - 2, t, SUB_WIDTH, SUB_LENGTH))
            pygame.draw.rect(DISPLAY_SURF, color, (l, t + i * SQUARE_SIZE - 2, SUB_LENGTH, SUB_WIDTH))

        GameUI.draw_big_grid(BIG_LINE_COLOR)

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


__all__ = ['GameUI']
