import copy
import pytest

from tests.sample_generator import SampleGenerator
from utils.players.random_player import RandomPlayer

class TestRandomPlayer:
    """ Class to test the functionality of the RandomPlayer class. """

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
    # happy path: A1 B2

    @pytest.mark.parametrize("prev_small_idx, initial_moves_setup, error_msg", (
        # A1 B2 (happy path)
        (2, "couple_moves_made", "RandomPlayer should choose one of nine available moves."),
        # A2 B2
        (45, "couple_moves_made", "RandomPlayer should not make move when index is out of range."),
        # A3 B2
        (None, "couple_moves_made", "RandomPlayer should make one of any available moves on the board."),
        # A1 B1
        (4, "empty_board", "Random player should choose one of nine available moves on an empty board."),
        # A1 B3,
        (1, "couple_boards_empty", "RandomPlayer should choose one of nine available moves mid-game."),
        # A1 B4
        (5, "couple_moves_left", "RandomPlayer should choose the only available move left."),
        # A1 B5
        (9, "full_board", "RandomPLayer should not make move on a full board."),
    ))
    def test_make_move(self, prev_small_idx, initial_moves_setup, error_msg):
        """ Test weather RandomPlayer makes legal moves. """

        legal_moves = self.test_get_legal_moves(initial_moves_setup)
        state = self.test_get_state(initial_moves_setup)

        player = RandomPlayer()
        player.legal_moves = legal_moves

        # TODO: maybe mock get_current_legal_moves

        # with patch.object(player, 'get_current_legal_moves', return_value=legal_moves):
        #     move = player.make_move(state, prev_small_idx)

        (big_idx, small_idx) = player.make_move(state, prev_small_idx)

        assert small_idx in legal_moves[big_idx], error_msg

        if prev_small_idx is not None:
            assert big_idx == prev_small_idx, ("RandomPlayer should make legal move on correct small board unless "
                                               "it is sent to a completed board.")