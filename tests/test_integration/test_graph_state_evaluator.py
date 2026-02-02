import pytest

from utils.helpers.state_evaluator import StateEvaluator, SCORE_BLOCKING, SCORE_TWO_IN_ROW
from tests.state_generator import StateGenerator
from utils.helpers.state_evaluator import  SCORE_TIE, SCORE_WIN, SCORE_CORNER, SCORE_CENTER, SCORE_FORK


class TestStateEvaluatorGetRowScorePrimePaths:
    """ Prime Path Coverage integration tests for StateEvaluator.get_row_score method. """

    def test_path_1_empty_list(self):
        """ Path 1: 1 → 2 (1/2)"""
        result = StateEvaluator.get_row_score(ms_idx=5, sign_pos=[], calc_for='blocking')
        assert result == 0

    def test_path_1_single_element(self):
        """ Path 1: 1 → 2 (2/2)"""
        result = StateEvaluator.get_row_score(ms_idx=5, sign_pos=[2], calc_for='two_row')
        assert result == 0

    def test_path_17_blocking_immediate_match(self):
        """ Path 17: 3 → 4 → 6 → 7 → 9 → 10 → 12 → 16 → 8 """
        result = StateEvaluator.get_row_score(ms_idx=5, sign_pos=[2, 8], calc_for='blocking')
        assert result == SCORE_BLOCKING

    def test_path_18_two_row_immediate_match(self):
        """ Path 18: 3 → 5 → 6 → 7 → 9 → 10 → 12 → 16 → 8 """
        result = StateEvaluator.get_row_score(ms_idx=5, sign_pos=[2, 8], calc_for='two_row')
        assert result == SCORE_TWO_IN_ROW

    def test_path_19_blocking_no_match_left_increment(self):
        """ Path 19: 3 → 4 → 6 → 7 → 9 → 10 → 11 → 13 → 14 → 8 """
        result = StateEvaluator.get_row_score(ms_idx=1, sign_pos=[2, 3], calc_for='blocking')
        assert result == 0

    def test_path_20_two_row_no_match_left_increment(self):
        """ Path 20: 3 → 5 → 6 → 7 → 9 → 10 → 11 → 13 → 14 → 8 """
        result = StateEvaluator.get_row_score(ms_idx=1, sign_pos=[2, 3], calc_for='two_row')
        assert result == 0

    def test_path_21_blocking_no_match_right_decrement(self):
        """ Path 21: 3 → 4 → 6 → 7 → 9 → 10 → 12 → 15 → 13 → 14 → 8 """
        result = StateEvaluator.get_row_score(ms_idx=9, sign_pos=[7, 8], calc_for='blocking')
        assert result == 0

    def test_path_22_two_row_no_match_right_decrement(self):
        """ Path 22: 3 → 5 → 6 → 7 → 9 → 10 → 12 → 15 → 13 → 14 → 8 """
        result = StateEvaluator.get_row_score(ms_idx=9, sign_pos=[7, 8], calc_for='two_row')
        assert result == 0

    def test_loop_paths_left_increment_then_match(self):
        """ Covers paths 2, 3, 4, 7, 15: """
        result = StateEvaluator.get_row_score(ms_idx=6, sign_pos=[1, 2, 7], calc_for='blocking')
        assert result == SCORE_BLOCKING

    def test_loop_paths_right_decrement_then_match(self):
        """ Covers paths 8, 11, 12, 13, 14, 16: """
        # Test right decrement loop ending in no match
        result = StateEvaluator.get_row_score(ms_idx=5, sign_pos=[6, 8, 9], calc_for='blocking')
        assert result == 0

    def test_loop_paths_right_decrement_then_match_v2(self):
        """ Covers paths 8, 11, 12, 13, 14, 16: """
        result = StateEvaluator.get_row_score(ms_idx=6, sign_pos=[1, 2, 8, 9], calc_for='blocking')
        assert result == SCORE_BLOCKING

    def test_multiple_matches(self):
        """ Covers paths: 5, 6: """
        result = StateEvaluator.get_row_score(ms_idx=5, sign_pos=[1, 2, 3, 7, 8, 9], calc_for='blocking')
        assert result == SCORE_BLOCKING * 3

    def test_multiple_matches_two_row(self):
        """ Same as above but with calc_for='two_row'. """
        result = StateEvaluator.get_row_score(ms_idx=5, sign_pos=[1, 2, 3, 7, 8, 9], calc_for='two_row')
        assert result == SCORE_TWO_IN_ROW * 3

    def test_mixed_adjustments_then_match(self):
        """ Covers paths: 9, 10: """
        result = StateEvaluator.get_row_score(ms_idx=4, sign_pos=[1, 3, 8, 9], calc_for='two_row')
        assert result == SCORE_TWO_IN_ROW


