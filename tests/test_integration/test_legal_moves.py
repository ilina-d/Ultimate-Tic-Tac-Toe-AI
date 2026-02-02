import pytest

from utils.helpers.state_checker import StateChecker
from utils.helpers.state_updater import StateUpdater
from utils.players.base_player import Player
from tests.state_generator import StateGenerator


class TestLegalMovesStateUpdaterIntegration:
    """
    Integration tests for legal moves maintenance as state changes through StateUpdater.

    BCC criteria:
    A: Move location
        1 - center (position 5), 2 - corner (positions 1,3,7,9), 3 - edge (positions 2,4,6,8)
    B: Sending effect
        1 - sends to uncompleted board, 2 - sends to completed board
    C: Legal moves update
        1 - removes single move, 2 - clears entire board
    D: Current legal moves after update
        1 - all from next big index, 2 - some from next big index, 3 - all legal from all boards

    Base choice (happy path): A1 B1 C1 D1
    """

    @pytest.fixture(autouse=True)
    def reset_state(self):
        """Reset player legal moves before each test."""

        Player.reset_legal_moves()

        state_checker = StateChecker()
        state_checker._instance.checked_boards = {}

        yield

        Player.reset_legal_moves()
        state_checker._instance.checked_boards = {}


    @pytest.fixture
    def player(self):
        """Create a concrete Player instance for testing."""

        class TestPlayer(Player):
            def make_move(self, state, prev_small_idx):
                return self.get_current_legal_moves(prev_small_idx)[0]

        return TestPlayer()


    # A1 B1 C1 D1 - Base choice (happy path)
    def test_base_choice_center_no_completion_sends_uncompleted_removes_single_all_from_next(self, player):
        state = StateGenerator.generate(_1='---------', _5='---------')

        updated_state, board_complete = StateUpdater.update_state(state, 1, 5, 'X')
        player.update_legal_moves(1, 5, board_complete)

        assert board_complete == False, "Board should not be completed."
        assert updated_state[0]['display'][1] == '-', "Big board should show board 1 incomplete."

        assert 5 not in Player.legal_moves[1], "Position 5 should be removed from board 1 legal moves."
        assert len(Player.legal_moves[1]) == 8, "Board 1 should have 8 remaining legal moves."

        current_legal = player.get_current_legal_moves(5)
        assert len(current_legal) == 9, "Should have all 9 moves available on board 5."
        assert all(move[0] == 5 for move in current_legal), "All moves should be on board 5."


    # A2 B1 C1 D1
    def test_vary_a_corner_no_completion_sends_uncompleted_removes_single_all_from_next(self, player):
        state = StateGenerator.generate(_1='---------', _7='---------')

        updated_state, board_complete = StateUpdater.update_state(state, 1, 7, 'X')
        player.update_legal_moves(1, 7, board_complete)

        assert board_complete == False, "Board should not be completed."
        assert 7 not in Player.legal_moves[1], "Position 7 should be removed from board 1 legal moves."
        assert len(Player.legal_moves[1]) == 8, "Board 1 should have 8 remaining legal moves."

        current_legal = player.get_current_legal_moves(7)
        assert len(current_legal) == 9, "Should have all 9 moves available on board 7."
        assert all(move[0] == 7 for move in current_legal), "All moves should be on board 7."


    # A3 B1 C1 D1
    def test_vary_a_edge_no_completion_sends_uncompleted_removes_single_all_from_next(self, player):
        state = StateGenerator.generate(_1='---------', _2='---------')

        updated_state, board_complete = StateUpdater.update_state(state, 1, 2, 'X')
        player.update_legal_moves(1, 2, board_complete)

        assert board_complete == False, "Board should not be completed."
        assert 2 not in Player.legal_moves[1], "Position 2 should be removed from board 1 legal moves."
        assert len(Player.legal_moves[1]) == 8, "Board 1 should have 8 remaining legal moves."

        current_legal = player.get_current_legal_moves(2)
        assert len(current_legal) == 9, "Should have all 9 moves available on board 2."
        assert all(move[0] == 2 for move in current_legal), "All moves should be on board 2."


    # A1 B2 C2 D1
    def test_vary_b_c_center_completion_sends_uncompleted_clears_board_all_from_next(self, player):
        state = StateGenerator.generate(_1='X-------X', _5='---------')

        updated_state, board_complete = StateUpdater.update_state(state, 1, 5, 'X')
        player.update_legal_moves(1, 5, board_complete)

        assert board_complete == True, "Board should be completed."
        assert updated_state[0]['display'][1] == 'X', "Big board should show X won board 1."

        assert len(Player.legal_moves[1]) == 0, "Board 1 should have no legal moves after completion."

        current_legal = player.get_current_legal_moves(5)
        assert len(current_legal) == 9, "Should have all 9 moves available on board 5."


    # A1 B2 C1 D3
    def test_vary_b_d_center_no_completion_sends_completed_removes_single_all_from_all(self, player):
        state = StateGenerator.generate(_0='----X----', _1='---------', _5='XXX------')

        Player.legal_moves[5] = []

        updated_state, board_complete = StateUpdater.update_state(state, 1, 5, 'X')
        player.update_legal_moves(1, 5, board_complete)

        assert board_complete == False, "Board 1 should not be completed."
        assert 5 not in Player.legal_moves[1], "Position 5 should be removed from board 1."

        current_legal = player.get_current_legal_moves(None)

        boards_in_legal = set(move[0] for move in current_legal)
        assert 5 not in boards_in_legal, "Completed board 5 should not be in legal moves."
        assert len(boards_in_legal) == 8, "Should have moves from 8 uncompleted boards."


    # A1 B1 C1 D2
    def test_vary_d_center_no_completion_sends_uncompleted_removes_single_some_from_next(self, player):
        state = StateGenerator.generate(_1='---------', _5='XO-XO----')

        Player.legal_moves[5] = [3, 6, 7, 8, 9]

        updated_state, board_complete = StateUpdater.update_state(state, 1, 5, 'X')
        player.update_legal_moves(1, 5, board_complete)

        assert board_complete == False, "Board should not be completed."
        assert 5 not in Player.legal_moves[1], "Position 5 should be removed from board 1."

        current_legal = player.get_current_legal_moves(5)
        assert len(current_legal) == 5, "Should have 5 moves available on partially filled board 5."
        assert all(move[0] == 5 for move in current_legal), "All moves should be on board 5."


    # A2 B2 C2 D1
    def test_vary_a_b_c_corner_completion_sends_uncompleted_clears_board_all_from_next(self, player):
        state = StateGenerator.generate(_1='-XX------')

        updated_state, board_complete = StateUpdater.update_state(state, 1, 1, 'X')
        player.update_legal_moves(1, 1, board_complete)

        assert board_complete == True, "Board should be completed with top row."
        assert updated_state[0]['display'][1] == 'X', "Big board should show X won board 1."
        assert len(Player.legal_moves[1]) == 0, "Board 1 should have no legal moves."

        current_legal = player.get_current_legal_moves(1)
        assert len(current_legal) == 0, "Completed board 1 should have no legal moves."


    # A3 B2 C2 D3
    def test_vary_a_b_c_d_edge_completion_sends_completed_clears_board_all_from_all(self, player):
        state = StateGenerator.generate(
            _0='---O-----',
            _1='X-----X--',
            _4='OOO------'
        )

        Player.legal_moves[4] = []

        updated_state, board_complete = StateUpdater.update_state(state, 1, 4, 'X')
        player.update_legal_moves(1, 4, board_complete)

        assert board_complete == True, "Board should be completed with left column."
        assert updated_state[0]['display'][1] == 'X', "Big board should show X won board 1."
        assert len(Player.legal_moves[1]) == 0, "Board 1 should have no legal moves."

        current_legal = player.get_current_legal_moves(None)
        boards_in_legal = set(move[0] for move in current_legal)
        assert 1 not in boards_in_legal, "Completed board 1 should not be in legal moves."
        assert 4 not in boards_in_legal, "Completed board 4 should not be in legal moves."


    # A2 B2 C1 D3
    def test_vary_a_b_d_corner_no_completion_sends_completed_removes_single_all_from_all(self, player):
        state = StateGenerator.generate(
            _0='--X------',
            _1='---------',
            _3='XXX------'
        )

        Player.legal_moves[3] = []

        updated_state, board_complete = StateUpdater.update_state(state, 1, 3, 'O')
        player.update_legal_moves(1, 3, board_complete)

        assert board_complete == False, "Board 1 should not be completed."
        assert 3 not in Player.legal_moves[1], "Position 3 should be removed from board 1."
        assert len(Player.legal_moves[1]) == 8, "Board 1 should have 8 remaining moves."

        current_legal = player.get_current_legal_moves(None)
        boards_in_legal = set(move[0] for move in current_legal)
        assert 3 not in boards_in_legal, "Completed board 3 should not be in legal moves."
        assert len(boards_in_legal) == 8, "Should have moves from 8 uncompleted boards."


    # A3 B1 C1 D2
    def test_vary_a_d_edge_no_completion_sends_uncompleted_removes_single_some_from_next(self, player):
        state = StateGenerator.generate(_1='---------', _6='XOX-O-XO-')

        Player.legal_moves[6] = [4, 6, 9]

        updated_state, board_complete = StateUpdater.update_state(state, 1, 6, 'X')
        player.update_legal_moves(1, 6, board_complete)

        assert board_complete == False, "Board should not be completed."
        assert 6 not in Player.legal_moves[1], "Position 6 should be removed from board 1."

        current_legal = player.get_current_legal_moves(6)
        assert len(current_legal) == 3, "Should have 3 moves available on board 6."
        assert all(move[0] == 6 for move in current_legal), "All moves should be on board 6."


    # A1 B2 C2 D3
    def test_vary_b_c_d_center_completion_sends_completed_clears_board_all_from_all(self, player):

        state = StateGenerator.generate(
            _0='----O----',
            _1='X-------X',
            _5='OOO------'
        )

        Player.legal_moves[5] = []

        updated_state, board_complete = StateUpdater.update_state(state, 1, 5, 'X')
        player.update_legal_moves(1, 5, board_complete)

        assert board_complete == True, "Board should be completed."
        assert updated_state[0]['display'][1] == 'X', "Big board should show X won board 1."
        assert len(Player.legal_moves[1]) == 0, "Board 1 should have no legal moves."

        current_legal = player.get_current_legal_moves(None)
        boards_in_legal = set(move[0] for move in current_legal)
        assert 1 not in boards_in_legal, "Completed board 1 should not be in legal moves."
        assert 5 not in boards_in_legal, "Completed board 5 should not be in legal moves."
        assert len(boards_in_legal) == 7, "Should have moves from 7 uncompleted boards."