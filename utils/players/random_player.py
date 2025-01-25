from .base_player import Player
import random


class RandomPlayer(Player):
    """ Class representing a player that makes random moves. """

    def __init__(self):
        """ Create an instance of the RandomPlayer class. """

        super().__init__()


    def make_move(self, state: tuple[dict, ...], prev_small_idx: int) -> tuple[int, int]:
        return random.choice(self.get_current_legal_moves(prev_small_idx))


__all__ = ['RandomPlayer']
