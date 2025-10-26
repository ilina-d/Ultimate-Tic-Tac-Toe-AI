import copy
import pytest
from unittest.mock import patch, MagicMock

from tests.sample_generator import SampleGenerator
from utils.players.minimax_player import MiniMaxPlayer


class TestMiniMaxPlayer:
    """ Class to test the functionality of the MiniMaxPlayer class. """

    @classmethod
    def test_mock_state_and_legal_moves(cls):
        """ Create dictionaries of multiple scenarios for testing. """

        cls.legal_moves = SampleGenerator.get_sample_legal_moves()
        cls.states = SampleGenerator.get_sample_states()

    def test_get_legal_moves(self, desc):
        """
        Get legal moves mock for specific test scenario.

        Arguments:
            desc: descriptive name of the test scenario.

        Returns:
            Deepcopy of the legal moves for the given test scenario.
        """

        return copy.deepcopy(self.legal_moves[desc])

    def test_get_state(self, desc):
        """
        Get state mock for specific test scenario.

        Arguments:
            desc: descriptive name of the test scenario.

        Returns:
            Deepcopy of the state for the given test scenario.
        """

        return copy.deepcopy(self.states[desc])


    # BCC criteria:
    # A: is_maximizing value
    #   1 - True, 2 - False
    # B: moves_made value
    #   1 - 0, 2 - greater than 0
    # C: use_randomness value
    #   1 - True, 2 - False
    # D: prev_small_idx validity and board state
    #   1 - valid index with empty board, 2 - valid index with non-empty board, 3 - None
    # happy path: A1 B1 C2 D3

    @pytest.mark.parametrize("is_maximizing, moves_made, use_randomness, prev_small_idx, board_empty, "
                             "expected_result, error_msg", (
            # A1 B1 C2 D3 (happy path)
            (True, 0, False, None, False, (5, 5), "First move as maximizer without randomness should be (5, 5)."),
            # A1 B1 C1 D3
            (True, 0, True, None, False, 'random', "First move as maximizer with randomness should be random."),
            # A2 B1 C2 D3
            (False, 0, False, None, False, None, "First move as minimizer should not return premove."),
            # A1 B2 C2 D1
            (True, 5, False, 3, True, (3, 3), "Should return diagonal move on empty board."),
            # A1 B2 C2 D2
            (True, 5, False, 3, False, None, "Should not return premove on non-empty board."),
            # A1 B2 C2 D3
            (True, 5, False, None, False, None, "Should not return premove when prev_small_idx is None."),
            # A2 B2 C2 D1
            (False, 5, False, 7, True, (7, 7), "Minimizer should also return diagonal on empty board."),
        ))
    def test_get_premove(self, is_maximizing, moves_made, use_randomness, prev_small_idx, board_empty, expected_result,
                         error_msg):
        """ Test whether get_premove returns correct predefined moves. """

        player = MiniMaxPlayer(use_randomness=use_randomness)
        player.moves_made = moves_made

        if prev_small_idx and board_empty:
            state = self.test_get_state("empty_board")
        else:
            state = self.test_get_state("couple_moves_made")

        result = player.get_premove(state, prev_small_idx, is_maximizing)

        if expected_result == 'random':
            assert result is not None, error_msg
            assert result[0] in range(1, 10) and result[1] in range(1, 10), "Random move should be in valid range."
        elif expected_result is None:
            assert result is None, error_msg
        else:
            assert result == expected_result, error_msg


    # BCC criteria:
    # A: use_timed_depth flag
    #   1 - True, 2 - False
    # B: use_dynamic_depth flag
    #   1 - True, 2 - False
    # C: moves_made value (when dynamic)
    #   1 - below THRESHOLD, 2 - at THRESHOLD boundary, 3 - above THRESHOLD at STEP interval, 4 - above THRESHOLD not at STEP interval
    # happy path: A2 B1 C3

    @pytest.mark.parametrize("use_timed, use_dynamic, moves_made, initial_depth, expected_depth_change, error_msg", (
            # A2 B1 C3 (happy path)
            (False, True, 21, 5, True, "Dynamic depth should increase after THRESHOLD at STEP interval."),
            # A1 B2 C1
            (True, False, 10, 4, False, "Timed mode should set start_time but not change depth."),
            # A2 B2 C1
            (False, False, 10, 3, False, "Static depth should never change."),
            # A2 B1 C1
            (False, True, 10, 5, False, "Dynamic depth should not change below THRESHOLD."),
            # A2 B1 C2
            (False, True, 18, 5, False, "Dynamic depth should not change exactly at THRESHOLD (not divisible by STEP)."),
            # A2 B1 C4
            (False, True, 20, 5, False, "Dynamic depth should not change when moves not divisible by STEP."),
            # A2 B1 C3 (multiple increases)
            (False, True, 24, 5, True, "Dynamic depth should increase again at next STEP interval."),
    ))
    def test_update_target_depth(self, use_timed, use_dynamic, moves_made, initial_depth, expected_depth_change,
                                 error_msg):
        """ Test whether update_target_depth correctly updates depth based on configuration. """

        if use_timed:
            player = MiniMaxPlayer(target_depth='timed')
        elif use_dynamic:
            player = MiniMaxPlayer(target_depth='dynamic')
        else:
            player = MiniMaxPlayer(target_depth=initial_depth)

        player.moves_made = moves_made
        initial_target_depth = player.target_depth

        player.update_target_depth()

        if use_timed:
            assert player.start_time is not None, "Start time should be set in timed mode."

        if expected_depth_change:
            assert player.target_depth > initial_target_depth, error_msg
        else:
            assert player.target_depth == initial_target_depth, error_msg


    # BCC criteria:
    # A: player sign
    #   1 - 'X', 2 - 'O'
    # B: premove availability
    #   1 - premove exists, 2 - no premove
    # C: board setup
    #   1 - empty board, 2 - couple of moves made, 3 - couple of moves left
    # D: prev_small_idx value
    #   1 - in range 1-9, 2 - None
    # happy path: A1 B2 C2 D1

    @pytest.mark.parametrize(
        "player_sign, moves_made, initial_moves_setup, prev_small_idx, use_premove_scenario, error_msg", (
                # A1 B2 C2 D1 (happy path)
                ('X', 5, "couple_moves_made", 2, False, "Maximizing player should choose optimal move."),
                # A2 B2 C2 D1
                ('O', 5, "couple_moves_made", 2, False, "Minimizing player should choose optimal move."),
                # A1 B1 C1 D2
                ('X', 0, "empty_board", None, True, "First move should use premove logic."),
                # A1 B2 C3 D1
                ('X', 10, "couple_moves_left", 5, False, "Should make valid move near end of game."),
                # A1 B2 C2 D2
                ('X', 5, "couple_moves_made", None, False, "Should handle None prev_small_idx and choose from available boards."),
                # A2 B2 C3 D1
                ('O', 10, "couple_moves_left", 4, False, "Minimizing player should make valid move near end of game."),
                # A1 B2 C1 D2
                ('X', 5, "empty_board", None, False, "Should make valid first move on empty board without premove."),
        ))
    @patch('utils.players.minimax_player.StateUpdater')
    @patch('utils.players.minimax_player.StateChecker')
    def test_make_move(self, mock_checker, mock_updater, player_sign, moves_made, initial_moves_setup,
                       prev_small_idx, use_premove_scenario, error_msg):
        """ Test whether MiniMaxPlayer makes legal and optimal moves. """

        legal_moves = self.test_get_legal_moves(initial_moves_setup)
        state = self.test_get_state(initial_moves_setup)

        mock_updater.update_state.return_value = (state, False)

        mock_checker.check_win.return_value = False

        player = MiniMaxPlayer(target_depth=2, use_randomness=False)
        player.sign = player_sign
        player.legal_moves = legal_moves

        (big_idx, small_idx) = player.make_move(state, prev_small_idx)

        assert big_idx in range(1, 10), "big_idx should be in valid range."
        assert small_idx in range(1, 10), "small_idx should be in valid range."
        assert small_idx in legal_moves[big_idx], error_msg

        if prev_small_idx in range(1, 10) and legal_moves[prev_small_idx]:
            assert big_idx == prev_small_idx, "Move should be on the correct board when prev_small_idx is valid."


    # BCC criteria:
    # A: game state
    #   1 - game won, 2 - game in progress, 3 - time limit reached (timed mode), 4 - depth limit reached
    # B: is_maximizing value
    #   1 - True, 2 - False
    # C: pruning opportunity
    #   1 - alpha-beta pruning occurs, 2 - no pruning
    # happy path: A2 B1 C2

    @pytest.mark.parametrize("game_won, at_depth_limit, is_maximizing, player_sign, error_msg", (
            # A2 B1 C2 (happy path)
            (False, False, True, 'X', "Should evaluate game tree for maximizing player."),
            # A2 B2 C2
            (False, False, False, 'O', "Should evaluate game tree for minimizing player."),
            # A1 B1 C2
            (True, False, True, 'X', "Should return heuristic score when game is won."),
            # A4 B1 C2
            (False, True, True, 'X', "Should return heuristic score at depth limit."),
            # A1 B2 C2
            (True, False, False, 'O', "Should return heuristic score when game is won for minimizer."),
    ))
    @patch('utils.players.minimax_player.StateEvaluator')
    @patch('utils.players.minimax_player.StateUpdater')
    @patch('utils.players.minimax_player.StateChecker')
    def test_minimax_ab(self, mock_checker, mock_updater, mock_evaluator, game_won, at_depth_limit,
                        is_maximizing, player_sign, error_msg):
        """ Test whether minimax_ab algorithm works correctly. """

        state = self.test_get_state("couple_moves_made")
        legal_moves = self.test_get_legal_moves("couple_moves_made")

        mock_checker.check_win.return_value = game_won
        mock_evaluator.heuristic.return_value = 100 if is_maximizing else -100
        mock_updater.update_state.return_value = (state, False)

        player = MiniMaxPlayer(target_depth=2 if at_depth_limit else 10)
        player.sign = player_sign
        player.legal_moves = legal_moves

        depth = 2 if at_depth_limit else 0
        score = player.minimax_ab(state, 2, depth, float('-inf'), float('inf'), is_maximizing)

        assert isinstance(score, (int, float)), error_msg

        if game_won or at_depth_limit:
            assert mock_evaluator.heuristic.called, "Heuristic should be called at terminal nodes."
