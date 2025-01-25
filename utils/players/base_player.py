from abc import abstractmethod, ABC


class Player(ABC):
    """ Abstract class representing a player. """

    legal_moves = []
    _initialized = False


    def __init__(self):
        """ Create an instance of the Player class. """

        if not Player._initialized:
            Player.reset_legal_moves()
            Player._initialized = True

        self.sign = None


    def set_sign(self, sign: str):
        """
        Set the player's sign.

        Arguments:
            sign: The sign, X or O.
        """

        self.sign = sign


    @staticmethod
    def reset_legal_moves():
        """ Reset the legal moves list. """

        Player.legal_moves = [[i for i in range(1, 10)] for _ in range(1, 10)]
        Player.legal_moves.insert(0, [])


    @abstractmethod
    def make_move(self, state: tuple[dict, ...], prev_small_idx: int) -> tuple[int, int]:
        """
        Make a move.

        Arguments:
            state: The game state.
            prev_small_idx: The small index of the previous move made.

        Returns:
            The input for the chosen move.
        """

        return self.get_current_legal_moves(prev_small_idx)[0]


    @classmethod
    def update_legal_moves(cls, big_idx: int, small_idx: int, board_is_complete: bool = False):
        """
        Remove all moves that will be illegal for the rest of the game.

        Arguments:
             big_idx: Board index.
             small_idx: Position index.
             board_is_complete: Whether the board at big_idx is completed.
        """

        if board_is_complete:
            cls.legal_moves[big_idx].clear()

        else:
            cls.legal_moves[big_idx].remove(small_idx)


    def get_current_legal_moves(self, prev_small_idx: int | None) -> list[tuple[int, int]]:
        """
        Get all currently legal moves.

        Arguments:
            prev_small_idx: The small index of the previous move made
                or None if the previous move takes the next player to a completed board.

        Returns:
            A tuple of all legal moves in (big_idx, small_idx) format for the current state.
        """

        if prev_small_idx is None:
            return [
                (big_idx, small_idx)
                for big_idx in range(1, 10) if self.legal_moves[big_idx]
                for small_idx in self.legal_moves[big_idx]
            ]

        return [(prev_small_idx, i) for i in self.legal_moves[prev_small_idx]]


    def get_legal_moves_for_state(self, state: tuple[dict, ...], prev_small_idx: int | None) -> list[tuple[int, int]]:
        """
        Get all legal moves for a state.

        Arguments:
            state: The game state.
            prev_small_idx: The small index of the previous move made
                or None if the previous move takes the next player to a completed board.

        Returns:
            A tuple of all legal moves in (big_idx, small_idx) format for the given state.
        """

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


__all__ = ['Player']
