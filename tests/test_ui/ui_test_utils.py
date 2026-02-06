import pytest
import time
import threading
from utils.game.game_ui_v2 import GameUI
from utils.game.game_ui_assets import *
from utils.players import UserPlayer, MiniMaxPlayer, Player
from utils.helpers import StateUpdater, StateChecker, GameEvaluator


class VisualTestReporter:
    """Helper class to provide visual feedback during test execution."""

    def __init__(self, wait_time: float = 0.1):
        self.step_count = 0
        self.start_time = time.time()
        self.wait_time = wait_time

    def log_step(self, description: str, action: str = "", node_id: int = None):
        self.step_count += 1
        elapsed = time.time() - self.start_time

        header = f"STEP {self.step_count}"
        if node_id is not None:
            header += f" | Node {node_id}"
        header += f" | Time: {elapsed:.2f}s"

        print("\n" + "=" * 80)
        print(header)
        print(f"Description: {description}")
        if action:
            print(f"Action: {action}")
        print("=" * 80 + "\n")

    def log_assertion(self, condition: bool, message: str):
        status = "PASS" if condition else "FAIL"
        print(f"  [{status}] {message}")
        assert condition, f"Assertion failed: {message}"

    def wait(self, specific_time: float = None):
        time.sleep(self.wait_time if specific_time is None else specific_time)


class GameThread:
    """
    Wraps a GameUI.play() call in a daemon thread with clean lifecycle management.

    Each test gets its own GameThread with completely isolated GameUI and Player
    instances. The thread is a daemon so it won't prevent test process exit, and
    it can be explicitly stopped via a force_quit flag on the GameUI instance.
    """

    def __init__(self, game_ui: GameUI):
        self.game_ui = game_ui
        self.thread: threading.Thread | None = None
        self.exception: Exception | None = None
        self._started = threading.Event()
        self._stopped = threading.Event()

    def _run(self):
        """Thread target: signal readiness, then run the game loop."""
        try:
            self._started.set()
            self.game_ui.play()
        except Exception as e:
            if not getattr(self.game_ui, 'force_quit', False):
                self.exception = e
        finally:
            self._stopped.set()

    def start(self, timeout: float = 5.0):
        """
        Start the game loop thread and block until it signals readiness.

        Arguments:
            timeout: Maximum seconds to wait for the thread to start.

        Raises:
            RuntimeError: If the thread doesn't start within the timeout.
        """
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        if not self._started.wait(timeout):
            raise RuntimeError("Game thread failed to start within timeout")

    def stop(self, timeout: float = 3.0):
        """
        Signal the game loop to quit and wait for the thread to finish.
        """
        if self.thread is None or not self.thread.is_alive():
            return

        pygame.display.quit()
        self.thread.join(timeout)
        if self.thread.is_alive():
            print("[WARN] Game thread did not exit cleanly within timeout")

    @property
    def is_alive(self) -> bool:
        return self.thread is not None and self.thread.is_alive()

    @property
    def is_stopped(self) -> bool:
        return self._stopped.is_set()


def reset_player_class_state():
    """
    Forcefully reset ALL class-level shared state on Player.

    This is the nuclear option: we clear every class variable that could
    leak between tests. Call this before AND after each test.
    """
    Player.reset_legal_moves()

    for attr_name in list(vars(Player)):
        attr = getattr(Player, attr_name)
        if isinstance(attr, list):
            attr.clear()
        elif isinstance(attr, dict):
            attr.clear()
        elif isinstance(attr, set):
            attr.clear()


