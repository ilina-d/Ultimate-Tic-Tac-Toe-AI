from unittest.mock import patch, Mock

import pytest

from utils.helpers.state_updater import StateUpdater
from tests.state_generator import StateGenerator
from utils.helpers.state_checker import StateChecker

class TestStateUpdater:
    """ Class to test the functionality of the StateUpdater class. """

    @pytest.mark.parametrize("state, big_idx, small_idx, sign, return_check_win, expected, error_msg", (
        (StateGenerator.generate(_1='-X--O--OO'), 1, 3, "X", False, StateGenerator.generate(_0='---------', _1='-XX-O--OO'),
         "Move should be made on small board 1 and it should not be won."),

        (StateGenerator.generate(_5='O--XX----'), 5, 6, "X", "X", StateGenerator.generate(_0='----X----', _5='O--XXX---'),
         "Move should be made on small board and it should be won (row)."),

        (StateGenerator.generate(_4='XO--OX---'), 4, 8, "O", "O", StateGenerator.generate(_0='---O-----', _4='XO--OX-O-'),
         "Move should be made on small board and it should be won (column)."),

        (StateGenerator.generate(_9='----O---O'), 9, 1, "O", "O", StateGenerator.generate(_0='--------O', _9='O---O---O'),
         "Move should be made on small board and it should be won (diagonal 1/2)."),

        (StateGenerator.generate(_8='OOX-X----'), 8, 7, "X", "X", StateGenerator.generate(_0='-------X-', _8='OOX-X-X--'),
         "Move should be made on small board and it should be won (diagonal 2/2)."),

        (StateGenerator.generate(_2='-X-X-X-XO'), 2, 5, "X", "X", StateGenerator.generate(_0='-X-------', _2='-X-XXX-XO'),
         "Move should be made on small board and it should be won (multiple win combination)."),

        (StateGenerator.generate(_3='X-XOXOOXO'), 3, 2, "O", "T", StateGenerator.generate(_0='--T------', _3='XOXOXOOXO'),
         "Move should be made on small board and it should be tied."),

        (StateGenerator.generate(_9='----O---O'), 9, 9, "X", False, StateGenerator.generate(_0='---------', _9='----O---O'),
         "Move should not rewrite already made move on small board."),

        (StateGenerator.generate(_6='XXX------'), 6, 8, "0", False, StateGenerator.generate(_0='-----X---', _9='XXX------'),
         "Move should be playable on won board."),

        (StateGenerator.generate(_6='XXX------'), 6, 1, "0", False, StateGenerator.generate(_0='-----X---', _9='XXX------'),
         "Move should be able to alter a won sequence."),

        (StateGenerator.generate(_3='XOXOXOOXO'), 3, 1, "O", "T", StateGenerator.generate(_0='--T------', _3='XOXOXOOXO'),
         "Move should playable on a completed board."),

        (StateGenerator.generate(), 12, 7, "O", False, StateGenerator.generate(),
         "Move with big_idx>9 should not be playable."),

        (StateGenerator.generate(), 2, 21, "O", False, StateGenerator.generate(),
         "Move with small_idx>9 should not be playable."),
    ))
    def test_update_state(self, state, big_idx, small_idx, sign, return_check_win, expected, error_msg):
        """ Tests whether state gets updated correctly. """

        with patch.object(StateChecker, 'check_win', return_value=return_check_win):
            result, board_is_complete = StateUpdater.update_state(state, big_idx, small_idx, sign)

        for i in range(10):
            assert expected[i]['display'] == result[i]['display']

        if return_check_win:
            assert board_is_complete
        else:
            assert not board_is_complete