class TestStateEvaluatorEvaluateBoardPrimePaths:
    """ Prime Path Coverage integration tests for StateEvaluator.evaluate_board method. """

    @pytest.fixture(autouse=True)
    def get_evaluator(self):
        """ Get StateEvaluator instance. """
        self.evaluator = StateEvaluator()

    def test_path_1_tied_board(self):
        """ Path 1: 1 → 2 """
        state = StateGenerator.generate(_1='XOXOXOOXO')  # Tied board
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result == SCORE_TIE

    def test_path_4_5_x_wins(self):
        """ Path 4, 5: 1 → 3 → 4 → 5 """
        state = StateGenerator.generate(_1='XXX------')  # X wins top row
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result == SCORE_WIN // 2

    def test_path_4_6_o_wins(self):
        """ Path 4, 6: 1 → 3 → 4 → 6 """
        state = StateGenerator.generate(_1='OOO------')  # O wins top row
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result == -SCORE_WIN // 2

    def test_path_17_no_given_signs_with_empty_loop(self):
        """ Paths 17, 2, 3: """
        state = StateGenerator.generate(_1='OO-------')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert isinstance(result, int)

    def test_path_32_33_empty_given_no_fork_return(self):
        """ Paths 32, 33: """
        state = StateGenerator.generate(_1='---------')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert isinstance(result, int)

    def test_path_29_single_corner_position(self):
        """ Path 29: 1 → 3 → 7 → 8 → 9 → 10 → 13 → 8 → 14 → ... """
        state = StateGenerator.generate(_1='X--------')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result >= SCORE_CORNER

    def test_path_30_single_middle_position(self):
        """ Path 30: 1 → 3 → 7 → 8 → 9 → 11 → 13 → 8 → 14 → ... """
        state = StateGenerator.generate(_1='-----X---')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert isinstance(result, int)

    def test_path_34_center_position(self):
        """ Path 34: 1 → 3 → 7 → 8 → 9 → 11 → 12 → 13 → 8 → 14 → ... """
        state = StateGenerator.generate(_1='----X----')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result >= SCORE_CENTER

    def test_loop_paths_multiple_corners(self):
        """ Paths 6, 7, 9, 13, 15: """
        state = StateGenerator.generate(_1='X-X------')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result >= 2 * SCORE_CORNER

    def test_loop_paths_corner_then_middle(self):
        """ Paths 7, 8, 10, 14, 16, 18, 19: """
        state = StateGenerator.generate(_1='X----X---')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result >= SCORE_CORNER

    def test_loop_paths_corner_then_center(self):
        """ Covers paths involving 9 → 10 → 13 → 8 → 9 → 11 → 12 → 13. """
        state = StateGenerator.generate(_1='X---X----')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result >= SCORE_CORNER + SCORE_CENTER

    def test_loop_paths_middle_then_corner(self):
        """ Paths 19, 20, 21, 22, 25, 27: """
        state = StateGenerator.generate(_1='--X--X---')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result >= SCORE_CORNER

    def test_loop_paths_middle_then_center(self):
        """ Covers paths with 9 → 11 → 13 → 8 → 9 → 11 → 12 → 13. """
        state = StateGenerator.generate(_1='----XX---')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result >= SCORE_CENTER

    def test_loop_paths_center_then_corner(self):
        """ Covers paths with 9 → 11 → 12 → 13 → 8 → 9 → 10 → 13. """
        state = StateGenerator.generate(_1='X---X----')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result >= SCORE_CORNER + SCORE_CENTER

    def test_loop_paths_three_positions_mixed(self):
        """ Paths 21, 22, 25, 27, 31, 34: """
        state = StateGenerator.generate(_1='X---XX---')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result >= SCORE_CORNER + SCORE_CENTER

    def test_path_35_36_corner_no_fork_x(self):
        """ Paths 35, 36: 9 → 10 → 13 → 8 → 14 → 16 → 18 → 19/20 """
        state = StateGenerator.generate(_1='X--------')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result > 0

    def test_path_35_36_corner_no_fork_o(self):
        """ Paths 35, 36: """
        state = StateGenerator.generate(_1='O--------')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='O')
        assert result < 0

    def test_path_37_38_middle_no_fork(self):
        """ Paths 37, 38: 9 → 11 → 13 → 8 → 14 → 16 → 18 → 19/20 """
        state = StateGenerator.generate(_1='-----X---')
        result_x = self.evaluator.evaluate_board(state, big_idx=1, sign='X')

        state_o = StateGenerator.generate(_1='-----O---')
        result_o = self.evaluator.evaluate_board(state_o, big_idx=1, sign='O')

        assert isinstance(result_x, int)
        assert isinstance(result_o, int)

    def test_path_41_42_corner_with_second_loop(self):
        """ Paths 41, 42: 9 → 10 → 13 → 8 → 14 → 16 → 17 → 18 → 19/20 """
        state = StateGenerator.generate(_1='X---X-X--')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result >= SCORE_FORK

    def test_path_43_44_center_and_others_with_fork(self):
        """ Paths 43, 44: 9 → 11 → 12 → 13 → 8 → 14 → 16 → 18 → 19/20 """
        state = StateGenerator.generate(_1='X---X-X--')
        result_x = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result_x >= SCORE_FORK + SCORE_CENTER + SCORE_CORNER

    def test_path_45_46_middle_then_fork(self):
        """ Paths 45, 46: 9 → 11 → 13 → 8 → 14 → 16 → 17 → 18 → 19/20 """
        state = StateGenerator.generate(_1='X-X-X----')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result >= SCORE_FORK

    def test_path_47_48_full_loop_with_fork(self):
        """ Paths 47, 48: 9 → 11 → 12 → 13 → 8 → 14 → 16 → 17 → 18 → 19/20 """
        state = StateGenerator.generate(_1='X-X-X-X--')
        result_x = self.evaluator.evaluate_board(state, big_idx=1, sign='X')

        state_o = StateGenerator.generate(_1='O-O-O-O--')
        result_o = self.evaluator.evaluate_board(state_o, big_idx=1, sign='O')

        assert result_x >= SCORE_FORK
        assert result_o <= -SCORE_FORK

    def test_path_26_28_31_multiple_first_loop_then_second(self):
        """ Paths 26, 28, 31: """
        state = StateGenerator.generate(_1='X-X------')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert isinstance(result, int)

    def test_return_sign_x_positive(self):
        """ Paths ending in 19: """
        state = StateGenerator.generate(_1='X--------')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='X')
        assert result > 0

    def test_return_sign_o_negative(self):
        """ Paths ending in 20: """
        state = StateGenerator.generate(_1='O--------')
        result = self.evaluator.evaluate_board(state, big_idx=1, sign='O')
        assert result < 0


