import cProfile
import time
import copy

from utils.game import Game
from utils.players import Player
from utils.helpers import StateChecker


StateChecker = StateChecker()


class Simulator:
    """ Class for simulating games and collecting results. """

    def __init__(self, num_simulations: int, player1: Player, player2: Player,
                 print_games: bool = False, measure_performance: bool = True):
        """
        Create an instance of the Simulator class.

        Arguments:
            num_simulations: Number of simulations to run.
            player1: The first player object.
            player2: The second player object.
            print_games: Whether to print the game states. Leave disabled for faster simulations.
            measure_performance: Whether to measure the performance of the code.
        """

        self.num_simulations = num_simulations
        self.player1 = player1
        self.player2 = player2
        self.print_games = print_games
        self.wait_after_move = 0.5 if print_games else None
        self.show_evaluation = False
        self.measure_performance = measure_performance


    def run_simulations(self):
        """ Run the simulations. """

        total_sim_time = time.time()
        game_times = []
        games_tied, games_won_x, games_won_o = 0, 0, 0
        thinking_times_x, thinking_times_o = [], []

        for n in range(1, self.num_simulations + 1):

            percent_done = (n / self.num_simulations) * 100
            estimated_tl = (sum(game_times) / n) * (self.num_simulations - n)
            if estimated_tl > 3600:
                estimated_tl = f'~{estimated_tl // 3600} hours'
            elif estimated_tl > 60:
                estimated_tl = f'~{estimated_tl // 60} minutes'
            elif estimated_tl == 0:
                estimated_tl = f'unknown'
            else:
                estimated_tl = f'~{int(estimated_tl)} seconds'

            print(
                f'[ SIMULATOR ] : Running Simulations... '
                f'{str(round(percent_done, 2)) + "%":<6} '
                f'<{"=" * int(percent_done)}{"-" * int(100 - int(percent_done))}> '
                f'| ETL: {estimated_tl}'
            )

            game_start_time = time.time()

            self.player1.reset_legal_moves()
            game = Game(
                copy.deepcopy(self.player1), copy.deepcopy(self.player2),
                printing = self.print_games,
                wait_after_move = self.wait_after_move,
                show_evaluation = self.show_evaluation,
                measure_thinking_time = True
            )
            game.play()

            game_times.append(time.time() - game_start_time)

            for t in game.player1_thinking_times:
                thinking_times_x.append(t)

            for t in game.player2_thinking_times:
                thinking_times_o.append(t)

            winner = StateChecker.check_win(game.state, big_idx = 0)
            match winner:
                case 'T':
                    games_tied += 1
                case 'X':
                    games_won_x += 1
                case 'O':
                    games_won_o += 1

        print(
            f'\n'
            f'    SIMULATOR : RESULTS \n'
            f'============================ \n'
            f'--- Duration Stats        : \n'
            f'* Total Simulation Time   : {round(time.time() - total_sim_time, 2)}s \n'
            f'* Total Game Time         : {round(sum(game_times), 2)}s \n'
            f'* Average Game Time       : {round(sum(game_times) / self.num_simulations, 2)}s \n'
            f'* Shortest Game           : {round(min(game_times), 2)}s \n'
            f'* Longest Game            : {round(max(game_times), 2)}s \n'
            f'============================ \n'
            f'--- Game Conclusion Stats : \n'
            f'* Games Tied              : {games_tied} \n'
            f'* Games Won/Lost X        : {games_won_x} / {games_won_o} \n'
            f'* Games Won/Lost O        : {games_won_o} / {games_won_x} \n'
            f'============================ \n'
            f'--- Thinking Time Stats   : \n'
            f'* Total TT X              : {round(sum(thinking_times_x), 2)}s \n'
            f'* Average TT X            : {round(sum(thinking_times_x) / len(thinking_times_x), 2)}s \n'
            f'* Shortest TT X           : {round(min(thinking_times_x), 2)}s \n'
            f'* Longest TT X            : {round(max(thinking_times_x), 2)}s \n'
            f' \n'
            f'* Total TT O              : {round(sum(thinking_times_o), 2)}s \n'
            f'* Average TT O            : {round(sum(thinking_times_o) / len(thinking_times_o), 2)}s \n'
            f'* Shortest TT O           : {round(min(thinking_times_o), 2)}s \n'
            f'* Longest TT O            : {round(max(thinking_times_o), 2)}s \n'
            f'============================ \n'
            f'\n'
        )


    def start(self):
        """ Start the simulator. """

        if self.measure_performance:
            profile = cProfile.Profile()
            profile.runcall(self.run_simulations)
            profile.print_stats()

        else:
            self.run_simulations()



__all__ = ['Simulator']
