import pytest
import time
from utils.game.game_ui_v2 import GameUI
from utils.players import UserPlayer
from utils.game.game_ui_assets import *
from utils.helpers import StateUpdater

# TODO: Whats the point of the logger, does it have to exist?


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

    def log_step(self, description: str, action: str = ""):
        """ Log a test step with visual formatting. """

        self.step_count += 1
        elapsed = time.time() - self.start_time

        print("\n" + "=" * 80)
        print(f"STEP {self.step_count} | Time: {elapsed:.2f}s")
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


class TestMoveLegality:
    """
    All Combination Coverage Tests for Move Legality

    A: Is the move free or restricted?
       1 - Free, 2 - Restricted
    B: Is the chosen board free or restricted?
       1 - Free, 2 - Restricted
    C: Is the chosen board completed?
       1 - Yes, 2 - No
    D: Is the chosen space free?
       1 - Yes, 2 - No
    E: Is the chosen move legal?
       1 - Yes, 2 - No
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

    def get_board_position_coords(self, big_idx: int, small_idx: int) -> tuple[int, int]:
        """Get pixel coordinates for a board position."""

        box_x, box_y = idx_to_rc[big_idx][small_idx]
        left = box_y * SQUARE_SIZE + X_MARGIN
        top = box_x * SQUARE_SIZE + Y_MARGIN
        return (left + SQUARE_SIZE // 2, top + SQUARE_SIZE // 2)

    def simulate_click_visual(self, x: int, y: int, reporter: VisualTestReporter, highlight_color: tuple = (255, 0, 0)):
        """Simulate a mouse click with visual feedback (visual only, no event posting)."""

        DISPLAY_SURF = pygame.display.get_surface()

        radius = 10
        area_rect = pygame.Rect(x - radius - 3, y - radius - 3, (radius + 3) * 2, (radius + 3) * 2)
        saved_area = DISPLAY_SURF.subsurface(area_rect).copy()

        pygame.draw.circle(DISPLAY_SURF, highlight_color, (x, y), radius, 3)
        pygame.display.update(area_rect)
        reporter.wait(0.15)

        DISPLAY_SURF.blit(saved_area, area_rect)
        pygame.display.update(area_rect)

        reporter.wait(0.1)

    def transition_to_game(self, game_ui: GameUI, reporter: VisualTestReporter):
        """Transition to game board."""

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

    def make_move_using_gameui(self, game_ui: GameUI, big_idx: int, small_idx: int,
                                sign: str, reporter: VisualTestReporter):
        """
        Make a move on the game board using the proper GameUI methods.
        This simulates what happens when a user clicks on a valid position.

        Arguments:
            game_ui: The game UI instance
            big_idx: Big board index
            small_idx: Small board index
            sign: Player sign ('X' or 'O')
            reporter: Visual test reporter

        Returns:
            True if move was successfully made
        """

        player = game_ui.player1 if sign == 'X' else game_ui.player2

        coords = self.get_board_position_coords(big_idx, small_idx)
        self.simulate_click_visual(coords[0], coords[1], reporter, (0, 255, 0))

        box_x, box_y = idx_to_rc[big_idx][small_idx]

        state, board_is_complete = StateUpdater.update_state(game_ui.state, big_idx, small_idx, sign)

        if game_ui.hinted_move:
            game_ui.cover_box(game_ui.hinted_move[0], game_ui.hinted_move[1])
            game_ui.hinted_move = None

        game_ui.draw_sign_on_box(box_x, box_y, sign)

        for i in set(i for i, _ in player.get_current_legal_moves(game_ui.prev_small_idx)):
            game_ui.draw_subgrid_at_board(i, SMALL_LINE_COLOR)

        game_ui.state = state

        if game_ui.state[0]['display'][big_idx] != '-':
            game_ui.draw_sign_on_big_board(big_idx, game_ui.state[0]['display'][big_idx])

        if game_ui.state[0]['display'][small_idx] != '-':
            game_ui.prev_small_idx = None
        else:
            game_ui.prev_small_idx = small_idx

        game_ui.prev_move_made = (big_idx, small_idx)

        player.update_legal_moves(big_idx, small_idx, board_is_complete=board_is_complete)

        next_player = game_ui.player2 if sign == 'X' else game_ui.player1
        opposite_color = OPPOSITE_SIGN_COLORS[sign]

        if game_ui.prev_small_idx is not None:
            game_ui.draw_subgrid_at_board(game_ui.prev_small_idx, opposite_color)
        else:
            for i in set(i for i, _ in next_player.get_current_legal_moves(game_ui.prev_small_idx)):
                game_ui.draw_subgrid_at_board(i, opposite_color)

        pygame.display.update()
        reporter.wait()

        return True

    def setup_game_state(self, game_ui: GameUI, moves: list, reporter: VisualTestReporter):
        """
        Setup a specific game state by making a sequence of moves.

        Arguments:
            game_ui: The game UI instance
            moves: List of tuples (big_idx, small_idx, sign)
            reporter: Visual test reporter
        """

        reporter.log_step("Setting up game state", f"Making {len(moves)} moves")

        for big_idx, small_idx, sign in moves:
            self.make_move_using_gameui(game_ui, big_idx, small_idx, sign, reporter)
            reporter.wait(0.2)

    def test_combination_1(self, game_ui):
        """ Test Combination 1: A1-C2-D1-E1 """

        reporter = VisualTestReporter()

        reporter.log_step("Test Combination 1: A1-C2-D1-E1", "Testing free move on incomplete board with free space (LEGAL)")

        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')

        game_ui.reset_state()
        game_ui.player1.reset_legal_moves()
        game_ui.player2.reset_legal_moves()

        self.transition_to_game(game_ui, reporter)

        reporter.log_step("Initial State", "Empty board - Player X has free choice of any space")

        reporter.log_assertion(game_ui.prev_small_idx is None, "No previous move restriction (A1: Free move)")
        reporter.log_assertion(game_ui.state[0]['display'].count('-') == 9, "All boards are empty and incomplete")

        legal_moves = game_ui.player1.get_current_legal_moves(game_ui.prev_small_idx)
        reporter.log_assertion(len(legal_moves) == 81, f"Player X has all 81 moves available (found {len(legal_moves)})")

        reporter.log_step("Attempting Legal Move",
                          "Player X attempts to play on board 5, space 5 (center of center board)")

        big_idx, small_idx = 5, 5

        reporter.log_assertion(game_ui.state[0]['display'][big_idx] == '-',
                               f"Board {big_idx} is NOT completed (C2: Incomplete board)")

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == '-',
                               f"Space ({big_idx}, {small_idx}) IS free (D1: Free space)")

        reporter.log_assertion((big_idx, small_idx) in legal_moves,
                               f"Move ({big_idx}, {small_idx}) IS in legal moves (E1: Legal move)")

        success = self.make_move_using_gameui(game_ui, big_idx, small_idx, 'X', reporter)
        reporter.log_assertion(success, "Move was successfully executed")

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == 'X',
                               "Board updated correctly with X marker")
        reporter.log_assertion(game_ui.prev_small_idx == small_idx, f"Next player restricted to board {small_idx}")

        reporter.log_step("Test Complete", "All assertions passed for combination A1-C2-D1-E1")
        print(f"\nCOMBINATION 1 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_2(self, game_ui):
        """ Test Combination 2: A1-C2-D2-E2 """

        reporter = VisualTestReporter()

        reporter.log_step("Test Combination 2: A1-C2-D2-E2",
                          "Testing free move on incomplete board with occupied space (ILLEGAL)")

        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')

        game_ui.reset_state()
        game_ui.player1.reset_legal_moves()
        game_ui.player2.reset_legal_moves()

        self.transition_to_game(game_ui, reporter)

        reporter.log_step("Setting up scenario", "Making initial moves to create occupied spaces")

        setup_moves = [
            (4, 5, 'X'),
            (5, 3, 'O'),
            (3, 7, 'X'),
        ]
        self.setup_game_state(game_ui, setup_moves, reporter)

        reporter.log_step("Current State",
                          "Board 7 is now the restricted board for O, giving X free choice next")

        game_ui.prev_small_idx = None

        reporter.log_step("Adjusting scenario", "Setting up X with free choice")

        reporter.log_step("Current State", "X now has FREE choice of any board (A1: Free move)")

        reporter.log_assertion(game_ui.prev_small_idx is None,
                               "No board restriction - X has free choice (A1: Free move)")

        legal_moves = game_ui.player1.get_current_legal_moves(game_ui.prev_small_idx)
        reporter.log_assertion(len(legal_moves) > 9,
                               f"X has multiple boards available (found {len(legal_moves)} legal moves)")

        reporter.log_step("Attempting Illegal Move",
                          "X attempts to play on board 4, space 5 - which is already occupied by X")

        big_idx, small_idx = 4, 5

        reporter.log_assertion(game_ui.state[0]['display'][big_idx] == '-',
                               f"Board {big_idx} is NOT completed (C2: Incomplete board)")

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == 'X',
                               f"Space ({big_idx}, {small_idx}) is NOT free - occupied by X (D2: Occupied space)")

        reporter.log_assertion((big_idx, small_idx) not in legal_moves,
                               f"Move ({big_idx}, {small_idx}) is NOT in legal moves (E2: Illegal move)")

        reporter.log_step("Visualizing illegal move attempt",
                          "Showing the attempted illegal move with red highlight")

        coords = self.get_board_position_coords(big_idx, small_idx)
        self.simulate_click_visual(coords[0], coords[1], reporter, (255, 0, 0))

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == 'X',
                               "Space still contains X (illegal move was not executed)")

        reporter.log_step("Test Complete",
                          "All assertions passed for combination A1-C2-D2-E2 - illegal move on occupied space")
        print(f"\nCOMBINATION 2 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_3(self, game_ui):
        """ Test Combination 3: A1-C1-D2-E2 """

        reporter = VisualTestReporter()

        reporter.log_step("Test Combination 3: A1-C1-D2-E2",
                          "Testing free move attempting to play on a completed board (ILLEGAL)")

        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')

        game_ui.reset_state()
        game_ui.player1.reset_legal_moves()
        game_ui.player2.reset_legal_moves()

        self.transition_to_game(game_ui, reporter)

        reporter.log_step("Setting up scenario", "Creating a completed board to test illegal move")

        setup_moves = [
            (4, 1, 'X'),
            (1, 4, 'O'),
            (4, 2, 'X'),
            (2, 4, 'O')
        ]
        self.setup_game_state(game_ui, setup_moves, reporter)

        reporter.log_step("Completing board 4", "Making final move to win board 4 with X")

        self.make_move_using_gameui(game_ui, 4, 3, 'X', reporter)
        reporter.log_step("Board 4 completed", "X has won board 4, which is now marked as complete")

        reporter.log_assertion(game_ui.state[0]['display'][4] == 'X',
                               "Board 4 IS completed and won by X (C1: Completed board)")

        game_ui.prev_small_idx = None

        reporter.log_step("Current State", "X now has FREE choice of boards (A1: Free move)")

        reporter.log_assertion(game_ui.prev_small_idx is None,
                               "No board restriction - X has free choice (A1: Free move)")

        legal_moves = game_ui.player1.get_current_legal_moves(game_ui.prev_small_idx)

        reporter.log_step("Checking legal moves", f"X has {len(legal_moves)} legal moves available")

        reporter.log_step("Attempting Illegal Move",
                          "X attempts to play on board 4, space 7 - but board 4 is completed")

        big_idx, small_idx = 4, 7

        reporter.log_assertion(game_ui.state[0]['display'][big_idx] == 'X',
                               f"Board {big_idx} IS completed (C1: Completed board)")

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == '-',
                               f"Space ({big_idx}, {small_idx}) is technically empty but on completed board (D2: Not available)")

        reporter.log_assertion((big_idx, small_idx) not in legal_moves,
                               f"Move ({big_idx}, {small_idx}) is NOT in legal moves - cannot play on completed board (E2: Illegal move)")

        reporter.log_step("Visualizing illegal move attempt",
                          "Showing the attempted illegal move on completed board with red highlight")

        coords = self.get_board_position_coords(big_idx, small_idx)
        self.simulate_click_visual(coords[0], coords[1], reporter, (255, 0, 0))

        reporter.log_assertion(game_ui.state[0]['display'][big_idx] == 'X',
                               "Board 4 still marked as completed by X (illegal move was not executed)")
        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == '-',
                               "Space still empty - no change occurred")

        reporter.log_step("Test Complete",
                          "All assertions passed for combination A1-C1-D2-E2 - illegal move on completed board")
        print(f"\nCOMBINATION 3 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_4(self, game_ui):
        """ Test Combination 4: A2-B2-D1-E1 """

        reporter = VisualTestReporter()

        reporter.log_step("Test Combination 4: A2-B2-D1-E1",
                          "Testing restricted move on restricted board with free space (LEGAL)")

        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')

        game_ui.reset_state()
        game_ui.player1.reset_legal_moves()
        game_ui.player2.reset_legal_moves()

        self.transition_to_game(game_ui, reporter)

        reporter.log_step("Setting up scenario", "Making initial moves to create restriction")

        setup_moves = [
            (5, 7, 'X'),
            (7, 3, 'O'),
        ]
        self.setup_game_state(game_ui, setup_moves, reporter)

        reporter.log_step("Current State",
                          "X is now RESTRICTED to board 3 (A2: Restricted move)")

        reporter.log_assertion(game_ui.prev_small_idx == 3,
                               f"X is restricted to board 3 (prev_small_idx = {game_ui.prev_small_idx}) (A2: Restricted move)")

        legal_moves = game_ui.player1.get_current_legal_moves(game_ui.prev_small_idx)

        board_3_moves = [move for move in legal_moves if move[0] == 3]
        reporter.log_assertion(len(board_3_moves) == len(legal_moves),
                               f"All {len(legal_moves)} legal moves are on board 3 (B2: Restricted board)")

        reporter.log_step("Verifying board state", "Checking that board 3 is incomplete and has free spaces")

        reporter.log_assertion(game_ui.state[0]['display'][3] == '-',
                               "Board 3 is NOT completed (C2: Incomplete board)")

        free_spaces_on_board_3 = game_ui.state[3]['display'].count('-')
        reporter.log_assertion(free_spaces_on_board_3 > 0,
                               f"Board 3 has {free_spaces_on_board_3} free spaces available")

        reporter.log_step("Attempting Legal Move",
                          "X attempts to play on board 3, space 5 (center of board 3)")

        big_idx, small_idx = 3, 5

        reporter.log_assertion(big_idx == game_ui.prev_small_idx,
                               f"Chosen board {big_idx} matches restricted board {game_ui.prev_small_idx} (B2: Restricted board)")

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == '-',
                               f"Space ({big_idx}, {small_idx}) IS free (D1: Free space)")

        reporter.log_assertion((big_idx, small_idx) in legal_moves,
                               f"Move ({big_idx}, {small_idx}) IS in legal moves (E1: Legal move)")

        success = self.make_move_using_gameui(game_ui, big_idx, small_idx, 'X', reporter)
        reporter.log_assertion(success, "Move was successfully executed")

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == 'X',
                               "Board 3, space 5 now contains X marker")
        reporter.log_assertion(game_ui.prev_small_idx == small_idx,
                               f"Next player (O) is now restricted to board {small_idx}")

        reporter.log_step("Verifying restriction transfer",
                          f"O is now restricted to board {small_idx}")

        reporter.log_step("Test Complete",
                          "All assertions passed for combination A2-B2-D1-E1 - legal restricted move")
        print(f"\nCOMBINATION 4 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_5(self, game_ui):
        """ Test Combination 5: A2-B2-D2-E2 """

        reporter = VisualTestReporter()

        reporter.log_step("Test Combination 5: A2-B2-D2-E2",
                          "Testing restricted move on restricted board with occupied space (ILLEGAL)")

        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')

        game_ui.reset_state()
        game_ui.player1.reset_legal_moves()
        game_ui.player2.reset_legal_moves()

        self.transition_to_game(game_ui, reporter)

        reporter.log_step("Setting up scenario",
                          "Creating a game state where X is restricted to board 5 with some occupied spaces")

        setup_moves = [
            (4, 5, 'X'),
            (5, 1, 'O'),
            (1, 5, 'X'),
            (5, 2, 'O'),
            (2, 5, 'X'),
        ]
        self.setup_game_state(game_ui, setup_moves, reporter)

        reporter.log_step("Current State",
                          "O's last move sent X to board 5, which now has spaces 1 and 2 occupied by O")

        reporter.log_assertion(game_ui.prev_small_idx == 5,
                               f"X is RESTRICTED to board {game_ui.prev_small_idx} (A2: Restricted move)")

        legal_moves = game_ui.player1.get_current_legal_moves(game_ui.prev_small_idx)

        reporter.log_step("Checking restriction",
                          f"X has {len(legal_moves)} legal moves, all on board 5")

        all_on_board_5 = all(move[0] == 5 for move in legal_moves)
        reporter.log_assertion(all_on_board_5,
                               "All legal moves are restricted to board 5")

        reporter.log_step("Attempting Illegal Move",
                          "X attempts to play on board 5, space 1 - which is already occupied by O")

        big_idx, small_idx = 5, 1

        reporter.log_assertion(big_idx == game_ui.prev_small_idx,
                               f"Chosen board {big_idx} IS the restricted board (B2: Restricted board)")

        reporter.log_assertion(game_ui.state[0]['display'][big_idx] == '-',
                               f"Board {big_idx} is NOT completed")

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == 'O',
                               f"Space ({big_idx}, {small_idx}) is NOT free - occupied by O (D2: Occupied space)")

        reporter.log_assertion((big_idx, small_idx) not in legal_moves,
                               f"Move ({big_idx}, {small_idx}) is NOT in legal moves (E2: Illegal move)")

        reporter.log_step("Visualizing illegal move attempt",
                          "Showing the attempted illegal move with red highlight")

        coords = self.get_board_position_coords(big_idx, small_idx)
        self.simulate_click_visual(coords[0], coords[1], reporter, (255, 0, 0))

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == 'O',
                               "Space still contains O (illegal move was not executed)")

        reporter.log_assertion(game_ui.prev_small_idx == 5,
                               "X is still restricted to board 5 after illegal move attempt")

        reporter.log_step("Test Complete",
                          "All assertions passed for combination A2-B2-D2-E2 - illegal move on occupied space of restricted board")
        print(f"\nCOMBINATION 5 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_6(self, game_ui):
        """ Test Combination 6: A2-B1-C2-D1-E2 """

        reporter = VisualTestReporter()

        reporter.log_step("Test Combination 6: A2-B1-C2-D1-E2",
                          "Testing restricted move attempting to play on different incomplete board (ILLEGAL)")

        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')

        game_ui.reset_state()
        game_ui.player1.reset_legal_moves()
        game_ui.player2.reset_legal_moves()

        self.transition_to_game(game_ui, reporter)

        reporter.log_step("Setting up scenario", "Making initial moves to create board restriction")

        setup_moves = [
            (5, 3, 'X'),
            (3, 7, 'O'),
        ]
        self.setup_game_state(game_ui, setup_moves, reporter)

        reporter.log_step("Current State",
                          "X is now RESTRICTED to board 7 (A2: Restricted move)")

        reporter.log_assertion(game_ui.prev_small_idx == 7,
                               f"X is restricted to board 7 (prev_small_idx={game_ui.prev_small_idx}) (A2: Restricted move)")

        legal_moves = game_ui.player1.get_current_legal_moves(game_ui.prev_small_idx)

        legal_boards = set(move[0] for move in legal_moves)
        reporter.log_assertion(legal_boards == {7},
                               f"All legal moves are on board 7 only (found boards: {legal_boards})")

        reporter.log_step("Attempting Illegal Move",
                          "X attempts to play on board 4 (different board), space 5 - which is free but board is wrong")

        big_idx, small_idx = 4, 5

        reporter.log_assertion(big_idx != game_ui.prev_small_idx,
                               f"Board {big_idx} is NOT the restricted board (B1: Different board chosen)")

        reporter.log_assertion(game_ui.state[0]['display'][big_idx] == '-',
                               f"Board {big_idx} is NOT completed (C2: Incomplete board)")

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == '-',
                               f"Space ({big_idx}, {small_idx}) IS free (D1: Free space)")

        reporter.log_assertion((big_idx, small_idx) not in legal_moves,
                               f"Move ({big_idx}, {small_idx}) is NOT in legal moves - wrong board (E2: Illegal move)")

        reporter.log_step("Visualizing illegal move attempt",
                          "Showing the attempted illegal move on wrong board with red highlight")

        coords = self.get_board_position_coords(big_idx, small_idx)
        self.simulate_click_visual(coords[0], coords[1], reporter, (255, 0, 0))

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == '-',
                               "Space is still empty - no change occurred (illegal move was not executed)")
        reporter.log_assertion(game_ui.prev_small_idx == 7,
                               "X is still restricted to board 7")

        reporter.log_step("Verifying restriction still active",
                          "Confirming X can only play on board 7")

        legal_move_on_7 = (7, 1)
        reporter.log_assertion(legal_move_on_7 in legal_moves,
                               f"Legal move {legal_move_on_7} is available on the correct board 7")

        reporter.log_step("Test Complete",
                          "All assertions passed for combination A2-B1-C2-D1-E2 - illegal move on wrong board when restricted")
        print(f"\nCOMBINATION 6 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_7(self, game_ui):
        """ Test Combination 7: A2-B1-C2-D2-E2 """

        reporter = VisualTestReporter()

        reporter.log_step("Test Combination 7: A2-B1-C2-D2-E2",
                          "Testing restricted move attempting different incomplete board with occupied space (ILLEGAL)")

        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')

        game_ui.reset_state()
        game_ui.player1.reset_legal_moves()
        game_ui.player2.reset_legal_moves()

        self.transition_to_game(game_ui, reporter)

        reporter.log_step("Setting up scenario",
                          "Creating a game state where X is restricted to a specific board")

        setup_moves = [
            (4, 5, 'X'),
            (5, 2, 'O'),
            (2, 3, 'X'),
            (3, 7, 'O'),
            (7, 5, 'X'),
        ]
        self.setup_game_state(game_ui, setup_moves, reporter)

        reporter.log_step("Current State",
                          f"X is restricted to board 5 (prev_small_idx = {game_ui.prev_small_idx})")

        reporter.log_assertion(game_ui.prev_small_idx == 5,
                               f"X is RESTRICTED to board 5 (A2: Restricted move)")

        legal_moves = game_ui.player1.get_current_legal_moves(game_ui.prev_small_idx)

        reporter.log_step("Checking legal moves",
                          f"X has {len(legal_moves)} legal moves, all should be on board 5")

        all_on_board_5 = all(move[0] == 5 for move in legal_moves)
        reporter.log_assertion(all_on_board_5,
                               "All legal moves are restricted to board 5")

        reporter.log_step("Attempting Illegal Move",
                          "X attempts to play on board 3, space 7 - wrong board AND occupied space")

        big_idx, small_idx = 3, 7

        reporter.log_assertion(big_idx != game_ui.prev_small_idx,
                               f"Chosen board {big_idx} is FREE (not the restricted board 5) (B1: Free board choice)")

        reporter.log_assertion(game_ui.state[0]['display'][big_idx] == '-',
                               f"Board {big_idx} is NOT completed (C2: Incomplete board)")

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == 'O',
                               f"Space ({big_idx}, {small_idx}) is NOT free - occupied by O (D2: Occupied space)")

        reporter.log_assertion((big_idx, small_idx) not in legal_moves,
                               f"Move ({big_idx}, {small_idx}) is NOT in legal moves (E2: Illegal move)")

        reporter.log_step("Visualizing illegal move attempt",
                          "Showing the attempted illegal move on wrong board with occupied space (red highlight)")

        coords = self.get_board_position_coords(big_idx, small_idx)
        self.simulate_click_visual(coords[0], coords[1], reporter, (255, 0, 0))

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == 'O',
                               "Space still contains O (illegal move was not executed)")
        reporter.log_assertion(game_ui.prev_small_idx == 5,
                               "X is still restricted to board 5 (restriction unchanged)")

        reporter.log_step("Test Complete",
                          "All assertions passed for combination A2-B1-C2-D2-E2 - illegal move on wrong board with occupied space")
        print(f"\nCOMBINATION 7 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")

    def test_combination_8(self, game_ui):
        """ Test Combination 8: A2-B1-C1-D2-E2 """

        reporter = VisualTestReporter()

        reporter.log_step("Test Combination 8: A2-B1-C1-D2-E2",
                          "Testing restricted move attempting to play on different completed board (ILLEGAL)")

        game_ui.player1 = UserPlayer()
        game_ui.player1.set_sign('X')
        game_ui.player2 = UserPlayer()
        game_ui.player2.set_sign('O')

        game_ui.reset_state()
        game_ui.player1.reset_legal_moves()
        game_ui.player2.reset_legal_moves()

        self.transition_to_game(game_ui, reporter)

        reporter.log_step("Setting up scenario",
                          "Creating a completed board and restricting X to a different board")

        setup_moves = [
            (6, 1, 'X'),
            (1, 6, 'O'),
            (6, 2, 'X'),
            (2, 6, 'O'),
            (6, 3, 'X')
        ]
        self.setup_game_state(game_ui, setup_moves, reporter)

        reporter.log_step("Verifying board 6 completion", "Checking that board 6 is now completed")

        reporter.log_assertion(game_ui.state[0]['display'][6] == 'X',
                               "Board 6 IS completed and won by X (C1: Completed board)")

        reporter.log_step("Setting up restriction", "Making X restricted to board 8")

        self.make_move_using_gameui(game_ui, 3, 8, 'O', reporter)

        reporter.log_step("Current State",
                          f"X is now RESTRICTED to board 8 (prev_small_idx = {game_ui.prev_small_idx})")

        reporter.log_assertion(game_ui.prev_small_idx == 8,
                               f"X is RESTRICTED to board 8 (A2: Restricted move)")

        legal_moves = game_ui.player1.get_current_legal_moves(game_ui.prev_small_idx)

        reporter.log_step("Checking legal moves",
                          f"X has {len(legal_moves)} legal moves, all should be on board 8")

        all_on_board_8 = all(move[0] == 8 for move in legal_moves)
        reporter.log_assertion(all_on_board_8,
                               "All legal moves are restricted to board 8")

        reporter.log_step("Attempting Illegal Move",
                          "X attempts to play on board 6 (completed board), space 3 - wrong board AND completed")

        big_idx, small_idx = 6, 3

        reporter.log_assertion(big_idx != game_ui.prev_small_idx,
                               f"Chosen board {big_idx} is FREE (not the restricted board 8) (B1: Free board choice)")

        reporter.log_assertion(game_ui.state[0]['display'][big_idx] == 'X',
                               f"Board {big_idx} IS completed (C1: Completed board)")

        reporter.log_assertion(game_ui.state[big_idx]['display'][small_idx] == 'X',
                               f"Space ({big_idx}, {small_idx}) is NOT available - board is completed (D2: Not free)")

        reporter.log_assertion((big_idx, small_idx) not in legal_moves,
                               f"Move ({big_idx}, {small_idx}) is NOT in legal moves (E2: Illegal move)")

        reporter.log_step("Visualizing illegal move attempt",
                          "Showing the attempted illegal move on wrong completed board (red highlight)")

        coords = self.get_board_position_coords(big_idx, small_idx)
        self.simulate_click_visual(coords[0], coords[1], reporter, (255, 0, 0))

        reporter.log_assertion(game_ui.state[0]['display'][big_idx] == 'X',
                               "Board 6 is still marked as completed by X (illegal move was not executed)")
        reporter.log_assertion(game_ui.prev_small_idx == 8,
                               "X is still restricted to board 8 (restriction unchanged)")

        reporter.log_step("Verifying restriction still active",
                          "Confirming X can only play on board 8, not on completed board 6")

        board_6_moves = [move for move in legal_moves if move[0] == 6]
        reporter.log_assertion(len(board_6_moves) == 0,
                               "No legal moves exist on completed board 6")

        reporter.log_step("Test Complete",
                          "All assertions passed for combination A2-B1-C1-D2-E2 - illegal move on wrong completed board when restricted")
        print(f"\nCOMBINATION 8 TEST COMPLETED in {time.time() - reporter.start_time:.2f}s")