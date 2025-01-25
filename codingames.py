from abc import abstractmethod, ABC
import sys
import random
import time


########################################################################################################################


class Debugger:
    enabled = True


    @staticmethod
    def debug(message):
        if Debugger.enabled:
            print(message, file=sys.stderr, flush=True)


########################################################################################################################


class Convert:
    idx_to_rc = (
        ((-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)),
        ((-1, -1), (0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)),
        ((-1, -1), (0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)),
        ((-1, -1), (0, 6), (0, 7), (0, 8), (1, 6), (1, 7), (1, 8), (2, 6), (2, 7), (2, 8)),
        ((-1, -1), (3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2)),
        ((-1, -1), (3, 3), (3, 4), (3, 5), (4, 3), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)),
        ((-1, -1), (3, 6), (3, 7), (3, 8), (4, 6), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8)),
        ((-1, -1), (6, 0), (6, 1), (6, 2), (7, 0), (7, 1), (7, 2), (8, 0), (8, 1), (8, 2)),
        ((-1, -1), (6, 3), (6, 4), (6, 5), (7, 3), (7, 4), (7, 5), (8, 3), (8, 4), (8, 5)),
        ((-1, -1), (6, 6), (6, 7), (6, 8), (7, 6), (7, 7), (7, 8), (8, 6), (8, 7), (8, 8))
    )

    rc_to_idx = (
        ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)),
        ((1, 4), (1, 5), (1, 6), (2, 4), (2, 5), (2, 6), (3, 4), (3, 5), (3, 6)),
        ((1, 7), (1, 8), (1, 9), (2, 7), (2, 8), (2, 9), (3, 7), (3, 8), (3, 9)),
        ((4, 1), (4, 2), (4, 3), (5, 1), (5, 2), (5, 3), (6, 1), (6, 2), (6, 3)),
        ((4, 4), (4, 5), (4, 6), (5, 4), (5, 5), (5, 6), (6, 4), (6, 5), (6, 6)),
        ((4, 7), (4, 8), (4, 9), (5, 7), (5, 8), (5, 9), (6, 7), (6, 8), (6, 9)),
        ((7, 1), (7, 2), (7, 3), (8, 1), (8, 2), (8, 3), (9, 1), (9, 2), (9, 3)),
        ((7, 4), (7, 5), (7, 6), (8, 4), (8, 5), (8, 6), (9, 4), (9, 5), (9, 6)),
        ((7, 7), (7, 8), (7, 9), (8, 7), (8, 8), (8, 9), (9, 7), (9, 8), (9, 9))
    )


    @staticmethod
    def to_rc(big_idx, small_idx):
        row, col = Convert.idx_to_rc[big_idx][small_idx]
        return f'{row} {col}'


    @staticmethod
    def to_idx(row_col):
        big_idx, small_idx = map(int, row_col.split(' '))
        return Convert.rc_to_idx[big_idx][small_idx]


########################################################################################################################


class GameData:
    _instance = None


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameData, cls).__new__(cls)
            cls._instance.first_input = None
            cls._instance.current_legal_moves = []
        return cls._instance


    def set_first_input(self, value):
        self._instance.first_input = value


    def get_current_legal_moves(self):
        self._instance.current_legal_moves.clear()

        num_valid_moves = int(input())
        for _ in range(num_valid_moves):
            self._instance.current_legal_moves.append(Convert.to_idx(input()))


    @staticmethod
    def ignore_legal_moves_input():
        num_valid_moves = int(input())
        for _ in range(num_valid_moves):
            input()


########################################################################################################################


class StateChecker:
    _instance = None


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateChecker, cls).__new__(cls)
            cls._instance.checked_boards = {}

        return cls._instance


    @staticmethod
    def check_win_helper(sign, positions):
        positions = sorted(positions)
        length = len(positions)

        for i in range(length - 2):
            left = i + 1
            right = length - 1

            while left != right:
                score = positions[i] + positions[left] + positions[right]
                if score < 15:
                    left += 1
                elif score > 15:
                    right -= 1
                else:
                    return sign

        return False


    def check_win(self, state, big_idx):
        if big_idx != 0:
            winning_sign = state[0]['display'][big_idx]
            if winning_sign != '-':
                return winning_sign

        board_display = state[big_idx]['display']
        if board_display in self._instance.checked_boards:
            return self._instance.checked_boards[board_display]

        board = state[big_idx]
        len_x, len_o = len(board['X']), len(board['O'])

        result = None

        if len_x >= 3:
            result = self.check_win_helper('X', board['X'])

        if not result and len_o >= 3:
            result = self.check_win_helper('O', board['O'])

        inverted_board_display = inverse_board_display(board_display)

        if result:
            self._instance.checked_boards[board_display] = result
            self._instance.checked_boards[inverted_board_display] = 'X' if result == 'O' else 'O'
            return result

        if '-' not in board['display']:
            self._instance.checked_boards[board_display] = 'T'
            self._instance.checked_boards[inverted_board_display] = 'T'
            return 'T'

        self._instance.checked_boards[board_display] = False
        self._instance.checked_boards[inverted_board_display] = False
        return False


