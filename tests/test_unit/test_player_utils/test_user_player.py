import copy
import pytest
from unittest.mock import patch

from tests.sample_generator import SampleGenerator
from utils.players.user_player import UserPlayer


class TestUserPlayer:
    """ Class to test the functionality of the UserPlayer class. """

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
    # A: prev_small_idx value
    #   1 - in range 1-9, 2 - out of range 1-9, 3 - None
    # B: board setup
    #   1 - empty board, 2 - couple of moves made, 3 - couple of boards empty, 4 - couple of moves left, 5 - full board
    # C: user input validity
    #   1 - valid on first try, 2 - invalid then valid, 3 - multiple invalid then valid
    # happy path: A1 B2 C1

    @pytest.mark.parametrize("prev_small_idx, initial_moves_setup, user_inputs, error_msg", (
        # A1 B2 C1 (happy path)
        (2, "couple_moves_made", ["2 3"], "UserPlayer should accept valid move on first try."),
        # A1 B2 C2
        (2, "couple_moves_made", ["2 1", "2 3"], "UserPlayer should reject occupied cell and accept valid move."),
        # A1 B2 C3
        (2, "couple_moves_made", ["10 5", "2 20", "abc", "2 3"],
            "UserPlayer should handle multiple invalid inputs before accepting valid move."),
        # A2 B2 C1
        (45, "couple_moves_made", ["1 1"], "UserPlayer should handle out of range prev_small_idx."),
        # A3 B2 C1
        (None, "couple_moves_made", ["1 5"], "UserPlayer should accept any valid board when prev_small_idx is None."),
        # A3 B2 C2
        (None, "couple_moves_made", ["9 1", "1 5"],
            "UserPlayer should reject completed board and accept valid move on open board."),
        # A1 B1 C1
        (4, "empty_board", ["4 5"], "UserPlayer should accept valid move on empty board."),
        # A1 B1 C2
        (4, "empty_board", ["5 5", "4 5"],
            "UserPlayer should reject wrong board index and accept correct one on empty board."),
        # A1 B3 C1
        (1, "couple_boards_empty", ["1 7"], "UserPlayer should accept valid move on empty board mid-game."),
        # A1 B4 C1
        (5, "couple_moves_left", ["5 9"], "UserPlayer should accept the last available move on a board."),
        # A1 B4 C2
        (5, "couple_moves_left", ["5 1", "5 9"],
            "UserPlayer should reject occupied position and accept available move."),
    ))
    @patch('builtins.input')
    def test_make_move(self, mock_input, prev_small_idx, initial_moves_setup, user_inputs, error_msg):
        """ Test whether UserPlayer correctly validates and accepts moves. """

        legal_moves = self.test_get_legal_moves(initial_moves_setup)
        state = self.test_get_state(initial_moves_setup)

        mock_input.side_effect = user_inputs

        player = UserPlayer()
        player.legal_moves = legal_moves

        (big_idx, small_idx) = player.make_move(state, prev_small_idx)

        assert small_idx in legal_moves[big_idx], error_msg
        assert state[big_idx]['display'][small_idx] == '-', "UserPlayer should only select empty cells."
        assert state[0]['display'][big_idx] == '-', "UserPlayer should only select from non-completed boards."

        if prev_small_idx is not None and prev_small_idx in range(1, 10) and state[0]['display'][prev_small_idx] == '-':
            assert big_idx == prev_small_idx, "UserPlayer should make move on correct board when prev_small_idx is valid."


    @pytest.mark.parametrize("invalid_inputs, valid_input, expected_error_count", (
        (["abc"], "1 1", 1),
        (["10 10"], "1 1", 1),
        (["1"], "1 1", 1),
        (["", "  "], "1 1", 2),
        (["0 0", "-1 5", "11 11"], "1 1", 3),
    ))
    @patch('builtins.print')
    @patch('builtins.input')
    def test_invalid_input_handling(self, mock_input, mock_print, invalid_inputs, valid_input, expected_error_count):
        """ Additional tests for handling various invalid inputs and checking error messages. """

        state = self.test_get_state("empty_board")
        legal_moves = self.test_get_legal_moves("empty_board")

        mock_input.side_effect = invalid_inputs + [valid_input]

        player = UserPlayer()
        player.legal_moves = legal_moves

        player.make_move(state, 1)

        error_calls = [call for call in mock_print.call_args_list if '--- Invalid move... 🙄' in str(call)]
        assert len(error_calls) == expected_error_count, f"Expected {expected_error_count} error messages for invalid inputs."