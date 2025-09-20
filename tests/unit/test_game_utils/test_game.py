import pytest
from unittest.mock import Mock, patch
from utils.game.game import Game

# what the fuckkkk

class TestGame:
    """
    Class for testing functionality of main components of the Game class.

    Methods covered:
    - reset_state()
    - make_move(sign, player)
    - play()
    """

    @pytest.fixture
    def mock_players(self):
        """ Fixture to create mock players. """
        player1 = Mock()
        player2 = Mock()
        return player1, player2


    @pytest.fixture
    def initial_state(self):
        """ Fixture for initial game state. """
        return tuple(
            {'X': (), 'O': (), 'display': ('/', '-', '-', '-', '-', '-', '-', '-', '-', '-')}
            for _ in range(10)
        )


    @pytest.mark.parametrize("prev_small_idx, prev_move_made, expected_prev_small_idx, expected_prev_move_made", [
        (None, None, None, None),
        (5, (5, 2), None, None),
        (3, (3, 9), None, None),
        (9, (8, 7), None, None),
    ])
    def test_reset_state(self, prev_small_idx, prev_move_made,
                         expected_prev_small_idx, expected_prev_move_made, mock_players):
        """ Test that reset_state properly resets the game state with various initial conditions. """

        player1, player2 = mock_players
        game = Game(player1=player1, player2=player2)

        game.prev_small_idx = prev_small_idx
        game.prev_move_made = prev_move_made

        game.reset_state()

        assert game.prev_small_idx == expected_prev_small_idx

        assert len(game.state) == 10

        for board in game.state:
            assert 'X' in board
            assert 'O' in board
            assert 'display' in board
            assert board['X'] == ()
            assert board['O'] == ()
            assert len(board['display']) == 10
            assert board['display'][0] == '/'
            assert all(cell == '-' for cell in board['display'][1:])

        assert game.prev_move_made == expected_prev_move_made


    @pytest.mark.parametrize("move, player, sign", [
        ((1, 1), 1, "X"),
        ((1, 1), 2, "O"),
        ((3, 5), 1, "O"),
    ])
    @patch('utils.helpers.StateUpdater.update_state')
    def test_make_move(self, mock_update_state, mock_players, initial_state, move, player, sign):
        """ Test whether make_move calls appropriate classes for both players. """

        mock_update_state.return_value = (initial_state, False)
        player1, player2 = mock_players
        player1.make_move = Mock(return_value=move)
        player1.update_legal_moves = Mock()
        player2.make_move = Mock(return_value=move)
        player2.update_legal_moves = Mock()

        current_player = player1 if player==1 else player2

        game = Game(player1=player1, player2=player2, printing=False, measure_thinking_time=False)
        game_state = game.state

        game.make_move(sign, current_player)

        current_player.make_move.assert_called_once_with(game_state, None)

        mock_update_state.assert_called_once()

        current_player.update_legal_moves.assert_called_once()


    @pytest.mark.parametrize("play_sequence", [
        ('X'),
        ('O'),
        (False, 'O'),
        (False, False, False, False, 'X'),
        (False, False, False, False, False, 'X'),
        (False, False, False, False, False, False, 'T'),
    ])
    @patch('builtins.input', lambda *args: None)
    @patch('utils.helpers.StateChecker.check_win')
    def test_play(self, mock_check_win, mock_players, play_sequence):
        """ Test whether game ends after various move sequences. """

        mock_check_win.side_effect = play_sequence
        player1, player2 = mock_players
        player1.make_move = Mock(return_value=(1,2))
        player2.make_move = Mock(return_value=(7,4))

        game = Game(player1=player1, player2=player2, printing=False)
        game.play()

        expected_num_calls = len(play_sequence)
        actual_num_calls = mock_check_win.call_count

        assert actual_num_calls == expected_num_calls