########################################################################################################################


class StateUpdater:

    @staticmethod
    def update_state(state, big_idx, small_idx, sign):
        updated_state = list(dict(d) for d in state)
        updated_state[big_idx]['display'] = list(updated_state[big_idx]['display'])

        updated_state[big_idx][sign] = updated_state[big_idx][sign] + (magic_square[small_idx],)
        updated_state[big_idx]['display'][small_idx] = sign

        updated_state[big_idx]['display'] = tuple(updated_state[big_idx]['display'])
        winning_sign = StateChecker.check_win(tuple(updated_state), big_idx)

        board_is_complete = False
        if winning_sign:
            if winning_sign != 'T':
                updated_state[0][winning_sign] = updated_state[0][winning_sign] + (magic_square[big_idx],)

            updated_state[0]['display'] = list(updated_state[0]['display'])
            updated_state[0]['display'][big_idx] = winning_sign
            updated_state[0]['display'] = tuple(updated_state[0]['display'])

            board_is_complete = True

        return tuple(updated_state), board_is_complete


########################################################################################################################


class StateEvaluator:
    _instance = None


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateEvaluator, cls).__new__(cls)
            cls._instance.evaluated_boards = {}

        return cls._instance


    @staticmethod
    def get_row_score(ms_idx, sign_pos, calc_for):
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


    def evaluate_board(self, state, big_idx, sign = None):
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
            score += self.get_row_score(ms_idx, other_sign_pos, calc_for='blocking')

        # Check for placing two in a row
        for ms_idx in empty_sign_pos:
            score += self.get_row_score(ms_idx, given_sign_pos, calc_for='two_row')

        # Check for forks
        if len([pos for pos in given_sign_pos if pos in MS_FORKS]) >= 3:
            score += SCORE_FORK

        return score if sign == 'X' else -score


    def heuristic(self, state, next_big_idx, sign):
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


########################################################################################################################


class Player(ABC):
    legal_moves = []
    _initialized = False


    def __init__(self):
        if not Player._initialized:
            Player.reset_legal_moves()
            Player._initialized = True

        self.sign = None

    def set_sign(self, sign: str):
        self.sign = sign


    @staticmethod
    def reset_legal_moves():
        Player.legal_moves = [[i for i in range(1, 10)] for _ in range(1, 10)]
        Player.legal_moves.insert(0, [])


    @abstractmethod
    def make_move(self, state, prev_small_idx):
        return self.get_current_legal_moves(prev_small_idx)[0]


    @classmethod
    def update_legal_moves(cls, big_idx, small_idx, board_is_complete):
        if board_is_complete:
            cls.legal_moves[big_idx].clear()

        else:
            cls.legal_moves[big_idx].remove(small_idx)


    def get_current_legal_moves(self, prev_small_idx):
        if GameData.current_legal_moves:
            return GameData.current_legal_moves

        if prev_small_idx is None:
            return [
                (big_idx, small_idx)
                for big_idx in range(1, 10) if self.legal_moves[big_idx]
                for small_idx in self.legal_moves[big_idx]
            ]

        return [(prev_small_idx, i) for i in self.legal_moves[prev_small_idx]]


    def get_legal_moves_for_state(self, state, prev_small_idx):
        if prev_small_idx is None or state[0]['display'][prev_small_idx] != '-':
            unoccupied_boards = [big_idx for big_idx, elem in enumerate(state[0]['display']) if elem == '-']
            return [
                (big_idx, small_idx)
                for big_idx in unoccupied_boards
                for small_idx in self.legal_moves[big_idx]
            ]

        else:
            return [
                (prev_small_idx, small_idx)
                for small_idx, sign in enumerate(state[prev_small_idx]['display']) if sign == '-'
            ]


#######################################################################################################################


class RandomPlayer(Player):

    def __init__(self):
        super().__init__()


    def make_move(self, state, prev_small_idx):
        return random.choice(self.get_current_legal_moves(prev_small_idx))


#######################################################################################################################


