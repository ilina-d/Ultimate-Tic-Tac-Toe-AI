from utils.helpers import magic_square


class StateGenerator:
    """ Helper class for generating game states used in testing. """

    @staticmethod
    def generate(_0: str = None, _1: str = None, _2: str = None, _3: str = None, _4: str = None,
                 _5: str = None, _6: str = None, _7: str = None, _8: str = None, _9: str = None) -> tuple[dict, ...]:
        """
        Generate a new state.

        Each argument corresponds to a board index (0 for big board) and takes a display string as its value,
        without the offset ( "/" ). None values are treated as empty boards.
        """

        state = []

        boards = [_0, _1, _2, _3, _4, _5, _6, _7, _8, _9]
        for board in boards:
            if board is None:
                state.append({'X' : (), 'O' : (), 'display' : ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')})
                continue

            board_dict = {'X' : [], 'O' : [], 'display' : tuple(f'/{board}')}

            for idx, sign in enumerate(board):
                if sign in board_dict:
                    board_dict[sign].append(magic_square[idx + 1])

            board_dict['X'] = tuple(board_dict['X'])
            board_dict['O'] = tuple(board_dict['O'])

            state.append(board_dict)

        return tuple(state)