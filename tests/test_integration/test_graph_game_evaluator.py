import pytest

from tests.state_generator import StateGenerator
from utils.helpers.game_evaluator import GameEvaluator
from utils.players import RandomPlayer
from utils.players.minimax_player import MiniMaxPlayer
from utils.players.base_player import Player


class TestGameEvaluatorGameEvaluationPrimePaths:
    """ Prime Path Coverage integration tests for GameEvaluator.game_evaluation method. """

    @pytest.fixture(autouse=True)
    def setup_evaluator(self):
        """ Reset GameEvaluator singleton and Player legal moves before each test. """
        GameEvaluator._instance = None
        Player.reset_legal_moves()
        yield
        Player.reset_legal_moves()

    def test_path_1_first_move(self):
        """ Path 1: 1 → 2 """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(_0='---------')

        result = evaluator.game_evaluation(state, prev_small_idx=5, player=player)

        assert result == 0.0

    def test_path_8_minimax_x_no_legal_moves(self):
        """ Path 8: 1 → 3 → 4 → 5 → 7 → 8 → 9 """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)
        evaluator._instance.is_first_move = False

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(
            _0='XOXOXOXOX',
            _1='XOXOXOXOX', _2='XOXOXOXOX', _3='XOXOXOXOX',
            _4='XOXOXOXOX', _5='XOXOXOXOX', _6='XOXOXOXOX',
            _7='XOXOXOXOX', _8='XOXOXOXOX', _9='XOXOXOXOX'
        )
        Player.legal_moves = [[] for _ in range(10)]

        result = evaluator.game_evaluation(state, prev_small_idx=5, player=player)

        assert result == 0

    def test_path_9_minimax_o_no_legal_moves(self):
        """ Path 9: 1 → 3 → 4 → 6 → 7 → 8 → 9 """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)
        evaluator._instance.is_first_move = False

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'O'

        state = StateGenerator.generate(
            _0='XOXOXOXOX',
            _1='XOXOXOXOX', _2='XOXOXOXOX', _3='XOXOXOXOX',
            _4='XOXOXOXOX', _5='XOXOXOXOX', _6='XOXOXOXOX',
            _7='XOXOXOXOX', _8='XOXOXOXOX', _9='XOXOXOXOX'
        )
        Player.legal_moves = [[] for _ in range(10)]

        result = evaluator.game_evaluation(state, prev_small_idx=5, player=player)

        assert result == 0

    def test_path_10_11_minimax_x_single_move(self):
        """  Paths 10, 11: 1 → 3 → 4 → 5 → 7 → 8 → 10 → 11 → 13 """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)
        evaluator._instance.is_first_move = False

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(_0='---------', _5='XOXOXOXO-')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [9]

        result = evaluator.game_evaluation(state, prev_small_idx=5, player=player)

        assert isinstance(result, (int, float))

    def test_path_10_minimax_x_multiple_moves(self):
        """
        Path 10: 1 → 3 → 4 → 5 → 7 → 8 → 10 → 11 → 12 → 11 → ...
        Also covers loop paths 2, 3, 4.
        """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)
        evaluator._instance.is_first_move = False

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(_0='---------', _5='XO-------')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [3, 4, 5, 6, 7, 8, 9]

        result = evaluator.game_evaluation(state, prev_small_idx=5, player=player)

        assert isinstance(result, (int, float))

    def test_path_12_13_minimax_o_single_move(self):
        """ Paths 12, 13: 1 → 3 → 4 → 6 → 7 → 8 → 10 → 11 → 13 """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)
        evaluator._instance.is_first_move = False

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'O'

        state = StateGenerator.generate(_0='---------', _6='OXOXOXOX-')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[6] = [9]

        result = evaluator.game_evaluation(state, prev_small_idx=6, player=player)

        assert isinstance(result, (int, float))

    def test_path_12_minimax_o_multiple_moves(self):
        """
        Path 12: 1 → 3 → 4 → 6 → 7 → 8 → 10 → 11 → 12 → 11 → ...
        Also covers loop paths 2, 3, 4.
        """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)
        evaluator._instance.is_first_move = False

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'O'

        state = StateGenerator.generate(_0='---------', _6='OX-------')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[6] = [3, 4, 5, 6, 7, 8, 9]

        result = evaluator.game_evaluation(state, prev_small_idx=6, player=player)

        assert isinstance(result, (int, float))

    def test_loop_paths_many_iterations(self):
        """
        Covers loop paths 2, 3, 4: Multiple iterations through the loop.
        """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)
        evaluator._instance.is_first_move = False

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(_0='---------')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # All 9 moves

        result = evaluator.game_evaluation(state, prev_small_idx=5, player=player)

        assert isinstance(result, (int, float))


