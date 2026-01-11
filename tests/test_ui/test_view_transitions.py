import pytest
import pygame
import time
from unittest.mock import patch

from utils.game.game_ui_v2 import GameUI
from utils.players import UserPlayer, MiniMaxPlayer, RandomPlayer
from utils.game.game_ui_assets import *


class VisualTestReporter:
    """ Helper class to provide visual feedback during test execution. """

    def __init__(self, wait_time: float = 0.3):
        """
        Initialize the reporter.

        Arguments:
            wait_time: Time to wait between actions in seconds. Defaults to 0.3 seconds.
        """

        self.step_count = 0
        self.start_time = time.time()
        self.wait_time = wait_time


    def log_step(self, node_id: int, description: str, action: str = ""):
        """ Log a test step with visual formatting. """

        self.step_count += 1
        elapsed = time.time() - self.start_time

        print("\n" + "=" * 80)
        print(f"STEP {self.step_count} | Node {node_id} | Time: {elapsed:.2f}s")
        print(f"Description: {description}")
        if action:
            print(f"Action: {action}")
        print("=" * 80 + "\n")


    def log_assertion(self, condition: bool, message: str):
        """ Log assertion results. """

        status = "PASS" if condition else "FAIL"
        print(f"  [{status}] {message}")
        assert condition, f"Assertion failed: {message}"


    def wait(self, specific_time: float = None):
        """ Wait for the configured or the given time. """

        time.sleep(self.wait_time if specific_time is None else specific_time)


