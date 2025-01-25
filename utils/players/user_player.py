from .base_player import Player


class UserPlayer(Player):
    """ Class representing a human player. """

    def __init__(self):
        super().__init__()


    def make_move(self, state: tuple[dict, ...], prev_small_idx: int) -> tuple[int, int]:
        while True:
            try:
                big_idx, small_idx = map(int, input('> ').split(' '))

                if prev_small_idx is None and state[0]['display'][big_idx] == '-':
                    prev_small_idx = big_idx

                if big_idx in range(1, 10) and small_idx in range(1, 10) \
                   and state[big_idx]['display'][small_idx] == '-' \
                   and state[0]['display'][big_idx] == '-' \
                   and prev_small_idx == big_idx:
                    break

            except ValueError:
                pass

            print('--- Invalid move... 🙄')

        return big_idx, small_idx


__all__ = ['UserPlayer']
