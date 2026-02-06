import time
import pygame
from .ui_test_utils import BaseUITest, VisualTestReporter
from utils.players import UserPlayer
from utils.helpers import StateChecker

_state_checker = StateChecker()


class TestGameEndStates(BaseUITest):
    """
    All Combinations Coverage Tests for Game End States.

    Each test:
      1. Creates a fresh GameUI via the game_ui fixture
      2. Starts play() in a daemon thread via the game_thread fixture
      3. Posts real MOUSEBUTTONUP events to drive the game loop
      4. Polls game_ui.state to confirm each move was processed
      5. The game_thread fixture's teardown stops the thread automatically

    A: Winner
       1 - X wins, 2 - O wins, 3 - Tie
    B: Win type (for wins)
       1 - Row, 2 - Column, 3 - Diagonal

    7 Test Cases covering all combinations.
    """

    def play_game_with_moves(self, game_ui, game_thread, moves, reporter):
        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')

        game_ui.reset_state()
        game_ui.player1.reset_legal_moves()
        game_ui.player2.reset_legal_moves()

        game_ui.reset = True

        game_thread.start(timeout=5.0)

        reporter.wait(0.5)

        self.play_moves_via_events(
            game_ui, game_thread, moves, reporter, move_wait=0.3
        )

        reporter.wait(0.5)
        pygame.display.quit()

        game_thread.thread.join(timeout=3.0)
        reporter.wait(0.3)

    def test_x_wins_row(self, game_ui, game_thread):
        """Test Case A1-B1: X wins by completing a row"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B1: X wins by row",
                          "X will win boards 4, 5, 6 (middle row of big board)")

        game_moves = [
            (4, 1, 'X'), (1, 4, 'O'),
            (4, 2, 'X'), (2, 4, 'O'),
            (4, 3, 'X'), (3, 5, 'O'),

            (5, 1, 'X'), (1, 5, 'O'),
            (5, 2, 'X'), (2, 5, 'O'),
            (5, 3, 'X'), (3, 6, 'O'),

            (6, 1, 'X'), (1, 6, 'O'),
            (6, 2, 'X'), (2, 6, 'O'),
            (6, 3, 'X')
        ]

        self.play_game_with_moves(game_ui, game_thread, game_moves, reporter)

        reporter.log_assertion(game_ui.state[0]['display'][4] == 'X', "Board 4 won by X")
        reporter.log_assertion(game_ui.state[0]['display'][5] == 'X', "Board 5 won by X")
        reporter.log_assertion(game_ui.state[0]['display'][6] == 'X', "Board 6 won by X")

        result = _state_checker.check_win(state=game_ui.state, big_idx=0)
        reporter.log_assertion(result == 'X', f"X wins the game (got: {result})")

        reporter.log_step("Test Complete", "A1-B1 passed")
        print(f"\nX WINS ROW TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_x_wins_column(self, game_ui, game_thread):
        """Test Case A1-B2: X wins by completing a column"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B2: X wins by column",
                          "X will win boards 3, 6, 9 (left column of big board)")

        game_moves = [
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

        self.play_game_with_moves(game_ui, game_thread, game_moves, reporter)

        reporter.log_assertion(game_ui.state[0]['display'][3] == 'X', "Board 3 won by X")
        reporter.log_assertion(game_ui.state[0]['display'][6] == 'X', "Board 6 won by X")
        reporter.log_assertion(game_ui.state[0]['display'][9] == 'X', "Board 9 won by X")

        result = _state_checker.check_win(state=game_ui.state, big_idx=0)
        reporter.log_assertion(result == 'X', f"X wins the game (got: {result})")

        reporter.log_step("Test Complete", "A1-B2 passed")
        print(f"\nX WINS COLUMN TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_x_wins_diagonal(self, game_ui, game_thread):
        """Test Case A1-B3: X wins by completing a diagonal"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B3: X wins by diagonal",
                          "X will win boards 1, 5, 9 (main diagonal of big board)")

        game_moves = [
            (5, 5, 'X'), (5, 1, 'O'),
            (1, 1, 'X'), (1, 5, 'O'),
            (5, 7, 'X'), (7, 5, 'O'),
            (5, 3, 'X'),

            (3, 1, 'O'),
            (1, 4, 'X'), (4, 1, 'O'),
            (1, 7, 'X'),

            (7, 9, 'O'),
            (9, 5, 'X'), (3, 9, 'O'),
            (9, 8, 'X'), (8, 9, 'O'),
            (9, 2, 'X')
        ]

        self.play_game_with_moves(game_ui, game_thread, game_moves, reporter)

        reporter.log_assertion(game_ui.state[0]['display'][1] == 'X', "Board 1 won by X")
        reporter.log_assertion(game_ui.state[0]['display'][5] == 'X', "Board 5 won by X")
        reporter.log_assertion(game_ui.state[0]['display'][9] == 'X', "Board 9 won by X")

        result = _state_checker.check_win(state=game_ui.state, big_idx=0)
        reporter.log_assertion(result == 'X', f"X wins the game (got: {result})")

        reporter.log_step("Test Complete", "A1-B3 passed")
        print(f"\nX WINS DIAGONAL TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_o_wins_row(self, game_ui, game_thread):
        """Test Case A2-B1: O wins by completing a row"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A2-B1: O wins by row",
                          "O will win boards 4, 5, 6 (middle row of big board)")

        game_moves = [
            (7, 4, 'X'),
            (4, 1, 'O'), (1, 4, 'X'),
            (4, 2, 'O'), (2, 4, 'X'),
            (4, 3, 'O'), (3, 5, 'X'),

            (5, 1, 'O'), (1, 5, 'X'),
            (5, 2, 'O'), (2, 5, 'X'),
            (5, 3, 'O'), (3, 6, 'X'),

            (6, 1, 'O'), (1, 6, 'X'),
            (6, 2, 'O'), (2, 6, 'X'),
            (6, 3, 'O')
        ]

        self.play_game_with_moves(game_ui, game_thread, game_moves, reporter)

        reporter.log_assertion(game_ui.state[0]['display'][4] == 'O', "Board 4 won by O")
        reporter.log_assertion(game_ui.state[0]['display'][5] == 'O', "Board 5 won by O")
        reporter.log_assertion(game_ui.state[0]['display'][6] == 'O', "Board 6 won by O")

        result = _state_checker.check_win(state=game_ui.state, big_idx=0)
        reporter.log_assertion(result == 'O', f"O wins the game (got: {result})")

        reporter.log_step("Test Complete", "A2-B1 passed")
        print(f"\nO WINS ROW TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_o_wins_column(self, game_ui, game_thread):
        """Test Case A2-B2: O wins by completing a column"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A2-B2: O wins by column",
                          "O will win boards 3, 6, 9 (left column of big board)")

        game_moves = [
            (7, 3, 'X'),
            (3, 3, 'O'), (3, 6, 'X'),
            (6, 6, 'O'), (6, 3, 'X'),
            (3, 2, 'O'), (2, 3, 'X'),
            (3, 1, 'O'),

            (1, 6, 'X'),
            (6, 5, 'O'), (5, 6, 'X'),
            (6, 4, 'O'),

            (4, 9, 'X'),
            (9, 1, 'O'), (1, 9, 'X'),
            (9, 5, 'O'), (5, 9, 'X'),
            (9, 9, 'O')
        ]

        self.play_game_with_moves(game_ui, game_thread, game_moves, reporter)

        reporter.log_assertion(game_ui.state[0]['display'][3] == 'O', "Board 3 won by O")
        reporter.log_assertion(game_ui.state[0]['display'][6] == 'O', "Board 6 won by O")
        reporter.log_assertion(game_ui.state[0]['display'][9] == 'O', "Board 9 won by O")

        result = _state_checker.check_win(state=game_ui.state, big_idx=0)
        reporter.log_assertion(result == 'O', f"O wins the game (got: {result})")

        reporter.log_step("Test Complete", "A2-B2 passed")
        print(f"\nO WINS COLUMN TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_o_wins_diagonal(self, game_ui, game_thread):
        """Test Case A2-B3: O wins by completing a diagonal"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A2-B3: O wins by diagonal",
                          "O will win boards 1, 5, 9 (main diagonal of big board)")

        game_moves = [
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

        self.play_game_with_moves(game_ui, game_thread, game_moves, reporter)

        reporter.log_assertion(game_ui.state[0]['display'][1] == 'O', "Board 1 won by O")
        reporter.log_assertion(game_ui.state[0]['display'][5] == 'O', "Board 5 won by O")
        reporter.log_assertion(game_ui.state[0]['display'][9] == 'O', "Board 9 won by O")

        result = _state_checker.check_win(state=game_ui.state, big_idx=0)
        reporter.log_assertion(result == 'O', f"O wins the game (got: {result})")

        reporter.log_step("Test Complete", "A2-B3 passed")
        print(f"\nO WINS DIAGONAL TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_tie(self, game_ui, game_thread):
        """Test Case A3: X and O tie"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A3: X and O tie",
                          "X and O will tie")

        game_moves = [
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

        self.play_game_with_moves(game_ui, game_thread, game_moves, reporter)

        print(game_ui.state[0]['display'])
        result = _state_checker.check_win(state=game_ui.state, big_idx=0)
        reporter.log_assertion(result == 'T', f"Game is a tie (got: {result})")

        reporter.log_step("Test Complete", "A3 passed")
        print(f"\nX AND O TIE TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")
