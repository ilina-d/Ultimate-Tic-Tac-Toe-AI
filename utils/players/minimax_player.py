import time
import random

from .base_player import Player
from utils.helpers import StateEvaluator, StateEvaluatorV2, StateChecker, StateUpdater


StateEvaluator = StateEvaluator()
StateEvaluatorV2 = StateEvaluatorV2()
StateChecker = StateChecker()

INIT_DYNAMIC_DEPTH = 5
INIT_COUNTER = 0
THRESHOLD = 18
STEP = 3
BASE = 2
TIME_BREAK = 0.085


class MiniMaxPlayer(Player):
    """ Class representing a player that uses the MiniMaxPlayer algorithm. """

    def __init__(self, target_depth: int | str = 'dynamic', use_randomness: bool = False):
        """
        Create an instance of the MiniMax class.

        Depths:
            - int | Static value for the maximum searching depth.
            - "dynamic" | The searching depth is increased dynamically.
            - "timed" | The searching stops when a time limit is reached.

        Arguments:
            target_depth: The target depth value or option.
            use_randomness: Whether to randomize the first move.
        """

        super().__init__()

        match target_depth:
            case 'dynamic':
                self.target_depth = INIT_DYNAMIC_DEPTH
                self.use_dynamic_depth = True
                self.use_timed_depth = False

            case 'timed':
                self.target_depth = 4
                self.use_dynamic_depth = False
                self.use_timed_depth = True

            case _:
                self.target_depth = target_depth
                self.use_dynamic_depth = False
                self.use_timed_depth = False

        self.sign = None
        self.use_randomness = use_randomness
        self.moves_made = -1
        self.counter = INIT_COUNTER
        self.start_time = None


    def minimax_ab(self, state: tuple[dict, ...], prev_small_idx: int, curr_depth: int,
                   alpha: float, beta: float, is_maximizing: bool) -> float:
        """
        Find the best score from the given state using MiniMax with Alpha-Beta pruning.

        Arguments:
            state: The current state.
            prev_small_idx: The index of the previous move made.
            curr_depth: The current depth of the MiniMax tree.
            alpha: The alpha value.
            beta: The beta value.
            is_maximizing: Whether the current move is maximizing.

        Returns:
            The score for the best move from the starting state.
        """

        is_won = StateChecker.check_win(state, 0)
        sign = 'X' if is_maximizing else 'O'

        if is_won:
            return StateEvaluator.heuristic(state, prev_small_idx, sign)

        elif self.use_timed_depth and time.time() - self.start_time >= TIME_BREAK:
            return StateEvaluator.heuristic(state, prev_small_idx, sign)

        elif curr_depth == self.target_depth:
            return StateEvaluator.heuristic(state, prev_small_idx, sign)

        if is_maximizing:
            max_score = float('-inf')

            for big_idx, small_idx in self.get_legal_moves_for_state(state, prev_small_idx):
                updated_state, _ = StateUpdater.update_state(state, big_idx, small_idx, sign)
                score = self.minimax_ab(updated_state, small_idx, curr_depth + 1, alpha, beta, False)
                max_score = max(max_score, score)
                alpha = max(alpha, score)

                if alpha >= beta:
                    break

            return max_score

        else:
            min_score = float('inf')

            for big_idx, small_idx in self.get_legal_moves_for_state(state, prev_small_idx):
                updated_state, _ = StateUpdater.update_state(state, big_idx, small_idx, sign)
                score = self.minimax_ab(updated_state, small_idx, curr_depth + 1, alpha, beta, True)
                min_score = min(min_score, score)
                beta = min(beta, score)

                if alpha >= beta:
                    break

            return min_score


    def get_premove(self, state: tuple[dict, ...], prev_small_idx: int, is_maximizing: bool) -> tuple[int, int] | None:
        """
        Get a predefined move for the given state.

        Arguments:
            state: The game state.
            prev_small_idx: The small index of the previous move made.
            is_maximizing: Whether the current move is maximizing.

        Returns:
            The input for the chosen move or None if there's no predefined move for the given state.
        """

        if is_maximizing and self.moves_made == 0:
            if self.use_randomness:
                return random.randint(1, 9), random.randint(1, 9)
            return 5, 5

        if prev_small_idx and state[prev_small_idx]['display'].count('-') == 9:
            return prev_small_idx, prev_small_idx

        return None


    def update_target_depth(self):
        """ Update the target depth value based on the depth option. """

        if self.use_timed_depth:
            self.start_time = time.time()

        elif self.use_dynamic_depth and self.moves_made > THRESHOLD and self.moves_made % STEP == 0:
            self.target_depth += BASE ** self.counter
            self.counter += 1


    def make_move(self, state: tuple[dict, ...], prev_small_idx: int) -> tuple[int, int]:
        self.moves_made += 1

        init_alpha = float('-inf')
        init_beta = float('inf')

        is_maximizing = True if self.sign == 'X' else False

        premove = self.get_premove(state, prev_small_idx, is_maximizing)
        if premove:
            return premove

        self.update_target_depth()

        best_score = init_alpha if is_maximizing else init_beta
        best_move = None

        for big_idx, small_idx in self.get_current_legal_moves(prev_small_idx):
            move = (big_idx, small_idx)

            updated_state, _ = StateUpdater.update_state(state, big_idx, small_idx, self.sign)
            curr_score = self.minimax_ab(updated_state, small_idx, 1, init_alpha, init_beta, not is_maximizing)

            if is_maximizing:
                if curr_score > best_score:
                    best_score = curr_score
                    best_move = move
            else:
                if curr_score < best_score:
                    best_score = curr_score
                    best_move = move

        return best_move


__all__ = ['MiniMaxPlayer']
