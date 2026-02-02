import pytest

from tests.state_generator import StateGenerator
from utils.players.minimax_player import MiniMaxPlayer
from utils.players.base_player import Player


class TestMiniMaxPrimePaths:
    """
    Prime Path Coverage integration tests for MiniMaxPlayer.make_move method.
    """

    @pytest.fixture(autouse=True)
    def reset_legal_moves(self):
        """Reset legal moves before each test to ensure clean state."""
        Player.reset_legal_moves()
        yield
        Player.reset_legal_moves()

    def test_path_1(self):
        """
        Path 1: 1 → 2 → 4 → 5
        """
        player = MiniMaxPlayer(target_depth=3, use_randomness=False)
        player.sign = 'X'
        player.moves_made = -1

        state = StateGenerator.generate()

        big_idx, small_idx = player.make_move(state, None)

        assert (big_idx, small_idx) == (5, 5)


    def test_path_2(self):
        """
        Path 2: 1 → 3 → 4 → 5
        """
        player = MiniMaxPlayer(target_depth=3, use_randomness=False)
        player.sign = 'X'
        player.moves_made = 5

        state = StateGenerator.generate()

        big_idx, small_idx = player.make_move(state, 7)

        assert (big_idx, small_idx) == (7, 7)


    def test_path_25_27(self):
        """
        Paths 25, 27: 1 → 2 → 4 → 6 → 7 → 9 → 11 and 1 → 3 → 4 → 6 → 7 → 9 → 11
        """
        player = MiniMaxPlayer(target_depth=2, use_randomness=False)
        player.sign = 'X'
        player.moves_made = 10

        state = StateGenerator.generate(
            _0='XOXOXOXOX',
            _1='XOXOXOXOX', _2='XOXOXOXOX', _3='XOXOXOXOX',
            _4='XOXOXOXOX', _5='XOXOXOXOX', _6='XOXOXOXOX',
            _7='XOXOXOXOX', _8='XOXOXOXOX', _9='XOXOXOXOX'
        )

        Player.legal_moves = [[] for _ in range(10)]

        result = player.make_move(state, 5)

        assert result is None


    def test_path_26_28(self):
        """
        Paths 26, 28: 1 → 2 → 4 → 6 → 8 → 9 → 11 and 1 → 3 → 4 → 6 → 8 → 9 → 11
        """
        player = MiniMaxPlayer(target_depth=2, use_randomness=False)
        player.sign = 'O'
        player.moves_made = 10

        state = StateGenerator.generate(
            _0='XOXOXOXOX',
            _1='XOXOXOXOX', _2='XOXOXOXOX', _3='XOXOXOXOX',
            _4='XOXOXOXOX', _5='XOXOXOXOX', _6='XOXOXOXOX',
            _7='XOXOXOXOX', _8='XOXOXOXOX', _9='XOXOXOXOX'
        )

        Player.legal_moves = [[] for _ in range(10)]

        result = player.make_move(state, 5)

        assert result is None


    def test_path_29_33_and_loop_paths_maximizing(self):
        """
        Paths 29, 33: 1 → 2/3 → 4 → 6 → 7 → 9 → 10 → 12 → 14
        Also covers loop sub-paths: 3, 7, 9, 11, 15, 19, 21
        """
        player = MiniMaxPlayer(target_depth=2, use_randomness=False)
        player.sign = 'X'
        player.moves_made = 10

        state = StateGenerator.generate(
            _0='---------',
            _5='XO-------'
        )

        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [3, 4, 5, 6, 7, 8, 9]

        big_idx, small_idx = player.make_move(state, 5)

        assert big_idx == 5
        assert small_idx in [3, 4, 5, 6, 7, 8, 9]


    def test_path_32_36_and_loop_paths_minimizing(self):
        """
        Paths 32, 36: 1 → 2/3 → 4 → 6 → 8 → 9 → 10 → 13 → 15
        Also covers loop sub-paths: 5, 8, 10, 13, 17, 20, 22
        """
        player = MiniMaxPlayer(target_depth=2, use_randomness=False)
        player.sign = 'O'
        player.moves_made = 10

        state = StateGenerator.generate(
            _0='---------',
            _6='OX-------'
        )

        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[6] = [3, 4, 5, 6, 7, 8, 9]

        big_idx, small_idx = player.make_move(state, 6)

        assert big_idx == 6
        assert small_idx in [3, 4, 5, 6, 7, 8, 9]


    def test_path_4_12_maximizing_single_move(self):
        """
        Paths 4, 12: 10 → 12 → 9 → 11 and 10 → 12 → 14 → 9 → 11
        """
        player = MiniMaxPlayer(target_depth=2, use_randomness=False)
        player.sign = 'X'
        player.moves_made = 20

        state = StateGenerator.generate(
            _0='---------',
            _3='XOXOXOXO-'
        )

        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[3] = [9]

        big_idx, small_idx = player.make_move(state, 3)

        assert big_idx == 3
        assert small_idx == 9

    def test_path_6_14_minimizing_single_move(self):
        """
        Paths 6, 14: 10 → 13 → 9 → 11 and 10 → 13 → 15 → 9 → 11
        """
        player = MiniMaxPlayer(target_depth=2, use_randomness=False)
        player.sign = 'O'
        player.moves_made = 20

        state = StateGenerator.generate(
            _0='---------',
            _7='OXOXOXOX-'
        )

        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[7] = [9]

        big_idx, small_idx = player.make_move(state, 7)

        assert big_idx == 7
        assert small_idx == 9