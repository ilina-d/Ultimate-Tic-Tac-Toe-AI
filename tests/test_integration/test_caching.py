import pytest

from utils.helpers.state_checker import StateChecker
from utils.helpers.state_updater import StateUpdater
from utils.helpers.state_evaluator import StateEvaluator
from utils.helpers.assets import inverse_board_display
from tests.state_generator import StateGenerator


class TestStateCheckerCaching:
    """
    Integration tests for caching behavior between StateChecker and StateUpdater.

    BCC criteria:
    A: board result after check
        1 - X wins, 2 - O wins, 3 - tie, 4 - in progress
    B: cache state before check
        1 - empty cache, 2 - original board cached, 3 - inverted board cached
    C: board index
        1 - small board (1-9), 2 - big board (0)

    Base choice (happy path): A1 B1 C1
    """

    @pytest.fixture(autouse=True)
    def reset_caches(self):
        """Reset singleton caches before each test."""

        state_checker = StateChecker()
        state_checker._instance.checked_boards = {}

        yield

        state_checker._instance.checked_boards = {}


    # A1 B1 C1 - Base choice (happy path)
    def test_base_choice_x_wins_empty_cache_small_board(self):
        state = StateGenerator.generate(_1='XXX------')
        state_checker = StateChecker()

        assert len(state_checker._instance.checked_boards) == 0, "Cache should start empty."

        result = state_checker.check_win(state, 1)

        assert result == 'X', "X should win."
        assert state[1]['display'] in state_checker._instance.checked_boards, \
            "Board should be cached."
        assert inverse_board_display(state[1]['display']) in state_checker._instance.checked_boards, \
            "Inverted board should also be cached."


    # A2 B1 C1
    def test_vary_a_o_wins_empty_cache_small_board(self):
        state = StateGenerator.generate(_1='OOO------')
        state_checker = StateChecker()

        assert len(state_checker._instance.checked_boards) == 0, "Cache should start empty."

        result = state_checker.check_win(state, 1)

        assert result == 'O', "O should win."
        assert state[1]['display'] in state_checker._instance.checked_boards, \
            "Board should be cached."
        inverted = inverse_board_display(state[1]['display'])
        assert state_checker._instance.checked_boards[inverted] == 'X', \
            "Inverted O win should be cached as X win."


    # A3 B1 C1
    def test_vary_a_tie_empty_cache_small_board(self):
        state = StateGenerator.generate(_1='XOXXOXOXO')
        state_checker = StateChecker()

        assert len(state_checker._instance.checked_boards) == 0, "Cache should start empty."

        result = state_checker.check_win(state, 1)

        assert result == 'T', "Board should be tied."
        assert state[1]['display'] in state_checker._instance.checked_boards, \
            "Board should be cached."
        inverted = inverse_board_display(state[1]['display'])
        assert state_checker._instance.checked_boards[inverted] == 'T', \
            "Inverted tie should also be cached as tie."


    # A4 B1 C1
    def test_vary_a_in_progress_empty_cache_small_board(self):
        state = StateGenerator.generate(_1='XO-------')
        state_checker = StateChecker()

        assert len(state_checker._instance.checked_boards) == 0, "Cache should start empty."

        result = state_checker.check_win(state, 1)

        assert result == False, "Board should be in progress."
        assert state[1]['display'] in state_checker._instance.checked_boards, \
            "In-progress board should be cached as False."
        assert state_checker._instance.checked_boards[state[1]['display']] == False


    # A1 B2 C1
    def test_vary_b_x_wins_original_cached_small_board(self):
        state = StateGenerator.generate(_1='XXX------')
        state_checker = StateChecker()

        # Pre-populate cache with the board
        state_checker._instance.checked_boards[state[1]['display']] = 'X'
        cache_size_before = len(state_checker._instance.checked_boards)

        result = state_checker.check_win(state, 1)

        assert result == 'X', "Should return cached X win."
        # Verify cache was used by checking that no new entries were added
        # (if recalculated, the inverted board would also be added)
        assert len(state_checker._instance.checked_boards) == cache_size_before, \
            "Cache size should not change when hitting cached entry."


    # A1 B3 C1
    def test_vary_b_x_wins_inverted_cached_small_board(self):
        state = StateGenerator.generate(_1='XXX------')
        state_checker = StateChecker()

        inverted = inverse_board_display(state[1]['display'])
        state_checker._instance.checked_boards[inverted] = 'O'

        result = state_checker.check_win(state, 1)

        assert result == 'X', "Should return X win."
        assert state[1]['display'] in state_checker._instance.checked_boards


    # A1 B1 C2
    def test_vary_c_x_wins_empty_cache_big_board(self):
        state = StateGenerator.generate(_0='XXX------')
        state_checker = StateChecker()

        assert len(state_checker._instance.checked_boards) == 0, "Cache should start empty."

        result = state_checker.check_win(state, 0)

        assert result == 'X', "X should win on big board."
        assert state[0]['display'] in state_checker._instance.checked_boards, \
            "Big board should be cached."