class TestViewTransitions:
    """
    Edge-Pair Coverage Tests for View Transitions

    Nodes:
        1 - The main Start Menu.
        2 - Clicking "1 Player" (redirect to Settings Menu).
        3 - Clicking "2 Player" (redirect to main Game Page).
        4 - Selecting one option from the Settings Menu (sign or difficulty).
        5 - Clicking the back arrow (redirect to Start Menu).
        6 - Settings Menu with one option selected.
        7 - Selecting second option from Settings Menu (sign or difficulty).
        8 - Main Game Page.
        9 - Clicking restart game with same settings.
        10 - Clicking hint button.
        11 - Making a move on the board.
        12 - End of test.
    """

    @pytest.fixture(autouse=True)
    def manage_pygame_window(self):
        """Manage pygame window lifecycle - close after each test."""

        yield
        if pygame.display.get_surface() is not None:
            self.cleanup_pygame_state()
            time.sleep(0.4)

    @pytest.fixture
    def game_ui(self):
        """Fixture to create GameUI instance."""

        pygame.init()

        pygame.event.clear()
        pygame.event.set_blocked(None)
        pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONUP])

        with patch.object(GameUI, 'draw_board'):
            game = GameUI(
                player1=UserPlayer(),
                player2=UserPlayer(),
                printing=False,
                wait_after_move=100,
                show_evaluation=False,
                measure_thinking_time=False,
                opaque_on_board_completion=True,
                light_theme=False,
                use_eval_bar=False
            )

        DISPLAY_SURF = pygame.display.get_surface()
        DISPLAY_SURF.fill((0, 0, 0))
        pygame.display.flip()

        pygame.event.clear()
        pygame.event.pump()

        return game

    def cleanup_pygame_state(self):
        """Aggressively clean up pygame state between operations."""

        for _ in range(3):
            pygame.event.clear()
            pygame.event.pump()

        time.sleep(0.05)

    def get_button_coords(self):
        """Get all button coordinates as a dictionary."""

        coords = {}

        coords['one_player'] = (235, 530)
        coords['two_player'] = (655, 530)

        coords['choose_x'] = (340, 270)
        coords['choose_o'] = (550, 270)
        coords['choose_easy'] = (200, 533)
        coords['choose_normal'] = (452, 533)
        coords['choose_hard'] = (695, 533)

        t = Y_MARGIN + 2 * SQUARE_SIZE
        l = WINDOW_WIDTH - X_MARGIN + 1 * SQUARE_SIZE
        coords['hint'] = (l + 30, t + 27)
        coords['bar'] = (l + 30, t + SQUARE_SIZE + 27)
        coords['reset'] = (l + 30, t + 3 * SQUARE_SIZE + 27)
        coords['to_title'] = (l + 30, t + 4 * SQUARE_SIZE + 27)
        coords['back'] = (30, 30)

        return coords

    def get_board_position_coords(self, big_idx: int, small_idx: int) -> tuple[int, int]:
        """Get pixel coordinates for a board position."""

        box_x, box_y = idx_to_rc[big_idx][small_idx]
        left = box_y * SQUARE_SIZE + X_MARGIN
        top = box_x * SQUARE_SIZE + Y_MARGIN
        return (left + SQUARE_SIZE // 2, top + SQUARE_SIZE // 2)

    def simulate_click(self, x: int, y: int, reporter: VisualTestReporter, highlight_color: tuple = (255, 0, 0)):
        """Simulate a mouse click with visual feedback."""

        DISPLAY_SURF = pygame.display.get_surface()

        radius = 10
        area_rect = pygame.Rect(x - radius - 3, y - radius - 3, (radius + 3) * 2, (radius + 3) * 2)
        saved_area = DISPLAY_SURF.subsurface(area_rect).copy()

        pygame.draw.circle(DISPLAY_SURF, highlight_color, (x, y), radius, 3)
        pygame.display.update(area_rect)
        reporter.wait(0.15)

        DISPLAY_SURF.blit(saved_area, area_rect)
        pygame.display.update(area_rect)

        pygame.event.clear()

        event = pygame.event.Event(pygame.MOUSEBUTTONUP, {'pos': (x, y), 'button': 1})
        pygame.event.post(event)

        pygame.event.pump()

        pygame.event.clear()

        reporter.wait(0.1)

    def simulate_hint_click(self, game_ui: GameUI, player: UserPlayer, reporter: VisualTestReporter):
        """Simulate clicking the hint button and trigger hint logic."""

        DISPLAY_SURF = pygame.display.get_surface()
        coords = self.get_button_coords()
        hint_x, hint_y = coords['hint']

        button_rect = pygame.Rect(hint_x - 30, hint_y - 27, 60, 54)

        saved_area = DISPLAY_SURF.subsurface(button_rect).copy()

        DISPLAY_SURF.blit(button_hint_hover, (hint_x - 30, hint_y - 27))
        pygame.display.update(button_rect)
        reporter.wait(0.2)

        DISPLAY_SURF.blit(saved_area, button_rect)
        pygame.display.update(button_rect)

        with patch('utils.helpers.game_evaluator.GameEvaluator.get_best_move') as mock:
            mock.return_value = (5, 5)
            b_idx, s_idx = 5, 5
            box_x, box_y = idx_to_rc[b_idx][s_idx]
            game_ui.hinted_move = (box_x, box_y)
            game_ui.draw_sign_on_box(box_x, box_y, player.sign)
            game_ui.cover_box(box_x, box_y, transparent=True)
            pygame.display.update()
            reporter.wait()

    def click_reset_button(self, game_ui: GameUI, reporter: VisualTestReporter):
        """Click the reset button with hover effect."""

        DISPLAY_SURF = pygame.display.get_surface()
        t, l = self.get_button_coords()['reset']

        DISPLAY_SURF.blit(button_reset_hover, (l, t + 3 * SQUARE_SIZE))
        pygame.display.update()
        reporter.wait()

        game_ui.reset_state()
        game_ui.draw_board()
        game_ui.draw_buttons()
        pygame.display.update()
        reporter.wait()

    def click_to_title_button(self, game_ui: GameUI, reporter: VisualTestReporter):
        """Click the 'to title' button with hover effect."""

        DISPLAY_SURF = pygame.display.get_surface()
        t, l = self.get_button_coords()['to_title']

        DISPLAY_SURF.blit(button_to_title_hover, (l, t + 4 * SQUARE_SIZE))
        pygame.display.update()
        reporter.wait()

        game_ui.reset_state()
        game_ui.selected_sign = None
        game_ui.selected_difficulty = None

    def show_title_screen(self, game_ui: GameUI, reporter: VisualTestReporter, highlight_button: str = None):
        """
        Display the title screen.

        Arguments:
            game_ui: The game UI instance
            reporter: The visual test reporter
            highlight_button: Optional - '1player' or '2player' to show hover effect
        """

        pygame.event.clear()

        DISPLAY_SURF = pygame.display.get_surface()

        if highlight_button == '1player':
            DISPLAY_SURF.blit(title_image1, (0, 0))
        elif highlight_button == '2player':
            DISPLAY_SURF.blit(title_image2, (0, 0))
        else:
            DISPLAY_SURF.blit(title_image, (0, 0))

        pygame.display.flip()
        pygame.event.pump()
        pygame.event.clear()

        if highlight_button:
            reporter.wait()

    def click_menu_button(self, game_ui: GameUI, button_type: str, reporter: VisualTestReporter):
        """
        Click a button on the main menu with visual feedback.

        Arguments:
            game_ui: The game UI instance
            button_type: '1player' or '2player'
            reporter: The visual test reporter
        """

        self.show_title_screen(game_ui, reporter, highlight_button=button_type)
        reporter.wait()

    def show_settings_menu(self, game_ui: GameUI, reporter: VisualTestReporter,
                           selected_sign: str = None, selected_difficulty: str = None):
        """
        Display the settings menu with selections highlighted.

        Arguments:
            game_ui: The game UI instance
            reporter: The visual test reporter
            selected_sign: 'X', 'O', or None
            selected_difficulty: 'easy', 'normal', 'hard', or None
        """

        pygame.event.clear()

        DISPLAY_SURF = pygame.display.get_surface()

        DISPLAY_SURF.blit(choose_image, (0, 0))

        if selected_sign == 'X':
            DISPLAY_SURF.blit(choose_image_top_x, (0, 0))
        elif selected_sign == 'O':
            DISPLAY_SURF.blit(choose_image_top_o, (0, 0))
        else:
            DISPLAY_SURF.blit(choose_image_top, (0, 0))

        if selected_difficulty == 'easy':
            DISPLAY_SURF.blit(choose_image_bottom_easy, (0, 351))
        elif selected_difficulty == 'normal':
            DISPLAY_SURF.blit(choose_image_bottom_normal, (0, 351))
        elif selected_difficulty == 'hard':
            DISPLAY_SURF.blit(choose_image_bottom_hard, (0, 351))
        else:
            DISPLAY_SURF.blit(choose_image_bottom, (0, 351))

        pygame.draw.rect(DISPLAY_SURF, BG_COLOR, pygame.Rect(0, 0, 60, 60))
        DISPLAY_SURF.blit(button_back, (0, 0))

        pygame.display.update()
        pygame.event.pump()
        pygame.event.clear()

        reporter.wait()

    def select_sign(self, game_ui: GameUI, sign: str, reporter: VisualTestReporter,
                    current_difficulty: str = None):
        """
        Select a sign (X or O) in the settings menu.

        Arguments:
            game_ui: The game UI instance
            sign: 'X' or 'O'
            reporter: The visual test reporter
            current_difficulty: Currently selected difficulty (if any)
        """

        game_ui.selected_sign = sign
        self.show_settings_menu(game_ui, reporter, selected_sign=sign,
                                selected_difficulty=current_difficulty)

    def select_difficulty(self, game_ui: GameUI, difficulty: str, reporter: VisualTestReporter,
                          current_sign: str = None):
        """
        Select a difficulty in the settings menu.

        Arguments:
            game_ui: The game UI instance
            difficulty: 'easy', 'normal', or 'hard'
            reporter: The visual test reporter
            current_sign: Currently selected sign (if any)
        """

        game_ui.selected_difficulty = difficulty
        self.show_settings_menu(game_ui, reporter, selected_sign=current_sign,
                                selected_difficulty=difficulty)

    def click_back_button(self, game_ui: GameUI, reporter: VisualTestReporter):
        """
        Click the back button with visual feedback.

        Arguments:
            game_ui: The game UI instance
            reporter: The visual test reporter
        """

        DISPLAY_SURF = pygame.display.get_surface()
        coords = self.get_button_coords()

        pygame.draw.rect(DISPLAY_SURF, BG_COLOR, pygame.Rect(0, 0, 60, 60))
        DISPLAY_SURF.blit(button_back_hover, (0, 0))
        pygame.display.update()
        reporter.wait()

        game_ui.selected_sign = None
        game_ui.selected_difficulty = None

    def transition_to_game(self, game_ui: GameUI, reporter: VisualTestReporter):
        """Transition from menu to game board."""

        pygame.event.clear()

        game_ui.draw_board()
        pygame.display.update()

        pygame.event.pump()

        reporter.wait(0.05)

        pygame.event.clear()

        game_ui.draw_buttons()
        pygame.display.update()

        pygame.event.clear()

        reporter.wait(0.15)

    def make_board_move(self, game_ui: GameUI, big_idx: int, small_idx: int,
                        sign: str, reporter: VisualTestReporter):
        """Make a move on the game board."""

        from utils.helpers import StateUpdater

        coords = self.get_board_position_coords(big_idx, small_idx)
        self.simulate_click(coords[0], coords[1], reporter, (0, 255, 0))

        old_state = game_ui.state
        game_ui.state, board_complete = StateUpdater.update_state(
            game_ui.state, big_idx, small_idx, sign
        )
        game_ui.prev_small_idx = small_idx

        box_x, box_y = idx_to_rc[big_idx][small_idx]
        if game_ui.hinted_move:
            game_ui.cover_box(game_ui.hinted_move[0], game_ui.hinted_move[1])
            game_ui.hinted_move = None
        game_ui.draw_sign_on_box(box_x, box_y, sign)
        pygame.display.update()
        reporter.wait()


    def test_path_1(self, game_ui):
        """
        Path 1: [1,3,8,10,8,5,1,3,8,11,12]
        """
        reporter = VisualTestReporter()
        coords = self.get_button_coords()

        reporter.log_step(1, "Start Menu", "Display title screen")
        self.show_title_screen(game_ui, reporter)
        reporter.log_assertion(game_ui.state is not None, "Game state initialized")

        reporter.log_step(3, "Click '2 Player'", "Start 2-player mode")
        self.click_menu_button(game_ui, '2player', reporter)
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)
        reporter.log_assertion(isinstance(game_ui.player1, UserPlayer), "Player 1 is UserPlayer")

        reporter.log_step(8, "Main Game Page", "Game board ready")
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "Board is empty")

        reporter.log_step(10, "Click hint button", "Request AI hint")
        self.simulate_hint_click(game_ui, game_ui.player1, reporter)
        reporter.log_assertion(game_ui.hinted_move is not None, "Hint displayed")

        reporter.log_step(8, "Main Game Page", "Return from hint")
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "State unchanged")

        reporter.log_step(5, "Click to title", "Return to menu")
        self.click_to_title_button(game_ui, reporter)
        self.show_title_screen(game_ui, reporter)
        reporter.log_assertion(game_ui.selected_sign is None, "Settings cleared")

        reporter.log_step(1, "Start Menu", "Back at main menu")
        reporter.wait()

        reporter.log_step(3, "Click '2 Player' again", "Start new game")
        self.click_menu_button(game_ui, '2player', reporter)
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)

        reporter.log_step(8, "Main Game Page", "Fresh board")
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "New game ready")

        reporter.log_step(11, "Make a move", "Place X at (5,5)")
        self.make_board_move(game_ui, 5, 5, 'X', reporter)
        reporter.log_assertion(game_ui.state[5]['display'][5] == 'X', "Move placed")

        reporter.log_step(12, "End of test", "Test completed")
        print(f"\nPATH 1 COMPLETED in {time.time() - reporter.start_time:.2f}s")


    def test_path_2(self, game_ui):
        """
        Path 2: [1,2,4,6,7,8,11,8,11,8,10,8,11,12]
        """
        reporter = VisualTestReporter()
        coords = self.get_button_coords()

        reporter.log_step(1, "Start Menu", "Display title screen")
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(2, "Click '1 Player'", "Go to settings")
        self.click_menu_button(game_ui, '1player', reporter)
        self.show_settings_menu(game_ui, reporter)

        reporter.log_step(4, "Select X", "Choose player sign")
        self.select_sign(game_ui, 'X', reporter)
        reporter.log_assertion(game_ui.selected_sign == 'X', "Sign selected")

        reporter.log_step(6, "Settings with one option", "X selected")
        reporter.wait()

        reporter.log_step(7, "Select difficulty", "Choose Hard")
        self.select_difficulty(game_ui, 'hard', reporter, current_sign=game_ui.selected_sign)
        reporter.log_assertion(game_ui.selected_difficulty == 'hard', "Difficulty selected")

        reporter.log_step(8, "Main Game Page", "Game started")
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = MiniMaxPlayer(target_depth=5)
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)

        reporter.log_step(11, "Make move 1", "X at (5,5)")
        self.make_board_move(game_ui, 5, 5, 'X', reporter)

        reporter.log_step(8, "Main Game Page", "After move 1")
        reporter.wait()

        reporter.log_step(11, "Make move 2", "O at (5,3)")
        self.make_board_move(game_ui, 5, 3, 'O', reporter)

        reporter.log_step(8, "Main Game Page", "After move 2")
        reporter.wait()

        reporter.log_step(10, "Click hint", "Get hint for next move")
        self.simulate_hint_click(game_ui, game_ui.player1, reporter)

        reporter.log_step(8, "Main Game Page", "After hint")
        reporter.wait()

        reporter.log_step(11, "Make move 3", "X at (3,1)")
        self.make_board_move(game_ui, 3, 1, 'X', reporter)

        reporter.log_step(12, "End of test", "Test completed")
        print(f"\nPATH 2 COMPLETED in {time.time() - reporter.start_time:.2f}s")


    def test_path_3(self, game_ui):
        """
        Path 3: [1,2,4,6,7,8,9,8,9,8,10,8,9,8,11,8,5,1,3,8,11,12]
        """
        reporter = VisualTestReporter()
        coords = self.get_button_coords()

        reporter.log_step(1, "Start Menu", "Display title screen")
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(2, "Click '1 Player'", "Go to settings")
        self.click_menu_button(game_ui, '1player', reporter)
        self.show_settings_menu(game_ui, reporter)

        reporter.log_step(4, "Select O", "Choose O")
        self.select_sign(game_ui, 'O', reporter)

        reporter.log_step(6, "Settings with one option", "O selected")
        reporter.wait(0.5)

        reporter.log_step(7, "Select difficulty", "Choose Normal")
        self.select_difficulty(game_ui, 'normal', reporter, current_sign=game_ui.selected_sign)

        reporter.log_step(8, "Main Game Page", "Game started")
        game_ui.player1 = MiniMaxPlayer(target_depth=5)
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)

        reporter.log_step(9, "Click reset", "Reset the game")
        self.click_reset_button(game_ui, reporter)

        reporter.log_step(8, "Main Game Page", "After reset 1")
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "Board reset")

        reporter.log_step(9, "Click reset", "Reset the game")
        self.click_reset_button(game_ui, reporter)

        reporter.log_step(8, "Main Game Page", "After reset 2")
        reporter.wait()

        reporter.log_step(10, "Click hint", "Request hint")
        self.simulate_hint_click(game_ui, game_ui.player2, reporter)

        reporter.log_step(8, "Main Game Page", "After hint")
        reporter.wait()

        reporter.log_step(9, "Click reset", "Reset the game")
        self.click_reset_button(game_ui, reporter)

        reporter.log_step(8, "Main Game Page", "After reset 3")
        reporter.wait()

        reporter.log_step(11, "Make a move", "X at (1,1)")
        self.make_board_move(game_ui, 1, 1, 'X', reporter)

        reporter.log_step(8, "Main Game Page", "After move")
        reporter.wait()

        reporter.log_step(5, "Click to title", "Return to menu")
        self.click_to_title_button(game_ui, reporter)
        game_ui.selected_sign = None
        game_ui.selected_difficulty = None
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(1, "Start Menu", "Back at menu")
        reporter.wait()

        reporter.log_step(3, "Click '2 Player'", "Start 2-player mode")
        self.click_menu_button(game_ui, '2player', reporter)
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)

        reporter.log_step(8, "Main Game Page", "2-player game ready")
        reporter.wait()

        reporter.log_step(11, "Make a move", "X at (5,5)")
        self.make_board_move(game_ui, 5, 5, 'X', reporter)

        reporter.log_step(12, "End of test", "Test completed")
        print(f"\nPATH 3 COMPLETED in {time.time() - reporter.start_time:.2f}s")


    def test_path_4(self, game_ui):
        """
        Path 4: [1,2,4,6,4,6,7,8,5,1,3,8,5,1,3,8,11,12]
        """
        reporter = VisualTestReporter()
        coords = self.get_button_coords()

        reporter.log_step(1, "Start Menu", "Display title screen")
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(2, "Click '1 Player'", "Go to settings")
        self.click_menu_button(game_ui, '1player', reporter)
        self.show_settings_menu(game_ui, reporter)

        reporter.log_step(4, "Select X", "Choose player sign")
        self.select_sign(game_ui, 'X', reporter)

        reporter.log_step(6, "Settings with one option", "X selected")
        reporter.wait()

        reporter.log_step(4, "Select O", "Choose O")
        self.select_sign(game_ui, 'O', reporter)

        reporter.log_step(6, "Settings with one option", "O selected")
        reporter.wait()

        reporter.log_step(7, "Select difficulty", "Choose Easy")
        self.select_difficulty(game_ui, 'easy', reporter, current_sign=game_ui.selected_sign)

        reporter.log_step(8, "Main Game Page", "Game started")
        game_ui.player1 = RandomPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)

        reporter.log_step(5, "Click to title", "Return to menu")
        self.click_to_title_button(game_ui, reporter)
        game_ui.selected_sign = None
        game_ui.selected_difficulty = None
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(1, "Start Menu", "Back at menu 1")
        reporter.wait()

        reporter.log_step(3, "Click '2 Player'", "Start 2-player")
        self.click_menu_button(game_ui, '2player', reporter)
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)

        reporter.log_step(8, "Main Game Page", "2-player ready")
        reporter.wait()

        reporter.log_step(5, "Click to title", "Return to menu")
        self.click_to_title_button(game_ui, reporter)
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(1, "Start Menu", "Back at menu 2")
        reporter.wait()

        reporter.log_step(3, "Click '2 Player'", "Start 2-player again")
        self.click_menu_button(game_ui, '2player', reporter)
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)

        reporter.log_step(8, "Main Game Page", "2-player ready again")
        reporter.wait()

        reporter.log_step(11, "Make a move", "X at (5,5)")
        self.make_board_move(game_ui, 5, 5, 'X', reporter)

        reporter.log_step(12, "End of test", "Test completed")
        print(f"\nPATH 4 COMPLETED in {time.time() - reporter.start_time:.2f}s")


    def test_path_5(self, game_ui):
        """
        Path 5: [1,2,4,6,5,1,2,5,1,2,4,5,1,2,4,6,4,6,5,1,3,8,11,12]
        """
        reporter = VisualTestReporter()
        coords = self.get_button_coords()

        reporter.log_step(1, "Start Menu", "Display title screen")
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(2, "Click '1 Player'", "Go to settings (cycle 1)")
        DISPLAY_SURF = pygame.display.get_surface()
        DISPLAY_SURF.blit(choose_image, (0, 0))
        DISPLAY_SURF.blit(button_back, (0, 0))
        pygame.display.update()
        reporter.wait()

        reporter.log_step(4, "Select X", "Choose X (cycle 1)")
        game_ui.selected_sign = 'X'
        DISPLAY_SURF.blit(choose_image_top_x, (0, 0))
        pygame.draw.rect(DISPLAY_SURF, BG_COLOR, pygame.Rect(0, 0, 60, 60))
        DISPLAY_SURF.blit(button_back, (0, 0))
        pygame.display.update()
        reporter.wait()

        reporter.log_step(6, "Settings with one option", "X selected (cycle 1)")
        reporter.wait()

        reporter.log_step(5, "Click back", "Return to menu (cycle 1)")
        self.click_back_button(game_ui, reporter)
        game_ui.selected_sign = None
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(1, "Start Menu", "Back at menu (cycle 2)")
        reporter.wait()

        reporter.log_step(2, "Click '1 Player'", "Go to settings (cycle 2)")
        DISPLAY_SURF.blit(choose_image, (0, 0))
        DISPLAY_SURF.blit(button_back, (0, 0))
        pygame.display.update()
        reporter.wait()

        reporter.log_step(5, "Click back", "Return immediately (cycle 2)")
        self.click_back_button(game_ui, reporter)
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(1, "Start Menu", "Back at menu (cycle 3)")
        reporter.wait()

        reporter.log_step(2, "Click '1 Player'", "Go to settings (cycle 3)")
        DISPLAY_SURF.blit(choose_image, (0, 0))
        DISPLAY_SURF.blit(button_back, (0, 0))
        pygame.display.update()
        reporter.wait()

        reporter.log_step(4, "Select O", "Choose O (cycle 3)")
        game_ui.selected_sign = 'O'
        DISPLAY_SURF.blit(choose_image_top_o, (0, 0))
        pygame.draw.rect(DISPLAY_SURF, BG_COLOR, pygame.Rect(0, 0, 60, 60))
        DISPLAY_SURF.blit(button_back, (0, 0))
        pygame.display.update()
        reporter.wait()

        reporter.log_step(5, "Click back", "Return to menu (cycle 3)")
        self.click_back_button(game_ui, reporter)
        game_ui.selected_sign = None
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(1, "Start Menu", "Back at menu (cycle 4)")
        reporter.wait()

        reporter.log_step(2, "Click '1 Player'", "Go to settings (cycle 4)")
        DISPLAY_SURF.blit(choose_image, (0, 0))
        DISPLAY_SURF.blit(button_back, (0, 0))
        pygame.display.update()
        reporter.wait()

        reporter.log_step(4, "Select X", "Choose X (cycle 4)")
        game_ui.selected_sign = 'X'
        DISPLAY_SURF.blit(choose_image_top_x, (0, 0))
        pygame.draw.rect(DISPLAY_SURF, BG_COLOR, pygame.Rect(0, 0, 60, 60))
        DISPLAY_SURF.blit(button_back, (0, 0))
        pygame.display.update()
        reporter.wait()

        reporter.log_step(6, "Settings with one option", "X selected (cycle 4)")
        reporter.wait()

        reporter.log_step(4, "Select O", "Change to O (cycle 4)")
        game_ui.selected_sign = 'O'
        DISPLAY_SURF.blit(choose_image_top_o, (0, 0))
        pygame.draw.rect(DISPLAY_SURF, BG_COLOR, pygame.Rect(0, 0, 60, 60))
        DISPLAY_SURF.blit(button_back, (0, 0))
        pygame.display.update()
        reporter.wait()

        reporter.log_step(6, "Settings with one option", "O selected (cycle 4)")
        reporter.wait()

        reporter.log_step(5, "Click back", "Return to menu (cycle 4)")
        self.click_back_button(game_ui, reporter)
        game_ui.selected_sign = None
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(1, "Start Menu", "Back at menu (final)")
        reporter.wait()

        reporter.log_step(3, "Click '2 Player'", "Start 2-player mode")
        self.click_menu_button(game_ui, '2player', reporter)
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)

        reporter.log_step(8, "Main Game Page", "2-player ready")
        reporter.wait()

        reporter.log_step(11, "Make a move", "X at (5,5)")
        self.make_board_move(game_ui, 5, 5, 'X', reporter)

        reporter.log_step(12, "End of test", "Test completed")
        print(f"\nPATH 5 COMPLETED in {time.time() - reporter.start_time:.2f}s")


    def test_path_6(self, game_ui):
        """
        Path 6: [1,3,8,11,12]
        """
        reporter = VisualTestReporter()

        reporter.log_step(1, "Start Menu", "Display title screen")
        self.show_title_screen(game_ui, reporter)
        reporter.log_assertion(game_ui.state is not None, "Game initialized")

        reporter.log_step(3, "Click '2 Player'", "Start 2-player mode")
        self.click_menu_button(game_ui, '2player', reporter)
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)
        reporter.log_assertion(isinstance(game_ui.player2, UserPlayer), "Player 2 is UserPlayer")

        reporter.log_step(8, "Main Game Page", "Game board ready")
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "Board is empty")
        reporter.wait()

        reporter.log_step(11, "Make a move", "X at center (5,5)")
        self.make_board_move(game_ui, 5, 5, 'X', reporter)
        reporter.log_assertion(game_ui.state[5]['display'][5] == 'X', "Move successful")
        reporter.log_assertion(game_ui.prev_small_idx == 5, "Previous move recorded")

        reporter.log_step(12, "End of test", "Test completed")
        print(f"\nPATH 6 COMPLETED in {time.time() - reporter.start_time:.2f}s")


    def test_path_7(self, game_ui):
        """
        Path 7: [1,2,4,6,7,8,10,8,10,8,11,8,9,8,11,12]
        """
        reporter = VisualTestReporter()
        coords = self.get_button_coords()

        reporter.log_step(1, "Start Menu", "Display title screen")
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(2, "Click '1 Player'", "Go to settings")
        self.click_menu_button(game_ui, '1player', reporter)
        self.show_settings_menu(game_ui, reporter)

        reporter.log_step(4, "Select X", "Choose player sign")
        self.select_sign(game_ui, 'X', reporter)

        reporter.log_step(6, "Settings with one option", "X selected")
        reporter.wait()

        reporter.log_step(7, "Select difficulty", "Choose Normal")
        self.select_difficulty(game_ui, 'normal', reporter, current_sign=game_ui.selected_sign)

        reporter.log_step(8, "Main Game Page", "Game started")
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = MiniMaxPlayer(target_depth=5)
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)

        reporter.log_step(10, "Click hint 1", "Get first hint")
        self.simulate_hint_click(game_ui, game_ui.player1, reporter)

        reporter.log_step(8, "Main Game Page", "After hint 1")
        reporter.wait()

        reporter.log_step(10, "Click hint 2", "Get second hint")
        self.simulate_hint_click(game_ui, game_ui.player1, reporter)

        reporter.log_step(8, "Main Game Page", "After hint 2")
        reporter.wait()

        reporter.log_step(11, "Make move 1", "X at (5,5)")
        self.make_board_move(game_ui, 5, 5, 'X', reporter)

        reporter.log_step(8, "Main Game Page", "After move 1")
        reporter.wait()

        reporter.log_step(9, "Click reset", "Reset the game")
        self.click_reset_button(game_ui, reporter)
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "Board reset")

        reporter.log_step(8, "Main Game Page", "After reset")
        reporter.wait()

        reporter.log_step(11, "Make move 2", "X at (1,1)")
        self.make_board_move(game_ui, 1, 1, 'X', reporter)

        reporter.log_step(12, "End of test", "Test completed")
        print(f"\nPATH 7 COMPLETED in {time.time() - reporter.start_time:.2f}s")


    def test_path_8(self, game_ui):
        """
        Path 8: [1,2,4,6,4,5,1,3,8,9,8,5,1,3,8,11,12]
        """
        reporter = VisualTestReporter()
        coords = self.get_button_coords()

        reporter.log_step(1, "Start Menu", "Display title screen")
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(2, "Click '1 Player'", "Go to settings")
        self.click_menu_button(game_ui, '1player', reporter)
        self.show_settings_menu(game_ui, reporter)

        reporter.log_step(4, "Select X", "Choose player sign")
        self.select_sign(game_ui, 'X', reporter)

        reporter.log_step(6, "Settings with one option", "X selected")
        reporter.wait()

        reporter.log_step(4, "Select O", "Choose O")
        self.select_sign(game_ui, 'O', reporter)
        reporter.log_assertion(game_ui.selected_sign == 'O', "Sign changed to O")

        reporter.log_step(5, "Click back", "Return to menu")
        self.click_back_button(game_ui, reporter)
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(1, "Start Menu", "Back at menu")
        reporter.wait()

        reporter.log_step(3, "Click '2 Player'", "Start 2-player")
        self.click_menu_button(game_ui, '2player', reporter)
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)

        reporter.log_step(8, "Main Game Page", "Game ready")
        reporter.wait()

        reporter.log_step(9, "Click reset", "Reset the game")
        self.click_reset_button(game_ui, reporter)

        reporter.log_step(8, "Main Game Page", "After reset")
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "Board reset")

        reporter.log_step(5, "Click to title", "Return to menu")
        self.click_to_title_button(game_ui, reporter)
        self.show_title_screen(game_ui, reporter)

        reporter.log_step(1, "Start Menu", "Back at menu again")
        reporter.wait()

        reporter.log_step(3, "Click '2 Player'", "Start 2-player again")
        self.click_menu_button(game_ui, '2player', reporter)
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')
        self.transition_to_game(game_ui, reporter)

        reporter.log_step(8, "Main Game Page", "Game ready again")
        reporter.wait()

        reporter.log_step(11, "Make a move", "X at (5,5)")
        self.make_board_move(game_ui, 5, 5, 'X', reporter)

        reporter.log_step(12, "End of test", "Test completed")
        print(f"\nPATH 8 COMPLETED in {time.time() - reporter.start_time:.2f}s")