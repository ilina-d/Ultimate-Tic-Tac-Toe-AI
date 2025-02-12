from .state_evaluator import StateEvaluator
from .state_updater import StateUpdater
from utils.players import Player


StateEvaluator = StateEvaluator()


class GameEvaluator:
    """ Helper singleton class for evaluating game states. """

    _instance = None


    def __new__(cls, algorithm: Player = None) -> 'GameEvaluator':
        """
        Create a new instance of the GameEvaluator class if it doesn't already exist.

        Arguments:
            algorithm: Which algorithm to use when evaluating.

        Returns:
            Instance of the GameEvaluator class.
        """

        if cls._instance is None:
            cls._instance = super(GameEvaluator, cls).__new__(cls)
            cls._instance.algorithm = algorithm
            cls._instance.is_first_move = True

        return cls._instance


    def game_evaluation(self, state: tuple[dict, ...], prev_small_idx: int, player: Player) -> float:
        """
        Evaluate the given game state by looking into the future.

        Arguments:
            state: The state to evaluate.
            prev_small_idx: The small index of the previous move made.
            player: The player making the first move from the given state.

        Returns:
            The evaluation score for the given state.
        """

        if self._instance.is_first_move:
            self._instance.is_first_move = False
            return 0.0

        if self._instance.algorithm.__class__.__name__ == 'MiniMaxPlayer':
            self._instance.algorithm.moves_made += 0.5

            init_alpha = float('-inf')
            init_beta = float('inf')

            is_maximizing = True if player.sign == 'X' else False

            self._instance.algorithm.update_target_depth()

            run_algorithm = self._instance.algorithm.minimax_ab
            algorithm_args = {'curr_depth' : 1, 'alpha' : init_alpha, 'beta' : init_beta,
                              'is_maximizing' : not is_maximizing}

        legal_moves = player.get_current_legal_moves(prev_small_idx)
        if len(legal_moves) == 0:
            return 0

        score = 0
        for big_idx, small_idx in legal_moves:
            updated_state, _ = StateUpdater.update_state(state, big_idx, small_idx, player.sign)
            score += run_algorithm(updated_state, small_idx, **algorithm_args)

        return score / len(legal_moves)


    def get_best_move(self, state: tuple[dict, ...], prev_small_idx: int, player: Player) -> tuple[int, int] | None:
        """
        Finds the best move for a given state.

        Arguments:
            state: The state to evaluate.
            prev_small_idx: The small index of the previous move made.
            player: The player making the first move from the given state.

        Returns:
            The best move from the given state or None if there are no legal moves.
        """

        if self._instance.algorithm.__class__.__name__ == 'MiniMaxPlayer':
            self._instance.algorithm.moves_made += 0.5

            init_alpha = float('-inf')
            init_beta = float('inf')

            is_maximizing = True if player.sign == 'X' else False

            self._instance.algorithm.update_target_depth()

            run_algorithm = self._instance.algorithm.minimax_ab
            algorithm_args = {'curr_depth' : 1, 'alpha' : init_alpha, 'beta' : init_beta,
                              'is_maximizing' : not is_maximizing}

        legal_moves = player.get_current_legal_moves(prev_small_idx)
        best_move = None
        best_score = float('-inf') if player.sign == 'X' else float('inf')

        for big_idx, small_idx in legal_moves:
            updated_state, _ = StateUpdater.update_state(state, big_idx, small_idx, player.sign)
            score = run_algorithm(updated_state, small_idx, **algorithm_args)
            if (score > best_score and player.sign == 'X') or (score<best_score and player.sign == 'O'):
                best_move = (big_idx, small_idx)
                best_score = score

        return best_move

__all__ = ['GameEvaluator']
