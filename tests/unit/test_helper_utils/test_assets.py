import pytest
from utils.helpers.assets import inverse_board_display


class TestAssets:
    """ Class for testing the functionality of the assets module. """

    @pytest.mark.parametrize('original, expected, fail_msg', (
        (tuple('/XO-XO--XO'), tuple('/OX-OX--OX'), 'Result does not match expected outcome.'),
        (tuple('/---------'), tuple('/---------'), 'Empty board should remain unchanged.'),
        (tuple('/XXX------'), tuple('/OOO------'), 'Invalid inversion of X-only board.'),
        (tuple('/OOO------'), tuple('/XXX------'), 'Invalid inversion of O-only board.'),
        (tuple('/XOTXOT---'), tuple('/OXTOXT---'), 'Invalid inversion of board with ties.'),
        (tuple('/T-T-T----'), tuple('/T-T-T----'), 'Invalid inversion of tie-only board.'),
        (tuple('/XOXOXOT--'), tuple('/OXOXOXT--'), '(1/2) Double inversion should return original.'),
        (tuple('/OXOXOXT--'), tuple('/XOXOXOT--'), '(2/2) Double inversion should return original.'),
        (tuple('/XO12XOT-!'), tuple('/OX12OXT-!'), 'Only X and O should be swapped.'),
    ))
    def test_inverse_board_display(self, original, expected, fail_msg):
        """ Tests whether the board display inversion correctly swaps X and O. """

        assert inverse_board_display(original) == expected, fail_msg