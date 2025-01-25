from os import system
import time

from utils.players import Player, UserPlayer
from utils.helpers import StateChecker, StateEvaluator, StateUpdater, GameEvaluator


StateChecker = StateChecker()
StateEvaluator = StateEvaluator()


class Game:
    """ Class representing the game state. """

    def __init__(self, player1: Player = UserPlayer(), player2: Player = UserPlayer(),
                 printing: bool = True, wait_after_move: int | str | None = 'input',
                 show_evaluation: bool = False, measure_thinking_time: bool = False):
        """
        Create an instance of the Game class.

        Waiting Methods:
            - int | Number of milliseconds to wait.
            - "input" | Wait until input is given.
            - None | No waiting.

        Arguments:
             player1: The first player object.
             player2: The second player object.
             printing: Whether to print the board after each move.
             wait_after_move: The method for waiting after each move.
             show_evaluation: Whether to show the heuristic evaluation throughout the game.
                Printing needs to be turned on for this to work.
             measure_thinking_time: Whether to measure the time it takes for each player to make a move.
        """

        self.state = None
        self.player1, self.player2 = player1, player2
        self.player1.set_sign('X'), self.player2.set_sign('O')
        self.prev_small_idx = None
        self.prev_move_made = None

        self.printing = printing
        self.show_evaluation = show_evaluation
        self.game_evaluator = GameEvaluator()

        self.measure_thinking_time = measure_thinking_time
        self.player1_thinking_times = []
        self.player2_thinking_times = []

        def waiting(start_time: float = None):
            if wait_after_move is None:
                return
            if wait_after_move == 'input':
                input('... waiting for input ...')
                return
            if start_time:
                if time.time() - start_time <= wait_after_move:
                    time.sleep(int(wait_after_move - (time.time() - start_time)) / 1000)
                return
            else:
                time.sleep(wait_after_move / 1000)
        self.wait_after_move = waiting

        self.reset_state()


    def reset_state(self):
        """ Reset the current state to its starting form. """

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


    def print_board(self):
        """ Prints the entire board. """

        s = self.state

        for i in (1, 4, 7):
            for j in (1, 4, 7):
                print(f'{s[i + 0]["display"][j]} {s[i + 0]["display"][j + 1]} {s[i + 0]["display"][j + 2]}  |  '
                      f'{s[i + 1]["display"][j]} {s[i + 1]["display"][j + 1]} {s[i + 1]["display"][j + 2]}  |  '
                      f'{s[i + 2]["display"][j]} {s[i + 2]["display"][j + 1]} {s[i + 2]["display"][j + 2]}')

            if i != 7:
                print('-------------------------')

        print('\n')

        for i in (1, 4, 7):
            print(f'{s[0]["display"][i]} | {s[0]["display"][i + 1]} | {s[0]["display"][i + 2]}')
            if i != 7:
                print('---------')

        print('\n')


    def make_move(self, sign: str, player: Player):
        """
        Make a move for a given sign.

        Arguments:
             sign: X or O.
             player: The player whose turn it is.
        """

        if self.measure_thinking_time:
            thinking_time_start = time.time()
            big_idx, small_idx = player.make_move(self.state, self.prev_small_idx)
            thinking_times = self.player1_thinking_times if sign == 'X' else self.player2_thinking_times
            thinking_times.append(time.time() - thinking_time_start)

        else:
            big_idx, small_idx = player.make_move(self.state, self.prev_small_idx)

        state, board_is_complete = StateUpdater.update_state(self.state, big_idx, small_idx, sign)
        self.state = state

        if self.state[0]['display'][small_idx] != '-':
            self.prev_small_idx = None
        else:
            self.prev_small_idx = small_idx

        self.prev_move_made = (big_idx, small_idx)

        player.update_legal_moves(big_idx, small_idx, board_is_complete = board_is_complete)


    def play(self):
        """ Start the game. """

        sign = 'X'
        player = self.player1
        move_start_time = None

        while not StateChecker.check_win(self.state, big_idx = 0):
            if self.printing:
                system('cls')
                self.print_board()
                print(f'{"X" if sign == "O" else "O"} made the move: {self.prev_move_made}')

                if self.measure_thinking_time:
                    if sign == 'O' and self.player1_thinking_times:
                        print(f'Time taken for move: {self.player1_thinking_times[-1]}')
                    elif sign == 'X' and self.player2_thinking_times:
                        print(f'Time taken for move: {self.player2_thinking_times[-1]}')

                if self.show_evaluation:
                    print(f'Game Evaluation  : '
                          f'{self.game_evaluator.game_evaluation(self.state, self.prev_small_idx, player)}')

            if not isinstance(player, UserPlayer):
                self.wait_after_move(move_start_time)

            move_start_time = time.time()
            self.make_move(sign, player)

            sign = 'O' if sign == 'X' else 'X'
            player = self.player2 if player == self.player1 else self.player1

        if self.printing:
            system('cls')
            self.print_board()
            print(f'WINNER: {StateChecker.check_win(self.state, big_idx = 0)}')

        self.wait_after_move()


__all__ = ['Game']