class UserPlayer(Player):
    def __init__(self):
        super().__init__()


    def make_move(self, state, prev_small_idx):
        if GameData.first_input:
            big_idx, small_idx = Convert.to_idx(GameData.first_input)
            GameData.set_first_input(None)

        else:
            big_idx, small_idx = Convert.to_idx(input())

        return big_idx, small_idx


#######################################################################################################################


class MiniMaxPlayer(Player):

    def __init__(self, target_depth, use_randomness=False):
        super().__init__()

        if target_depth == 'dynamic':
            self.target_depth = INIT_DYNAMIC_DEPTH
            self.use_dynamic_depth = True
            self.use_timed_depth = False

        elif target_depth == 'timed':
            self.target_depth = 4
            self.use_dynamic_depth = False
            self.use_timed_depth = True

        else:
            self.target_depth = target_depth
            self.use_dynamic_depth = False
            self.use_timed_depth = False

        self.sign = None
        self.use_randomness = use_randomness
        self.moves_made = -1
        self.counter = INIT_COUNTER
        self.start_time = None


    def minimax_ab(self, state, prev_small_idx, curr_depth, alpha, beta, is_maximizing):
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


    def get_premove(self, state, prev_small_idx, is_maximizing):
        if is_maximizing and self.moves_made == 0:
            if self.use_randomness:
                return random.randint(1, 9), random.randint(1, 9)
            return 5, 5

        if prev_small_idx and state[prev_small_idx]['display'].count('-') == 9:
            return prev_small_idx, prev_small_idx

        return None


    def update_target_depth(self):
        if self.use_timed_depth:
            self.start_time = time.time()

        elif self.use_dynamic_depth and self.moves_made > THRESHOLD and self.moves_made % STEP == 0:
            self.target_depth += BASE ** self.counter
            self.counter += 1


    def make_move(self, state, prev_small_idx):
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


########################################################################################################################


class Game:

    def __init__(self, player1, player2):
        self.state = None
        self.player1, self.player2 = player1, player2
        self.player1.set_sign('X'), self.player2.set_sign('O')
        self.prev_small_idx = None
        self.prev_move_made = None

        self.reset_state()


    def reset_state(self):
        self.prev_small_idx = None
        self.state = (
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # Big board
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # Top-left small board
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # Top-middle small board
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # Top-right small board
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # Mid-left small board
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},  # ...
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')},
        )


    def make_move(self, sign: str, player: Player):
        big_idx, small_idx = player.make_move(self.state, self.prev_small_idx)

        if not isinstance(player, UserPlayer):
            print(Convert.to_rc(big_idx, small_idx))
        else:
            GameData.get_current_legal_moves()

        state, board_is_complete = StateUpdater.update_state(self.state, big_idx, small_idx, sign)
        self.state = state

        if self.state[0]['display'][small_idx] != '-':
            self.prev_small_idx = None
        else:
            self.prev_small_idx = small_idx

        self.prev_move_made = (big_idx, small_idx)
        player.update_legal_moves(big_idx, small_idx, board_is_complete=board_is_complete)


    def play(self):
        sign = 'X'
        player = self.player1

        while True:
            self.make_move(sign, player)
            sign = 'O' if sign == 'X' else 'X'
            player = self.player2 if player == self.player1 else self.player1


########################################################################################################################


# Assets
magic_square = (None,
                2, 7, 6,
                9, 5, 1,
                4, 3, 8)

translation_table = str.maketrans('XO', 'OX')


def inverse_board_display(board_display):
    return tuple(''.join(board_display).translate(translation_table))


# Classes
CORNERS = MS_MIDDLES = {1, 3, 7, 9}
MIDDLES = MS_CORNERS = {2, 4, 6, 8}
MS_FORKS = {2, 4, 6, 8, 5}
GameData = GameData()
StateChecker = StateChecker()
StateEvaluator = StateEvaluator()

# Debugging
Debugger.enabled = False

# MiniMax Settings
INIT_DYNAMIC_DEPTH = 3
INIT_COUNTER = 0
THRESHOLD = 18
STEP = 3
BASE = 2
TIME_BREAK = 0.085

# Heuristic Weights
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

########################################################################################################################


first_input = input()
if first_input == '-1 -1':
    game = Game(
        MiniMaxPlayer(target_depth = 3),
        UserPlayer()
    )

    GameData.ignore_legal_moves_input()

else:
    game = Game(
        UserPlayer(),
        MiniMaxPlayer(target_depth = 3)
    )

    GameData.set_first_input(first_input)

game.play()