class TestStateUpdaterCheckerIntegration:
    """
    Integration tests for StateUpdater triggering StateChecker cache population.

    BCC criteria:
    A: move completes board
        1 - yes with win, 2 - yes with tie, 3 - no
    B: sign making the move
        1 - X, 2 - O
    C: board state before move
        1 - nearly complete (one move from win/tie), 2 - mid-game, 3 - empty

    Base choice (happy path): A1 B1 C1
    """

    @pytest.fixture(autouse=True)
    def reset_caches(self):
        """Reset singleton caches before each test."""

        state_checker = StateChecker()
        state_checker._instance.checked_boards = {}

        yield

        state_checker._instance.checked_boards = {}


    # A1 B1 C1 - Base choice (happy path)
    def test_base_choice_completes_win_x_nearly_complete(self):
        state = StateGenerator.generate(_1='XX-------')
        state_checker = StateChecker()

        updated_state, board_complete = StateUpdater.update_state(state, 1, 3, 'X')

        assert board_complete == True, "Board should be completed."
        assert updated_state[0]['display'][1] == 'X', "Big board should show X won."
        assert updated_state[1]['display'] in state_checker._instance.checked_boards, \
            "Completed board should be cached."
        assert state_checker._instance.checked_boards[updated_state[1]['display']] == 'X'


    # A2 B1 C1
    def test_vary_a_completes_tie_x_nearly_complete(self):
        state = StateGenerator.generate(_1='OXOXXOXO-')
        state_checker = StateChecker()

        updated_state, board_complete = StateUpdater.update_state(state, 1, 9, 'X')

        assert board_complete == True, "Board should be completed."
        assert updated_state[0]['display'][1] == 'T', "Big board should show tie."
        assert state_checker._instance.checked_boards[updated_state[1]['display']] == 'T'


    # A3 B1 C1
    def test_vary_a_no_completion_x_nearly_complete(self):
        state = StateGenerator.generate(_1='XO-------')
        state_checker = StateChecker()

        updated_state, board_complete = StateUpdater.update_state(state, 1, 3, 'X')

        assert board_complete == False, "Board should not be completed."
        assert updated_state[0]['display'][1] == '-', "Big board should still be empty."
        assert updated_state[1]['display'] in state_checker._instance.checked_boards, \
            "In-progress board should still be cached."
        assert state_checker._instance.checked_boards[updated_state[1]['display']] == False


    # A1 B2 C1
    def test_vary_b_completes_win_o_nearly_complete(self):
        state = StateGenerator.generate(_1='OO-------')
        state_checker = StateChecker()

        updated_state, board_complete = StateUpdater.update_state(state, 1, 3, 'O')

        assert board_complete == True, "Board should be completed."
        assert updated_state[0]['display'][1] == 'O', "Big board should show O won."
        assert state_checker._instance.checked_boards[updated_state[1]['display']] == 'O'


    # A1 B1 C2
    def test_vary_c_completes_win_x_mid_game(self):
        state = StateGenerator.generate(_1='X-O-X-O--')
        state_checker = StateChecker()

        updated_state, board_complete = StateUpdater.update_state(state, 1, 9, 'X')

        assert board_complete == True, "Board should be completed with diagonal win."
        assert updated_state[0]['display'][1] == 'X', "Big board should show X won."
        assert state_checker._instance.checked_boards[updated_state[1]['display']] == 'X'


    # A1 B1 C3
    def test_vary_c_no_completion_x_empty(self):
        state = StateGenerator.generate(_1='---------')
        state_checker = StateChecker()

        updated_state, board_complete = StateUpdater.update_state(state, 1, 5, 'X')

        assert board_complete == False, "Single move on empty board cannot complete it."
        assert updated_state[0]['display'][1] == '-', "Big board should still be empty."
        assert updated_state[1]['display'] in state_checker._instance.checked_boards


