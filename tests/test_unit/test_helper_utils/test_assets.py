import pytest
from utils.helpers.assets import inverse_board_display


class TestAssets:
    """ Class for testing the functionality of the assets module. """

    # BCC criteria:
    # A: symbols present on board
    #   1 - only X, 2 - only O, 3 - both X and O, 4 - neither X nor O, 5 - invalid characters present
    # B: board fullness
    #   1 - empty, 2 - partially full, 3 - completely full
    # happy path: A3 B2

    @pytest.mark.parametrize('original, expected, fail_msg', (
        # A3 B2 (happy path)
        (tuple('/XO-XO--XO'), tuple('/OX-OX--OX'), 'Result does not match expected outcome.'),
        # A1 B2
        (tuple('/XXX------'), tuple('/OOO------'), 'Invalid inversion of X-only board.'),
        # A2 B2
        (tuple('/OOO------'), tuple('/XXX------'), 'Invalid inversion of O-only board.'),
        # A2 B4 infeasible -> A4 B1
        (tuple('/---------'), tuple('/---------'), 'Empty board should remain unchanged.'),
        # A5 B2
        (tuple('/XO12XOT-!'), tuple('/OX12OXT-!'), 'Only X and O should be swapped.'),
        # A3 B1 infeasible -> A4 B1 (already covered)
        # A3 B3
        (tuple('/XOXXOXOXO'), tuple('/OXOOXOXOX'), 'Result does not match expected outcome.'),

        # extras:
        (tuple('/XOTXOT---'), tuple('/OXTOXT---'), 'Invalid inversion of board with ties.'),
        (tuple('/T-T-T----'), tuple('/T-T-T----'), 'Invalid inversion of tie-only board.'),
        (tuple('/XOXOXOT--'), tuple('/OXOXOXT--'), '(1/2) Double inversion should return original.'),
        (tuple('/OXOXOXT--'), tuple('/XOXOXOT--'), '(2/2) Double inversion should return original.'),

    ))
    def test_inverse_board_display(self, original, expected, fail_msg):
        """ Tests whether the board display inversion correctly swaps X and O. """

        assert inverse_board_display(original) == expected, fail_msg