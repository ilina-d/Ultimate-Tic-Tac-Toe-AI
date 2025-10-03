import pytest
from unittest.mock import Mock, patch

from utils.helpers.state_checker import StateChecker
from tests.state_generator import StateGenerator


class TestStateChecker:
    """ Class to test the functionality of the StateChecker class. """

    # BCC criteria:
    # A: number of positions occupied
    #   1 - zero, 2 - one, 3 - two, 4 - three or more
    # B: has sum 15
    #   1 - true , 2 - false
    # C: has winning combination
    #   1 - true, 2 - false
    #   11 - one winning sequence, 12 - more than one winning sequence
    # D: makeup of positions
    #   1 - all in range 1-9, 2 - elements present out of range 1-9
    #   11 - all unique, 12 - duplicates present
    # happy path: A4 B1 C11 D11

    @pytest.mark.parametrize("sign, positions, expected, error_msg", (
        # A4 B1 C11 D11 (happy path) + extras
        ("X", (1, 9, 5), "X", "X should be winning (row)."),
        ("O", (6, 1, 8), "O", "O should be winning (column)."),
        ("O", (8, 5, 2), "O", "O should be winning (diagonal 1/2)."),
        ("X", (4, 6, 5), "X", "X should be winning (diagonal 2/2)."),
        # A1 B1 C11 D11 infeasible -> A1 B2 C11 D11 -> A1 B2 C2 D11
        ("X", (), False, "X should not be winning with no moves made."),
        # A2 B1 C11 D11 infeasible -> A2 B2 C11 D11 -> A2 B2 C2 D11
        ("X", (5,), False, "X should not be winning (not enough moves)."),
        # A3 B1 C11 D11 infeasible -> A3 B2 C11 D11 -> A3 B2 C2 D11
        ("O", (5, 6), False, "O should not be winning (not enough moves)."),
        # A4 B2 C11 D11 infeasible -> A4 B2 C2 D11
        ("X", (1, 2, 3), False, "X should not be winning."),
        # A4 B1 C12 D11
        ("O", (4, 8, 6, 1, 3), "O", "O should be winning with more than one sequence."),
        # A4 B1 C2 D11
        ("X", (7, 8, 3), False, "X should not be winning, but sum to 15 present."),
        # A4 B1 C11 D12 infeasible -> A4 B1 C12 D12
        ("O", (6, 6, 7, 3), False, "Doubled positions."),
        # A4 B1 C11 D2 infeasible -> A4 B1 C12 D2
        ("O", (10, 2, 0, 1), False, "(1/4) Impossible positions."),
        # extras:
        ("O", (10, 5, 0, 1), False, "(2/4) Impossible positions."),
        ("O", (10, 2, 3, 1), False, "(3/4) Impossible positions."),
        ("O", (15, 7, 1, 2), False, "(4/4) Impossible positions."),
        ("X", (2, 7, 6, 9, 3), "X", "X should be winning with extra spaces occupied."),
        ("X", (3, 7, 9, 6, 2), "X", "X should be winning with sequence shuffled."),
        ("X", (1, 2, 3, 4, 5, 6, 7, 8, 9), "X", "X should be winning with filled board."),
    ))
    def test_check_win_helper(self, sign, positions, expected, error_msg):
        """ Tests whether the check_win_helper function works correctly. """

        assert StateChecker.check_win_helper(sign, positions) == expected, error_msg


    # BCC criteria:
    # A: board being checked
    #   1 - big board, 2 - small board
    # B: board has been checked before
    #   1 - true, 2 - false
    # C: board is complete
    #   1 - true (win), 2 - true (tie), 3 - false
    #   11 - row, 12 - column, 13 - diagonal, 14 - multiple win sequence
    # happy path: A1 B2 C3

    @pytest.mark.parametrize("state, big_idx, return_checked, return_helper, return_inverse, expected, error_msg", (
            # A1 B2 C3 (happy path)
            (StateGenerator.generate('XOX------'), 0, None, False, tuple('/OXO------'), False,
             "There shouldn't be a winner yet on the big board."),
            # A2 B2 C3
            (StateGenerator.generate(_1='XOX-----X'), 1, None, False, tuple('/OXO-----O'), False,
             "There shouldn't be a winner yet on small board 1."),
            # A1 B1 C3
            (StateGenerator.generate('XOX------'), 0, False, False, tuple('/OXO------'), False,
             "There shouldn't be a winner yet on the big board, but it's cached."),
            # A1 B2 C11
            (StateGenerator.generate('XXX---O--'), 0, None, 'X', tuple('OOO---X--'), 'X',
             "X should be winning on the big board (row)."),
            # A1 B2 C12
            (StateGenerator.generate('X-X--XO-X'), 0, None, 'X', tuple('O-O--OX-O'), 'X',
             "X should be winning on the big board (column)."),
            # A1 B2 C13
            (StateGenerator.generate('--O-O-O--'), 0, None, 'O', tuple('/--X-X-X--'), 'O',
             "O should be winning on the big board (diagonal 1/2)."),
            (StateGenerator.generate('XO--X---X'), 0, None, 'X', tuple('/OX--O---O'), 'X',
             "X should be winning on the big board (diagonal 2/2)."),
            # A1 B2 C14
            (StateGenerator.generate('X-O-O-OOO'), 0, None, 'O', tuple('/O-X-X-XXX'), 'O',
             "O should be winning (in more than one way)."),
            # A1 B2 C2
            (StateGenerator.generate('XOXOXOOXO'), 0, None, 'T', tuple('/OXOXOXXOX'), 'T',
             "There should be a tie on the big board."),

            # extras:
            (StateGenerator.generate('-X-------', _2='X--X--XOO'), 2, None, 'X', tuple('/O--O--OXX'), 'X',
             "X should be winning on small board 2 (column)."),

            (StateGenerator.generate('------O--', _7='OOO------'), 7, None, 'O', tuple('/XXX------'), 'O',
             "O should be winning on small board 7."),

            (StateGenerator.generate('---T-----', _4='XOXOXOOXO'), 4, None, 'T', tuple('/OXOXOXXOX'), 'T',
             "There should be a tie on small board 4."),

            (StateGenerator.generate('XOX------'), 0, 'X', None, tuple('/OXO------'), 'X',
             "Cached board was not found in cache (X)."),

            (StateGenerator.generate('OXO------'), 0, 'O', None, tuple('/XOX------'), 'O',
             "Cached board was not found in cache (O)."),

            (StateGenerator.generate('XXX------'), 0, 'T', None, tuple('/OOO------'), 'T',
             "Cached board was not found in cache (T)."),

            (StateGenerator.generate(), 0, None, False, tuple('/---------'), False,
             "A completely empty board shouldn't have a winner nor a tie."),

            (StateGenerator.generate(), 1, None, False, tuple('/---------'), False,
             "An empty small board shouldn't have a winner nor a tie."),
    ))
    def test_check_win(self, state, big_idx, return_checked, return_helper, return_inverse, expected, error_msg):
        """ Tests whether the check_win function works correctly. """

        sc = StateChecker()
        sc._instance.checked_boards = {}

        if return_checked:
            sc._instance.checked_boards = {state[big_idx]['display']: return_checked}

        sc.check_win_helper = Mock(return_value=return_helper)

        with patch('utils.helpers.state_checker.inverse_board_display', return_value=return_inverse):
            result = sc.check_win(state, big_idx)

        assert result == expected, error_msg