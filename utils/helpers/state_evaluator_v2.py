from .state_checker import StateChecker
from .assets import inverse_board_display


StateChecker = StateChecker()

# Board Positions
CORNERS = MS_MIDDLES = [1, 3, 7, 9]
MIDDLES = MS_CORNERS = [2, 4, 6, 8]

# Weights
SCORE_GAME_WIN = 100
SCORE_GAME_TIE = 0

SCORE_BOARD_TIE = 0
SCORE_BOARD_WIN = 5
MODIFIER_CENTER_WIN = 10
MODIFIER_CORNER_WIN = 3
MODIFIER_MIDDLE_WIN = 0

SCORE_CENTER_SQUARE = 3
SCORE_CORNER_SQUARE = 2
SCORE_PER_CENTER_BOARD_SQUARE = 3

SCORE_TWO_ROW_SQUARES = 2
SCORE_TWO_ROW_BOARDS = 4
SCORE_FORK_SQUARES = 2
SCORE_FORK_BOARDS = 4
SCORE_BLOCK_SQUARES = 2
SCORE_BLOCK_BOARDS = 4

PENALTY_FREE_MOVE = -2
TOGGLE_ADVANTAGE_CALCULATION = True

THRESHOLD_TROLL = 50
MODIFIER_TROLL = 5


class StateEvaluatorV2:
    """ Helper singleton class for evaluating game states. """

    _instance = None


    def __new__(cls) -> 'StateEvaluatorV2':
        """
        Create a new instance of the StateEvaluator class if it doesn't already exist.

        Returns:
            Instance of the StateEvaluator class.
        """

        if cls._instance is None:
            cls._instance = super(StateEvaluatorV2, cls).__new__(cls)
            cls._instance.evaluated_boards = {}

        return cls._instance


    @staticmethod
    def get_row_score(big_idx: int, ms_idx: int, sign_pos: list[int], calc_for: str) -> int:
        """
        Get the score for the given magic square position depending on what's being calculated.

        Calculation Options:
            - "blocking" | Calculates score for blocking opponent's two in a row.
            - "two_row" | Calculates score for placing two signs in a row.

        Arguments:
            big_idx: Board index, 0 for big board.
            ms_idx: A magic square index of the position (given sign or empty space).
            sign_pos: Magic square positions of the other sign (opposing or given signs).
            calc_for: What's being calculated.

        Returns:
            The score gain based on the calculation option.
        """

        if len(sign_pos) < 2:
            return 0

        if big_idx == 0:
            score_gain = SCORE_BLOCK_BOARDS if calc_for == 'blocking' else SCORE_TWO_ROW_BOARDS
        else:
            score_gain = SCORE_BLOCK_SQUARES if calc_for == 'blocking' else SCORE_TWO_ROW_SQUARES

        score = 0
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
                    score += score_gain
                    sign_pos.pop(right)
                    sign_pos.pop(left)
                    break

                if left == right:
                    blocks_found = False
                    break

            if not blocks_found:
                break

        return score


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

        board = state[big_idx]['display']
        if board in self._instance.evaluated_boards:
            return self._instance.evaluated_boards[board]

        inverted_board = inverse_board_display(board)
        if inverted_board in self._instance.evaluated_boards:
            return -self._instance.evaluated_boards[inverted_board]

        winner = StateChecker.check_win(state, big_idx)

        # Check if board is tied
        if winner == 'T':
            return SCORE_BOARD_TIE

        # Check if board is won
        if winner:
            if big_idx == 5:
                score = SCORE_BOARD_WIN + MODIFIER_CENTER_WIN
            elif big_idx in CORNERS:
                score = SCORE_BOARD_WIN + MODIFIER_CORNER_WIN
            else:
                score = SCORE_BOARD_WIN + MODIFIER_MIDDLE_WIN

            return score if sign == 'X' else -score

        score = 0
        given_sign_pos = sorted(list(state[big_idx][sign]))
        other_sign_pos = sorted(state[big_idx]['X' if sign == 'O' else 'O'])
        empty_sign_pos = [pos for pos in range(1, 10) if pos not in given_sign_pos + other_sign_pos]

        # Check for squares in the center board
        if big_idx == 5:
            score += SCORE_PER_CENTER_BOARD_SQUARE * len(given_sign_pos)

        # Calculate advantage
        if TOGGLE_ADVANTAGE_CALCULATION and big_idx != 0:
            score += len(state[big_idx]['X']) - len(state[big_idx]['O'])

        for ms_idx in given_sign_pos:
            # Check if the corner square is taken
            if ms_idx in MS_CORNERS:
                score += SCORE_CORNER_SQUARE

            # Check if the center square is taken
            elif ms_idx == 5:
                score += SCORE_CENTER_SQUARE

            # Check for blocking opponent's two in a row
            score += self.get_row_score(big_idx, ms_idx, other_sign_pos, calc_for = 'blocking')

        # Check for placing two in a row
        for ms_idx in empty_sign_pos:
            score += self.get_row_score(big_idx, ms_idx, given_sign_pos, calc_for = 'two_row')

        # Check for forks
        if len([pos for pos in given_sign_pos if pos in MS_CORNERS + [5]]) >= 3:
            score += SCORE_FORK_BOARDS if big_idx == 0 else SCORE_FORK_SQUARES

        score = score if sign == 'X' else -score
        self._instance.evaluated_boards[board] = score
        self._instance.evaluated_boards[inverted_board] = -score

        return score


    def heuristic(self, state: tuple[dict, ...], next_big_idx: int | None, sign: str, depth: int = None) -> float:
        """
        Evaluate the given state.

        Arguments:
            state: A game state.
            next_big_idx: Board index where the next player makes a move, or None if any move is possible.
            sign: The sign to evaluate for.
            depth: The depth at which the state is being evaluated.

        Returns:
            The heuristic value for the state being evaluated.
        """

        winner = StateChecker.check_win(state, big_idx = 0)

        # Check if game ended in a tie
        if winner == 'T':
            return SCORE_GAME_TIE

        # Check if game ended in a win
        if winner:
            return SCORE_GAME_WIN if winner == 'X' else -SCORE_BOARD_WIN

        score = 0

        # Calculate score gain from each board
        for big_idx in range(10):
            score += self.evaluate_board(state, big_idx, 'X') + self.evaluate_board(state, big_idx, 'O')

        # Check if the next move is free
        if next_big_idx and state[0]['display'][next_big_idx] != '-':
            score += PENALTY_FREE_MOVE if sign == 'X' else -PENALTY_FREE_MOVE

        score = score if sign == 'X' else -score

        # Check if the evaluation meets the trolling threshold
        if depth:
            if sign == 'X' and score >= THRESHOLD_TROLL:
                score += depth * MODIFIER_TROLL
            elif sign == 'O' and score <= -THRESHOLD_TROLL:
                score -= depth * MODIFIER_TROLL

        return score


__all__ = ['StateEvaluatorV2']
