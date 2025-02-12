import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

from utils.game import Game, GameUI
from utils.players import UserPlayer, RandomPlayer, MiniMaxPlayer, ExpectiMaxPlayer
from utils.simulator import Simulator
from utils.helpers import GameEvaluator, StateChecker


if __name__ == '__main__':

    # simulator = Simulator(
    #     num_simulations = 10,
    #     player1 = MiniMaxPlayer(target_depth = 5),
    #     player2 = MiniMaxPlayer(target_depth = 5),
    #     print_games = False,
    #     measure_performance = True
    # )
    #
    # simulator.start()

    GameEvaluator(
        algorithm = MiniMaxPlayer(target_depth = 5, use_randomness = True)
    )

    game = GameUI(
        printing = False,
        show_evaluation = False,
        wait_after_move = 300,
        opaque_on_board_completion = False,
        light_theme = False
    )

    game.play()

    input('... waiting for input ...')
