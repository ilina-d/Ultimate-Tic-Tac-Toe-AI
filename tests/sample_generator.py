from state_generator import StateGenerator

class SampleGenerator:
    """
    Helper class for generating sample states and legal moves used in testing.

    Scenarios include: empty_board, full_board, couple_boards_empty and couple_moves_made.
    """

    @staticmethod
    def get_sample_legal_moves():
        """
        Method that generates legal moves for several state scenarios used for testing purposes.

        Returns:
            Dictionary containing the legal moves for a given scenario.
        """
        sample_legal_moves = dict()

        sample_legal_moves["empty_board"] = [[i for i in range(1, 10)] for _ in range(1, 10)]
        sample_legal_moves["empty_board"].insert(0, [])

        sample_legal_moves["full_board"] = [[] for _ in range(1, 11)]

        sample_legal_moves["couple_boards_empty"] = [[] for _ in range(1, 7)]
        sample_legal_moves["couple_boards_empty"].insert(1, [i for i in range(1, 10)])
        sample_legal_moves["couple_boards_empty"].insert(2, [i for i in range(1, 10)])
        sample_legal_moves["couple_boards_empty"].insert(4, [i for i in range(1, 10)])
        sample_legal_moves["couple_boards_empty"].insert(8, [i for i in range(1, 10)])

        sample_legal_moves["couple_moves_left"] = [[] for _ in range(1, 6)]
        sample_legal_moves["couple_moves_left"].insert(3, [1, 2, 7, 6])
        sample_legal_moves["couple_moves_left"].insert(4, [8, 9])
        sample_legal_moves["couple_moves_left"].insert(5, [9, ])
        sample_legal_moves["couple_moves_left"].insert(7, [1, 2, 3, 4, 5])
        sample_legal_moves["couple_moves_left"].insert(9, [2, ])

        sample_legal_moves["couple_moves_made"] = [[i for i in range(1, 10)] for _ in range(1, 10)]
        sample_legal_moves["couple_moves_made"].insert(0, [])
        sample_legal_moves["couple_moves_made"][4].remove(4)
        sample_legal_moves["couple_moves_made"][4].remove(9)
        sample_legal_moves["couple_moves_made"][9].remove(1)
        sample_legal_moves["couple_moves_made"][1].remove(2)

        return sample_legal_moves


    @staticmethod
    def get_sample_states():
        """
        Method that generates legal moves for several state scenarios used for testing purposes.

        Returns:
            Dictionary containing the legal moves for a given scenario.
        """

        sample_states = dict()

        sample_states["empty_board"] = StateGenerator.generate()

        sample_states["full_board"] = StateGenerator.generate(_0='XOXOXXTTX',
                                                              _1='---XXX---', _2='OOO------', _3='---XXX---',
                                                              _4='O--O--O--', _5='XXX------', _6='X---X---X',
                                                              _7='XOOOXXXOO', _8='XOOOXXXOO', _9='XXX------')

        sample_states["couple_boards_empty"] = StateGenerator.generate(_0='--X-O0X-X', _3='--X-OXO-X', _5='OO-OXXO--',
                                                                       _6='-O--O--O-', _7='------XXX', _9='XXX------')

        sample_states["couple_moves_left"] = StateGenerator.generate(_0='XO---X-T-',
                                                                     _1='---XXX---', _2='OOO------', _3='--XOX--OO',
                                                                     _4='XOXOXOO--', _5='XOXOXOOX-', _6='X---X---X',
                                                                     _7='-----XXOO', _8='XOOOXXXOO', _9='X-XOXOOXO')

        sample_states["couple_moves_made"] = StateGenerator.generate(_1='-O-------', _4='---X----O', _9='X--------')

        return sample_states

