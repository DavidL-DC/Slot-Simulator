import random
import pygame

from game import (
    GameState,
    add_free_spins,
    apply_bet,
    apply_win,
    can_spin,
    consume_free_spin,
    is_free_spin,
)
from slot_machine import (
    evaluate_total_win,
    spin_reels,
    trigger_debug_yin_yang_feature,
    spin_reels_free_spins,
    count_bulls,
)
from symbols import ALL_SYMBOLS, Symbol

from bull_feature import play_bull_feature
from config import PAYLINES


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

GRID_COLS = 5
GRID_ROWS = 3

CELL_WIDTH = 120
CELL_HEIGHT = 120
CELL_GAP = 10

GRID_X = 170
GRID_Y = 160

BACKGROUND_COLOR = (20, 20, 30)
PANEL_COLOR = (35, 35, 50)
CELL_COLOR = (220, 220, 230)
TEXT_COLOR = (245, 245, 245)
ACCENT_COLOR = (212, 175, 55)
BUTTON_COLOR = (180, 50, 50)
BUTTON_HOVER_COLOR = (210, 70, 70)
BUTTON_DISABLED_COLOR = (90, 90, 90)
SMALL_BUTTON_COLOR = (70, 120, 200)
SMALL_BUTTON_HOVER_COLOR = (90, 140, 220)
WIN_COLOR = (80, 180, 90)
FEATURE_COLOR = (160, 90, 180)


