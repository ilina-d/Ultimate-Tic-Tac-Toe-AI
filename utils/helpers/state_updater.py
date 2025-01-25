from .assets import magic_square
from .state_checker import StateChecker


StateChecker = StateChecker()


class StateUpdater:
    """ Helper class for updating the state of a board. """

    @staticmethod
    def update_state(state: tuple[dict, ...], big_idx: int, small_idx: int, sign: str) -> tuple[tuple[dict, ...], bool]:
        """
        Update the given state based on the last move made.

        Arguments:
            state: The board state to update.
            big_idx: At which board the move was made.
            small_idx: Position of the move made on the board.
            sign: Sign of the player who made the move.

        Returns:
            The updated state and whether the board at big_idx is complete.
        """

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


__all__ = ['StateUpdater']
