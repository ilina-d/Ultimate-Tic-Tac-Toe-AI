import time
import random

from .base_player import Player
from utils.helpers import StateEvaluator, StateChecker, StateUpdater


StateEvaluator = StateEvaluator()
StateChecker = StateChecker()

INIT_DYNAMIC_DEPTH = 5
INIT_COUNTER = 0
THRESHOLD = 18
STEP = 3
BASE = 2
TIME_BREAK = 0.085


class ExpectiMaxPlayer(Player):
    """ Class representing a player that uses the ExpectiMax algorithm. """

    def __init__(self, target_depth: int | str = 'dynamic', use_randomness: bool = False):
        """
        Create an instance of the ExpectiMaxPlayer class.

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


    def expectimax(self, state: tuple[dict, ...], prev_small_idx: int, curr_depth: int,
                   is_maximizing: bool, is_averaging: bool) -> float:
        """
        Find the best score from the given state using ExpectiMax.

        Arguments:
            state: The current state.
            prev_small_idx: The index of the previous move made.
            curr_depth: The current depth of the MiniMax tree.
            is_maximizing: Whether the current move is maximizing.
            is_averaging: Whether the current move is averaging.

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

        if is_averaging:
            avg_score, num_scores = 0, 0

            for big_idx, small_idx in self.get_legal_moves_for_state(state, prev_small_idx):
                updated_state, _ = StateUpdater.update_state(state, big_idx, small_idx, sign)
                avg_score += self.expectimax(updated_state, small_idx, curr_depth + 1, not is_maximizing, False)
                num_scores += 1

            return avg_score / num_scores

        if is_maximizing:
            max_score = float('-inf')

            for big_idx, small_idx in self.get_legal_moves_for_state(state, prev_small_idx):
                updated_state, _ = StateUpdater.update_state(state, big_idx, small_idx, 'X')
                score = self.expectimax(updated_state, small_idx, curr_depth + 1, False, True)
                max_score = max(max_score, score)

            return max_score

        else:
            min_score = float('inf')

            for big_idx, small_idx in self.get_legal_moves_for_state(state, prev_small_idx):
                updated_state, _ = StateUpdater.update_state(state, big_idx, small_idx, 'O')
                score = self.expectimax(updated_state, small_idx, curr_depth + 1, True, True)
                min_score = min(min_score, score)

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

        is_maximizing = True if self.sign == 'X' else False

        premove = self.get_premove(state, prev_small_idx, is_maximizing)
        if premove:
            return premove

        self.update_target_depth()

        best_score = float('-inf') if is_maximizing else float('inf')
        best_move = None

        for big_idx, small_idx in self.get_current_legal_moves(prev_small_idx):
            move = (big_idx, small_idx)

            updated_state, _ = StateUpdater.update_state(state, big_idx, small_idx, self.sign)
            curr_score = self.expectimax(updated_state, small_idx, 1, not is_maximizing, True)

            if is_maximizing:
                if curr_score > best_score:
                    best_score = curr_score
                    best_move = move
            else:
                if curr_score < best_score:
                    best_score = curr_score
                    best_move = move

        return best_move


__all__ = ['ExpectiMaxPlayer']
