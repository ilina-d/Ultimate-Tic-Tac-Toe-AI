from .state_checker import StateChecker
from .assets import inverse_board_display


StateChecker = StateChecker()


# Weights
WEIGHT_FACTOR = 8

SCORE_CENTER = 5 * WEIGHT_FACTOR  # 10
SCORE_CORNER = 2 * WEIGHT_FACTOR  # 5
SCORE_TWO_IN_ROW = 7 * WEIGHT_FACTOR  # 15
SCORE_FORK = 10 * WEIGHT_FACTOR  # 20
SCORE_BLOCKING = 5 * WEIGHT_FACTOR  # 10

SCORE_WIN = 100 * 10
SCORE_TIE = 0
SCORE_FREE_MOVE_PENALTY = 0

SCALE_CORNER = 0.15
SCALE_MIDDLE = 0.05
SCALE_CENTER = 0.2

# Board Positions
CORNERS = MS_MIDDLES = {1, 3, 7, 9}
MIDDLES = MS_CORNERS = {2, 4, 6, 8}
MS_FORKS = {2, 4, 6, 8, 5}


class StateEvaluator:
    """ Helper singleton class for evaluating game states. """

    _instance = None


    def __new__(cls) -> 'StateEvaluator':
        """
        Create a new instance of the StateEvaluator class if it doesn't already exist.

        Returns:
            Instance of the StateEvaluator class.
        """

        if cls._instance is None:
            cls._instance = super(StateEvaluator, cls).__new__(cls)
            cls._instance.evaluated_boards = {}

        return cls._instance


    @staticmethod
    def get_row_score(ms_idx: int, sign_pos: list[int], calc_for: str) -> int:
        """
        Get the score for the given magic square position depending on what's being calculated.

        Calculation Options:
            - "blocking" | Calculates score for blocking opponent's two in a row.
            - "two_row" | Calculates score for placing two signs in a row.

        Arguments:
            ms_idx: A magic square index of the position (given sign or empty space).
            sign_pos: Magic square positions of the other sign (opposing or given signs).
            calc_for: What's being calculated.

        Returns:
            The score gain based on the calculation option.
        """

        if len(sign_pos) < 2:
            return 0

        score_addition = SCORE_BLOCKING if calc_for == 'blocking' else SCORE_TWO_IN_ROW
        score_gain = 0
        blocks_found = True
        sign_pos = sign_pos.copy()

        while len(sign_pos) >= 2:
            left = 0
            right = len(sign_pos) - 1

            while True:
                temp_score = ms_idx + sign_pos[left] + sign_pos[right]

                if temp_score < 15:
                    left += 1
                elif temp_score > 15:
                    right -= 1
                else:
                    score_gain += score_addition
                    sign_pos.pop(right)
                    sign_pos.pop(left)
                    break

                if left == right:
                    blocks_found = False
                    break

            if not blocks_found:
                break

        return score_gain


    def evaluate_board(self, state: tuple[dict, ...], big_idx: int, sign: str = None) -> int:
        """
        Evaluate the board at the given index for given sign.

        Arguments:
            state: The game state.
            big_idx: Board index, 0 for big board.
            sign: The sign to evaluate for.

        Returns:
            The value of the board in range between -100 and 100.
        """

        winner = StateChecker.check_win(state, big_idx)

        # Check if game ended in a tie
        if winner == 'T':
            return SCORE_TIE

        # Check if game ended in a win
        if winner:
            return SCORE_WIN // 2 if winner == 'X' else -SCORE_WIN // 2

        score = 0
        given_sign_pos = sorted(list(state[big_idx][sign]))
        other_sign_pos = sorted(state[big_idx]['X' if sign == 'O' else 'O'])
        empty_sign_pos = set(range(1, 10)) - set(given_sign_pos) - set(other_sign_pos)

        for ms_idx in given_sign_pos:

            # Check for sign in corner
            if ms_idx in MS_CORNERS:
                score += SCORE_CORNER

            # Check for sign in center
            elif ms_idx == 5:
                score += SCORE_CENTER

            # Check for blocking opponent's two in a row
            score += self.get_row_score(ms_idx, other_sign_pos, calc_for = 'blocking')

        # Check for placing two in a row
        for ms_idx in empty_sign_pos:
            score += self.get_row_score(ms_idx, given_sign_pos, calc_for = 'two_row')

        # Check for forks
        if len([pos for pos in given_sign_pos if pos in MS_FORKS]) >= 3:
            score += SCORE_FORK

        return score if sign == 'X' else -score


    def heuristic(self, state: tuple[dict, ...], next_big_idx: int | None, sign: str) -> float:
        """
        Evaluate the given state.

        Arguments:
            state: A game state.
            next_big_idx: Board index where the next player makes a move, or None if any move is possible.
            sign: The sign to evaluate for.

        Returns:
            The heuristic value for the state being evaluated.
        """

        winner = StateChecker.check_win(state, big_idx = 0)

        # Check if game ended in a tie
        if winner == 'T':
            return SCORE_TIE

        # Check if game ended in a win
        if winner:
            return SCORE_WIN if winner == 'X' else -SCORE_WIN

        score = 0

        for big_idx in range(1, 10):
            board_display = state[big_idx]['display']
            if board_display in self._instance.evaluated_boards:
                temp_score = self._instance.evaluated_boards[board_display]

            else:
                temp_score = self.evaluate_board(state, big_idx, 'X') + self.evaluate_board(state, big_idx, 'O')
                self._instance.evaluated_boards[board_display] = temp_score
                self._instance.evaluated_boards[inverse_board_display(board_display)] = -temp_score

            if big_idx in CORNERS:
                temp_score *= SCALE_CORNER
            elif big_idx in MIDDLES:
                temp_score *= SCALE_MIDDLE
            else:
                temp_score *= SCALE_CENTER

            score += temp_score

        if next_big_idx is None or state[0]['display'][next_big_idx] != '-':
            score -= SCORE_FREE_MOVE_PENALTY if sign == 'X' else -SCORE_FREE_MOVE_PENALTY

        return score


__all__ = ['StateEvaluator']
