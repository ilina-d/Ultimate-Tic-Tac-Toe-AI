magic_square = (None,
                2, 7, 6,
                9, 5, 1,
                4, 3, 8)


translation_table = str.maketrans('XO', 'OX')
def inverse_board_display(board_display: tuple[str, ...]) -> tuple[str, ...]:
    """
    Invert the signs on the given board display.

    Arguments:
        board_display: The board display.

    Returns:
        An inverted board display where only X and O are switched.
    """

    return tuple(''.join(board_display).translate(translation_table))


__all__ = ['magic_square', 'inverse_board_display']
