import copy
import pytest

from utils.players.base_player import Player
from tests.state_generator import StateGenerator

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
    def test_mock_legal_moves(cls):
        """ Create a dictionary of multiple legal move scenarios for testing. """
        cls.legal_moves = dict()

        cls.legal_moves["empty_board"] = [[i for i in range(1, 10)] for _ in range(1, 10)]
        cls.legal_moves["empty_board"].insert(0, [])

        cls.legal_moves["full_board"] = [[] for _ in range(1, 11)]

        cls.legal_moves["couple_boards_empty"] = [[] for _ in range(1, 7)]
        cls.legal_moves["couple_boards_empty"].insert(1, [i for i in range(1, 10)])
        cls.legal_moves["couple_boards_empty"].insert(2, [i for i in range(1, 10)])
        cls.legal_moves["couple_boards_empty"].insert(4, [i for i in range(1, 10)])
        cls.legal_moves["couple_boards_empty"].insert(8, [i for i in range(1, 10)])

        cls.legal_moves["couple_moves_left"] = [[] for _ in range(1, 6)]
        cls.legal_moves["couple_moves_left"].insert(3, [1, 2, 7, 6])
        cls.legal_moves["couple_moves_left"].insert(4, [8, 9])
        cls.legal_moves["couple_moves_left"].insert(5, [9, ])
        cls.legal_moves["couple_moves_left"].insert(7, [1, 2, 3, 4, 5])
        cls.legal_moves["couple_moves_left"].insert(9, [2, ])

        cls.legal_moves["couple_moves_made"] = [[i for i in range(1, 10)] for _ in range(1, 10)]
        cls.legal_moves["couple_moves_made"].insert(0, [])
        cls.legal_moves["couple_moves_made"][4].remove(4)
        cls.legal_moves["couple_moves_made"][4].remove(9)
        cls.legal_moves["couple_moves_made"][9].remove(1)
        cls.legal_moves["couple_moves_made"][1].remove(2)


    def test_get_legal_moves(self, desc):
        """ Get legal moves mock for specific test scenario."""

        return copy.deepcopy(self.legal_moves[desc])


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

    @pytest.mark.parametrize("big_idx, small_idx, board_is_complete, initial_moves_setup, error_msg", (
        (1, 1, False, "empty_board", "First move should be removed from legal_moves list (1/2)."),
        (5, 7, False, "empty_board", "First move should be removed from legal_moves list (2/2)."),
        (12, 2, False, "empty_board", "Impossible move should not result in change on empty board (1/2)."),
        (4, 81, False, "empty_board", "Impossible move should not result in change on empty board (2/2)."),
        (8, 9, True, "full_board", "Board is full, legal moves should not be updated."),
        (13, 21, True, "full_board", "Impossible move should not result in change on full board."),
        (5, 9, True, "couple_moves_left", "Move that finishes board should render it unusable."),
        (3, 7, False, "couple_boards_empty", "Board is full, legal moves should not be updated."),
        (4, 4, False, "couple_moves_left", "Move on unfinished board that is occupied should not change legal moves."),
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

    @pytest.mark.parametrize("prev_small_idx, initial_moves_setup, error_msg", (
        (1, "empty_board", "Should return all 9 moves on empty board."),
        (8, "full_board", "Finished game should have no remaining legal moves."),
        (33, "empty_board", "Should have no legal moves for impossible previous move (1/2)."),
        (11, "full_board", "Should have no legal moves for impossible previous move (2/2)."),
        (4, "couple_moves_left", "Should show remaining moves (1/4)."),
        (5, "couple_moves_left", "Should show remaining moves (2/4)."),
        (4, "couple_moves_made", "Should show remaining moves (3/4)"),
        (1, "couple_moves_made", "Should show remaining moves (4/4)"),
        (None, "empty_board", "No previous small index should return all possible legal moves (1/3)."),
        (None, "full_board", "No previous small index should return all possible legal moves (2/3)."),
        (None, "couple_moves_left", "No previous small index should return all possible legal moves (3/3)."),
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


    @pytest.mark.parametrize("state, prev_small_idx, initial_moves_setup, error_msg", (
        (StateGenerator.generate(), 1, "empty_board", "Should return all 9 moves on empty board."),

        (StateGenerator.generate(_0='XOXOXXTTX', _1='---XXX---', _2='OOO------', _3='---XXX---', _4='O--O--O--', _5='XXX------', _6='X---X---X', _7='XOOOXXXOO', _8='XOOOXXXOO', _9='XXX------'),
            8, "full_board", "Finished game should have no remaining legal moves."),

        (StateGenerator.generate(), 33, "empty_board", "Should have no legal moves for impossible previous move (1/2)."),

        (StateGenerator.generate(_0='XOXOXXTTX', _1='---XXX---', _2='OOO------', _3='---XXX---', _4='O--O--O--', _5='XXX------', _6='X---X---X', _7='XOOOXXXOO', _8='XOOOXXXOO', _9='XXX------'),
            11, "full_board", "Should have no legal moves for impossible previous move (2/2)."),

        (StateGenerator.generate(_0='XO---X-T-', _1='---XXX---', _2='OOO------', _3='--XOX--OO', _4='XOXOXOO--', _5='XOXOXOOX-', _6='X---X---X', _7='-----XXOO', _8='XOOOXXXOO', _9='X-XOXOOXO'),
            4, "couple_moves_left", "Should show remaining moves (1/4)."),

        (StateGenerator.generate(_0='XO---X-T-', _1='---XXX---', _2='OOO------', _3='--XOX--OO', _4='XOXOXOO--', _5='XOXOXOOX-', _6='X---X---X', _7='-----XXOO', _8='XOOOXXXOO', _9='X-XOXOOXO'),
            5, "couple_moves_left", "Should show remaining moves (2/4)."),

        (StateGenerator.generate(_1='-O-------', _4='---X----O', _9='X--------'),

            4, "couple_moves_made", "Should show remaining moves (3/4)"),

        (StateGenerator.generate(_1='-O-------', _4='---X----O', _9='X--------'),
            1, "couple_moves_made", "Should show remaining moves (4/4)"),

        (StateGenerator.generate(), None, "empty_board", "No previous small index should return all possible legal moves (1/3)."),

        (StateGenerator.generate(_0='XOXOXXTTX', _1='---XXX---', _2='OOO------', _3='---XXX---', _4='O--O--O--', _5='XXX------', _6='X---X---X', _7='XOOOXXXOO', _8='XOOOXXXOO', _9='XXX------'),
            None, "full_board", "No previous small index should return all possible legal moves (2/3)."),

        (StateGenerator.generate(_0='XO---X-T-', _1='---XXX---', _2='OOO------', _3='--XOX--OO', _4='XOXOXOO--', _5='XOXOXOOX-', _6='X---X---X', _7='-----XXOO', _8='XOOOXXXOO', _9='X-XOXOOXO'),
            None, "couple_moves_left", "No previous small index should return all possible legal moves (3/3)."),
    ))
    def test_get_legal_moves_for_state(self, test_player, state, prev_small_idx, initial_moves_setup, error_msg):
        """ Test whether get_legal_moves_for_state is working correctly. """

        legal_moves = self.test_get_legal_moves(initial_moves_setup)

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