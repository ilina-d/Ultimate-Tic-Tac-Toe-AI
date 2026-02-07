import time
import pygame
from tests.test_ui.ui_test_utils import BaseUITest, VisualTestReporter
from utils.game.game_ui_assets import COLOR_BLUE, COLOR_YELLOW, X_MARGIN, Y_MARGIN


class TestEvalBarUI(BaseUITest):
    """
    BCC coverage for Evaluation Bar UI

    A: Eval bar toggle state
       1 - On, 2 - Off
    B: Game state
       1 - X advantage, 2 - O advantage, 3 - Even, 4 - X won, 5 - O won, 6 - Tie
    C: After action
       1 - After move, 2 - After reset, 3 - After toggle

    happy path: A1 B1 C1
    """

    def get_game_evaluation(self, game_ui) -> float:
        """
        Get the current game evaluation score using GameEvaluator.

        Arguments:
            game_ui: The game UI instance

        Returns:
            The evaluation score (positive favors X, negative favors O)
        """
        # Determine which player's turn it is
        x_pieces = sum(len(game_ui.state[i]['X']) for i in range(10))
        o_pieces = sum(len(game_ui.state[i]['O']) for i in range(10))

        if x_pieces > o_pieces:
            current_player = game_ui.player2
        else:
            current_player = game_ui.player1

        score = game_ui.game_evaluator.game_evaluation(
            game_ui.state,
            game_ui.prev_small_idx,
            current_player
        )

        return score

    def click_game_button(self, button_name: str, reporter: VisualTestReporter):
        """Click a button on the game page (hint, bar, reset, to_title)."""
        coords = self.get_button_coords()
        x, y = coords[button_name]
        reporter.log_step(
            f"Click '{button_name}' game button",
            action=f"post MOUSEBUTTONUP at ({x}, {y})"
        )
        self.post_click_event(x, y, reporter)

    def wait_for_reset_complete(self, game_ui, reporter: VisualTestReporter,
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

    def verify_eval_bar_visible(self, game_ui, reporter: VisualTestReporter) -> bool:
        """Verify that the eval bar is visible on screen."""
        t, l = Y_MARGIN - 3, X_MARGIN - 100
        W = 16
        H = 546

        surface = pygame.display.get_surface()
        if surface is None:
            reporter.log_assertion(False, "Display surface not available")
            return False

        pixels_found = 0
        for y in range(t, t + H, 50):
            for x in range(l, l + W):
                try:
                    color = surface.get_at((x, y))
                    if color[:3] == COLOR_BLUE or color[:3] == COLOR_YELLOW:
                        pixels_found += 1
                except IndexError:
                    pass

        visible = pixels_found > 0
        reporter.log_assertion(visible, f"Eval bar visible (found {pixels_found} colored pixels)")
        return visible

    def verify_eval_bar_hidden(self, game_ui, reporter: VisualTestReporter) -> bool:
        """Verify that the eval bar is hidden from screen."""
        t, l = Y_MARGIN - 3, X_MARGIN - 100
        W = 16
        H = 546

        surface = pygame.display.get_surface()
        if surface is None:
            reporter.log_assertion(True, "Display surface not available - assuming hidden")
            return True

        pixels_found = 0
        for y in range(t, t + H, 50):
            for x in range(l, l + W):
                try:
                    color = surface.get_at((x, y))
                    if color[:3] == COLOR_BLUE or color[:3] == COLOR_YELLOW:
                        pixels_found += 1
                except IndexError:
                    pass

        hidden = pixels_found == 0
        reporter.log_assertion(hidden, f"Eval bar hidden (found {pixels_found} colored pixels)")
        return hidden

    def test_combination_a1_b1_c1(self, game_ui, game_thread):
        """Test Case A1-B1-C1: Eval bar on, X advantage, after move (happy path)"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B1-C1: Eval bar on, X advantage, after move",
                          "Testing eval bar displays X advantage after X wins a board")

        game_ui.use_eval_bar = True
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        reporter.log_step("Initial state", "Eval bar should be enabled")
        reporter.log_assertion(game_ui.use_eval_bar == True, "Eval bar is enabled")

        moves = [
            (5, 1, 'X'),
            (1, 1, 'O'),
            (1, 9, 'X'),
            (9, 1, 'O'),
            (1, 8, 'X'),
            (8, 1, 'O'),
            (1, 7, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After X wins board 1", "Eval bar should show X advantage")

        board_won = self.wait_for_board_won(game_ui, 1, 'X')
        reporter.log_assertion(board_won, "Board 1 won by X")

        visible = self.verify_eval_bar_visible(game_ui, reporter)
        reporter.log_assertion(visible, "Eval bar is visible after moves")

        eval_score = self.get_game_evaluation(game_ui)
        reporter.log_assertion(eval_score > 0, f"X advantage shown (eval: {eval_score:.2f})")

        reporter.log_step("Test Complete", "A1-B1-C1 passed")
        print(f"\nA1-B1-C1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a2_b1_c1(self, game_ui, game_thread):
        """Test Case A2-B1-C1: Eval bar off, X advantage, after move"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A2-B1-C1: Eval bar off, X advantage, after move",
                          "Testing eval bar stays hidden when disabled even with X winning")

        game_ui.use_eval_bar = False
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        reporter.log_step("Initial state", "Eval bar should be disabled")
        reporter.log_assertion(game_ui.use_eval_bar == False, "Eval bar is disabled")

        moves = [
            (5, 1, 'X'),
            (1, 1, 'O'),
            (1, 9, 'X'),
            (9, 1, 'O'),
            (1, 8, 'X'),
            (8, 1, 'O'),
            (1, 7, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After X wins board 1", "Eval bar should remain hidden")

        board_won = self.wait_for_board_won(game_ui, 1, 'X')
        reporter.log_assertion(board_won, "Board 1 won by X")

        hidden = self.verify_eval_bar_hidden(game_ui, reporter)
        reporter.log_assertion(hidden, "Eval bar remains hidden after moves")

        reporter.log_step("Test Complete", "A2-B1-C1 passed")
        print(f"\nA2-B1-C1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b2_c1(self, game_ui, game_thread):
        """Test Case A1-B2-C1: Eval bar on, O advantage, after move"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B2-C1: Eval bar on, O advantage, after move",
                          "Testing eval bar displays O advantage when O wins a board")

        game_ui.use_eval_bar = True
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        reporter.log_step("Initial state", "Eval bar enabled")

        moves = [
            (1, 1, 'X'),
            (1, 9, 'O'),
            (9, 1, 'X'),
            (1, 8, 'O'),
            (8, 1, 'X'),
            (1, 7, 'O')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After O wins board 1", "Eval bar should show O advantage")

        board_won = self.wait_for_board_won(game_ui, 1, 'O')
        reporter.log_assertion(board_won, "Board 1 won by O")

        visible = self.verify_eval_bar_visible(game_ui, reporter)
        reporter.log_assertion(visible, "Eval bar is visible")

        eval_score = self.get_game_evaluation(game_ui)
        reporter.log_assertion(eval_score < 0, f"O advantage shown (eval: {eval_score:.2f})")

        reporter.log_step("Test Complete", "A1-B2-C1 passed")
        print(f"\nA1-B2-C1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b3_c1(self, game_ui, game_thread):
        """Test Case A1-B3-C1: Eval bar on, even game state, after move"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B3-C1: Eval bar on, even game state, after move",
                          "Testing eval bar displays even position")

        game_ui.use_eval_bar = True
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (1, 1, 'X'),
            (1, 9, 'O'),
            (9, 1, 'X'),
            (1, 3, 'O'),
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After moves", "Eval bar should show relatively even position")

        visible = self.verify_eval_bar_visible(game_ui, reporter)
        reporter.log_assertion(visible, "Eval bar is visible")

        eval_score = self.get_game_evaluation(game_ui)
        reporter.log_assertion(abs(eval_score) < 50, f"Even position shown (eval: {eval_score:.2f})")

        reporter.log_step("Test Complete", "A1-B3-C1 passed")
        print(f"\nA1-B3-C1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b4_c1(self, game_ui, game_thread):
        """Test Case A1-B4-C1: Eval bar on, X wins, after move"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B4-C1: Eval bar on, X wins, after move",
                          "Testing eval bar displays even position")

        game_ui.use_eval_bar = True
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (3, 3, 'X'), (3, 6, 'O'),
            (6, 6, 'X'), (6, 3, 'O'),
            (3, 2, 'X'), (2, 3, 'O'),
            (3, 1, 'X'),

            (1, 6, 'O'),
            (6, 5, 'X'), (5, 6, 'O'),
            (6, 4, 'X'),

            (4, 9, 'O'),
            (9, 1, 'X'), (1, 9, 'O'),
            (9, 5, 'X'), (5, 9, 'O'),
            (9, 9, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After moves", "Eval bar should show max score")

        visible = self.verify_eval_bar_visible(game_ui, reporter)
        reporter.log_assertion(visible, "Eval bar is visible")

        eval_score = self.get_game_evaluation(game_ui)
        reporter.log_assertion(eval_score == 1000, f"Max score shown (eval: {eval_score:.2f})")

        reporter.log_step("Test Complete", "A1-B5-C1 passed")
        print(f"\nA1-B4-C1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b5_c1(self, game_ui, game_thread):
        """Test Case A1-B5-C1: Eval bar on, O wins, after move"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B5-C1: Eval bar on, O wins, after move",
                          "Testing eval bar displays even position")

        game_ui.use_eval_bar = True
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (6, 5, 'X'),
            (5, 5, 'O'), (5, 1, 'X'),
            (1, 1, 'O'), (1, 5, 'X'),
            (5, 7, 'O'), (7, 5, 'X'),
            (5, 3, 'O'),

            (3, 1, 'X'),
            (1, 4, 'O'), (4, 1, 'X'),
            (1, 7, 'O'),

            (7, 9, 'X'),
            (9, 5, 'O'), (3, 9, 'X'),
            (9, 8, 'O'), (8, 9, 'X'),
            (9, 2, 'O')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After moves", "Eval bar should show min score")

        visible = self.verify_eval_bar_visible(game_ui, reporter)
        reporter.log_assertion(visible, "Eval bar is visible")

        eval_score = self.get_game_evaluation(game_ui)
        reporter.log_assertion(eval_score == -1000, f"Min score shown (eval: {eval_score:.2f})")

        reporter.log_step("Test Complete", "A1-B5-C1 passed")
        print(f"\nA1-B5-C1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b6_c1(self, game_ui, game_thread):
        """Test Case A1-B5-C1: Eval bar on, tie, after move"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B5-C1: Eval bar on, tie, after move",
                          "Testing eval bar displays even position")

        game_ui.use_eval_bar = True
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (1, 5, 'X'), (5, 1, 'O'),
            (1, 2, 'X'), (2, 1, 'O'),
            (1, 8, 'X'), (8, 4, 'O'),
            (4, 5, 'X'), (5, 5, 'O'),
            (5, 2, 'X'), (2, 5, 'O'),
            (5, 9, 'X'), (9, 9, 'O'),
            (9, 2, 'X'), (2, 9, 'O'),
            (9, 5, 'X'), (5, 4, 'O'),
            (4, 4, 'X'), (4, 6, 'O'),
            (6, 2, 'X'), (5, 6, 'O'),
            (6, 9, 'X'), (9, 8, 'O'),
            (8, 9, 'X'), (9, 7, 'O'),
            (7, 5, 'X'), (7, 9, 'O'),
            (6, 7, 'X'), (7, 8, 'O'),
            (8, 7, 'X'), (7, 7, 'O'),
            (8, 8, 'X'), (3, 3, 'O'),
            (3, 6, 'X'), (6, 3, 'O'),
            (3, 5, 'X'), (3, 7, 'O'),
            (6, 8, 'X'), (3, 8, 'O'),
            (3, 4, 'X'), (4, 3, 'O'),
            (4, 9, 'X'), (4, 8, 'O'),
            (4, 1, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After moves", "Eval bar should show 0")

        visible = self.verify_eval_bar_visible(game_ui, reporter)
        reporter.log_assertion(visible, "Eval bar is visible")

        eval_score = self.get_game_evaluation(game_ui)
        reporter.log_assertion(eval_score == 0, f"Tied score shown (eval: {eval_score:.2f})")

        reporter.log_step("Test Complete", "A1-B6-C1 passed")
        print(f"\nA1-B6-C1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b1_c2(self, game_ui, game_thread):
        """Test Case A1-B1-C2: Eval bar on, X advantage, after reset"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B1-C2: Eval bar on, X advantage, after reset",
                          "Testing eval bar updates after reset")

        game_ui.use_eval_bar = True
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (5, 1, 'X'),
            (1, 1, 'O'),
            (1, 9, 'X'),
            (9, 1, 'O'),
            (1, 8, 'X'),
            (8, 1, 'O'),
            (1, 7, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("Before reset", "X has won board 1")
        board_won = self.wait_for_board_won(game_ui, 1, 'X')
        reporter.log_assertion(board_won, "Board 1 won by X")

        eval_before = self.get_game_evaluation(game_ui)
        reporter.log_assertion(eval_before > 0, f"X advantage before reset (eval: {eval_before:.2f})")

        reporter.log_step("Clicking reset", "Reset the game")
        self.click_game_button('reset', reporter)
        reset_done = self.wait_for_reset_complete(game_ui, reporter, timeout=5.0)
        reporter.log_assertion(reset_done, "Board reset completed")
        reporter.wait(0.5)

        reporter.log_step("After reset", "Eval bar should show neutral/initial state")

        eval_after = self.get_game_evaluation(game_ui)
        reporter.log_assertion(abs(eval_after) < abs(eval_before),
                               f"Eval more balanced after reset (before: {eval_before:.2f}, after: {eval_after:.2f})")

        reporter.log_step("Test Complete", "A1-B1-C2 passed")
        print(f"\nA1-B1-C2 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b1_c3(self, game_ui, game_thread):
        """Test Case A1-B1-C3: Eval bar on, X advantage, after toggle"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B1-C3: Eval bar on, X advantage, after toggle",
                          "Testing eval bar toggle functionality")

        game_ui.use_eval_bar = False
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        reporter.log_step("Initial state", "Eval bar disabled")
        reporter.log_assertion(game_ui.use_eval_bar == False, "Eval bar is off")

        moves = [
            (5, 1, 'X'),
            (1, 1, 'O'),
            (1, 9, 'X'),
            (9, 1, 'O'),
            (1, 8, 'X'),
            (8, 1, 'O'),
            (1, 7, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("Before toggle", "X won board 1, eval bar should be hidden")
        board_won = self.wait_for_board_won(game_ui, 1, 'X')
        reporter.log_assertion(board_won, "Board 1 won by X")

        hidden_before = self.verify_eval_bar_hidden(game_ui, reporter)
        reporter.log_assertion(hidden_before, "Eval bar hidden before toggle")

        reporter.log_step("Clicking bar toggle", "Enable eval bar")
        self.click_game_button('bar', reporter)
        reporter.wait(0.5)

        reporter.log_step("After toggle", "Eval bar should appear with X advantage")
        reporter.log_assertion(game_ui.use_eval_bar == True, "Eval bar is now on")

        visible = self.verify_eval_bar_visible(game_ui, reporter)
        reporter.log_assertion(visible, "Eval bar is visible after toggle")

        eval_score = self.get_game_evaluation(game_ui)
        reporter.log_assertion(eval_score > 0, f"X advantage shown (eval: {eval_score:.2f})")

        reporter.log_step("Test Complete", "A1-B1-C3 passed")
        print(f"\nA1-B1-C3 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

