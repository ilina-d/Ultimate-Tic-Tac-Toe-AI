import time
import pygame

from tests.test_ui.ui_test_utils import BaseUITest, VisualTestReporter
from utils.game.game_ui_assets import COLOR_YELLOW, COLOR_BLUE
from utils.game.game_ui_assets import X_MARGIN, Y_MARGIN


class TestGridHighlightingUI(BaseUITest):
    """
    All Combinations Coverage for Grid Highlighting UI

    A: Restriction state
       1 - Single board highlighted, 2 - All boards highlighted (free move)
    B: Player turn
       1 - X's turn (yellow), 2 - O's turn (blue)
    C: Board availability (If A1)
       1 - All 9 spaces free, 2 - Some spaces occupied, 3 - Only 1 space left
    """

    def get_board_coords(self) -> dict:
        """Get the top-left corner coordinates for each of the 9 boards."""

        board_size = 180
        spacing = 10

        coords = {}
        for row in range(3):
            for col in range(3):
                board_idx = row * 3 + col + 1
                x = X_MARGIN + col * (board_size + spacing)
                y = Y_MARGIN + row * (board_size + spacing)
                coords[board_idx] = (x, y)

        return coords

    def verify_single_board_highlighted(self, game_ui, board_idx: int,
                                        expected_color: tuple, reporter: VisualTestReporter) -> bool:
        """Verify that a single board is highlighted with the expected color."""
        board_coords = self.get_board_coords()
        if board_idx not in board_coords:
            reporter.log_assertion(False, f"Invalid board index: {board_idx}")
            return False

        x, y = board_coords[board_idx]
        surface = pygame.display.get_surface()

        if surface is None:
            reporter.log_assertion(False, "Display surface not available")
            return False

        cell_size = 60

        highlight_pixels = 0
        total_samples = 0

        for grid_x in [cell_size, cell_size * 2]:
            for sample_y in range(0, 180, 10):
                try:
                    color = surface.get_at((x + grid_x, y + sample_y))
                    total_samples += 1
                    if color[:3] == expected_color:
                        highlight_pixels += 1
                except (IndexError, ValueError, pygame.error):
                    pass

        for grid_y in [cell_size, cell_size * 2]:
            for sample_x in range(0, 180, 10):
                try:
                    color = surface.get_at((x + sample_x, y + grid_y))
                    total_samples += 1
                    if color[:3] == expected_color:
                        highlight_pixels += 1
                except (IndexError, ValueError, pygame.error):
                    pass

        highlighted = highlight_pixels > 0
        color_name = "yellow" if expected_color == COLOR_YELLOW else "blue"
        reporter.log_assertion(highlighted,
                               f"Board {board_idx} highlighted with {color_name} ({highlight_pixels}/{total_samples} pixels on grid lines)")
        return highlighted

    def verify_all_boards_highlighted(self, game_ui, expected_color: tuple,
                                      reporter: VisualTestReporter) -> bool:
        """Verify that all non-completed boards are highlighted."""

        non_completed_boards = []
        for board_idx in range(1, 10):
            if game_ui.state[0]['display'][board_idx] == '-':
                non_completed_boards.append(board_idx)

        print(f"--------------> NON COMPLETED BOARDS {non_completed_boards}")

        if len(non_completed_boards) == 0:
            reporter.log_assertion(False, "No non-completed boards to check")
            return False

        highlighted_count = 0

        for board_idx in non_completed_boards:
            if not self.verify_single_board_highlighted(game_ui, board_idx, expected_color, reporter):
                return False
            highlighted_count += 1

        color_name = "yellow" if expected_color == COLOR_YELLOW else "blue"
        reporter.log_assertion(True,
                               f"All boards highlighted with {color_name} ({highlighted_count}/{len(non_completed_boards)} non-completed boards)")
        return True

    def get_board_free_spaces(self, game_ui, board_idx: int) -> int:
        """Count the number of free spaces in a board."""
        if board_idx < 1 or board_idx > 9:
            return 0
        return game_ui.state[board_idx]['display'].count('-')

    def test_combination_a1_b1_c1(self, game_ui, game_thread):
        """Test Case A1-B1-C1: Single board highlighted, X's turn, all 9 spaces free"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B1-C1: Single board highlighted, X's turn, all 9 spaces free",
                          "Testing single board highlight for X on empty board")

        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (1, 5, 'X'),
            (5, 2, 'O')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After second move", "Board 2 should be highlighted for X, all 9 spaces free")

        free_spaces = self.get_board_free_spaces(game_ui, 2)
        reporter.log_assertion(free_spaces == 9, f"Board 1 has all 9 spaces free (actual: {free_spaces})")

        reporter.log_assertion(game_ui.prev_small_idx == 2, f"Single board (1) is highlighted")
        self.verify_single_board_highlighted(game_ui, 2, COLOR_YELLOW, reporter)

        reporter.log_step("Test Complete", "A1-B1-C1 passed")
        print(f"\nA1-B1-C1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b1_c2(self, game_ui, game_thread):
        """Test Case A1-B1-C2: Single board highlighted, X's turn, some spaces occupied"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B1-C2: Single board highlighted, X's turn, some spaces occupied",
                          "Testing single board highlight for X on partially filled board")

        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (2, 8, 'X'),
            (8, 2, 'O'),
            (2, 7, 'X'),
            (7, 2, 'O')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After moves", "Board 2 should be highlighted for X with some spaces occupied")

        free_spaces = self.get_board_free_spaces(game_ui, 2)
        reporter.log_assertion(1 < free_spaces < 9, f"Board 2 has some spaces occupied (free: {free_spaces})")

        reporter.log_assertion(game_ui.prev_small_idx == 2, f"Single board (2) is highlighted")
        self.verify_single_board_highlighted(game_ui, 2, COLOR_YELLOW, reporter)

        reporter.log_step("Test Complete", "A1-B1-C2 passed")
        print(f"\nA1-B1-C2 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b1_c3(self, game_ui, game_thread):
        """Test Case A1-B1-C3: Single board highlighted, X's turn, only 1 space left"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B1-C3: Single board highlighted, X's turn, only 1 space left",
                          "Testing single board highlight for X on nearly full board")

        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (8, 8, 'X'),
            (8, 9, 'O'),
            (9, 1, 'X'),
            (1, 9, 'O'),
            (9, 4, 'X'),
            (4, 9, 'O'),
            (9, 3, 'X'),
            (3, 9, 'O'),
            (9, 6, 'X'),
            (6, 6, 'O'),
            (6, 9, 'X'),
            (9, 2, 'O'),
            (2, 9, 'X'),
            (9, 5, 'O'),
            (5, 9, 'X'),
            (9, 7, 'O'),
            (7, 9, 'X'),
            (9, 9, 'O')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After moves", "Board 9 should be highlighted for X with only 1 space left")

        free_spaces = self.get_board_free_spaces(game_ui, 9)
        reporter.log_assertion(free_spaces == 1, f"Board 9 has only 1 space left (free: {free_spaces})")

        reporter.log_assertion(game_ui.prev_small_idx == 9, f"Single board (1) is highlighted")
        self.verify_single_board_highlighted(game_ui, 9, COLOR_YELLOW, reporter)

        reporter.log_step("Test Complete", "A1-B1-C3 passed")
        print(f"\nA1-B1-C3 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b2_c1(self, game_ui, game_thread):
        """Test Case A1-B2-C1: Single board highlighted, O's turn, all 9 spaces free"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B2-C1: Single board highlighted, O's turn, all 9 spaces free",
                          "Testing single board highlight for O on empty board")

        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (1, 5, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After first move", "Board 5 should be highlighted for O, all 9 spaces free")

        free_spaces = self.get_board_free_spaces(game_ui, 5)
        reporter.log_assertion(free_spaces == 9, f"Board 5 has all 9 spaces free (actual: {free_spaces})")

        reporter.log_assertion(game_ui.prev_small_idx == 5, f"Single board (5) is highlighted")
        self.verify_single_board_highlighted(game_ui, 5, COLOR_BLUE, reporter)

        reporter.log_step("Test Complete", "A1-B2-C1 passed")
        print(f"\nA1-B2-C1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b2_c2(self, game_ui, game_thread):
        """Test Case A1-B2-C2: Single board highlighted, O's turn, some spaces occupied"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B2-C2: Single board highlighted, O's turn, some spaces occupied",
                          "Testing single board highlight for O on partially filled board")

        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (1, 5, 'X'),
            (5, 5, 'O'),
            (5, 3, 'X'),
            (3, 7, 'O'),
            (7, 5, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After moves", "Board 5 should be highlighted for O with some spaces occupied")

        free_spaces = self.get_board_free_spaces(game_ui, 5)
        reporter.log_assertion(1 < free_spaces < 9, f"Board 5 has some spaces occupied (free: {free_spaces})")

        reporter.log_assertion(game_ui.prev_small_idx == 5, f"Single board (5) is highlighted")
        self.verify_single_board_highlighted(game_ui, 5, COLOR_BLUE, reporter)

        reporter.log_step("Test Complete", "A1-B2-C2 passed")
        print(f"\nA1-B2-C2 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a1_b2_c3(self, game_ui, game_thread):
        """Test Case A1-B2-C3: Single board highlighted, O's turn, only 1 space left"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A1-B2-C3: Single board highlighted, O's turn, only 1 space left",
                          "Testing single board highlight for O on nearly full board")

        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (4, 8, 'X'),
            (8, 4, 'O'),
            (4, 6, 'X'),
            (6, 4, 'O'),
            (4, 3, 'X'),
            (3, 4, 'O'),
            (4, 1, 'X'),
            (1, 4, 'O'),
            (4, 4, 'X'),
            (4, 2, 'O'),
            (2, 4, 'X'),
            (4, 5, 'O'),
            (5, 4, 'X'),
            (4, 7, 'O'),
            (7, 4, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After moves", "Board 4 should be highlighted for O with only 1 space left")

        free_spaces = self.get_board_free_spaces(game_ui, 4)
        reporter.log_assertion(free_spaces == 1, f"Board 5 has only 1 space left (free: {free_spaces})")

        reporter.log_assertion(game_ui.prev_small_idx == 4, f"Single board (5) is highlighted")
        self.verify_single_board_highlighted(game_ui, 4, COLOR_BLUE, reporter)

        reporter.log_step("Test Complete", "A1-B2-C3 passed")
        print(f"\nA1-B2-C3 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a2_b1_d2(self, game_ui, game_thread):
        """Test Case A2-B1: All boards highlighted, X's turn"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A2-B1-D2: All boards highlighted, X's turn",
                          "Testing free move highlight for X")

        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (2, 2, 'X'),
            (2, 1, 'O'),
            (1, 1, 'X'),
            (1, 2, 'O'),
            (2, 5, 'X'),
            (5, 2, 'O'),
            (2, 8, 'X'),
            (8, 2, 'O')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After winning board 2", "Board 2 is complete")
        board_won = self.wait_for_board_won(game_ui, 2, 'X')
        reporter.log_assertion(board_won, "Board 2 won by X")

        reporter.log_step("After O moves to position that sends play to completed board",
                          "X should have free move with some boards completed")

        completed_boards = sum(1 for i in range(1, 10) if game_ui.state[0]['display'][i - 1] != '-')
        reporter.log_assertion(completed_boards > 0, f"Some boards completed ({completed_boards} done)")

        self.verify_all_boards_highlighted(game_ui, COLOR_YELLOW, reporter)

        reporter.log_step("Test Complete", "A2-B1 passed")
        print(f"\nA2-B1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_a2_b2_d2(self, game_ui, game_thread):
        """Test Case A2-B2: All boards highlighted, O's turn"""
        reporter = VisualTestReporter()

        reporter.log_step("Test A2-B2-D2: All boards highlighted, O's turn",
                          "Testing free move highlight for O")

        game_ui.reset = True
        game_thread.start()
        reporter.wait(0.5)

        moves = [
            (2, 2, 'X'),
            (2, 1, 'O'),
            (1, 1, 'X'),
            (1, 2, 'O'),
            (2, 5, 'X'),
            (5, 2, 'O'),
            (2, 8, 'X'),
            (8, 8, 'O'),
            (8, 2, 'X')
        ]

        self.play_moves_via_events(game_ui, game_thread, moves, reporter)
        reporter.wait(0.5)

        reporter.log_step("After winning board 2", "Board 2 is complete")
        board_won = self.wait_for_board_won(game_ui, 2, 'X')
        reporter.log_assertion(board_won, "Board 2 won by X")

        reporter.log_step("After O sent to completed board", "O should have free move")

        completed_boards = sum(1 for i in range(1, 10) if game_ui.state[0]['display'][i - 1] != '-')
        reporter.log_assertion(completed_boards > 0, f"Some boards completed ({completed_boards} done)")

        self.verify_all_boards_highlighted(game_ui, COLOR_BLUE, reporter)

        reporter.log_step("Test Complete", "A2-B2 passed")
        print(f"\nA2-B2 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")