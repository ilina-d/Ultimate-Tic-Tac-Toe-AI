import pytest
from utils.helpers.state_checker import StateChecker


class TestStateChecker:
    """ Class to test the functionality of the StateChecker class. """

    @pytest.mark.parametrize("sign, positions, expected, error_msg", (
        ("X", (1, 2, 3), False, "X is not winning."),
        ("X", (1, 9, 5), "X", "X is winning (row)."),
        ("O", (6, 1, 8), "O", "O is winning (column)."),
        ("X", (7, 8, 3), False, "X is not winning, but sum to 15 present."),
        ("X", (), False, "X is not winning with no moves made."),
        ("O", (5, 6), False, "O is not winning (not enough moves)."),
        ("X", (5,), False, "X is not winning (not enough moves)."),
        ("X", (2, 7, 6, 9, 3), "X", "X is winning with extra spaces occupied."),
        ("X", (3, 7, 9, 6, 2), "X", "X is winning with sequence shuffled."),
        ("O", (8, 5, 2), "O", "O is winning (diagonal 1/2)."),
        ("X", (4, 6, 5), "X", "X is winning (diagonal 2/2)."),
        ("O", (4, 8, 6, 1, 3), "O", "O winning with more than one sequence."),
        ("X", (1, 2, 3, 4, 5, 6, 7, 8, 9), "X", "X winning with filled board."),
        ("O", (10, 2, 0, 1), False, "(1/4) Impossible positions."),
        ("O", (10, 5, 0, 1), False, "(2/4) Impossible positions."),
        ("O", (10, 2, 3, 1), False, "(3/4) Impossible positions."),
        ("O", (15, 7, 1, 2), False, "(4/4) Impossible positions."),
        ("O", (6, 6, 7, 3), False, "Doubled positions."),
    ))
    def test_check_win_helper(self, sign, positions, expected, error_msg):
        """ Tests whether the check_win_helper function works correctly. """

        assert StateChecker.check_win_helper(sign, positions) == expected, error_msg


    def test_check_win(self, state, big_idx, expected, error_msg):
        """ Tests whether the check_win function works correctly. """

        pass