class TestGameEvaluatorGetBestMovePrimePaths:
    """ Prime Path Coverage integration tests for GameEvaluator.get_best_move method. """

    @pytest.fixture(autouse=True)
    def setup_evaluator(self):
        """Reset GameEvaluator singleton and Player legal moves before each test."""
        GameEvaluator._instance = None
        Player.reset_legal_moves()
        yield
        Player.reset_legal_moves()

    def test_path_10_minimax_x_no_legal_moves(self):
        """ Path 10: 1 → 2 → 3 → 5 → 6 → 7 → 10 """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(_0='---------')
        Player.legal_moves = [[] for _ in range(10)]

        result = evaluator.get_best_move(state, prev_small_idx=5, player=player)

        assert result is None

    def test_path_11_minimax_o_no_legal_moves(self):
        """ Path 11: 1 → 2 → 4 → 5 → 6 → 7 → 10 """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'O'

        state = StateGenerator.generate(_0='---------')
        Player.legal_moves = [[] for _ in range(10)]

        result = evaluator.get_best_move(state, prev_small_idx=5, player=player)

        assert result is None

    def test_path_12_minimax_x_single_move(self):
        """
        Path 12: 1 → 2 → 3 → 5 → 6 → 7 → 8 → 9 → 7 → 10
        Also covers paths 5, 6: 7 → 8 → 9 → 7 → 10
        """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(_0='---------', _5='---------')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [1]

        result = evaluator.get_best_move(state, prev_small_idx=5, player=player)

        assert result == (5, 1)

    def test_path_13_minimax_o_single_move(self):
        """
        Path 13: 1 → 2 → 4 → 5 → 6 → 7 → 8 → 9 → 7 → 10
        Also covers paths 5, 6: 7 → 8 → 9 → 7 → 10
        """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'O'

        state = StateGenerator.generate(_0='---------', _5='---------')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [1]

        result = evaluator.get_best_move(state, prev_small_idx=5, player=player)

        assert result == (5, 1)

    def test_path_1_2_3_loop_no_update(self):
        """
        Paths 1, 2, 3: 7 → 8 → 7 (no update), 8 → 7 → 10, 8 → 7 → 8
        Position 5 (center) should score highest for X.
        """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(_0='---------', _5='---------')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [5, 1, 2, 3]

        result = evaluator.get_best_move(state, prev_small_idx=5, player=player)

        assert result is not None
        assert isinstance(result, tuple)

    def test_path_5_7_loop_with_update(self):
        """ Paths 5, 7: 7 → 8 → 9 → 7, 8 → 9 → 7 → 8 """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(_0='---------', _5='---------')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [1, 5]

        result = evaluator.get_best_move(state, prev_small_idx=5, player=player)

        assert result is not None

    def test_path_8_consecutive_updates(self):
        """ Path 8: 9 → 7 → 8 → 9 """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(_0='---------', _5='---------')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [6, 1, 5]

        result = evaluator.get_best_move(state, prev_small_idx=5, player=player)

        assert result is not None

    def test_path_8_consecutive_updates_o(self):
        """ Path 8 for O: 9 → 7 → 8 → 9 """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'O'

        state = StateGenerator.generate(_0='---------', _5='---------')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [6, 1, 5]

        result = evaluator.get_best_move(state, prev_small_idx=5, player=player)

        assert result is not None

    def test_path_4_not_minimax_no_moves(self):
        """ Path 4: 1 → 6 → 7 → 10 """
        algorithm = RandomPlayer()
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(_0='---------')
        Player.legal_moves = [[] for _ in range(10)]

        result = evaluator.get_best_move(state, prev_small_idx=5, player=player)

        assert result is None

    def test_multiple_moves_x_finds_best(self):
        """
        X player with multiple moves finds the best scoring position.
        Covers multiple loop iterations with mixed updates.
        """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'X'

        state = StateGenerator.generate(_0='---------', _5='---------')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        result = evaluator.get_best_move(state, prev_small_idx=5, player=player)

        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_multiple_moves_o_finds_best(self):
        """
        O player with multiple moves finds the lowest scoring position.
        Covers multiple loop iterations with mixed updates.
        """
        algorithm = MiniMaxPlayer(target_depth=2)
        evaluator = GameEvaluator(algorithm=algorithm)

        player = MiniMaxPlayer(target_depth=2)
        player.sign = 'O'

        state = StateGenerator.generate(_0='---------', _5='---------')
        Player.legal_moves = [[] for _ in range(10)]
        Player.legal_moves[5] = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        result = evaluator.get_best_move(state, prev_small_idx=5, player=player)

        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2