class TestStateEvaluatorCaching:
    """
    Integration tests for StateEvaluator caching behavior.

    Note: Caching in StateEvaluator happens in the `heuristic` method, not `evaluate_board`.
    The heuristic method caches combined scores (X eval + O eval) for each board.

    BCC criteria:
    A: board state complexity
        1 - board with pieces (non-empty), 2 - empty board, 3 - completed board (won/tied)
    B: cache state before evaluation
        1 - empty cache, 2 - original cached, 3 - inverted cached
    C: sign evaluating for
        1 - X, 2 - O

    Base choice (happy path): A1 B1 C1
    """

    @pytest.fixture(autouse=True)
    def reset_caches(self):
        """Reset singleton caches before each test."""

        state_evaluator = StateEvaluator()
        state_evaluator._instance.evaluated_boards = {}

        state_checker = StateChecker()
        state_checker._instance.checked_boards = {}

        yield

        state_evaluator._instance.evaluated_boards = {}
        state_checker._instance.checked_boards = {}


    # A1 B1 C1 - Base choice (happy path)
    def test_base_choice_pieces_on_board_empty_cache_x(self):
        state = StateGenerator.generate(_1='X---X----')
        state_evaluator = StateEvaluator()

        assert len(state_evaluator._instance.evaluated_boards) == 0, "Cache should start empty."

        score = state_evaluator.heuristic(state, None, 'X')

        assert state[1]['display'] in state_evaluator._instance.evaluated_boards, \
            "Board should be cached after heuristic call."
        assert inverse_board_display(state[1]['display']) in state_evaluator._instance.evaluated_boards, \
            "Inverted board should also be cached."


    # A2 B1 C1
    def test_vary_a_empty_board_empty_cache_x(self):
        state = StateGenerator.generate()
        state_evaluator = StateEvaluator()

        assert len(state_evaluator._instance.evaluated_boards) == 0, "Cache should start empty."

        score = state_evaluator.heuristic(state, None, 'X')

        for big_idx in range(1, 10):
            assert state[big_idx]['display'] in state_evaluator._instance.evaluated_boards, \
                f"Board {big_idx} should be cached."


    # A3 B1 C1
    def test_vary_a_completed_board_empty_cache_x(self):
        state = StateGenerator.generate(_0='X--------', _1='XXX------')
        state_evaluator = StateEvaluator()

        assert len(state_evaluator._instance.evaluated_boards) == 0, "Cache should start empty."

        score = state_evaluator.heuristic(state, None, 'X')

        assert state[1]['display'] in state_evaluator._instance.evaluated_boards, \
            "Completed board should be cached."


    # A1 B2 C1
    def test_vary_b_pieces_on_board_original_cached_x(self):
        state = StateGenerator.generate(_1='X---X----')
        state_evaluator = StateEvaluator()

        cached_score = 999
        state_evaluator._instance.evaluated_boards[state[1]['display']] = cached_score

        # Record cache size before
        cache_size_before = len(state_evaluator._instance.evaluated_boards)

        score = state_evaluator.heuristic(state, None, 'X')

        # The cache should grow by entries for other boards (2-9), but board 1 should not be recalculated
        # We verify the cached value is still there unchanged
        assert state_evaluator._instance.evaluated_boards[state[1]['display']] == cached_score, \
            "Cached score for board 1 should remain unchanged (not recalculated)."


    # A1 B3 C1
    def test_vary_b_pieces_on_board_inverted_cached_x(self):
        state = StateGenerator.generate(_1='X---X----')
        state_evaluator = StateEvaluator()

        inverted = inverse_board_display(state[1]['display'])
        inverted_cached_score = -500
        state_evaluator._instance.evaluated_boards[inverted] = inverted_cached_score

        score = state_evaluator.heuristic(state, None, 'X')

        assert state[1]['display'] in state_evaluator._instance.evaluated_boards, \
            "Original board should be cached after heuristic."


    # A1 B1 C2
    def test_vary_c_pieces_on_board_empty_cache_o(self):
        state = StateGenerator.generate(_1='X---X----')  # X has advantage
        state_evaluator = StateEvaluator()

        assert len(state_evaluator._instance.evaluated_boards) == 0, "Cache should start empty."

        score = state_evaluator.heuristic(state, None, 'O')

        assert state[1]['display'] in state_evaluator._instance.evaluated_boards, \
            "Board should be cached."
        assert inverse_board_display(state[1]['display']) in state_evaluator._instance.evaluated_boards, \
            "Inverted board should also be cached."


