import time
import pygame
from tests.test_ui.ui_test_utils import BaseUITest, VisualTestReporter


class TestBoardCompletionUI(BaseUITest):
    """
    BCC coverage for Board Completion UI

    A: Completion type
       1 - X wins board, 2 - O wins board, 3 - Board tied
    B: Board position
       1 - Corner, 2 - Edge, 3 - Center
    C: Opacity setting
       1 - Opaque enabled, 2 - Opaque disabled

    happy path: A1 B1 C2
    """

    def test_combination_a1_b1_c2(self, game_ui, game_thread):
        """Test Case A1-B1-C2: X wins corner board, opaque disabled (happy path)"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B1-C2: X wins corner board, opaque disabled",
                          "Testing board completion visual for X win on corner board")

        game_ui.opaque_on_board_completion = False
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        reporter.log_step("Initial state", "Opaque overlay disabled")
        reporter.log_assertion(game_ui.opaque_on_board_completion == False, "Opaque is disabled")

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

        reporter.log_step("After X wins board 1", "Board 1 should be won by X")
        board_won = self.wait_for_board_won(game_ui, 1, 'X')
        reporter.log_assertion(board_won, "Board 1 (corner) won by X")

        reporter.log_step("Test Complete", "A1-B1-C2 passed")
        print(f"\nA1-B1-C2 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a2_b1_c2(self, game_ui, game_thread):
        """Test Case A2-B1-C2: O wins corner board, opaque disabled"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A2-B1-C2: O wins corner board, opaque disabled",
                          "Testing board completion visual for O win on corner board")

        game_ui.opaque_on_board_completion = False
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        reporter.log_step("Initial state", "Opaque overlay disabled")
        reporter.log_assertion(game_ui.opaque_on_board_completion == False, "Opaque is disabled")

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

        reporter.log_step("After O wins board 1", "Board 1 should be won by O")
        board_won = self.wait_for_board_won(game_ui, 1, 'O')
        reporter.log_assertion(board_won, "Board 1 (corner) won by O")

        reporter.log_step("Test Complete", "A2-B1-C2 passed")
        print(f"\nA2-B1-C2 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a3_b1_c2(self, game_ui, game_thread):
        """Test Case A3-B1-C2: Board tied on corner, opaque disabled"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A3-B1-C2: Board tied on corner, opaque disabled",
                          "Testing board completion visual for tied corner board")

        game_ui.opaque_on_board_completion = False
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        reporter.log_step("Initial state", "Opaque overlay disabled")
        reporter.log_assertion(game_ui.opaque_on_board_completion == False, "Opaque is disabled")

        moves = [
            (1, 1, 'X'),
            (1, 2, 'O'),
            (2, 1, 'X'),
            (1, 4, 'O'),
            (4, 1, 'X'),
            (1, 6, 'O'),
            (6, 1, 'X'),
            (1, 9, 'O'),
            (9, 1, 'X'),
            (1, 7, 'O'),
            (7, 2, 'X'),
            (2, 3, 'O'),
            (3, 3, 'X'),
            (3, 1, 'O'),
            (1, 5, 'X'),
            (5, 1, 'O'),
            (1, 8, 'X'),
            (8, 1, 'O'),
            (1, 3, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After board 1 is tied", "Board 1 should be tied")
        board_tied = self.wait_for_board_won(game_ui, 1, 'T')
        reporter.log_assertion(board_tied, "Board 1 (corner) is tied")

        reporter.log_step("Test Complete", "A3-B1-C2 passed")
        print(f"\nA3-B1-C2 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b2_c2(self, game_ui, game_thread):
        """Test Case A1-B2-C2: X wins edge board, opaque disabled"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B2-C2: X wins edge board, opaque disabled",
                          "Testing board completion visual for X win on edge board")

        game_ui.opaque_on_board_completion = False
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        reporter.log_step("Initial state", "Opaque overlay disabled")
        reporter.log_assertion(game_ui.opaque_on_board_completion == False, "Opaque is disabled")

        moves = [
            (2, 7, 'X'),
            (7, 2, 'O'),
            (2, 5, 'X'),
            (5, 2, 'O'),
            (2, 3, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After X wins board 2", "Board 2 should be won by X")
        board_won = self.wait_for_board_won(game_ui, 2, 'X')
        reporter.log_assertion(board_won, "Board 2 (edge) won by X")

        reporter.log_step("Test Complete", "A1-B2-C2 passed")
        print(f"\nA1-B2-C2 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b3_c2(self, game_ui, game_thread):
        """Test Case A1-B3-C2: X wins center board, opaque disabled"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B3-C2: X wins center board, opaque disabled",
                          "Testing board completion visual for X win on center board")

        game_ui.opaque_on_board_completion = False
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        reporter.log_step("Initial state", "Opaque overlay disabled")
        reporter.log_assertion(game_ui.opaque_on_board_completion == False, "Opaque is disabled")

        moves = [
            (5, 4, 'X'),
            (4, 5, 'O'),
            (5, 6, 'X'),
            (6, 5, 'O'),
            (5, 5, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After X wins board 5", "Board 5 should be won by X")
        board_won = self.wait_for_board_won(game_ui, 5, 'X')
        reporter.log_assertion(board_won, "Board 5 (center) won by X")

        reporter.log_step("Test Complete", "A1-B3-C2 passed")
        print(f"\nA1-B3-C2 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b1_c1(self, game_ui, game_thread):
        """Test Case A1-B1-C1: X wins corner board, opaque enabled"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B1-C1: X wins corner board, opaque enabled",
                          "Testing board completion visual for X win with opaque overlay")

        game_ui.opaque_on_board_completion = True
        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        reporter.log_step("Initial state", "Opaque overlay enabled")
        reporter.log_assertion(game_ui.opaque_on_board_completion == True, "Opaque is enabled")

        moves = [
            (7, 8, 'X'),
            (8, 7, 'O'),
            (7, 5, 'X'),
            (5, 7, 'O'),
            (7, 2, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After X wins board 1", "Board 1 should be won by X")
        board_won = self.wait_for_board_won(game_ui, 7, 'X')
        reporter.log_assertion(board_won, "Board 1 (corner) won by X")

        reporter.log_step("Test Complete", "A1-B1-C1 passed")
        print(f"\nA1-B1-C1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")