class SlotUI:
    def __init__(self, state: GameState) -> None:
        pygame.init()
        pygame.display.set_caption("Fortune Bull Prototype")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("arial", 36, bold=True)
        self.label_font = pygame.font.SysFont("arial", 24)
        self.symbol_font = pygame.font.SysFont("arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("arial", 20)
        self.button_font = pygame.font.SysFont("arial", 28, bold=True)

        self.state = state

        self.current_grid = self.create_random_grid()
        self.final_grid = self.current_grid

        self.last_total_win = 0
        self.last_line_win = 0
        self.last_scatter_win = 0
        self.last_yin_yang_win = 0
        self.last_scatter_count = 0
        self.last_yin_yang_count = 0
        self.last_awarded_free_spins = 0
        self.last_yin_yang_feature_result = None
        self.status_text = "Drücke LEERTASTE oder SPIN"
        self.overlay_text = ""
        self.overlay_subtext = ""
        self.overlay_color = ACCENT_COLOR
        self.overlay_end_time = 0

        self.running = True

        self.is_spinning = False
        self.reel_stop_times = [0, 0, 0, 0, 0]
        self.locked_reels = [False, False, False, False, False]

        self.pending_total_win = 0
        self.pending_line_win = 0
        self.pending_scatter_win = 0
        self.pending_yin_yang_win = 0
        self.pending_scatter_count = 0
        self.pending_yin_yang_count = 0
        self.pending_awarded_free_spins = 0
        self.pending_free_spin_mode = False
        self.pending_yin_yang_feature_result = None

        self.feature_mode = False
        self.feature_result = None
        self.feature_spin_index = -1
        self.feature_step_duration_ms = 900

        self.feature_display_grid = None
        self.feature_display_columns = None
        self.feature_display_spins_left = 0
        self.feature_display_new_positions = []

        self.feature_phase = "idle"

        self.feature_countup_value = 0
        self.feature_countup_target = 0
        self.feature_countup_start_time = 0
        self.feature_countup_duration_ms = 1200

        self.feature_waiting_for_input = False
        self.feature_finished_waiting = False
        self.feature_continue_button_rect = pygame.Rect(380, 610, 240, 52)

        self.feature_flash_until = 0

        self.feature_spinning_cells: list[tuple[int, int]] = []
        self.feature_current_completed_columns: list[int] = []
        self.feature_current_grand_column_index = None

        self.feature_grand_popup_text = ""
        self.feature_grand_popup_end_time = 0

        self.feature_spin_symbols = []

        self.feature_respin_animating = False
        self.feature_respin_animation_end_time = 0
        self.feature_pending_spin_result = None

        self.feature_background_grid = None

        self.bull_feature_mode = False
        self.bull_feature_result = None
        self.bull_feature_phase = "idle"

        self.bull_feature_display_multiplier_grid = None
        self.bull_feature_display_symbol_grid = None
        self.bull_feature_drop_index = -1
        self.bull_feature_drop_step_duration_ms = 350
        self.bull_feature_next_drop_time = 0

        self.bull_feature_fill_animating = False
        self.bull_feature_fill_animation_end_time = 0
        self.bull_feature_spinning_cells: list[tuple[int, int]] = []
        self.bull_feature_background_grid = None

        self.bull_feature_countup_value = 0
        self.bull_feature_countup_target = 0
        self.bull_feature_countup_start_time = 0
        self.bull_feature_countup_duration_ms = 1200

        self.bull_feature_waiting_for_input = False
        self.bull_feature_finished_waiting = False

        self.bull_feature_flash_cells: list[tuple[int, int]] = []
        self.bull_feature_flash_until = 0

        self.bull_feature_continue_button_rect = pygame.Rect(380, 610, 240, 52)
        self.bull_feature_win_applied = False

        self.spin_button_rect = pygame.Rect(830, 470, 140, 60)
        self.bet_minus_rect = pygame.Rect(20, 470, 60, 50)
        self.bet_plus_rect = pygame.Rect(90, 470, 60, 50)

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update_animation()
            self.update_feature_playback()
            self.update_feature_respin_animation()
            self.update_bull_feature_playback()
            self.update_bull_feature_fill_animation()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.handle_skip_or_continue()
                elif event.key == pygame.K_UP:
                    self.change_bet(10)
                elif event.key == pygame.K_DOWN:
                    self.change_bet(-10)
                elif event.key == pygame.K_f:
                    self.debug_trigger_free_spins()
                elif event.key == pygame.K_y:
                    self.debug_trigger_yin_yang()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if (
                    self.feature_mode
                    and self.feature_continue_button_rect.collidepoint(mouse_pos)
                ):
                    if self.feature_phase == "spins" and self.feature_waiting_for_input:
                        self.advance_feature_playback()
                    elif self.feature_phase == "done" and self.feature_finished_waiting:
                        self.advance_feature_playback()
                    return
                elif (
                    self.bull_feature_mode
                    and self.bull_feature_continue_button_rect.collidepoint(mouse_pos)
                ):
                    if (
                        self.bull_feature_phase == "done"
                        and self.bull_feature_finished_waiting
                    ):
                        self.close_bull_feature()
                    return
                elif self.spin_button_rect.collidepoint(mouse_pos):
                    self.handle_skip_or_continue()
                elif self.bet_minus_rect.collidepoint(mouse_pos):
                    self.change_bet(-10)
                elif self.bet_plus_rect.collidepoint(mouse_pos):
                    self.change_bet(10)

    def has_skippable_animation(self) -> bool:
        if self.is_spinning:
            return True

        if self.feature_mode:
            if self.feature_respin_animating:
                return True
            if self.feature_phase == "countup":
                return True

        if self.bull_feature_mode:
            if self.bull_feature_phase == "drops":
                return True
            if self.bull_feature_fill_animating:
                return True
            if self.bull_feature_phase == "countup":
                return True

        return False

    def handle_skip_or_continue(self) -> None:
        if self.has_skippable_animation():
            self.skip_current_animation()
            return

        if self.feature_mode:
            if self.feature_phase == "spins" and self.feature_waiting_for_input:
                self.advance_feature_playback()
                return

            if self.feature_phase == "done" and self.feature_finished_waiting:
                self.advance_feature_playback()
                return

            return

        if self.bull_feature_mode:
            if self.bull_feature_phase == "done" and self.bull_feature_finished_waiting:
                self.close_bull_feature()
            return

        self.try_spin()

    def skip_current_animation(self) -> None:
        self.status_text = "Animation übersprungen"
        if self.is_spinning:
            self.skip_base_spin_animation()
            return

        if self.feature_mode:
            if self.feature_respin_animating:
                self.skip_yin_yang_respin_animation()
                return

            if self.feature_phase == "countup":
                self.skip_yin_yang_countup()
                return

        if self.bull_feature_mode:
            if self.bull_feature_phase == "drops":
                self.skip_bull_drops()
                return

            if self.bull_feature_fill_animating:
                self.skip_bull_fill_animation()
                return

            if self.bull_feature_phase == "countup":
                self.skip_bull_countup()
                return

    def skip_base_spin_animation(self) -> None:
        if not self.is_spinning:
            return

        self.current_grid = [row.copy() for row in self.final_grid]
        self.locked_reels = [True, True, True, True, True]
        self.finish_spin()

    def skip_yin_yang_respin_animation(self) -> None:
        if not self.feature_mode or not self.feature_respin_animating:
            return

        if self.feature_pending_spin_result is None:
            self.feature_respin_animating = False
            self.feature_waiting_for_input = True
            return

        current_spin = self.feature_pending_spin_result

        self.feature_display_grid = [row.copy() for row in current_spin.grid_values]
        self.feature_display_columns = current_spin.column_values.copy()
        self.feature_display_spins_left = current_spin.spins_left_after
        self.feature_display_new_positions = current_spin.new_positions.copy()

        if self.feature_background_grid is None:
            self.feature_background_grid = self.create_feature_background_grid()

        for row_index in range(3):
            for col_index in range(5):
                if self.feature_display_grid[row_index][col_index] is None:
                    self.feature_background_grid[row_index][
                        col_index
                    ] = self.get_feature_spin_symbol()

        self.feature_current_completed_columns = current_spin.completed_columns.copy()
        self.feature_current_grand_column_index = current_spin.grand_column_index

        if current_spin.grand_activated:
            self.feature_grand_popup_text = "GRAND JACKPOT ACTIVATED!"
            self.feature_grand_popup_end_time = pygame.time.get_ticks() + 1800

        self.feature_flash_until = pygame.time.get_ticks() + 500
        self.feature_respin_animating = False
        self.feature_respin_animation_end_time = 0
        self.feature_waiting_for_input = True
        self.feature_pending_spin_result = None
        self.update_feature_spinning_cells()

    def skip_yin_yang_countup(self) -> None:
        if not self.feature_mode or self.feature_result is None:
            return

        self.feature_countup_value = self.feature_countup_target
        self.feature_phase = "done"
        self.feature_finished_waiting = True
        self.feature_waiting_for_input = False

        self.feature_current_completed_columns = (
            self.feature_result.completed_columns.copy()
        )
        self.feature_current_grand_column_index = self.feature_result.grand_column_index

    def skip_bull_drops(self) -> None:
        if (
            not self.bull_feature_mode
            or self.bull_feature_result is None
            or self.bull_feature_display_multiplier_grid is None
        ):
            return

        self.bull_feature_display_multiplier_grid = [
            row.copy() for row in self.bull_feature_result.multiplier_grid
        ]

        self.bull_feature_drop_index = len(self.bull_feature_result.drops) - 1
        self.bull_feature_flash_cells = []
        self.bull_feature_flash_until = 0

        self.bull_feature_phase = "fill"
        self.bull_feature_fill_animating = True
        self.bull_feature_fill_animation_end_time = pygame.time.get_ticks()
        self.update_bull_feature_fill_animation()

    def skip_bull_fill_animation(self) -> None:
        if not self.bull_feature_mode or self.bull_feature_result is None:
            return

        self.bull_feature_fill_animating = False
        self.bull_feature_fill_animation_end_time = 0
        self.bull_feature_display_symbol_grid = [
            row.copy() for row in self.bull_feature_result.final_symbol_grid
        ]
        self.bull_feature_spinning_cells = []
        self.bull_feature_phase = "countup"
        self.bull_feature_countup_start_time = pygame.time.get_ticks()

    def skip_bull_countup(self) -> None:
        if not self.bull_feature_mode or self.bull_feature_result is None:
            return

        self.bull_feature_countup_value = self.bull_feature_countup_target
        self.bull_feature_phase = "done"
        self.bull_feature_finished_waiting = True
        self.bull_feature_waiting_for_input = True

        if not self.bull_feature_win_applied:
            apply_win(self.state, self.bull_feature_result.total_win)
            self.last_total_win += self.bull_feature_result.total_win
            self.bull_feature_win_applied = True

    def get_feature_spin_symbol(self) -> Symbol:
        weighted_symbols = [
            symbol
            for symbol in ALL_SYMBOLS
            if symbol.name
            in {
                "yin_yang",
                "nine",
                "ten",
                "jack",
                "queen",
                "king",
                "gong",
                "house",
                "lantern",
                "vase",
            }
        ]

        extra_yin = [symbol for symbol in ALL_SYMBOLS if symbol.name == "yin_yang"] * 4
        pool = weighted_symbols + extra_yin

        return random.choice(pool)

    def create_feature_background_grid(self) -> list[list[Symbol]]:
        weighted_symbols = [
            symbol
            for symbol in ALL_SYMBOLS
            if symbol.name
            in {
                "yin_yang",
                "nine",
                "ten",
                "jack",
                "queen",
                "king",
                "gong",
                "house",
                "lantern",
                "vase",
            }
        ]

        extra_yin = [symbol for symbol in ALL_SYMBOLS if symbol.name == "yin_yang"] * 4
        pool = weighted_symbols + extra_yin

        return [[random.choice(pool) for _ in range(5)] for _ in range(3)]

    def update_animation(self) -> None:
        if not self.is_spinning:
            return

        current_time = pygame.time.get_ticks()

        for reel_index in range(GRID_COLS):
            if self.locked_reels[reel_index]:
                continue

            if current_time >= self.reel_stop_times[reel_index]:
                self.locked_reels[reel_index] = True

                for row_index in range(GRID_ROWS):
                    self.current_grid[row_index][reel_index] = self.final_grid[
                        row_index
                    ][reel_index]
            else:
                for row_index in range(GRID_ROWS):
                    self.current_grid[row_index][reel_index] = random.choice(
                        ALL_SYMBOLS
                    )

        if all(self.locked_reels):
            self.finish_spin()

    def create_random_grid(self) -> list[list[Symbol]]:
        return [
            [random.choice(ALL_SYMBOLS) for _ in range(GRID_COLS)]
            for _ in range(GRID_ROWS)
        ]

    def show_overlay(
        self,
        text: str,
        color: tuple[int, int, int],
        duration_ms: int = 1800,
        subtext: str = "",
    ) -> None:
        self.overlay_text = text
        self.overlay_color = color
        self.overlay_end_time = pygame.time.get_ticks() + duration_ms
        self.overlay_subtext = subtext

    def start_yin_yang_feature_playback(self, feature_result) -> None:
        self.feature_mode = True
        self.feature_result = feature_result
        self.feature_spin_index = -1

        self.feature_display_grid = [
            row.copy() for row in feature_result.start_grid_values
        ]
        self.feature_background_grid = self.create_feature_background_grid()
        self.feature_display_columns = feature_result.start_column_values.copy()
        self.feature_display_spins_left = 3
        self.feature_display_new_positions = []

        self.feature_phase = "spins"

        self.feature_countup_value = 0
        self.feature_countup_target = feature_result.total_win
        self.feature_countup_start_time = 0

        self.feature_waiting_for_input = True
        self.feature_finished_waiting = False
        self.feature_flash_until = 0

        self.feature_current_completed_columns = []
        self.feature_current_grand_column_index = None

        self.feature_spinning_cells = []
        self.update_feature_spinning_cells()

        self.feature_grand_popup_text = ""
        self.feature_grand_popup_end_time = 0

        self.feature_respin_animating = False
        self.feature_respin_animation_end_time = 0
        self.feature_pending_spin_result = None

    def update_feature_playback(self) -> None:
        if not self.feature_mode or self.feature_result is None:
            return

        current_time = pygame.time.get_ticks()

        if self.feature_phase == "spins":
            return

        if self.feature_phase == "countup":
            elapsed = current_time - self.feature_countup_start_time
            progress = min(1.0, elapsed / self.feature_countup_duration_ms)

            self.feature_countup_value = int(self.feature_countup_target * progress)

            if progress >= 1.0:
                self.feature_phase = "done"
                self.feature_finished_waiting = True
                self.feature_waiting_for_input = False

                self.feature_current_completed_columns = (
                    self.feature_result.completed_columns.copy()
                )
                self.feature_current_grand_column_index = (
                    self.feature_result.grand_column_index
                )
            return

    def advance_feature_playback(self) -> None:
        if not self.feature_mode or self.feature_result is None:
            return

        if self.feature_phase == "spins":
            if self.feature_respin_animating:
                return

            next_index = self.feature_spin_index + 1

            if next_index >= len(self.feature_result.spins):
                self.feature_phase = "countup"
                self.feature_countup_start_time = pygame.time.get_ticks()
                self.feature_display_new_positions = []
                self.feature_spinning_cells = []
                self.feature_waiting_for_input = False
                return

            self.feature_spin_index = next_index
            self.feature_pending_spin_result = self.feature_result.spins[
                self.feature_spin_index
            ]

            self.feature_respin_animating = True
            self.feature_respin_animation_end_time = pygame.time.get_ticks() + 900
            self.feature_waiting_for_input = False

            if self.feature_display_grid is not None:
                self.update_feature_spinning_cells()

            return

        if self.feature_phase == "done":
            self.feature_mode = False
            self.feature_result = None
            self.feature_display_new_positions = []
            self.feature_spinning_cells = []
            self.feature_background_grid = None
            self.feature_phase = "idle"
            self.feature_finished_waiting = False
            self.feature_waiting_for_input = False
            self.feature_grand_popup_text = ""
            self.feature_grand_popup_end_time = 0
            self.feature_respin_animating = False
            self.feature_respin_animation_end_time = 0
            self.feature_pending_spin_result = None

    def update_feature_respin_animation(self) -> None:
        if not self.feature_mode or not self.feature_respin_animating:
            return

        current_time = pygame.time.get_ticks()

        if current_time < self.feature_respin_animation_end_time:
            self.update_feature_spinning_cells()
            return

        if self.feature_pending_spin_result is None:
            self.feature_respin_animating = False
            self.feature_waiting_for_input = True
            return

        current_spin = self.feature_pending_spin_result

        self.feature_display_grid = [row.copy() for row in current_spin.grid_values]
        self.feature_display_columns = current_spin.column_values.copy()
        self.feature_display_spins_left = current_spin.spins_left_after
        self.feature_display_new_positions = current_spin.new_positions.copy()

        if self.feature_background_grid is None:
            self.feature_background_grid = self.create_feature_background_grid()

        for row_index in range(3):
            for col_index in range(5):
                if self.feature_display_grid[row_index][col_index] is None:
                    self.feature_background_grid[row_index][
                        col_index
                    ] = self.get_feature_spin_symbol()

        self.feature_current_completed_columns = current_spin.completed_columns.copy()
        self.feature_current_grand_column_index = current_spin.grand_column_index

        if current_spin.grand_activated:
            self.feature_grand_popup_text = "GRAND JACKPOT ACTIVATED!"
            self.feature_grand_popup_end_time = pygame.time.get_ticks() + 1800

        self.feature_flash_until = pygame.time.get_ticks() + 500
        self.feature_respin_animating = False
        self.feature_waiting_for_input = True
        self.feature_pending_spin_result = None
        self.update_feature_spinning_cells()

    def update_feature_spinning_cells(self) -> None:
        if self.feature_display_grid is None or not self.feature_respin_animating:
            self.feature_spinning_cells = []
            self.feature_spin_symbols = []
            return

        if self.feature_background_grid is None:
            self.feature_background_grid = self.create_feature_background_grid()

        spinning_cells: list[tuple[int, int]] = []
        spin_symbols: list[tuple[tuple[int, int], Symbol]] = []

        for row_index in range(3):
            for col_index in range(5):
                if self.feature_display_grid[row_index][col_index] is None:
                    spinning_cells.append((row_index, col_index))
                    symbol = self.get_feature_spin_symbol()
                    spin_symbols.append(((row_index, col_index), symbol))
                    self.feature_background_grid[row_index][col_index] = symbol

        self.feature_spinning_cells = spinning_cells
        self.feature_spin_symbols = spin_symbols

    def update_bull_feature_spinning_cells(self) -> None:
        if (
            not self.bull_feature_mode
            or self.bull_feature_display_multiplier_grid is None
            or not self.bull_feature_fill_animating
        ):
            self.bull_feature_spinning_cells = []
            return

        if self.bull_feature_background_grid is None:
            self.bull_feature_background_grid = self.create_feature_background_grid()

        spinning_cells: list[tuple[int, int]] = []

        for row_index in range(3):
            for col_index in range(5):
                if self.bull_feature_display_multiplier_grid[row_index][col_index] == 0:
                    spinning_cells.append((row_index, col_index))
                    self.bull_feature_background_grid[row_index][
                        col_index
                    ] = self.get_feature_spin_symbol()

        self.bull_feature_spinning_cells = spinning_cells

    def update_bull_feature_fill_animation(self) -> None:
        if (
            not self.bull_feature_mode
            or not self.bull_feature_fill_animating
            or self.bull_feature_result is None
        ):
            return

        current_time = pygame.time.get_ticks()

        if current_time < self.bull_feature_fill_animation_end_time:
            self.update_bull_feature_spinning_cells()
            return

        self.bull_feature_fill_animating = False
        self.bull_feature_display_symbol_grid = [
            row.copy() for row in self.bull_feature_result.final_symbol_grid
        ]
        self.bull_feature_spinning_cells = []
        self.bull_feature_phase = "countup"
        self.bull_feature_countup_start_time = pygame.time.get_ticks()

    def update_bull_feature_playback(self) -> None:
        if (
            not self.bull_feature_mode
            or self.bull_feature_result is None
            or self.bull_feature_display_multiplier_grid is None
        ):
            return

        current_time = pygame.time.get_ticks()

        if self.bull_feature_phase == "drops":
            if current_time < self.bull_feature_next_drop_time:
                return

            next_index = self.bull_feature_drop_index + 1

            if next_index >= len(self.bull_feature_result.drops):
                self.bull_feature_phase = "fill"
                self.bull_feature_fill_animating = True
                self.bull_feature_fill_animation_end_time = current_time + 1100
                self.update_bull_feature_spinning_cells()
                return

            self.bull_feature_drop_index = next_index
            current_drop = self.bull_feature_result.drops[self.bull_feature_drop_index]

            row_index, col_index = current_drop.landing_position
            self.bull_feature_display_multiplier_grid[row_index][
                col_index
            ] = current_drop.multiplier_after

            self.bull_feature_flash_cells = [(row_index, col_index)]
            self.bull_feature_flash_until = current_time + 260
            self.bull_feature_next_drop_time = (
                current_time + self.bull_feature_drop_step_duration_ms
            )
            return

        if self.bull_feature_phase == "countup":
            elapsed = current_time - self.bull_feature_countup_start_time
            progress = min(1.0, elapsed / self.bull_feature_countup_duration_ms)

            self.bull_feature_countup_value = int(
                self.bull_feature_countup_target * progress
            )

            if progress >= 1.0:
                self.bull_feature_phase = "done"
                self.bull_feature_finished_waiting = True
                self.bull_feature_waiting_for_input = True

                if not self.bull_feature_win_applied:
                    apply_win(self.state, self.bull_feature_result.total_win)
                    self.last_total_win = self.bull_feature_result.total_win
                    self.bull_feature_win_applied = True
            return

    def change_bet(self, delta: int) -> None:
        if self.is_spinning:
            return

        new_bet = self.state.current_bet + delta

        if new_bet <= 0:
            self.status_text = "Einsatz muss größer als 0 sein."
            return

        if is_free_spin(self.state):
            self.status_text = (
                "Während Freispielen kann der Einsatz nicht geändert werden."
            )
            return

        if new_bet > self.state.balance:
            self.status_text = "Nicht genug Guthaben für diesen Einsatz."
            return

        self.state.current_bet = new_bet
        self.status_text = f"Einsatz geändert auf {self.state.current_bet}"

    def try_spin(self) -> None:
        if self.is_spinning:
            return

        if not can_spin(self.state):
            self.status_text = "Nicht genug Guthaben für einen Spin."
            return

        free_spin_mode = is_free_spin(self.state)
        self.pending_free_spin_mode = free_spin_mode

        if free_spin_mode:
            consume_free_spin(self.state)
            self.status_text = "Freispiel läuft..."
            self.final_grid = spin_reels_free_spins()
            self.state.collected_bulls += count_bulls(self.final_grid)
        else:
            apply_bet(self.state)
            self.status_text = "Walzen drehen..."
            self.final_grid = spin_reels()

        win_result = evaluate_total_win(self.final_grid, self.state.current_bet)

        total_win = win_result["total_win"]
        line_win = win_result["line_win"]
        scatter_win = win_result["scatter_win"]
        yin_yang_win = win_result["yin_yang_win"]
        yin_yang_feature_result = win_result["yin_yang_feature_result"]

        self.pending_total_win = total_win
        self.pending_line_win = line_win
        self.pending_scatter_win = scatter_win
        self.pending_yin_yang_win = yin_yang_win
        self.pending_scatter_count = win_result["scatter_count"]
        self.pending_yin_yang_count = win_result["yin_yang_count"]
        self.pending_awarded_free_spins = win_result["awarded_free_spins"]
        self.pending_yin_yang_feature_result = yin_yang_feature_result

        self.current_grid = self.create_random_grid()

        self.is_spinning = True
        self.locked_reels = [False, False, False, False, False]

        spin_start_time = pygame.time.get_ticks()
        base_delay = 700
        reel_delay = 250

        self.reel_stop_times = [
            spin_start_time + base_delay + reel_index * reel_delay
            for reel_index in range(GRID_COLS)
        ]

    def start_bull_feature(self) -> None:
        collected_bulls = self.state.collected_bulls

        if collected_bulls <= 0:
            return

        bull_feature_result = play_bull_feature(
            collected_bulls=collected_bulls,
            bet=self.state.current_bet,
            paylines=PAYLINES,
        )

        self.bull_feature_mode = True
        self.bull_feature_result = bull_feature_result
        self.bull_feature_phase = "drops"

        self.bull_feature_display_multiplier_grid = [
            [0 for _ in range(5)] for _ in range(3)
        ]
        self.bull_feature_display_symbol_grid = None

        self.bull_feature_drop_index = -1
        self.bull_feature_next_drop_time = pygame.time.get_ticks() + 250

        self.bull_feature_fill_animating = False
        self.bull_feature_fill_animation_end_time = 0
        self.bull_feature_spinning_cells = []
        self.bull_feature_background_grid = self.create_feature_background_grid()

        self.bull_feature_countup_value = 0
        self.bull_feature_countup_target = bull_feature_result.total_win
        self.bull_feature_countup_start_time = 0

        self.bull_feature_waiting_for_input = False
        self.bull_feature_finished_waiting = False

        self.bull_feature_flash_cells = []
        self.bull_feature_flash_until = 0
        self.bull_feature_win_applied = False

        self.show_overlay(
            "BULL FEATURE!",
            (255, 200, 120),
            2200,
            subtext=f"Collected Bulls: {collected_bulls}",
        )

        self.state.collected_bulls = 0

    def close_bull_feature(self) -> None:
        self.bull_feature_mode = False
        self.bull_feature_result = None
        self.bull_feature_phase = "idle"

        self.bull_feature_display_multiplier_grid = None
        self.bull_feature_display_symbol_grid = None
        self.bull_feature_drop_index = -1
        self.bull_feature_next_drop_time = 0

        self.bull_feature_fill_animating = False
        self.bull_feature_fill_animation_end_time = 0
        self.bull_feature_spinning_cells = []
        self.bull_feature_background_grid = None

        self.bull_feature_countup_value = 0
        self.bull_feature_countup_target = 0
        self.bull_feature_countup_start_time = 0

        self.bull_feature_waiting_for_input = False
        self.bull_feature_finished_waiting = False
        self.bull_feature_flash_cells = []
        self.bull_feature_flash_until = 0
        self.bull_feature_win_applied = False

    def debug_trigger_free_spins(self) -> None:
        if self.is_spinning:
            return

        awarded = 8
        add_free_spins(self.state, awarded)

        self.last_awarded_free_spins = awarded
        self.last_scatter_count = 3
        self.last_scatter_win = 0
        self.last_total_win = 0
        self.status_text = "DEBUG: Freispiele erzwungen"
        self.show_overlay(f"{awarded} FREE SPINS WON!", (255, 215, 80), 2200)

    def debug_trigger_yin_yang(self) -> None:
        if self.is_spinning:
            return

        result = trigger_debug_yin_yang_feature(self.state.current_bet)

        apply_win(self.state, result["total_win"])

        self.last_yin_yang_count = result["yin_yang_count"]
        self.last_yin_yang_win = result["yin_yang_win"]
        self.last_yin_yang_feature_result = result["yin_yang_feature_result"]
        self.last_total_win = result["total_win"]
        self.last_line_win = 0
        self.last_scatter_win = 0
        self.last_awarded_free_spins = 0
        self.status_text = f"DEBUG: Yin-Yang-Feature Gewinn {result['total_win']}"
        self.show_overlay(
            "YIN-YANG FEATURE!",
            (210, 160, 255),
            2200,
            subtext=f"Feature win: {result['total_win']}",
        )
        self.start_yin_yang_feature_playback(result["yin_yang_feature_result"])

    def finish_spin(self) -> None:
        self.is_spinning = False

        if self.pending_awarded_free_spins > 0:
            add_free_spins(self.state, self.pending_awarded_free_spins)

        apply_win(self.state, self.pending_total_win)

        self.last_total_win = self.pending_total_win
        self.last_line_win = self.pending_line_win
        self.last_scatter_win = self.pending_scatter_win
        self.last_yin_yang_win = self.pending_yin_yang_win
        self.last_yin_yang_feature_result = self.pending_yin_yang_feature_result
        self.last_scatter_count = self.pending_scatter_count
        self.last_yin_yang_count = self.pending_yin_yang_count
        self.last_awarded_free_spins = self.pending_awarded_free_spins

        if self.pending_awarded_free_spins > 0:
            self.show_overlay(
                f"{self.pending_awarded_free_spins} FREE SPINS WON!",
                (255, 215, 80),
                2200,
                subtext="Coin Feature triggered",
            )

        if (
            self.pending_yin_yang_count >= 3
            and self.pending_yin_yang_feature_result is not None
        ):
            self.show_overlay(
                "YIN-YANG FEATURE!",
                (210, 160, 255),
                1800,
                subtext=f"Feature win: {self.pending_yin_yang_win}",
            )
            self.start_yin_yang_feature_playback(self.pending_yin_yang_feature_result)
        elif self.pending_total_win > 0 and self.pending_awarded_free_spins == 0:
            self.show_overlay(
                f"WIN {self.pending_total_win}",
                (120, 220, 120),
                1400,
            )

        if self.pending_free_spin_mode:
            self.status_text = f"Freispiele beendet. Gewinn: {self.pending_total_win}"
        else:
            self.status_text = f"Spin beendet. Gewinn: {self.pending_total_win}"

        # Freispiele beendet → Bull Feature starten
        if (
            self.pending_free_spin_mode
            and self.state.free_spins_remaining == 0
            and self.state.collected_bulls > 0
        ):
            self.status_text = f"Freispiele beendet - Bull Feature startet"
            self.start_bull_feature()

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)

        self.draw_title()
        self.draw_top_panel()
        self.draw_grid()
        self.draw_controls()
        self.draw_bottom_panel()
        self.draw_overlay()
        self.draw_yin_yang_feature_board()
        self.draw_bull_feature_board()
        self.draw_help_text()

    def draw_title(self) -> None:
        title_surface = self.title_font.render(
            "Fortune Bull Prototype", True, ACCENT_COLOR
        )
        self.screen.blit(
            title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, 30)
        )

    def draw_top_panel(self) -> None:
        panel_rect = pygame.Rect(60, 80, 880, 60)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel_rect, border_radius=12)

        values = [
            f"Guthaben: {self.state.balance}",
            f"Einsatz: {self.state.current_bet}",
            f"Freispiele: {self.state.free_spins_remaining}",
            f"Bulls: {self.state.collected_bulls}",
            f"Letzter Gewinn: {self.last_total_win}",
        ]

        x = 80
        for text in values:
            surface = self.label_font.render(text, True, TEXT_COLOR)
            self.screen.blit(surface, (x, 97))
            x += 210

    def draw_grid(self) -> None:
        for row_index, row in enumerate(self.current_grid):
            for col_index, symbol in enumerate(row):
                x = GRID_X + col_index * (CELL_WIDTH + CELL_GAP)
                y = GRID_Y + row_index * (CELL_HEIGHT + CELL_GAP)

                cell_rect = pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)

                border_color = PANEL_COLOR
                inner_color = CELL_COLOR

                if symbol.is_scatter:
                    inner_color = (245, 225, 140)
                elif symbol.name == "yin_yang":
                    inner_color = (210, 180, 245)
                elif symbol.is_wild:
                    inner_color = (245, 170, 170)

                pygame.draw.rect(self.screen, inner_color, cell_rect, border_radius=12)
                pygame.draw.rect(
                    self.screen, border_color, cell_rect, width=3, border_radius=12
                )

                if self.is_spinning and not self.locked_reels[col_index]:
                    inner_rect = pygame.Rect(
                        x + 8, y + 8, CELL_WIDTH - 16, CELL_HEIGHT - 16
                    )
                    pygame.draw.rect(
                        self.screen, (180, 190, 210), inner_rect, border_radius=10
                    )

                symbol_surface = self.symbol_font.render(
                    symbol.display, True, (30, 30, 40)
                )
                self.screen.blit(
                    symbol_surface,
                    (
                        x + CELL_WIDTH // 2 - symbol_surface.get_width() // 2,
                        y + CELL_HEIGHT // 2 - symbol_surface.get_height() // 2,
                    ),
                )

    def draw_controls(self) -> None:
        self.draw_small_button(self.bet_minus_rect, "-", enabled=not self.is_spinning)
        self.draw_small_button(self.bet_plus_rect, "+", enabled=not self.is_spinning)
        self.draw_spin_button()

        bet_label = self.small_font.render("Einsatz", True, TEXT_COLOR)
        self.screen.blit(bet_label, (60, 440))

    def draw_small_button(self, rect: pygame.Rect, text: str, enabled: bool) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        if not enabled:
            color = BUTTON_DISABLED_COLOR
        elif hovered:
            color = SMALL_BUTTON_HOVER_COLOR
        else:
            color = SMALL_BUTTON_COLOR

        pygame.draw.rect(self.screen, color, rect, border_radius=10)

        text_surface = self.button_font.render(text, True, TEXT_COLOR)
        self.screen.blit(
            text_surface,
            (
                rect.x + rect.width // 2 - text_surface.get_width() // 2,
                rect.y + rect.height // 2 - text_surface.get_height() // 2,
            ),
        )

    def draw_spin_button(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.spin_button_rect.collidepoint(mouse_pos)
        enabled = not self.is_spinning and can_spin(self.state)

        if not enabled:
            color = BUTTON_DISABLED_COLOR
        elif hovered:
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        pygame.draw.rect(self.screen, color, self.spin_button_rect, border_radius=14)

        button_text = "SKIP" if self.has_skippable_animation() else "SPIN"
        text_surface = self.button_font.render(button_text, True, TEXT_COLOR)
        self.screen.blit(
            text_surface,
            (
                self.spin_button_rect.x
                + self.spin_button_rect.width // 2
                - text_surface.get_width() // 2,
                self.spin_button_rect.y
                + self.spin_button_rect.height // 2
                - text_surface.get_height() // 2,
            ),
        )

    def draw_bottom_panel(self) -> None:
        panel_rect = pygame.Rect(60, 560, 880, 100)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel_rect, border_radius=12)

        row_1 = (
            f"Linien: {self.last_line_win}   "
            f"Scatter: {self.last_scatter_win} (x{self.last_scatter_count})   "
            f"Yin-Yang: {self.last_yin_yang_win} (x{self.last_yin_yang_count})"
        )
        row_2 = (
            f"Neue Freispiele: {self.last_awarded_free_spins}   "
            f"Status: {self.status_text}"
        )

        row_1_surface = self.small_font.render(row_1, True, TEXT_COLOR)

        status_color = TEXT_COLOR
        if self.last_total_win > 0:
            status_color = WIN_COLOR
        if self.last_yin_yang_win > 0 or self.last_awarded_free_spins > 0:
            status_color = FEATURE_COLOR

        row_2_surface = self.small_font.render(row_2, True, status_color)

        self.screen.blit(row_1_surface, (80, 585))
        self.screen.blit(row_2_surface, (80, 620))

    def draw_overlay(self) -> None:
        current_time = pygame.time.get_ticks()

        if not self.overlay_text or current_time > self.overlay_end_time:
            return

        overlay_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 110))
        self.screen.blit(overlay_surface, (0, 0))

        box_rect = pygame.Rect(180, 260, 640, 140)
        pygame.draw.rect(self.screen, (25, 25, 35), box_rect, border_radius=18)
        pygame.draw.rect(
            self.screen, self.overlay_color, box_rect, width=4, border_radius=18
        )

        text_surface = self.title_font.render(
            self.overlay_text, True, self.overlay_color
        )
        self.screen.blit(
            text_surface,
            (
                box_rect.x + box_rect.width // 2 - text_surface.get_width() // 2,
                box_rect.y + 25,
            ),
        )

        if self.overlay_subtext:
            subtext_surface = self.label_font.render(
                self.overlay_subtext, True, TEXT_COLOR
            )
            self.screen.blit(
                subtext_surface,
                (
                    box_rect.x + box_rect.width // 2 - subtext_surface.get_width() // 2,
                    box_rect.y + 82,
                ),
            )

    def draw_yin_yang_feature_board(self) -> None:
        if (
            not self.feature_mode
            or self.feature_display_grid is None
            or self.feature_display_columns is None
        ):
            return

        overlay_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 180))
        self.screen.blit(overlay_surface, (0, 0))

        board_rect = pygame.Rect(120, 100, 760, 520)
        pygame.draw.rect(self.screen, (28, 24, 40), board_rect, border_radius=18)
        pygame.draw.rect(
            self.screen, (210, 160, 255), board_rect, width=4, border_radius=18
        )

        title_surface = self.title_font.render(
            "YIN-YANG FEATURE", True, (220, 180, 255)
        )
        self.screen.blit(
            title_surface,
            (board_rect.centerx - title_surface.get_width() // 2, 120),
        )

        phase_text = f"Respins left: {self.feature_display_spins_left}"
        if self.feature_phase == "countup":
            phase_text = "Counting feature win..."
        elif self.feature_phase == "done":
            phase_text = "Feature complete"

        info_surface = self.label_font.render(phase_text, True, TEXT_COLOR)
        self.screen.blit(
            info_surface,
            (board_rect.centerx - info_surface.get_width() // 2, 165),
        )

        feature_grid_x = 200
        feature_grid_y = 250
        feature_cell_w = 90
        feature_cell_h = 80
        feature_gap = 12

        pulse = (pygame.time.get_ticks() // 140) % 2 == 0

        for col_index, value in enumerate(self.feature_display_columns):
            x = feature_grid_x + col_index * (feature_cell_w + feature_gap)
            y = feature_grid_y - 50

            is_completed = col_index in self.feature_current_completed_columns
            is_grand = self.feature_current_grand_column_index == col_index

            if is_grand:
                if is_completed:
                    fill_color = (255, 225, 110)
                    border_color = (255, 255, 220)
                else:
                    fill_color = (170, 90, 40)
                    border_color = (255, 220, 140)
                label = "GRAND"
            elif is_completed:
                fill_color = (220, 180, 60)
                border_color = (255, 235, 170)
                label = str(value)
            else:
                fill_color = (85, 55, 110)
                border_color = (220, 180, 255)
                label = str(value)

            col_rect = pygame.Rect(x, y, feature_cell_w, 36)
            pygame.draw.rect(self.screen, fill_color, col_rect, border_radius=10)
            pygame.draw.rect(
                self.screen, border_color, col_rect, width=2, border_radius=10
            )

            value_surface = self.small_font.render(label, True, TEXT_COLOR)
            self.screen.blit(
                value_surface,
                (
                    x + feature_cell_w // 2 - value_surface.get_width() // 2,
                    y + col_rect.height // 2 - value_surface.get_height() // 2,
                ),
            )

        for row_index in range(3):
            for col_index in range(5):
                x = feature_grid_x + col_index * (feature_cell_w + feature_gap)
                y = feature_grid_y + row_index * (feature_cell_h + feature_gap)

                cell_rect = pygame.Rect(x, y, feature_cell_w, feature_cell_h)

                spinning = (row_index, col_index) in self.feature_spinning_cells
                value = self.feature_display_grid[row_index][col_index]
                is_new = (row_index, col_index) in self.feature_display_new_positions
                flashing = pygame.time.get_ticks() < self.feature_flash_until
                is_completed_column = (
                    col_index in self.feature_current_completed_columns
                )
                is_grand_column = self.feature_current_grand_column_index == col_index

                if value is None:
                    if spinning:
                        fill_color = (60, 60, 75)
                        border_color = (150, 150, 180)
                    else:
                        fill_color = (60, 60, 70)
                        border_color = (110, 110, 125)
                else:
                    if is_new and flashing and pulse:
                        fill_color = (255, 240, 140)
                    elif is_new and flashing:
                        fill_color = (250, 220, 130)
                    elif is_new:
                        fill_color = (235, 205, 150)
                    else:
                        fill_color = (205, 175, 240)

                    if is_grand_column:
                        border_color = (255, 240, 160)
                    elif is_completed_column:
                        border_color = (255, 220, 120)
                    else:
                        border_color = (235, 235, 250)

                pygame.draw.rect(self.screen, fill_color, cell_rect, border_radius=12)
                pygame.draw.rect(
                    self.screen, border_color, cell_rect, width=3, border_radius=12
                )

                if value is not None and is_completed_column:
                    highlight_color = (255, 225, 120)
                    if is_grand_column:
                        highlight_color = (255, 245, 180)

                    inner_highlight_rect = pygame.Rect(
                        x + 4, y + 4, feature_cell_w - 8, feature_cell_h - 8
                    )
                    pygame.draw.rect(
                        self.screen,
                        highlight_color,
                        inner_highlight_rect,
                        width=2,
                        border_radius=10,
                    )

                if value is None:
                    display_symbol = None

                    if self.feature_background_grid is not None:
                        display_symbol = self.feature_background_grid[row_index][
                            col_index
                        ]

                    display_text = (
                        display_symbol.display if display_symbol is not None else ""
                    )

                    if display_text:
                        spin_surface = self.small_font.render(
                            display_text, True, (230, 230, 240)
                        )
                        self.screen.blit(
                            spin_surface,
                            (
                                x + feature_cell_w // 2 - spin_surface.get_width() // 2,
                                y
                                + feature_cell_h // 2
                                - spin_surface.get_height() // 2,
                            ),
                        )

                if value is not None:
                    yin_surface = self.small_font.render("YIN", True, (30, 20, 40))
                    value_surface = self.symbol_font.render(
                        str(value), True, (30, 20, 40)
                    )

                    self.screen.blit(
                        yin_surface,
                        (
                            x + feature_cell_w // 2 - yin_surface.get_width() // 2,
                            y + 10,
                        ),
                    )
                    self.screen.blit(
                        value_surface,
                        (
                            x + feature_cell_w // 2 - value_surface.get_width() // 2,
                            y + 35,
                        ),
                    )

        if self.feature_result is not None:
            if self.feature_phase in {"countup", "done"}:
                total_display = self.feature_countup_value
            else:
                total_display = 0

            line_1 = (
                f"Symbols: {self.feature_result.symbol_total}    "
                f"Columns: {self.feature_result.column_bonus_total}"
            )
            line_2 = f"Total Win: {total_display}"

            summary_1_surface = self.label_font.render(line_1, True, (240, 230, 255))
            summary_2_surface = self.title_font.render(line_2, True, (255, 220, 120))

            self.screen.blit(
                summary_1_surface,
                (
                    board_rect.centerx - summary_1_surface.get_width() // 2,
                    530,
                ),
            )
            self.screen.blit(
                summary_2_surface,
                (
                    board_rect.centerx - summary_2_surface.get_width() // 2,
                    565,
                ),
            )

        if self.feature_phase == "spins" and self.feature_waiting_for_input:
            self.draw_feature_continue_button("CONTINUE RESPIN")

        elif self.feature_phase == "done" and self.feature_finished_waiting:
            self.draw_feature_continue_button("CLOSE FEATURE")

        current_time = pygame.time.get_ticks()
        if (
            self.feature_grand_popup_text
            and current_time < self.feature_grand_popup_end_time
        ):
            popup_rect = pygame.Rect(250, 205, 500, 55)
            pygame.draw.rect(self.screen, (255, 220, 100), popup_rect, border_radius=12)
            pygame.draw.rect(
                self.screen, (255, 255, 230), popup_rect, width=3, border_radius=12
            )

            popup_surface = self.label_font.render(
                self.feature_grand_popup_text, True, (40, 30, 20)
            )
            self.screen.blit(
                popup_surface,
                (
                    popup_rect.centerx - popup_surface.get_width() // 2,
                    popup_rect.centery - popup_surface.get_height() // 2,
                ),
            )

    def draw_bull_feature_board(self) -> None:
        if (
            not self.bull_feature_mode
            or self.bull_feature_result is None
            or self.bull_feature_display_multiplier_grid is None
        ):
            return

        overlay_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 185))
        self.screen.blit(overlay_surface, (0, 0))

        board_rect = pygame.Rect(120, 100, 760, 520)
        pygame.draw.rect(self.screen, (40, 28, 18), board_rect, border_radius=18)
        pygame.draw.rect(
            self.screen, (255, 200, 120), board_rect, width=4, border_radius=18
        )

        title_surface = self.title_font.render("BULL FEATURE", True, (255, 215, 140))
        self.screen.blit(
            title_surface,
            (board_rect.centerx - title_surface.get_width() // 2, 120),
        )

        phase_text = "Dropping collected Bulls..."
        if self.bull_feature_phase == "fill":
            phase_text = "Spinning empty cells..."
        elif self.bull_feature_phase == "countup":
            phase_text = "Counting Bull Feature win..."
        elif self.bull_feature_phase == "done":
            phase_text = "Bull Feature complete"

        info_surface = self.label_font.render(phase_text, True, TEXT_COLOR)
        self.screen.blit(
            info_surface,
            (board_rect.centerx - info_surface.get_width() // 2, 165),
        )

        feature_grid_x = 200
        feature_grid_y = 240
        feature_cell_w = 90
        feature_cell_h = 80
        feature_gap = 12

        pulse = (pygame.time.get_ticks() // 120) % 2 == 0
        flashing = pygame.time.get_ticks() < self.bull_feature_flash_until

        for row_index in range(3):
            for col_index in range(5):
                x = feature_grid_x + col_index * (feature_cell_w + feature_gap)
                y = feature_grid_y + row_index * (feature_cell_h + feature_gap)

                cell_rect = pygame.Rect(x, y, feature_cell_w, feature_cell_h)

                multiplier = self.bull_feature_display_multiplier_grid[row_index][
                    col_index
                ]
                is_flash = (row_index, col_index) in self.bull_feature_flash_cells

                if multiplier > 0:
                    if is_flash and flashing and pulse:
                        fill_color = (255, 240, 160)
                    elif is_flash and flashing:
                        fill_color = (250, 220, 130)
                    else:
                        fill_color = (245, 180, 130)

                    border_color = (255, 235, 190)
                else:
                    fill_color = (72, 72, 82)
                    border_color = (135, 135, 155)

                pygame.draw.rect(self.screen, fill_color, cell_rect, border_radius=12)
                pygame.draw.rect(
                    self.screen, border_color, cell_rect, width=3, border_radius=12
                )

                if multiplier > 0:
                    bull_surface = self.small_font.render("BULL", True, (35, 20, 20))
                    multi_surface = self.symbol_font.render(
                        f"x{multiplier}", True, (35, 20, 20)
                    )

                    self.screen.blit(
                        bull_surface,
                        (
                            x + feature_cell_w // 2 - bull_surface.get_width() // 2,
                            y + 10,
                        ),
                    )
                    self.screen.blit(
                        multi_surface,
                        (
                            x + feature_cell_w // 2 - multi_surface.get_width() // 2,
                            y + 34,
                        ),
                    )
                else:
                    display_symbol = None

                    if self.bull_feature_display_symbol_grid is not None:
                        display_symbol = self.bull_feature_display_symbol_grid[
                            row_index
                        ][col_index]
                    elif self.bull_feature_background_grid is not None:
                        display_symbol = self.bull_feature_background_grid[row_index][
                            col_index
                        ]

                    if display_symbol is not None:
                        symbol_surface = self.small_font.render(
                            display_symbol.display, True, (235, 235, 245)
                        )
                        self.screen.blit(
                            symbol_surface,
                            (
                                x
                                + feature_cell_w // 2
                                - symbol_surface.get_width() // 2,
                                y
                                + feature_cell_h // 2
                                - symbol_surface.get_height() // 2,
                            ),
                        )

        collected_text = f"Collected Bulls: {self.bull_feature_result.collected_bulls}"
        collected_surface = self.label_font.render(
            collected_text, True, (245, 230, 210)
        )
        self.screen.blit(
            collected_surface,
            (board_rect.centerx - collected_surface.get_width() // 2, 510),
        )

        if self.bull_feature_phase in {"countup", "done"}:
            total_display = self.bull_feature_countup_value
        else:
            total_display = 0

        total_surface = self.title_font.render(
            f"Total Win: {total_display}",
            True,
            (255, 220, 120),
        )
        self.screen.blit(
            total_surface,
            (board_rect.centerx - total_surface.get_width() // 2, 550),
        )

        if self.bull_feature_phase == "done" and self.bull_feature_finished_waiting:
            self.draw_bull_feature_continue_button("CLOSE FEATURE")

    def draw_feature_continue_button(self, text: str) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.feature_continue_button_rect.collidepoint(mouse_pos)

        color = (140, 90, 180) if not hovered else (170, 110, 210)

        pygame.draw.rect(
            self.screen, color, self.feature_continue_button_rect, border_radius=12
        )
        pygame.draw.rect(
            self.screen,
            (240, 230, 255),
            self.feature_continue_button_rect,
            width=3,
            border_radius=12,
        )

        text_surface = self.label_font.render(text, True, TEXT_COLOR)
        self.screen.blit(
            text_surface,
            (
                self.feature_continue_button_rect.x
                + self.feature_continue_button_rect.width // 2
                - text_surface.get_width() // 2,
                self.feature_continue_button_rect.y
                + self.feature_continue_button_rect.height // 2
                - text_surface.get_height() // 2,
            ),
        )

    def draw_bull_feature_continue_button(self, text: str) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.bull_feature_continue_button_rect.collidepoint(mouse_pos)

        color = (180, 120, 70) if not hovered else (210, 145, 90)

        pygame.draw.rect(
            self.screen, color, self.bull_feature_continue_button_rect, border_radius=12
        )
        pygame.draw.rect(
            self.screen,
            (255, 235, 200),
            self.bull_feature_continue_button_rect,
            width=3,
            border_radius=12,
        )

        text_surface = self.label_font.render(text, True, TEXT_COLOR)
        self.screen.blit(
            text_surface,
            (
                self.bull_feature_continue_button_rect.x
                + self.bull_feature_continue_button_rect.width // 2
                - text_surface.get_width() // 2,
                self.bull_feature_continue_button_rect.y
                + self.bull_feature_continue_button_rect.height // 2
                - text_surface.get_height() // 2,
            ),
        )

    def draw_help_text(self) -> None:
        help_text = "SPACE = Spin | F = Freispiele | Y = Yin-Yang | Pfeil hoch/runter = Einsatz | Maus: Buttons | ESC = Beenden"
        help_surface = self.small_font.render(help_text, True, TEXT_COLOR)
        self.screen.blit(
            help_surface,
            (WINDOW_WIDTH // 2 - help_surface.get_width() // 2, 675),
        )
