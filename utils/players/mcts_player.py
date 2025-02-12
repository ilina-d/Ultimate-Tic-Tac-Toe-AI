import time
import random
import math

from .base_player import Player
from utils.helpers import StateEvaluator, StateChecker, StateUpdater


class MCTSNode():
    def __init__(self, state: tuple[dict, ...], parent: 'MCTSNode' = None, move: tuple[int, int] = None,
                 untried_moves: tuple[tuple[[int, int], ...]] = None):
        self.state = state
        self.parent = parent
        self.move = move
        self.untried_moves = untried_moves
        self.children = []
        self.score = 0
        self.visits = 0


    def ucb1(self, exploration_constant: float) -> float:
        if self.visits == 0:
            return float('inf')
        return (self.score / self.visits) + exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)


    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0


class MCTSPlayer(Player):
    def __init__(self, exploration_constant: float = 1.414, target_depth: int | str = 'dynamic'):
        self.exploration_constant = exploration_constant
        self.target_depth = target_depth


    # TODO: Continue here
    def make_move(self, state: tuple[dict, ...], prev_small_idx: int) -> tuple[int, int]:
        pass



__all__ = ['MCTSPlayer']