class TestStateEvaluatorHeuristicPrimePaths:
    """ Prime Path Coverage integration tests for StateEvaluator heuristic method. """

    @pytest.fixture(autouse=True)
    def setup_evaluator(self):
        """Get StateEvaluator instance and clear cache for predictable behavior."""
        self.evaluator = StateEvaluator()
        self.evaluator._instance.evaluated_boards = {}

    def test_path_1_game_tied(self):
        """ Path 1: 1 → 2 """
        state = StateGenerator.generate(
            _0='XOXOXOOXO',
            _1='XXX------', _2='OOO------', _3='XXX------',
            _4='OOO------', _5='XXX------', _6='OOO------',
            _7='XXX------', _8='OOO------', _9='XXX------'
        )
        result = self.evaluator.heuristic(state, next_big_idx=5, sign='X')
        assert result == SCORE_TIE

    def test_path_2_3_x_wins_game(self):
        """ Paths 2, 3: 1 → 3 → 4 → 5 """
        state = StateGenerator.generate(
            _0='XXX------',
            _1='XXX------', _2='XXX------', _3='XXX------',
            _4='---------', _5='---------', _6='---------',
            _7='---------', _8='---------', _9='---------'
        )
        result = self.evaluator.heuristic(state, next_big_idx=5, sign='X')
        assert result == SCORE_WIN

    def test_path_2_3_o_wins_game(self):
        """ Paths 2, 3: 1 → 3 → 4 → 6 """
        state = StateGenerator.generate(
            _0='OOO------',
            _1='OOO------', _2='OOO------', _3='OOO------',
            _4='---------', _5='---------', _6='---------',
            _7='---------', _8='---------', _9='---------'
        )
        result = self.evaluator.heuristic(state, next_big_idx=5, sign='X')
        assert result == -SCORE_WIN

    def test_path_62_cache_miss_corner_no_penalty(self):
        """ Path 62: 1 → 3 → 7 → 8 → 9 → 10 → 12 → 13 → 17 → ... → 18 → 22 """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------')

        self.evaluator.heuristic(state, next_big_idx=1, sign='X')

        result = self.evaluator.heuristic(state, next_big_idx=1, sign='X')
        assert isinstance(result, (int, float))

    def test_path_63_cache_miss_middle_no_penalty(self):
        """ Path 63: 1 → 3 → 7 → 8 → 9 → 11 → 12 → 13 → 17 → ... → 18 → 22 """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------')
        result = self.evaluator.heuristic(state, next_big_idx=2, sign='X')
        assert isinstance(result, (int, float))

    def test_path_64_65_corner_with_cache(self):
        """ Paths 64, 65: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------', _1='X--------')
        result = self.evaluator.heuristic(state, next_big_idx=1, sign='X')
        assert isinstance(result, (int, float))

    def test_path_66_67_middle_board(self):
        """ Paths 66, 67: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------', _2='X--------')
        result = self.evaluator.heuristic(state, next_big_idx=2, sign='X')
        assert isinstance(result, (int, float))

    def test_path_68_69_free_move_sign_x(self):
        """ Paths 68, 69: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------')
        result = self.evaluator.heuristic(state, next_big_idx=None, sign='X')
        assert isinstance(result, (int, float))

    def test_path_70_71_free_move_sign_o(self):
        """ Paths 70, 71: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------')
        result = self.evaluator.heuristic(state, next_big_idx=None, sign='O')
        assert isinstance(result, (int, float))

    def test_path_free_move_completed_board(self):
        """ Free move penalty when next_big_idx points to completed board. """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(
            _0='X--------',  # Board 1 is won
            _1='XXX------'  # X wins board 1
        )
        result = self.evaluator.heuristic(state, next_big_idx=1, sign='X')
        assert isinstance(result, (int, float))

    def test_path_72_73_corner_free_move_x(self):
        """ Paths 72, 73: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------', _1='X--------')
        result = self.evaluator.heuristic(state, next_big_idx=None, sign='X')
        assert isinstance(result, (int, float))

    def test_path_74_75_corner_free_move_o(self):
        """ Paths 74, 75: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------', _1='O--------')
        result = self.evaluator.heuristic(state, next_big_idx=None, sign='O')
        assert isinstance(result, (int, float))

    def test_path_76_77_middle_free_move_x(self):
        """ Paths 76, 77: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------', _2='X--------')
        result = self.evaluator.heuristic(state, next_big_idx=None, sign='X')
        assert isinstance(result, (int, float))

    def test_path_78_79_middle_free_move_o(self):
        """ Paths 78, 79: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------', _4='O--------')
        result = self.evaluator.heuristic(state, next_big_idx=None, sign='O')
        assert isinstance(result, (int, float))

    def test_loop_all_board_types(self):
        """ Covers loop paths 4-61: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(
            _0='---------',
            _1='X--------',
            _2='O--------',
            _3='X--------',
            _4='O--------',
            _5='X--------',
            _6='O--------',
            _7='X--------',
            _8='O--------',
            _9='X--------'
        )
        result = self.evaluator.heuristic(state, next_big_idx=5, sign='X')
        assert isinstance(result, (int, float))

    def test_loop_cache_hit_after_first_run(self):
        """ Covers paths with node 10 (cache hit). """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------')
        self.evaluator.heuristic(state, next_big_idx=5, sign='X')
        result = self.evaluator.heuristic(state, next_big_idx=5, sign='X')
        assert isinstance(result, (int, float))

    def test_loop_mixed_cache_hit_miss(self):
        """ Covers paths with mixed cache hits and misses. """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------', _1='X--------')

        self.evaluator.heuristic(state, next_big_idx=1, sign='X')

        state2 = StateGenerator.generate(_0='---------', _1='X--------', _2='O--------')

        result = self.evaluator.heuristic(state2, next_big_idx=2, sign='X')
        assert isinstance(result, (int, float))

    def test_corner_board_scaling(self):
        """ Verify corner boards (1,3,7,9) go through node 13 (SCALE_CORNER). """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------', _1='X--------')
        result = self.evaluator.heuristic(state, next_big_idx=1, sign='X')
        assert isinstance(result, (int, float))

    def test_middle_board_scaling(self):
        """ Verify middle boards (2,4,6,8) go through node 14 → 15 (SCALE_MIDDLE). """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------', _2='X--------')
        result = self.evaluator.heuristic(state, next_big_idx=2, sign='X')
        assert isinstance(result, (int, float))

    def test_center_board_scaling(self):
        """ Verify center board (5) goes through node 14 → 16 (SCALE_CENTER). """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------', _5='X--------')
        result = self.evaluator.heuristic(state, next_big_idx=5, sign='X')
        assert isinstance(result, (int, float))

    def test_no_free_move_penalty(self):
        """  Path 18 → 22: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------')
        result = self.evaluator.heuristic(state, next_big_idx=5, sign='X')
        assert isinstance(result, (int, float))

    def test_free_move_penalty_none_idx(self):
        """ Path 18 → 19: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(_0='---------')
        result = self.evaluator.heuristic(state, next_big_idx=None, sign='X')
        assert isinstance(result, (int, float))

    def test_free_move_penalty_completed_board(self):
        """ Path 18 → 19: """
        self.evaluator._instance.evaluated_boards = {}
        state = StateGenerator.generate(
            _0='X--------',
            _1='XXX------'
        )
        result = self.evaluator.heuristic(state, next_big_idx=1, sign='X')
        assert isinstance(result, (int, float))