class TestFullCachingIntegration:
    """
    Full integration tests across StateUpdater, StateChecker, and StateEvaluator.

    BCC criteria:
    A: number of moves made
        1 - single move, 2 - multiple moves same board, 3 - moves across different boards
    B: cache hits during sequence
        1 - all misses, 2 - some hits, 3 - all hits after initial population
    C: board completions in sequence
        1 - no completions, 2 - one completion, 3 - multiple completions

    Base choice (happy path): A2 B2 C2
    """

    @pytest.fixture(autouse=True)
    def reset_caches(self):
        """Reset all singleton caches before each test."""

        state_checker = StateChecker()
        state_checker._instance.checked_boards = {}

        state_evaluator = StateEvaluator()
        state_evaluator._instance.evaluated_boards = {}

        yield

        state_checker._instance.checked_boards = {}
        state_evaluator._instance.evaluated_boards = {}


    # A2 B2 C2 - Base choice (happy path)
    def test_base_choice_multiple_moves_mixed_hits_one_completion(self):
        state = StateGenerator.generate(_1='---------')
        state_checker = StateChecker()

        state1, _ = StateUpdater.update_state(state, 1, 1, 'X')
        state2, _ = StateUpdater.update_state(state1, 1, 5, 'O')
        state3, _ = StateUpdater.update_state(state2, 1, 2, 'X')
        state4, _ = StateUpdater.update_state(state3, 1, 9, 'O')
        state5, complete5 = StateUpdater.update_state(state4, 1, 3, 'X')

        assert complete5 == True, "X should win with top row."
        assert state5[0]['display'][1] == 'X', "Big board should show X won."

        assert len(state_checker._instance.checked_boards) > 0, \
            "Cache should have entries after moves."


    # A1 B2 C2
    def test_vary_a_single_move_mixed_hits_one_completion(self):
        state = StateGenerator.generate(_1='XX-------')
        state_checker = StateChecker()

        updated_state, board_complete = StateUpdater.update_state(state, 1, 3, 'X')

        assert board_complete == True, "Single move should complete board."
        assert updated_state[1]['display'] in state_checker._instance.checked_boards


    # A3 B2 C2
    def test_vary_a_different_boards_mixed_hits_one_completion(self):
        state = StateGenerator.generate(_1='XX-------', _2='---------', _3='---------')
        state_checker = StateChecker()

        state1, complete1 = StateUpdater.update_state(state, 2, 5, 'O')
        assert complete1 == False

        state2, complete2 = StateUpdater.update_state(state1, 3, 1, 'X')
        assert complete2 == False

        state3, complete3 = StateUpdater.update_state(state2, 1, 3, 'X')
        assert complete3 == True

        assert state1[2]['display'] in state_checker._instance.checked_boards
        assert state2[3]['display'] in state_checker._instance.checked_boards
        assert state3[1]['display'] in state_checker._instance.checked_boards


    # A2 B1 C2
    def test_vary_b_multiple_moves_all_misses_one_completion(self):
        state = StateGenerator.generate(_1='---------')
        state_checker = StateChecker()

        state1, _ = StateUpdater.update_state(state, 1, 1, 'X')
        state2, _ = StateUpdater.update_state(state1, 1, 5, 'O')
        state3, complete = StateUpdater.update_state(state2, 1, 2, 'X')

        assert state[1]['display'] != state1[1]['display'] != state2[1]['display'] != state3[1]['display']
        assert len(state_checker._instance.checked_boards) >= 3, \
            "Each unique board state should be cached."


    # A2 B3 C2
    def test_vary_b_multiple_moves_all_hits_one_completion(self):
        state = StateGenerator.generate(_1='XXX------')
        state_checker = StateChecker()

        # First call populates the cache
        result1 = state_checker.check_win(state, 1)
        cache_size_after_first = len(state_checker._instance.checked_boards)

        # Subsequent calls should hit cache - cache size should not change
        result2 = state_checker.check_win(state, 1)
        result3 = state_checker.check_win(state, 1)
        result4 = state_checker.check_win(state, 1)

        assert len(state_checker._instance.checked_boards) == cache_size_after_first, \
            "Cache size should not change on subsequent hits."
        assert result1 == result2 == result3 == result4 == 'X'


    # A2 B2 C1
    def test_vary_c_multiple_moves_mixed_hits_no_completions(self):
        state = StateGenerator.generate(_1='---------')
        state_checker = StateChecker()

        state1, complete1 = StateUpdater.update_state(state, 1, 1, 'X')
        state2, complete2 = StateUpdater.update_state(state1, 1, 5, 'O')
        state3, complete3 = StateUpdater.update_state(state2, 1, 9, 'X')
        state4, complete4 = StateUpdater.update_state(state3, 1, 3, 'O')

        assert not any([complete1, complete2, complete3, complete4]), \
            "No moves should complete the board."
        assert state4[0]['display'][1] == '-', "Big board should still show board 1 incomplete."


    # A2 B2 C3
    def test_vary_c_multiple_moves_mixed_hits_multiple_completions(self):
        state = StateGenerator.generate(_1='XX-------', _2='OO-------')
        state_checker = StateChecker()

        state1, complete1 = StateUpdater.update_state(state, 1, 3, 'X')
        assert complete1 == True, "Board 1 should be completed."

        state2, complete2 = StateUpdater.update_state(state1, 2, 3, 'O')
        assert complete2 == True, "Board 2 should be completed."

        assert state2[0]['display'][1] == 'X', "Big board should show X won board 1."
        assert state2[0]['display'][2] == 'O', "Big board should show O won board 2."

        assert state1[1]['display'] in state_checker._instance.checked_boards
        assert state2[2]['display'] in state_checker._instance.checked_boards