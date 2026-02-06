import time

from .ui_test_utils import BaseUITest, VisualTestReporter, GameThread
from utils.game.game_ui_v2 import GameUI
from utils.players import UserPlayer


class TestViewTransitions(BaseUITest):
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

    def wait_for_title_screen(self, game_ui: GameUI, reporter: VisualTestReporter,
                              timeout: float = 5.0) -> bool:
        """Wait until the title screen is being displayed."""
        return self.wait_for_state_condition(
            game_ui,
            lambda gui: gui.selected_sign is None and gui.selected_difficulty is None,
            "Title screen displayed",
            timeout=timeout
        )

    def wait_for_game_board_ready(self, game_ui: GameUI, reporter: VisualTestReporter,
                                  timeout: float = 5.0) -> bool:
        """Wait until the game board is ready (state is reset and board is drawn)."""
        return self.wait_for_state_condition(
            game_ui,
            lambda gui: gui.state is not None and gui.state[0]['display'][1] == '-',
            "Game board ready",
            timeout=timeout
        )

    def wait_for_settings_screen(self, game_ui: GameUI, reporter: VisualTestReporter,
                                 timeout: float = 5.0) -> bool:
        """Wait a short moment for the settings screen to render."""
        reporter.wait(0.1)
        return True

    def wait_for_sign_selected(self, game_ui: GameUI, sign: str,
                               reporter: VisualTestReporter, timeout: float = 5.0) -> bool:
        """Wait until the selected sign is set on the game UI."""
        return self.wait_for_state_condition(
            game_ui,
            lambda gui: gui.selected_sign == sign,
            f"Sign '{sign}' selected",
            timeout=timeout
        )

    def wait_for_difficulty_selected(self, game_ui: GameUI, difficulty: str,
                                     reporter: VisualTestReporter,
                                     timeout: float = 5.0) -> bool:
        """Wait until the selected difficulty is set on the game UI."""
        return self.wait_for_state_condition(
            game_ui,
            lambda gui: gui.selected_difficulty == difficulty,
            f"Difficulty '{difficulty}' selected",
            timeout=timeout
        )

    def wait_for_reset_complete(self, game_ui: GameUI, reporter: VisualTestReporter,
                                timeout: float = 5.0) -> bool:
        """Wait until a reset has completed (board is empty again)."""
        return self.wait_for_state_condition(
            game_ui,
            lambda gui: gui.state[0]['display'].count('-') == 9
                        and gui.prev_move_made is None
                        or gui.state[0]['display'].count('-') == 9
                        and gui.prev_small_idx is None,
            "Reset complete",
            timeout=timeout
        )

    def wait_for_hint_displayed(self, game_ui: GameUI, reporter: VisualTestReporter,
                                timeout: float = 10.0) -> bool:
        """Wait until a hint is displayed."""
        return self.wait_for_state_condition(
            game_ui,
            lambda gui: gui.hinted_move is not None,
            "Hint displayed",
            timeout=timeout
        )

    def click_title_button(self, button_name: str, reporter: VisualTestReporter):
        """Click a button on the title/settings screen by name."""
        coords = self.get_button_coords()
        key_map = {
            '1player': 'one_player',
            '2player': 'two_player',
            'choose_x': 'choose_x',
            'choose_o': 'choose_o',
            'easy': 'choose_easy',
            'normal': 'choose_normal',
            'hard': 'choose_hard',
            'back': 'back',
        }
        key = key_map.get(button_name, button_name)
        x, y = coords[key]
        reporter.log_step(
            f"Click '{button_name}' button",
            action=f"post MOUSEBUTTONUP at ({x}, {y})"
        )
        self.post_click_event(x, y, reporter)

    def click_game_button(self, button_name: str, reporter: VisualTestReporter):
        """Click a button on the game page (hint, bar, reset, to_title)."""
        coords = self.get_button_coords()
        x, y = coords[button_name]
        reporter.log_step(
            f"Click '{button_name}' game button",
            action=f"post MOUSEBUTTONUP at ({x}, {y})"
        )
        self.post_click_event(x, y, reporter)

    def test_path_1(self, game_ui, game_thread):
        """
        Path 1: [1,3,8,10,8,5,1,3,8,11,12]
        """
        reporter = VisualTestReporter()

        # [1] Start Menu
        reporter.log_step("Start Menu", "Display title screen", node_id=1)
        game_ui.reset = False
        game_thread.start()
        reporter.wait(0.5)
        reporter.log_assertion(game_ui.state is not None, "Game state initialized")

        # [3] Click '2 Player' -> Game Page
        reporter.log_step("Click '2 Player'", "Start 2-player mode", node_id=3)
        self.click_title_button('2player', reporter)
        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "Game board is ready")
        reporter.wait(0.5)

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "Game board ready", node_id=8)
        reporter.log_assertion(isinstance(game_ui.player1, UserPlayer), "Player 1 is UserPlayer")
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "Board is empty")

        # [10] Click hint button
        reporter.log_step("Click hint button", "Request AI hint", node_id=10)
        self.click_game_button('hint', reporter)
        hint_shown = self.wait_for_hint_displayed(game_ui, reporter, timeout=10.0)
        reporter.log_assertion(hint_shown, "Hint displayed")
        reporter.wait(0.5)

        # [8] Main Game Page (after hint)
        reporter.log_step("Main Game Page", "Return from hint", node_id=8)
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "State unchanged after hint")

        # [5] Click to title -> Return to menu
        reporter.log_step("Click to title", "Return to menu", node_id=5)
        self.click_game_button('to_title', reporter)
        reporter.wait(0.5)

        # [1] Start Menu
        reporter.log_step("Start Menu", "Back at main menu", node_id=1)
        reporter.log_assertion(game_ui.selected_sign is None, "Settings cleared")
        reporter.wait(0.5)

        # [3] Click '2 Player' again
        reporter.log_step("Click '2 Player' again", "Start new game", node_id=3)
        self.click_title_button('2player', reporter)
        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "New game board ready")
        reporter.wait(0.5)

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "Fresh board", node_id=8)
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "New game ready")

        # [11] Make a move: X at (5,5)
        reporter.log_step("Make a move", "Place X at (5,5)", node_id=11)
        self.post_move_click(5, 5, reporter)
        confirmed = self.wait_for_move_applied(game_ui, 5, 5, 'X', timeout=5.0)
        reporter.log_assertion(confirmed, "Move X at (5,5) placed")

        # [12] End of test
        reporter.log_step("End of test", "Test completed", node_id=12)
        print(f"\nPATH 1 COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_path_2(self, game_ui, game_thread):
        """
        Path 2: [1,2,4,6,7,8,11,8,11,8,10,8,11,12]
        """
        reporter = VisualTestReporter()

        # [1] Start Menu
        reporter.log_step("Start Menu", "Display title screen", node_id=1)
        game_ui.reset = False
        game_thread.start()
        reporter.wait(0.5)

        # [2] Click '1 Player' -> Settings
        reporter.log_step("Click '1 Player'", "Go to settings", node_id=2)
        self.click_title_button('1player', reporter)
        self.wait_for_settings_screen(game_ui, reporter)

        # [4] Select X
        reporter.log_step("Select X", "Choose player sign", node_id=4)
        self.click_title_button('choose_x', reporter)


        # [6] Settings with one option


        # [7] Select difficulty: Hard
        reporter.log_step("Select difficulty", "Choose Hard", node_id=7)
        self.click_title_button('hard', reporter)

        selected = self.wait_for_sign_selected(game_ui, 'X', reporter)
        reporter.log_assertion(selected, "Sign X selected")
        reporter.log_step("Settings with one option", "X selected", node_id=6)
        reporter.wait(0.3)
        diff_selected = self.wait_for_difficulty_selected(game_ui, 'hard', reporter)
        reporter.log_assertion(diff_selected, "Difficulty 'hard' selected")

        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "Game board ready after settings")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "Game started", node_id=8)
        reporter.wait(0.5)

        # [11] Make move
        reporter.log_step("Make move 1", "X at (5,5)", node_id=11)
        self.post_move_click(5, 5, reporter)
        confirmed = self.wait_for_move_applied(game_ui, 5, 5, 'X', timeout=5.0)
        reporter.log_assertion(confirmed, "Move 1: X at (5,5) applied")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "After move 1, waiting for AI", node_id=8)
        reporter.wait(2.0)

        # [11] Make move
        reporter.log_step("Make move 2", "User makes second move", node_id=11)
        moved = False
        deadline = time.time() + 10.0
        while not moved and time.time() < deadline:
            target_board = game_ui.prev_small_idx
            if target_board is not None:
                for cell in range(1, 10):
                    if game_ui.state[target_board]['display'][cell] == '-':
                        self.post_move_click(target_board, cell, reporter)
                        confirmed = self.wait_for_move_applied(
                            game_ui, target_board, cell, 'X', timeout=5.0
                        )
                        if confirmed:
                            reporter.log_assertion(True, f"Move 2: X at ({target_board},{cell}) applied")
                            moved = True
                            break
            else:
                for b in range(1, 10):
                    if game_ui.state[0]['display'][b] == '-':
                        for cell in range(1, 10):
                            if game_ui.state[b]['display'][cell] == '-':
                                self.post_move_click(b, cell, reporter)
                                confirmed = self.wait_for_move_applied(
                                    game_ui, b, cell, 'X', timeout=5.0
                                )
                                if confirmed:
                                    reporter.log_assertion(
                                        True, f"Move 2: X at ({b},{cell}) applied"
                                    )
                                    moved = True
                                    break
                    if moved:
                        break
            if not moved:
                reporter.wait(0.2)
        reporter.log_assertion(moved, "Move 2 was successfully made")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "After move 2", node_id=8)
        reporter.wait(2.0)

        # [10] Click hint
        reporter.log_step("Click hint", "Get hint for next move", node_id=10)
        self.click_game_button('hint', reporter)
        hint_shown = self.wait_for_hint_displayed(game_ui, reporter, timeout=10.0)
        reporter.log_assertion(hint_shown, "Hint displayed")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "After hint", node_id=8)
        reporter.wait(0.5)

        # [11] Make move
        reporter.log_step("Make move 3", "User makes third move", node_id=11)
        moved = False
        deadline = time.time() + 10.0
        while not moved and time.time() < deadline:
            target_board = game_ui.prev_small_idx
            if target_board is not None:
                for cell in range(1, 10):
                    if game_ui.state[target_board]['display'][cell] == '-':
                        self.post_move_click(target_board, cell, reporter)
                        confirmed = self.wait_for_move_applied(
                            game_ui, target_board, cell, 'X', timeout=5.0
                        )
                        if confirmed:
                            reporter.log_assertion(True, f"Move 3: X at ({target_board},{cell}) applied")
                            moved = True
                            break
            else:
                for b in range(1, 10):
                    if game_ui.state[0]['display'][b] == '-':
                        for cell in range(1, 10):
                            if game_ui.state[b]['display'][cell] == '-':
                                self.post_move_click(b, cell, reporter)
                                confirmed = self.wait_for_move_applied(
                                    game_ui, b, cell, 'X', timeout=5.0
                                )
                                if confirmed:
                                    reporter.log_assertion(
                                        True, f"Move 3: X at ({b},{cell}) applied"
                                    )
                                    moved = True
                                    break
                    if moved:
                        break
            if not moved:
                reporter.wait(0.2)
        reporter.log_assertion(moved, "Move 3 was successfully made")

        # [12] End of test
        reporter.log_step("End of test", "Test completed", node_id=12)
        print(f"\nPATH 2 COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_path_3(self, game_ui, game_thread):
        """
        Path 3: [1,2,4,6,7,8,9,8,9,8,10,8,9,8,11,8,5,1,3,8,11,12]
        """
        reporter = VisualTestReporter()

        # [1] Start Menu
        reporter.log_step("Start Menu", "Display title screen", node_id=1)
        game_ui.reset = False
        game_thread.start()
        reporter.wait(0.5)

        # [2] Click '1 Player'
        reporter.log_step("Click '1 Player'", "Go to settings", node_id=2)
        self.click_title_button('1player', reporter)
        self.wait_for_settings_screen(game_ui, reporter)

        # [4] Select O
        reporter.log_step("Select O", "Choose O", node_id=4)
        self.click_title_button('choose_o', reporter)

        # [6] Settings with one option


        # [7] Select difficulty: Normal
        reporter.log_step("Select difficulty", "Choose Normal", node_id=7)
        self.click_title_button('normal', reporter)

        selected = self.wait_for_sign_selected(game_ui, 'O', reporter)
        reporter.log_assertion(selected, "Sign O selected")
        reporter.log_step("Settings with one option", "O selected", node_id=6)
        reporter.wait(0.5)
        diff_selected = self.wait_for_difficulty_selected(game_ui, 'normal', reporter)
        reporter.log_assertion(diff_selected, "Difficulty 'normal' selected")

        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "Game board ready")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "Game started", node_id=8)
        reporter.wait(0.5)

        # [9] Click reset
        reporter.log_step("Click reset", "Reset the game", node_id=9)
        self.click_game_button('reset', reporter)
        reset_done = self.wait_for_reset_complete(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(reset_done, "Board reset after first reset")

        # [8] Main Game Page (after reset 1)
        reporter.log_step("Main Game Page", "After reset 1", node_id=8)
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "Board is empty")
        reporter.wait(0.5)

        # [9] Click reset again
        reporter.log_step("Click reset", "Reset the game again", node_id=9)
        self.click_game_button('reset', reporter)
        reset_done = self.wait_for_reset_complete(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(reset_done, "Board reset after second reset")

        # [8] Main Game Page (after reset 2)
        reporter.log_step("Main Game Page", "After reset 2", node_id=8)
        reporter.wait(0.5)

        # [10] Click hint
        reporter.log_step("Click hint", "Request hint", node_id=10)
        self.click_game_button('hint', reporter)
        hint_shown = self.wait_for_hint_displayed(game_ui, reporter, timeout=10.0)
        reporter.log_assertion(hint_shown, "Hint displayed")

        # [8] Main Game Page (after hint)
        reporter.log_step("Main Game Page", "After hint", node_id=8)
        reporter.wait(0.5)

        # [9] Click reset
        reporter.log_step("Click reset", "Reset the game", node_id=9)
        self.click_game_button('reset', reporter)
        reset_done = self.wait_for_reset_complete(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(reset_done, "Board reset after third reset")

        # [8] Main Game Page (after reset 3)
        reporter.log_step("Main Game Page", "After reset 3", node_id=8)
        reporter.wait(0.5)

        # [11] Make a move
        ai_moved = self.wait_for_state_condition(
            game_ui,
            lambda gui: gui.prev_move_made is not None,
            "AI made first move after reset",
            timeout=10.0
        )
        if ai_moved:
            reporter.log_step("Make a move", "O move after AI", node_id=11)
            moved = False
            deadline = time.time() + 10.0
            while not moved and time.time() < deadline:
                target_board = game_ui.prev_small_idx
                if target_board is not None:
                    for cell in range(1, 10):
                        if game_ui.state[target_board]['display'][cell] == '-':
                            self.post_move_click(target_board, cell, reporter)
                            confirmed = self.wait_for_move_applied(
                                game_ui, target_board, cell, 'O', timeout=5.0
                            )
                            if confirmed:
                                reporter.log_assertion(True, f"Move: O at ({target_board},{cell}) applied")
                                moved = True
                                break
                else:
                    for b in range(1, 10):
                        if game_ui.state[0]['display'][b] == '-':
                            for cell in range(1, 10):
                                if game_ui.state[b]['display'][cell] == '-':
                                    self.post_move_click(b, cell, reporter)
                                    confirmed = self.wait_for_move_applied(
                                        game_ui, b, cell, 'O', timeout=5.0
                                    )
                                    if confirmed:
                                        reporter.log_assertion(
                                            True, f"Move: O at ({b},{cell}) applied"
                                        )
                                        moved = True
                                        break
                        if moved:
                            break
                if not moved:
                    reporter.wait(0.2)
            reporter.log_assertion(moved, "User move was successfully made")
        else:
            reporter.log_assertion(False, "AI should have moved first")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "After move", node_id=8)
        reporter.wait(0.5)

        # [5] Click to title
        reporter.log_step("Click to title", "Return to menu", node_id=5)
        self.click_game_button('to_title', reporter)
        reporter.wait(0.5)

        # [1] Start Menu
        reporter.log_step("Start Menu", "Back at menu", node_id=1)
        reporter.wait(0.5)

        # [3] Click '2 Player'
        reporter.log_step("Click '2 Player'", "Start 2-player mode", node_id=3)
        self.click_title_button('2player', reporter)
        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "2-player game board ready")
        reporter.wait(0.5)

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "2-player game ready", node_id=8)
        reporter.wait(0.3)

        # [11] Make a move
        reporter.log_step("Make a move", "X at (5,5)", node_id=11)
        self.post_move_click(5, 5, reporter)
        confirmed = self.wait_for_move_applied(game_ui, 5, 5, 'X', timeout=5.0)
        reporter.log_assertion(confirmed, "Move X at (5,5) placed")

        # [12] End of test
        reporter.log_step("End of test", "Test completed", node_id=12)
        print(f"\nPATH 3 COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_path_4(self, game_ui, game_thread):
        """
        Path 4: [1,2,4,6,4,6,7,8,5,1,3,8,5,1,3,8,11,12]
        """
        reporter = VisualTestReporter()

        # [1] Start Menu
        reporter.log_step("Start Menu", "Display title screen", node_id=1)
        game_ui.reset = False
        game_thread.start()
        reporter.wait(0.5)

        # [2] Click '1 Player'
        reporter.log_step("Click '1 Player'", "Go to settings", node_id=2)
        self.click_title_button('1player', reporter)
        self.wait_for_settings_screen(game_ui, reporter)

        # [4] Select X
        reporter.log_step("Select X", "Choose player sign", node_id=4)
        self.click_title_button('choose_x', reporter)

        # [6] Settings with one option
        reporter.log_step("Settings with one option", "X selected", node_id=6)
        reporter.wait(0.3)

        # [4] Select O
        reporter.log_step("Select O", "Choose O", node_id=4)
        self.click_title_button('choose_o', reporter)

        # [6] Settings with one option


        # [7] Select difficulty: Easy
        reporter.log_step("Select difficulty", "Choose Easy", node_id=7)
        self.click_title_button('easy', reporter)

        selected = self.wait_for_sign_selected(game_ui, 'O', reporter)
        reporter.log_assertion(selected, "Sign changed to O")
        reporter.log_step("Settings with one option", "O selected", node_id=6)
        reporter.wait(0.3)
        diff_selected = self.wait_for_difficulty_selected(game_ui, 'easy', reporter)
        reporter.log_assertion(diff_selected, "Difficulty 'easy' selected")

        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "Game board ready")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "Game started", node_id=8)
        reporter.wait(0.5)

        # [5] Click to title
        reporter.log_step("Click to title", "Return to menu", node_id=5)
        self.click_game_button('to_title', reporter)
        reporter.wait(0.5)

        # [1] Start Menu
        reporter.log_step("Start Menu", "Back at menu 1", node_id=1)
        reporter.wait(0.5)

        # [3] Click '2 Player'
        reporter.log_step("Click '2 Player'", "Start 2-player", node_id=3)
        self.click_title_button('2player', reporter)
        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "2-player game board ready")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "2-player ready", node_id=8)
        reporter.wait(0.3)

        # [5] Click to title
        reporter.log_step("Click to title", "Return to menu", node_id=5)
        self.click_game_button('to_title', reporter)
        reporter.wait(0.5)

        # [1] Start Menu
        reporter.log_step("Start Menu", "Back at menu 2", node_id=1)
        reporter.wait(0.5)

        # [3] Click '2 Player'
        reporter.log_step("Click '2 Player'", "Start 2-player again", node_id=3)
        self.click_title_button('2player', reporter)
        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "2-player game board ready again")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "2-player ready again", node_id=8)
        reporter.wait(0.3)

        # [11] Make a move
        reporter.log_step("Make a move", "X at (5,5)", node_id=11)
        self.post_move_click(5, 5, reporter)
        confirmed = self.wait_for_move_applied(game_ui, 5, 5, 'X', timeout=5.0)
        reporter.log_assertion(confirmed, "Move X at (5,5) placed")

        # [12] End of test
        reporter.log_step("End of test", "Test completed", node_id=12)
        print(f"\nPATH 4 COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_path_5(self, game_ui, game_thread):
        """
        Path 5: [1,2,4,6,5,1,2,5,1,2,4,5,1,2,4,6,4,6,5,1,3,8,11,12]
        """
        reporter = VisualTestReporter()

        # [1] Start Menu
        reporter.log_step("Start Menu", "Display title screen", node_id=1)
        game_ui.reset = False
        game_thread.start()
        reporter.wait(0.5)

        # [2] Click '1 Player'
        reporter.log_step("Click '1 Player'", "Go to settings (cycle 1)", node_id=2)
        self.click_title_button('1player', reporter)
        self.wait_for_settings_screen(game_ui, reporter)

        # [4] Select X
        reporter.log_step("Select X", "Choose X (cycle 1)", node_id=4)
        self.click_title_button('choose_x', reporter)

        # [6] Settings with one option
        reporter.log_step("Settings with one option", "X selected (cycle 1)", node_id=6)
        reporter.wait(0.3)

        # [5] Click back
        reporter.log_step("Click back", "Return to menu (cycle 1)", node_id=5)
        self.click_title_button('back', reporter)
        reporter.wait(0.5)

        # [1] Start Menu
        reporter.log_step("Start Menu", "Back at menu (cycle 2)", node_id=1)
        reporter.wait(0.5)

        # [2] Click '1 Player'
        reporter.log_step("Click '1 Player'", "Go to settings (cycle 2)", node_id=2)
        self.click_title_button('1player', reporter)
        self.wait_for_settings_screen(game_ui, reporter)

        # [5] Click back
        reporter.log_step("Click back", "Return immediately (cycle 2)", node_id=5)
        self.click_title_button('back', reporter)
        reporter.wait(0.5)

        # [1] Start Menu
        reporter.log_step("Start Menu", "Back at menu (cycle 3)", node_id=1)
        reporter.wait(0.5)

        # [2] Click '1 Player'
        reporter.log_step("Click '1 Player'", "Go to settings (cycle 3)", node_id=2)
        self.click_title_button('1player', reporter)
        self.wait_for_settings_screen(game_ui, reporter)

        # [4] Select O
        reporter.log_step("Select O", "Choose O (cycle 3)", node_id=4)
        self.click_title_button('choose_o', reporter)

        # [5] Click back
        reporter.log_step("Click back", "Return to menu (cycle 3)", node_id=5)
        self.click_title_button('back', reporter)
        reporter.wait(0.5)

        # [1] Start Menu
        reporter.log_step("Start Menu", "Back at menu (cycle 4)", node_id=1)
        reporter.wait(0.5)

        # [2] Click '1 Player'
        reporter.log_step("Click '1 Player'", "Go to settings (cycle 4)", node_id=2)
        self.click_title_button('1player', reporter)
        self.wait_for_settings_screen(game_ui, reporter)

        # [4] Select X (cycle 4)
        reporter.log_step("Select X", "Choose X (cycle 4)", node_id=4)
        self.click_title_button('choose_x', reporter)

        # [6] Settings with one option
        reporter.log_step("Settings with one option", "X selected (cycle 4)", node_id=6)
        reporter.wait(0.3)

        # [4] Select O
        reporter.log_step("Select O", "Change to O (cycle 4)", node_id=4)
        self.click_title_button('choose_o', reporter)

        # [6] Settings with one option
        reporter.log_step("Settings with one option", "O selected (cycle 4)", node_id=6)
        reporter.wait(0.3)

        # [5] Click back
        reporter.log_step("Click back", "Return to menu (cycle 4)", node_id=5)
        self.click_title_button('back', reporter)
        reporter.wait(0.5)

        # [1] Start Menu
        reporter.log_step("Start Menu", "Back at menu (final)", node_id=1)
        reporter.wait(0.5)

        # [3] Click '2 Player'
        reporter.log_step("Click '2 Player'", "Start 2-player mode", node_id=3)
        self.click_title_button('2player', reporter)
        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "2-player game board ready")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "2-player ready", node_id=8)
        reporter.wait(0.3)

        # [11] Make a move
        reporter.log_step("Make a move", "X at (5,5)", node_id=11)
        self.post_move_click(5, 5, reporter)
        confirmed = self.wait_for_move_applied(game_ui, 5, 5, 'X', timeout=5.0)
        reporter.log_assertion(confirmed, "Move X at (5,5) placed")

        # [12] End of test
        reporter.log_step("End of test", "Test completed", node_id=12)
        print(f"\nPATH 5 COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_path_6(self, game_ui, game_thread):
        """
        Path 6: [1,3,8,11,12]
        """
        reporter = VisualTestReporter()

        # [1] Start Menu
        reporter.log_step("Start Menu", "Display title screen", node_id=1)
        game_ui.reset = False
        game_thread.start()
        reporter.wait(0.5)
        reporter.log_assertion(game_ui.state is not None, "Game initialized")

        # [3] Click '2 Player'
        reporter.log_step("Click '2 Player'", "Start 2-player mode", node_id=3)
        self.click_title_button('2player', reporter)
        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "Game board ready")
        reporter.log_assertion(isinstance(game_ui.player2, UserPlayer), "Player 2 is UserPlayer")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "Game board ready", node_id=8)
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "Board is empty")
        reporter.wait(0.5)

        # [11] Make a move
        reporter.log_step("Make a move", "X at center (5,5)", node_id=11)
        self.post_move_click(5, 5, reporter)
        confirmed = self.wait_for_move_applied(game_ui, 5, 5, 'X', timeout=5.0)
        reporter.log_assertion(confirmed, "Move X at (5,5) successful")
        reporter.log_assertion(game_ui.prev_small_idx == 5, "Previous move recorded correctly")

        # [12] End of test
        reporter.log_step("End of test", "Test completed", node_id=12)
        print(f"\nPATH 6 COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_path_7(self, game_ui, game_thread):
        """
        Path 7: [1,2,4,6,7,8,10,8,10,8,11,8,9,8,11,12]
        """
        reporter = VisualTestReporter()

        # [1] Start Menu
        reporter.log_step("Start Menu", "Display title screen", node_id=1)
        game_ui.reset = False
        game_thread.start()
        reporter.wait(0.5)

        # [2] Click '1 Player'
        reporter.log_step("Click '1 Player'", "Go to settings", node_id=2)
        self.click_title_button('1player', reporter)
        self.wait_for_settings_screen(game_ui, reporter)

        # [4] Select X
        reporter.log_step("Select X", "Choose player sign", node_id=4)
        self.click_title_button('choose_x', reporter)

        # [6] Settings with one option


        # [7] Select difficulty: Normal
        reporter.log_step("Select difficulty", "Choose Normal", node_id=7)
        self.click_title_button('normal', reporter)


        selected = self.wait_for_sign_selected(game_ui, 'X', reporter)
        reporter.log_assertion(selected, "Sign X selected")
        reporter.log_step("Settings with one option", "X selected", node_id=6)
        reporter.wait(0.3)
        diff_selected = self.wait_for_difficulty_selected(game_ui, 'normal', reporter)
        reporter.log_assertion(diff_selected, "Difficulty 'normal' selected")

        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "Game board ready")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "Game started", node_id=8)
        reporter.wait(0.5)

        # [10] Click hint 1
        reporter.log_step("Click hint 1", "Get first hint", node_id=10)
        self.click_game_button('hint', reporter)
        hint_shown = self.wait_for_hint_displayed(game_ui, reporter, timeout=10.0)
        reporter.log_assertion(hint_shown, "First hint displayed")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "After hint 1", node_id=8)
        reporter.wait(0.5)

        # [10] Click hint 2
        reporter.log_step("Click hint 2", "Get second hint", node_id=10)
        game_ui.hinted_move = None
        self.click_game_button('hint', reporter)
        hint_shown = self.wait_for_hint_displayed(game_ui, reporter, timeout=10.0)
        reporter.log_assertion(hint_shown, "Second hint displayed")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "After hint 2", node_id=8)
        reporter.wait(0.5)

        # [11] Make move 1
        reporter.log_step("Make move 1", "X at (5,5)", node_id=11)
        self.post_move_click(5, 5, reporter)
        confirmed = self.wait_for_move_applied(game_ui, 5, 5, 'X', timeout=5.0)
        reporter.log_assertion(confirmed, "Move 1: X at (5,5) applied")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "After move 1, waiting for AI", node_id=8)
        reporter.wait(2.0)

        # [9] Click reset
        reporter.log_step("Click reset", "Reset the game", node_id=9)
        self.click_game_button('reset', reporter)
        reset_done = self.wait_for_reset_complete(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(reset_done, "Board reset")
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "Board is empty after reset")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "After reset", node_id=8)
        reporter.wait(0.5)

        # [11] Make move
        reporter.log_step("Make move 2", "X at (1,1)", node_id=11)
        self.post_move_click(1, 1, reporter)
        confirmed = self.wait_for_move_applied(game_ui, 1, 1, 'X', timeout=5.0)
        reporter.log_assertion(confirmed, "Move 2: X at (1,1) applied")

        # [12] End of test
        reporter.log_step("End of test", "Test completed", node_id=12)
        print(f"\nPATH 7 COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_path_8(self, game_ui, game_thread):
        """
        Path 8: [1,2,4,6,4,5,1,3,8,9,8,5,1,3,8,11,12]
        """
        reporter = VisualTestReporter()

        # [1] Start Menu
        reporter.log_step("Start Menu", "Display title screen", node_id=1)
        game_ui.reset = False
        game_thread.start()
        reporter.wait(0.5)

        # [2] Click '1 Player'
        reporter.log_step("Click '1 Player'", "Go to settings", node_id=2)
        self.click_title_button('1player', reporter)
        self.wait_for_settings_screen(game_ui, reporter)

        # [4] Select X
        reporter.log_step("Select X", "Choose player sign", node_id=4)
        self.click_title_button('choose_x', reporter)

        # [6] Settings with one option
        reporter.log_step("Settings with one option", "X selected", node_id=6)
        reporter.wait(0.3)

        # [4] Select O
        reporter.log_step("Select O", "Choose O", node_id=4)
        self.click_title_button('choose_o', reporter)

        # [5] Click back
        reporter.log_step("Click back", "Return to menu", node_id=5)
        self.click_title_button('back', reporter)
        reporter.wait(0.5)

        # [1] Start Menu
        reporter.log_step("Start Menu", "Back at menu", node_id=1)
        reporter.wait(0.5)

        # [3] Click '2 Player'
        reporter.log_step("Click '2 Player'", "Start 2-player", node_id=3)
        self.click_title_button('2player', reporter)
        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "Game board ready")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "Game ready", node_id=8)
        reporter.wait(0.3)

        # [9] Click reset
        reporter.log_step("Click reset", "Reset the game", node_id=9)
        self.click_game_button('reset', reporter)
        reset_done = self.wait_for_reset_complete(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(reset_done, "Board reset")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "After reset", node_id=8)
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "Board is empty after reset")
        reporter.wait(0.3)

        # [5] Click to title
        reporter.log_step("Click to title", "Return to menu", node_id=5)
        self.click_game_button('to_title', reporter)
        reporter.wait(0.5)

        # [1] Start Menu
        reporter.log_step("Start Menu", "Back at menu again", node_id=1)
        reporter.wait(0.5)

        # [3] Click '2 Player' again
        reporter.log_step("Click '2 Player'", "Start 2-player again", node_id=3)
        self.click_title_button('2player', reporter)
        ready = self.wait_for_game_board_ready(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(ready, "Game board ready again")

        # [8] Main Game Page
        reporter.log_step("Main Game Page", "Game ready again", node_id=8)
        reporter.wait(0.3)

        # [11] Make a move
        reporter.log_step("Make a move", "X at (5,5)", node_id=11)
        self.post_move_click(5, 5, reporter)
        confirmed = self.wait_for_move_applied(game_ui, 5, 5, 'X', timeout=5.0)
        reporter.log_assertion(confirmed, "Move X at (5,5) placed")

        # [12] End of test
        reporter.log_step("End of test", "Test completed", node_id=12)
        print(f"\nPATH 8 COMPLETED in {time.time() - reporter.start_time:.2f}s")