import copy
import pytest

from utils.players.base_player import Player
from tests.sample_generator import SampleGenerator

class TestBasePlayer:
    """ Class to test the functionality of the Player class. """

    @pytest.fixture
    def test_player(self):
        """ Create a concrete Player implementation for testing. """

        class TestPlayer(Player):
            def make_move(self, *args, **kwargs):
                pass

        return TestPlayer()


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


    # Small amount of combinations, did them all

    @pytest.mark.parametrize("old_sign, new_sign, expected_sign, error_msg", (
        ("X", "X", "X", "Sign should remain unchanged."),
        ("X", "O", "O", "Sign should change from X to O."),
        ("O", "X", "X", "Sign should change from O to X."),
        ("X", "T", "X", "Sign should remain unchanged (Invalid sign 1/2)."),
        ("O", "R", "O", "Sign should remain unchanged (Invalid sign 2/2)."),
        (None, "O", "O", "Sign should be initially settable."),
    ))
    def test_set_sign(self, test_player, old_sign, new_sign, expected_sign, error_msg):
        """ Test whether set_sign is working correctly. """

        test_player.sign = old_sign
        test_player.set_sign(new_sign)

        assert test_player.sign == expected_sign, error_msg


    # BCC criteria:
    # A: board gets completed after update
    #   1 - true, 2 - false
    # B: big_idx has valid value
    #   1 - true, 2 - false
    # C: small_idx is present in legal moves of board
    #   1 - true, 2 - false
    # D: board setup
    #   1 - empty board, 2 - couple of moves made, 3 - couple of boards empty, 4 - couple of moves left, 5 - full board
    # E: small_idx has valid value
    #   1 - true, 2 - false
    # happy path: A2 B1 C1 D1 E1

    @pytest.mark.parametrize("big_idx, small_idx, board_is_complete, initial_moves_setup, error_msg", (
        # A2 B1 C1 D1 E1 (happy path) + extra
        (1, 1, False, "empty_board", "First move should be removed from legal_moves list (1/2)."),
        (5, 7, False, "empty_board", "First move should be removed from legal_moves list (2/2)."),
        # A1 B1 C1 D1 E1 infeasible -> A1 B1 C1 D4 E1
        (5, 9, True, "couple_moves_left", "Move that finishes board should render it unusable."),
        # A2 B2 C1 D1 E1 infeasible -> A2 B2 C2 D1 E1
        (12, 2, False, "empty_board", "Impossible move should not result in change on empty board (1/2)."),
        # A2 B1 C1 D1 E2 infeasible -> # A2 B1 C2 D1 E2
        (4, 81, False, "empty_board", "Impossible move should not result in change on empty board (2/2)."),
        # A2 B1 C2 D1 E1 infeasible -> A2 B1 C2 D2 E1
        (1, 2, False, "couple_moves_made", "Cannot make move that has already been made on a small board."),
        # A2 B1 C1 D2 E1
        (1, 3, False, "couple_moves_made", "Move should be removed form board that has moves made on it."),
        # A2 B1 C1 D3 E1
        (1, 2, False, "couple_boards_empty", "Move should be made on empty board mid-game."),
        # A2 B1 C1 D4 E1
        (4, 8, False, "couple_moves_left", "Move on unfinished board that does not complete it should be made."),
        # A2 B1 C1 D5 E1
        (8, 9, True, "full_board", "Board is full, legal moves should not be updated."),
    ))
    def test_update_legal_moves(self, test_player, big_idx, small_idx, board_is_complete, initial_moves_setup, error_msg):
        """ Test whether update_legal_moves is working correctly. """

        init_legal_moves = self.test_get_legal_moves(initial_moves_setup)
        expected_legal_moves = self.test_get_legal_moves(initial_moves_setup)

        if board_is_complete:
            for item in init_legal_moves[big_idx]:
                expected_legal_moves[big_idx].remove(item)
        else:
            if small_idx in expected_legal_moves[big_idx]: expected_legal_moves[big_idx].remove(small_idx)

        Player.legal_moves = init_legal_moves
        test_player.update_legal_moves(big_idx, small_idx, board_is_complete)
        result = Player.legal_moves

        assert result == expected_legal_moves, error_msg


    # BCC criteria:
    # A: prev_small_idx value
    #   1 - in range 1-9, 2 - out of range 1-9, 3 - None
    # B: board setup
    #   1 - empty board, 2 - couple of moves made, 3 - couple of boards empty, 4 - couple of moves left, 5 - full board
    # happy path: A1 B2

    @pytest.mark.parametrize("prev_small_idx, initial_moves_setup, error_msg", (
        # A1 B2 (happy path)
        (4, "couple_moves_made", "Should show remaining moves on started board."),
        # A2 B2 + extras
        (28, "couple_moves_made", "Should have no legal moves for impossible previous move (1/3)."),
        (33, "empty_board", "Should have no legal moves for impossible previous move (2/3)."),
        (11, "full_board", "Should have no legal moves for impossible previous move (3/3)."),
        # A3 B2 + extras
        (None, "couple_moves_made", "No previous small index should return all possible legal moves (1/3)."),
        (None, "empty_board", "No previous small index should return all possible legal moves (2/3)."),
        (None, "couple_moves_left", "No previous small index should return all possible legal moves (3/3)."),
        # A1 B1
        (1, "empty_board", "Should return all 9 moves on empty board (1/2)."),
        # A1 B3
        (8, "couple_boards_empty", "Should return all 9 moves on empty board (2/2)."),
        # A1 B4 + extra
        (4, "couple_moves_left", "Should show remaining moves (1/2)."),
        (5, "couple_moves_left", "Should show remaining moves (2/2)."),
        # A1 B5
        (8, "full_board", "Finished game should have no remaining legal moves."),
    ))
    def test_get_current_legal_moves(self, test_player, prev_small_idx, initial_moves_setup, error_msg):
        """ Test whether get_current_legal_moves is working correctly. """

        legal_moves = self.test_get_legal_moves(initial_moves_setup)

        moves = legal_moves[prev_small_idx] if prev_small_idx in range(1,10) else []

        expected = []

        for move in moves:
            expected.append((prev_small_idx, move))

        if prev_small_idx is None:
            index = -1
            for board in legal_moves:
                index += 1
                if board:
                    for move in board:
                        expected.append((index, move))


        Player.legal_moves = legal_moves
        result = test_player.get_current_legal_moves(prev_small_idx)

        assert result == expected, error_msg


    # BCC criteria:
    # A: prev_small_idx value
    #   1 - in range 1-9, 2 - out of range 1-9, 3 - None
    # B: board setup
    #   1 - empty board, 2 - couple of moves made, 3 - couple of boards empty, 4 - couple of moves left, 5 - full board
    # happy path: A1 B2

    @pytest.mark.parametrize("prev_small_idx, initial_moves_setup, error_msg", (
        # A1 B2 (happy path)
        (4, "couple_moves_made", "Should show remaining moves on started board."),
        # A2 B2 + extras
        (28, "couple_moves_made", "Should have no legal moves for impossible previous move (1/3)."),
        (33, "empty_board", "Should have no legal moves for impossible previous move (2/3)."),
        (11, "full_board", "Should have no legal moves for impossible previous move (3/3)."),
        # A3 B2 + extras
        (None, "couple_moves_made", "No previous small index should return all possible legal moves (1/3)."),
        (None, "empty_board", "No previous small index should return all possible legal moves (2/3)."),
        (None, "couple_moves_left", "No previous small index should return all possible legal moves (3/3)."),
        # A1 B1
        (1, "empty_board", "Should return all 9 moves on empty board (1/2)."),
        # A1 B3
        (8, "couple_boards_empty", "Should return all 9 moves on empty board (2/2)."),
        # A1 B4 + extra
        (4, "couple_moves_left", "Should show remaining moves (1/2)."),
        (5, "couple_moves_left", "Should show remaining moves (2/2)."),
        # A1 B5
        (8, "full_board", "Finished game should have no remaining legal moves."),
    ))
    def test_get_legal_moves_for_state(self, test_player, prev_small_idx, initial_moves_setup, error_msg):
        """ Test whether get_legal_moves_for_state is working correctly. """

        legal_moves = self.test_get_legal_moves(initial_moves_setup)
        state = self.test_get_state(initial_moves_setup)

        moves = legal_moves[prev_small_idx] if prev_small_idx in range(1, 10) else []

        expected = []

        for move in moves:
            expected.append((prev_small_idx, move))

        if prev_small_idx is None:
            index = -1
            for board in legal_moves:
                index += 1
                if board:
                    for move in board:
                        expected.append((index, move))

        Player.legal_moves = legal_moves
        result = test_player.get_legal_moves_for_state(state, prev_small_idx)

        assert result == expected, error_msg