class BaseUITest:
    """Base class for UI tests with common fixtures and helper methods."""

    state_checker = StateChecker()

    @pytest.fixture(autouse=True)
    def manage_pygame_window(self):
        """
        Manage pygame window lifecycle.

        Resets all shared state before the test, yields control, then
        aggressively tears down pygame so the next test starts clean.
        """
        reset_player_class_state()

        yield

        reset_player_class_state()

        if pygame.display.get_surface() is not None:
            self.cleanup_pygame_state()
            time.sleep(0.4)

    @pytest.fixture
    def game_ui(self):
        """
        Fixture to create a fully isolated GameUI instance.

        Each call produces brand-new Player instances and a fresh GameUI
        with its own state. The `reset` flag is set so play() skips the
        main menu and jumps straight to the game board.
        """
        pygame.init()
        pygame.event.clear()
        pygame.event.set_allowed(True)

        reset_player_class_state()

        player1 = UserPlayer()
        player2 = UserPlayer()
        Player.reset_legal_moves()

        GameEvaluator(algorithm = MiniMaxPlayer(target_depth="dynamic", use_randomness=True))

        game = GameUI(
            player1=player1,
            player2=player2,
            printing=False,
            wait_after_move=100,
            show_evaluation=False,
            measure_thinking_time=False,
            opaque_on_board_completion=True,
            light_theme=False,
            use_eval_bar=False
        )

        game.reset_state()
        game.force_quit = False

        DISPLAY_SURF = pygame.display.get_surface()
        if DISPLAY_SURF is not None:
            DISPLAY_SURF.fill((0, 0, 0))
            pygame.display.flip()

        pygame.event.clear()
        pygame.event.pump()

        return game

    @pytest.fixture
    def game_thread(self, game_ui):
        """
        Fixture that provides a GameThread wrapping the game_ui.

        Automatically stops the thread during teardown so every test
        gets a clean exit regardless of pass/fail.
        """
        gt = GameThread(game_ui)

        yield gt

        gt.stop(timeout=3.0)

    def cleanup_pygame_state(self):
        """Aggressively clean up pygame state between operations."""
        for _ in range(3):
            pygame.event.clear()
            pygame.event.pump()
        time.sleep(0.05)

    def get_board_position_coords(self, big_idx: int, small_idx: int) -> tuple[int, int]:
        """Get pixel coordinates for a board position."""
        box_x, box_y = idx_to_rc[big_idx][small_idx]
        left = box_y * SQUARE_SIZE + X_MARGIN
        top = box_x * SQUARE_SIZE + Y_MARGIN
        return (left + SQUARE_SIZE // 2, top + SQUARE_SIZE // 2)

    def get_button_coords(self) -> dict[str, tuple[int, int]]:
        """Get all button coordinates as a dictionary."""
        coords = {}

        coords['one_player'] = (235, 530)
        coords['two_player'] = (655, 530)

        coords['choose_x'] = (340, 270)
        coords['choose_o'] = (550, 270)
        coords['choose_easy'] = (200, 533)
        coords['choose_normal'] = (452, 533)
        coords['choose_hard'] = (695, 533)

        t = Y_MARGIN + 2 * SQUARE_SIZE
        l = WINDOW_WIDTH - X_MARGIN + 1 * SQUARE_SIZE
        coords['hint'] = (l + 30, t + 27)
        coords['bar'] = (l + 30, t + SQUARE_SIZE + 27)
        coords['reset'] = (l + 30, t + 3 * SQUARE_SIZE + 27)
        coords['to_title'] = (l + 30, t + 4 * SQUARE_SIZE + 27)
        coords['back'] = (30, 30)

        return coords

    def post_click_event(self, x: int, y: int, reporter: VisualTestReporter,
                         highlight_color: tuple = (0, 255, 0)):
        """
        Post a real MOUSEBUTTONUP event into the pygame event queue.

        This is the key difference from the old approach: we inject events
        that the actual play() game loop will pick up and process, so we're
        testing the real click handling code path.

        Arguments:
            x: Pixel x-coordinate of the click
            y: Pixel y-coordinate of the click
            reporter: Visual test reporter for timing/logging
            highlight_color: Color of the visual click indicator
        """
        DISPLAY_SURF = pygame.display.get_surface()
        if DISPLAY_SURF is not None:
            radius = 10
            area_rect = pygame.Rect(
                x - radius - 3, y - radius - 3,
                (radius + 3) * 2, (radius + 3) * 2
            )

            try:
                saved_area = DISPLAY_SURF.subsurface(area_rect).copy()
                pygame.draw.circle(DISPLAY_SURF, highlight_color, (x, y), radius, 3)
                pygame.display.update(area_rect)
                reporter.wait(0.1)
                DISPLAY_SURF.blit(saved_area, area_rect)
                pygame.display.update(area_rect)
            except (ValueError, pygame.error):
                pass

        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONUP,
            {'pos': (x, y), 'button': 1}
        )
        pygame.event.pump()
        pygame.event.post(click_event)
        reporter.wait(0.05)

    def post_move_click(self, big_idx: int, small_idx: int,
                        reporter: VisualTestReporter):
        """
        Post a click event at the board position corresponding to (big_idx, small_idx).

        The actual play() loop handles the move logic — we're just providing input.

        Arguments:
            big_idx: Big board index (1-9)
            small_idx: Small board index (1-9)
            reporter: Visual test reporter
        """
        x, y = self.get_board_position_coords(big_idx, small_idx)
        reporter.log_step(
            f"Click at board {big_idx}, cell {small_idx}",
            action=f"post MOUSEBUTTONUP at ({x}, {y})"
        )
        self.post_click_event(x, y, reporter)

    def wait_for_state_condition(self, game_ui: GameUI, condition_fn,
                                 description: str, timeout: float = 10.0,
                                 poll_interval: float = 0.1) -> bool:
        """
        Poll until a condition on the game state becomes true.

        This is how the test thread synchronizes with the game thread:
        after posting a click, we poll the shared game_ui.state until
        the expected change appears (or we time out).

        Arguments:
            game_ui: The game UI instance whose state we're watching
            condition_fn: Callable that takes game_ui and returns bool
            description: Human-readable description for logging
            timeout: Maximum seconds to wait
            poll_interval: Seconds between polls

        Returns:
            True if the condition was met, False on timeout.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                if condition_fn(game_ui):
                    return True
            except (IndexError, KeyError, TypeError):
                pass
            time.sleep(poll_interval)
        print(f"[TIMEOUT] Condition not met: {description}")
        return False

    def wait_for_move_applied(self, game_ui: GameUI, big_idx: int,
                              small_idx: int, sign: str,
                              timeout: float = 5.0) -> bool:
        """
        Wait until a specific move appears in the game state.

        Arguments:
            game_ui: The game UI instance
            big_idx: Big board index
            small_idx: Small board index
            sign: Expected sign ('X' or 'O')
            timeout: Maximum wait time

        Returns:
            True if the move appeared in state, False on timeout.
        """

        def check(gui):
            return gui.state[big_idx]['display'][small_idx] == sign

        return self.wait_for_state_condition(
            game_ui, check,
            f"Move {sign} at ({big_idx},{small_idx})",
            timeout=timeout
        )

    def wait_for_board_won(self, game_ui: GameUI, big_idx: int, sign: str,
                           timeout: float = 5.0) -> bool:
        """
        Wait until a big board cell shows a specific sign (board won).

        Arguments:
            game_ui: The game UI instance
            big_idx: Big board index
            sign: Expected sign ('X' or 'O')
            timeout: Maximum wait time

        Returns:
            True if the board was won, False on timeout.
        """

        def check(gui):
            return gui.state[0]['display'][big_idx] == sign

        return self.wait_for_state_condition(
            game_ui, check,
            f"Board {big_idx} won by {sign}",
            timeout=timeout
        )

    def play_moves_via_events(self, game_ui: GameUI, game_thread: GameThread,
                              moves: list[tuple[int, int, str]],
                              reporter: VisualTestReporter,
                              move_wait: float = 0.1):
        """
        Play a sequence of moves by posting real click events into the game loop.

        For each move, we:
          1. Post a MOUSEBUTTONUP at the right coordinates
          2. Poll the game state until the move is reflected
          3. Move on to the next move

        This tests the actual play() input handling and game logic.

        Arguments:
            game_ui: The game UI instance
            game_thread: The running game thread
            moves: List of (big_idx, small_idx, sign) tuples
            reporter: Visual test reporter
            move_wait: Seconds to wait after each confirmed move
        """
        for i, (big_idx, small_idx, sign) in enumerate(moves):
            if not game_thread.is_alive:
                reporter.log_step(
                    f"Game thread died before move {i + 1}",
                    action="ABORT"
                )
                break

            self.post_move_click(big_idx, small_idx, reporter)

            confirmed = self.wait_for_move_applied(
                game_ui, big_idx, small_idx, sign, timeout=5.0
            )
            reporter.log_assertion(
                confirmed,
                f"Move {i + 1}/{len(moves)}: {sign} at ({big_idx},{small_idx}) applied"
            )

            reporter.wait(move_wait)