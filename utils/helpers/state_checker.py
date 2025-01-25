from .assets import inverse_board_display


class StateChecker:
    """ Helper class for checking the state of a board. """

    _instance = None


    def __new__(cls) -> 'StateChecker':
        """
        Create a new instance of the StateChecker class if it doesn't already exist.

        Returns:
            Instance of the StateChecker class.
        """

        if cls._instance is None:
            cls._instance = super(StateChecker, cls).__new__(cls)
            cls._instance.checked_boards = {}

        return cls._instance


    @staticmethod
    def check_win_helper(sign: str, positions: tuple[int]) -> str | bool:
        """
        Helper function for check_win.

        Arguments:
            sign: X or O.
            positions: List of moves made for given sign.

        Returns:
            False if it's not winning, otherwise the sign itself.
        """

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


    def check_win(self, state: tuple[dict, ...], big_idx: int) -> str | bool:
        """
        Checks if there's a winner in a specific board.

        Arguments:
            state: The board state being checked.
            big_idx: Board index, 0 for big board.

        Returns:
            The winning sign ("T" if it's a tie) or False if it's neither tied nor won.
        """

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


__all__ = ['StateChecker']
