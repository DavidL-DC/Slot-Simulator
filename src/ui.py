import math
import random
from pathlib import Path

import pygame

from game import (
    GameState,
    add_free_spins,
    apply_bet,
    apply_win,
    can_spin,
    consume_free_spin,
    is_free_spin,
    set_denom,
    set_credits_bet,
    can_set_credits,
    can_set_denom,
)
from slot_machine import (
    evaluate_total_win,
    spin_reels,
    trigger_debug_yin_yang_feature,
    count_bulls,
    spin_reels_with_stops,
    spin_free_spins_with_stops,
)
from symbols import ALL_SYMBOLS, Symbol, COLLECTOR, CREDIT, BULL, YIN_YANG
from bull_feature import play_bull_feature
from config import PAYLINES
from sound_manager import SoundManager

BASE_DIR = Path(__file__).resolve().parent.parent

BASE_WIDTH = 1600
BASE_HEIGHT = 900

GRID_COLS = 5
GRID_ROWS = 3

CELL_WIDTH = 211
CELL_HEIGHT = 211
CELL_GAP_HORIZONTAL = 40
CELL_GAP_VERTICAL = 10

GRID_X = 192
GRID_Y = 89

TEXT_COLOR = (255, 255, 255)
GOLD_COLOR = (255, 204, 0)
ACCENT_COLOR = (212, 175, 55)
BUTTON_COLOR = (0, 0, 0, 0)
BUTTON_HOVER_COLOR = (245, 245, 245, 50)
BUTTON_DISABLED_COLOR = (90, 90, 90, 100)


def make_nullable_grid(grid: list[list[Symbol]]) -> list[list[Symbol | None]]:
    return [[symbol for symbol in row] for row in grid]


class SlotUI:
    def __init__(self, state: GameState) -> None:
        pygame.init()
        pygame.display.set_caption("Fortune Bull Prototype")

        self.windowed_size = (1280, 720)
        self.fullscreen = False

        self.screen = pygame.display.set_mode(
            self.windowed_size,
            pygame.RESIZABLE,
        )

        self.canvas = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        self.clock = pygame.time.Clock()

        self.background_image = pygame.image.load(
            BASE_DIR / "assets" / "backgrounds" / "base.png"
        ).convert()
        self.free_spin_background_image = pygame.image.load(
            BASE_DIR / "assets" / "backgrounds" / "free_spins.png"
        ).convert()
        self.yin_yang_background_image = pygame.image.load(
            BASE_DIR / "assets" / "backgrounds" / "yin_yang.png"
        ).convert()

        self.sounds = SoundManager(BASE_DIR)

        self.title_font = pygame.font.SysFont("arial", 36, bold=True)
        self.label_font = pygame.font.SysFont("arial", 24)
        self.symbol_font = pygame.font.SysFont("arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("arial", 20)
        self.button_font = pygame.font.SysFont("arial", 28, bold=True)
        self.credit_font = pygame.font.SysFont("arial", 50, bold=True)

        self.state = state

        self.current_grid: list[list[Symbol | None]] = make_nullable_grid(
            spin_reels(self.state.credits_bet)
        )
        self.final_grid: list[list[Symbol | None]] = [
            row.copy() for row in self.current_grid
        ]

        self.last_total_win = 0
        self.last_credit_values = {}

        self.overlay_text = ""
        self.overlay_subtext = ""
        self.overlay_color = ACCENT_COLOR
        self.overlay_end_time = 0

        self.running = True

        self.is_spinning = False
        self.locked_reels = [False, False, False, False, False]

        self.pending_total_win = 0
        self.pending_yin_yang_count = 0
        self.pending_awarded_free_spins = 0
        self.pending_free_spin_mode = False
        self.pending_yin_yang_feature_result = None
        self.pending_instant_win = 0
        self.pending_credit_values = {}
        self.pending_free_spin_bull_count = 0

        self.pending_total_line_win = 0
        self.pending_winning_line_results = []

        self.feature_mode = False
        self.feature_result = None
        self.feature_spin_index = -1

        self.feature_display_grid = None
        self.feature_display_columns = None
        self.feature_display_spins_left = 0

        self.feature_phase = "idle"

        self.feature_countup_value = 0
        self.feature_countup_target = 0
        self.feature_countup_start_time = 0
        self.feature_countup_duration_ms = 1200

        self.feature_waiting_for_input = False
        self.feature_finished_waiting = False

        self.feature_current_completed_columns: list[int] = []

        self.feature_respin_animating = False
        self.feature_pending_spin_result = None
        self.feature_win_applied = False

        self.feature_return_grid: list[list[Symbol | None]] | None = None

        self.yin_yang_cell_spin_offsets: dict[tuple[int, int], float] = {}
        self.yin_yang_cell_spin_targets: dict[tuple[int, int], float] = {}
        self.yin_yang_cell_spin_strips: dict[tuple[int, int], list[Symbol]] = {}
        self.yin_yang_cell_spin_start_time = 0
        self.yin_yang_cell_spin_duration = 1300

        self.yin_yang_visible_symbols: list[list[Symbol | None]] = [
            [None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)
        ]

        self.bull_feature_mode = False
        self.bull_feature_result = None
        self.bull_feature_phase = "idle"
        # idle, armed, drops, ready_to_spin, spinning, countup, done

        self.bull_feature_display_multiplier_grid: list[list[int]] | None = None
        self.bull_feature_drop_index = -1
        self.bull_feature_next_drop_time = 0
        self.bull_feature_win_applied = False

        self.bull_feature_countup_value = 0
        self.bull_feature_countup_target = 0
        self.bull_feature_countup_start_time = 0
        self.bull_feature_countup_duration_ms = 1800

        self.bull_feature_cell_spin_offsets: dict[tuple[int, int], float] = {}
        self.bull_feature_cell_spin_targets: dict[tuple[int, int], float] = {}
        self.bull_feature_cell_spin_strips: dict[tuple[int, int], list[Symbol]] = {}
        self.bull_feature_cell_spin_start_time = 0
        self.bull_feature_cell_spin_duration = 1300

        self.spin_button_rect = pygame.Rect(1467, 665, 113, 48)

        self.last_winning_line_results = []
        self.last_total_line_win = 0
        self.active_line_win_index = 0
        self.active_line_win_start_time = 0
        self.line_win_display_duration_ms = 2000

        self.symbol_images = self.load_symbol_images()

        self.info_messages = [
            f"{len(PAYLINES)} Gewinnlinien",
            f"Credits per Line: {int(self.state.credits_bet/len(PAYLINES))}",
        ]
        self.info_message_index = 0
        self.info_message_start_time = 0
        self.info_message_duration_ms = 2500

        self.credits_button_rect = pygame.Rect(17, 795, 113, 87)
        self.denom_button_rect = pygame.Rect(1467, 792, 113, 87)

        self.selection_popup_open = False
        self.selection_popup_type = None  # "denom" oder "credits"
        self.selection_popup_buttons = []

        self.reel_animation_strips = []
        self.reel_animation_offsets = [0.0 for _ in range(GRID_COLS)]
        self.reel_animation_start_offsets = [0.0 for _ in range(GRID_COLS)]
        self.reel_animation_target_offsets = [0.0 for _ in range(GRID_COLS)]
        self.reel_animation_start_times = [0 for _ in range(GRID_COLS)]
        self.reel_animation_durations = [0 for _ in range(GRID_COLS)]

        self.bull_feature_bump_cell: tuple[int, int] | None = None
        self.bull_feature_bump_start_time = 0
        self.bull_feature_bump_duration_ms = 220

        self.overlay_waiting_for_input = False
        self.overlay_action: str | None = None

        self.deposit_popup_open = False
        self.deposit_input_text = ""

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update_animation()
            self.update_feature_playback()
            self.update_feature_respin_animation()
            self.update_bull_feature_playback()
            self.update_line_win_display()
            self.update_info_message_display()
            self.draw()
            self.blit_scaled_canvas()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def get_canvas_mouse_pos(self) -> tuple[int, int] | None:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        window_width, window_height = self.screen.get_size()

        scale = min(
            window_width / BASE_WIDTH,
            window_height / BASE_HEIGHT,
        )

        scaled_width = int(BASE_WIDTH * scale)
        scaled_height = int(BASE_HEIGHT * scale)

        offset_x = (window_width - scaled_width) // 2
        offset_y = (window_height - scaled_height) // 2

        canvas_x = (mouse_x - offset_x) / scale
        canvas_y = (mouse_y - offset_y) / scale

        if canvas_x < 0 or canvas_x >= BASE_WIDTH:
            return None

        if canvas_y < 0 or canvas_y >= BASE_HEIGHT:
            return None

        # print(canvas_x, canvas_y)
        return int(canvas_x), int(canvas_y)

    def is_window_maximized(self) -> bool:
        window_w, window_h = self.screen.get_size()
        desktop_w, desktop_h = pygame.display.get_desktop_sizes()[0]

        # kleiner Toleranzbereich wegen Taskleiste
        return abs(window_w - desktop_w) < 10 and window_h >= desktop_h - 80

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.VIDEORESIZE and not self.fullscreen:
                if not self.is_window_maximized():
                    self.resize_window_16_9(event.w, event.h)
                else:
                    self.windowed_size = (event.w, event.h)

            elif event.type == pygame.KEYDOWN:
                if self.deposit_popup_open:
                    self.handle_deposit_key(event)
                    return

                if event.key == pygame.K_SPACE:
                    self.handle_skip_or_continue()
                elif event.key == pygame.K_f:
                    self.debug_trigger_free_spins()
                elif event.key == pygame.K_y:
                    self.debug_trigger_yin_yang()
                elif event.key == pygame.K_i:
                    self.debug_trigger_instant_win()
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_m:
                    self.sounds.enabled = not self.sounds.enabled
                elif event.key == pygame.K_c:
                    self.open_deposit_popup()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = self.get_canvas_mouse_pos()

                if mouse_pos is None:
                    return

                if self.selection_popup_open:
                    for rect, value in self.selection_popup_buttons:
                        if rect.collidepoint(mouse_pos):
                            if self.selection_popup_type == "denom":
                                set_denom(self.state, value)

                            elif self.selection_popup_type == "credits":
                                set_credits_bet(self.state, value)

                            self.refresh_info_messages()
                            self.close_selection_popup()
                            return

                    self.close_selection_popup()
                    return

                if self.denom_button_rect.collidepoint(mouse_pos):
                    if not self.can_change_bet_settings():
                        return
                    self.open_selection_popup("denom")
                    return

                if self.credits_button_rect.collidepoint(mouse_pos):
                    if not self.can_change_bet_settings():
                        return
                    self.open_selection_popup("credits")
                    return

                if self.spin_button_rect.collidepoint(mouse_pos):
                    self.handle_skip_or_continue()

    def open_deposit_popup(self) -> None:
        if self.is_spinning or self.feature_mode or self.bull_feature_mode:
            return

        self.deposit_popup_open = True
        self.deposit_input_text = ""

    def close_deposit_popup(self) -> None:
        self.deposit_popup_open = False
        self.deposit_input_text = ""

    def handle_deposit_key(self, event) -> None:
        if event.key == pygame.K_ESCAPE:
            self.close_deposit_popup()
            return

        if event.key == pygame.K_RETURN:
            try:
                amount = round(float(self.deposit_input_text.replace(",", ".")), 2)
            except ValueError:
                return

            if amount > 0:
                self.state.balance += amount
                self.close_deposit_popup()

            return

        if event.key == pygame.K_BACKSPACE:
            self.deposit_input_text = self.deposit_input_text[:-1]
            return

        char = event.unicode

        if char.isdigit():
            self.deposit_input_text += char
        elif (
            char in {".", ","}
            and "." not in self.deposit_input_text
            and "," not in self.deposit_input_text
        ):
            self.deposit_input_text += char

    def resize_window_16_9(self, width: int, height: int) -> None:
        target_height = int(width * 9 / 16)

        if target_height <= height:
            new_width = width
            new_height = target_height
        else:
            new_height = height
            new_width = int(height * 16 / 9)

        self.windowed_size = (new_width, new_height)
        self.screen = pygame.display.set_mode(
            self.windowed_size,
            pygame.RESIZABLE,
        )

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            self.screen = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN,
            )
        else:
            self.screen = pygame.display.set_mode(
                self.windowed_size,
                pygame.RESIZABLE,
            )

    def can_change_bet_settings(self) -> bool:
        return (
            not self.is_spinning
            and not is_free_spin(self.state)
            and not self.feature_mode
            and not self.bull_feature_mode
        )

    def has_skippable_animation(self) -> bool:
        if self.is_spinning:
            return True

        if self.feature_mode:
            if self.feature_respin_animating:
                return True
            if self.feature_phase == "countup":
                return True

        if self.bull_feature_mode and self.bull_feature_phase in {
            "drops",
            "spinning",
            "countup",
        }:
            return True

        return False

    def handle_skip_or_continue(self) -> None:
        if self.overlay_text and self.overlay_waiting_for_input:
            action = self.overlay_action
            self.close_overlay()

            if action == "start_free_spin_feature":
                self.try_spin()
            elif action == "start_bull_feature_final_spin":
                self.start_bull_feature_final_spin()
            elif action == "start_yin_yang_feature":
                self.start_yin_yang_feature_playback(
                    self.pending_yin_yang_feature_result
                )
            return

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
            if self.bull_feature_phase == "armed":
                self.start_bull_feature()
                return

            if self.bull_feature_phase == "done":
                self.close_bull_feature()
                return

            return

        self.try_spin()

    def close_overlay(self) -> None:
        self.overlay_text = ""
        self.overlay_subtext = ""
        self.overlay_end_time = 0
        self.overlay_waiting_for_input = False
        self.overlay_action = None

    def skip_current_animation(self) -> None:
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

            if self.bull_feature_phase == "spinning":
                self.skip_bull_feature_spin()
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

        self.current_grid = [row.copy() for row in self.yin_yang_visible_symbols]

        for row_index in range(GRID_ROWS):
            for col_index in range(GRID_COLS):
                if self.feature_display_grid[row_index][col_index] is not None:
                    self.current_grid[row_index][col_index] = YIN_YANG

        old_completed = set(self.feature_current_completed_columns)
        new_completed = set(current_spin.completed_columns)

        if current_spin.new_positions:
            self.sounds.play("yin_yang_column_step")

        if new_completed - old_completed:
            self.sounds.play("yin_yang_column_complete")

        if current_spin.grand_activated:
            self.sounds.play("grand_activated")

        self.feature_current_completed_columns = current_spin.completed_columns.copy()

        if current_spin.grand_activated:
            self.sounds.play("grand_activated")
            self.show_overlay("GRAND JACKPOT ACTIVATED!", GOLD_COLOR, 1800)

        self.yin_yang_cell_spin_offsets = {}
        self.yin_yang_cell_spin_targets = {}
        self.yin_yang_cell_spin_strips = {}

        self.feature_respin_animating = False
        self.feature_waiting_for_input = True
        self.feature_pending_spin_result = None

    def skip_yin_yang_countup(self) -> None:
        if not self.feature_mode or self.feature_result is None:
            return

        self.feature_countup_value = self.feature_countup_target
        self.feature_phase = "done"
        self.sounds.stop("countup")
        self.feature_finished_waiting = True
        self.feature_waiting_for_input = False

        self.feature_current_completed_columns = (
            self.feature_result.completed_columns.copy()
        )

        self.apply_yin_yang_feature_win_once()

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

        self.current_grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        for row_index in range(GRID_ROWS):
            for col_index in range(GRID_COLS):
                if self.bull_feature_display_multiplier_grid[row_index][col_index] > 0:
                    self.current_grid[row_index][col_index] = BULL

        self.bull_feature_drop_index = len(self.bull_feature_result.drops) - 1
        self.bull_feature_bump_cell = None

        self.bull_feature_phase = "ready_to_spin"

        self.show_overlay(
            "PRESS SPIN / SPACE",
            (255, 200, 120),
            subtext="to start Bull Feature Spin",
            wait_for_input=True,
            action="start_bull_feature_final_spin",
        )

    def skip_bull_feature_spin(self) -> None:
        if not self.bull_feature_mode or self.bull_feature_result is None:
            return

        self.current_grid = make_nullable_grid(
            self.bull_feature_result.final_symbol_grid
        )

        self.bull_feature_cell_spin_offsets = {}
        self.bull_feature_cell_spin_targets = {}
        self.bull_feature_cell_spin_strips = {}

        self.last_winning_line_results = [
            {
                "line_index": line_win.line_index,
                "payline": PAYLINES[line_win.line_index - 1],
                "win": line_win.win,
                "match_count": line_win.match_count,
                "target_symbol": line_win.matched_symbol_name,
            }
            for line_win in self.bull_feature_result.line_wins
        ]

        self.active_line_win_index = 0
        self.active_line_win_start_time = pygame.time.get_ticks()

        self.bull_feature_phase = "countup"
        self.sounds.play_loop("countup")
        self.bull_feature_countup_start_time = pygame.time.get_ticks()
        self.bull_feature_countup_target = self.bull_feature_result.total_win
        self.bull_feature_countup_value = 0

    def skip_bull_countup(self) -> None:
        if not self.bull_feature_mode or self.bull_feature_result is None:
            return

        self.bull_feature_countup_value = self.bull_feature_countup_target
        self.bull_feature_phase = "done"
        self.sounds.stop("countup")

        if not self.bull_feature_win_applied:
            apply_win(self.state, self.bull_feature_result.total_win)
            self.last_total_win = self.bull_feature_result.total_win
            self.bull_feature_win_applied = True

    def load_symbol_images(self) -> dict[str, pygame.Surface]:
        image_paths = {
            "nine": BASE_DIR / "assets" / "symbols" / "nine.png",
            "ten": BASE_DIR / "assets" / "symbols" / "ten.png",
            "jack": BASE_DIR / "assets" / "symbols" / "jack.png",
            "queen": BASE_DIR / "assets" / "symbols" / "queen.png",
            "king": BASE_DIR / "assets" / "symbols" / "king.png",
            "gong": BASE_DIR / "assets" / "symbols" / "gong.png",
            "house": BASE_DIR / "assets" / "symbols" / "house.png",
            "lantern": BASE_DIR / "assets" / "symbols" / "lantern.png",
            "vase": BASE_DIR / "assets" / "symbols" / "vase.png",
            "coin": BASE_DIR / "assets" / "symbols" / "coin.png",
            "bull": BASE_DIR / "assets" / "symbols" / "bull.png",
            "credit": BASE_DIR / "assets" / "symbols" / "credit.png",
            "collector": BASE_DIR / "assets" / "symbols" / "collector.png",
            "yin_yang": BASE_DIR / "assets" / "symbols" / "yin_yang.png",
        }

        images = {}
        for name, path in image_paths.items():
            image = pygame.image.load(path).convert_alpha()
            images[name] = pygame.transform.smoothscale(
                image,
                (CELL_WIDTH - 20, CELL_HEIGHT - 20),
            )

        return images

    def blit_scaled_canvas(self) -> None:
        window_width, window_height = self.screen.get_size()

        scale = min(
            window_width / BASE_WIDTH,
            window_height / BASE_HEIGHT,
        )

        scaled_width = int(BASE_WIDTH * scale)
        scaled_height = int(BASE_HEIGHT * scale)

        x = (window_width - scaled_width) // 2
        y = (window_height - scaled_height) // 2

        scaled_canvas = pygame.transform.smoothscale(
            self.canvas,
            (scaled_width, scaled_height),
        )

        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled_canvas, (x, y))

    def open_selection_popup(self, popup_type: str) -> None:
        self.selection_popup_open = True
        self.selection_popup_type = popup_type
        self.selection_popup_buttons = []

        if popup_type == "denom":
            values = [0.01, 0.02, 0.05, 0.10, 1.00]
        elif popup_type == "credits":
            values = [50, 100, 150, 250, 500]
        else:
            return

        button_w = 130
        button_h = 50
        gap = 14

        start_x = BASE_WIDTH // 2 - (
            (button_w * len(values) + gap * (len(values) - 1)) // 2
        )
        y = BASE_HEIGHT // 2

        for index, value in enumerate(values):
            rect = pygame.Rect(
                start_x + index * (button_w + gap), y, button_w, button_h
            )
            self.selection_popup_buttons.append((rect, value))

    def close_selection_popup(self) -> None:
        self.selection_popup_open = False
        self.selection_popup_type = None
        self.selection_popup_buttons = []

    def get_active_winning_positions(self) -> list[tuple[int, int]]:
        if not self.last_winning_line_results:
            return []

        result = self.last_winning_line_results[self.active_line_win_index]
        payline = result["payline"]
        match_count = result["match_count"]

        return [(payline[reel_index], reel_index) for reel_index in range(match_count)]

    def ease_out_cubic(self, t: float) -> float:
        return 1 - pow(1 - t, 3)

    def update_animation(self) -> None:
        if not self.is_spinning:
            return

        current_time = pygame.time.get_ticks()

        for reel_index in range(GRID_COLS):
            if self.locked_reels[reel_index]:
                continue

            elapsed = current_time - self.reel_animation_start_times[reel_index]
            duration = self.reel_animation_durations[reel_index]
            progress = min(1.0, elapsed / duration)

            eased = self.ease_out_cubic(progress)

            start_offset = self.reel_animation_start_offsets[reel_index]
            target_offset = self.reel_animation_target_offsets[reel_index]

            self.reel_animation_offsets[reel_index] = (
                start_offset + (target_offset - start_offset) * eased
            )

            if progress >= 1.0:
                self.locked_reels[reel_index] = True
                self.sounds.play("spin")

                bull_landed = False

                for row_index in range(GRID_ROWS):
                    self.current_grid[row_index][reel_index] = self.final_grid[
                        row_index
                    ][reel_index]

                    symbol = self.current_grid[row_index][reel_index]

                    if (
                        self.pending_free_spin_mode
                        and symbol is not None
                        and symbol.name == "bull"
                    ):
                        bull_landed = True

                if bull_landed:
                    self.sounds.play("bull_collect_or_drop")

        if all(self.locked_reels):
            self.finish_spin()

    def update_line_win_display(self) -> None:
        if not self.last_winning_line_results:
            return

        current_time = pygame.time.get_ticks()

        if (
            current_time - self.active_line_win_start_time
            >= self.line_win_display_duration_ms
        ):
            self.active_line_win_index = (self.active_line_win_index + 1) % len(
                self.last_winning_line_results
            )
            self.active_line_win_start_time = current_time

    def show_overlay(
        self,
        text: str,
        color: tuple[int, int, int],
        duration_ms: int | None = 500,
        subtext: str = "",
        wait_for_input: bool = False,
        action: str | None = None,
    ) -> None:
        self.overlay_text = text
        self.overlay_color = color
        self.overlay_subtext = subtext
        self.overlay_waiting_for_input = wait_for_input
        self.overlay_action = action

        if duration_ms is None:
            self.overlay_end_time = 0
        else:
            self.overlay_end_time = pygame.time.get_ticks() + duration_ms
            self.overlay_subtext = subtext

    def apply_yin_yang_feature_win_once(self) -> None:
        if self.feature_result is None:
            return

        if self.feature_win_applied:
            return

        apply_win(self.state, self.feature_result.total_win)
        self.last_total_win = self.feature_result.total_win
        self.feature_win_applied = True

    def start_yin_yang_feature_playback(self, feature_result) -> None:
        self.feature_mode = True
        self.feature_result = feature_result
        self.feature_spin_index = -1

        self.feature_return_grid = [row.copy() for row in self.current_grid]
        self.last_winning_line_results = []
        self.pending_winning_line_results = []
        self.active_line_win_index = 0
        self.active_line_win_start_time = 0

        self.feature_display_grid = [
            row.copy() for row in feature_result.start_grid_values
        ]
        self.yin_yang_visible_symbols = [
            [None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)
        ]
        self.current_grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        for row_index in range(GRID_ROWS):
            for col_index in range(GRID_COLS):
                if self.feature_display_grid[row_index][col_index] is not None:
                    self.current_grid[row_index][col_index] = YIN_YANG

        self.feature_display_columns = feature_result.start_column_values.copy()
        self.feature_display_spins_left = 3

        self.feature_phase = "spins"

        self.feature_countup_value = 0
        self.feature_countup_target = feature_result.total_win
        self.feature_countup_start_time = 0

        self.feature_waiting_for_input = True
        self.feature_finished_waiting = False

        self.feature_current_completed_columns = []

        self.feature_respin_animating = False
        self.feature_pending_spin_result = None
        self.feature_win_applied = False

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
                self.sounds.stop("countup")
                self.feature_finished_waiting = True
                self.feature_waiting_for_input = False
                self.feature_countup_value = self.feature_countup_target

                self.apply_yin_yang_feature_win_once()

                self.feature_current_completed_columns = (
                    self.feature_result.completed_columns.copy()
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
                self.sounds.play_loop("countup")
                self.feature_countup_start_time = pygame.time.get_ticks()
                self.feature_waiting_for_input = False
                return

            self.feature_spin_index = next_index
            self.feature_pending_spin_result = self.feature_result.spins[
                self.feature_spin_index
            ]

            self.feature_respin_animating = True
            self.feature_waiting_for_input = False

            self.prepare_yin_yang_respin_animation(self.feature_pending_spin_result)

            return

        if self.feature_phase == "done":
            if self.feature_return_grid is not None:
                self.current_grid = [row.copy() for row in self.feature_return_grid]

            self.feature_mode = False
            self.feature_result = None
            self.feature_phase = "idle"
            self.feature_finished_waiting = False
            self.feature_waiting_for_input = False
            self.feature_respin_animating = False
            self.feature_pending_spin_result = None
            self.feature_return_grid = None

    def update_feature_respin_animation(self) -> None:
        if not self.feature_mode or not self.feature_respin_animating:
            return

        if self.feature_pending_spin_result is None:
            self.feature_respin_animating = False
            self.feature_waiting_for_input = True
            return

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.yin_yang_cell_spin_start_time
        progress = min(1.0, elapsed / self.yin_yang_cell_spin_duration)
        eased = self.ease_out_cubic(progress)

        for pos, target in self.yin_yang_cell_spin_targets.items():
            self.yin_yang_cell_spin_offsets[pos] = target * eased

        if progress < 1.0:
            return

        current_spin = self.feature_pending_spin_result

        self.feature_display_grid = [row.copy() for row in current_spin.grid_values]
        self.feature_display_columns = current_spin.column_values.copy()
        self.feature_display_spins_left = current_spin.spins_left_after

        self.current_grid = [row.copy() for row in self.yin_yang_visible_symbols]

        for row_index in range(GRID_ROWS):
            for col_index in range(GRID_COLS):
                if self.feature_display_grid[row_index][col_index] is not None:
                    self.current_grid[row_index][col_index] = YIN_YANG

        if current_spin.grand_activated:
            self.sounds.play("grand_activated")
            self.show_overlay("GRAND JACKPOT ACTIVATED!", GOLD_COLOR, 1800)

        if current_spin.new_positions:
            self.sounds.play("yin_yang_column_step")

        old_completed = set(self.feature_current_completed_columns)

        self.feature_current_completed_columns = current_spin.completed_columns.copy()

        new_completed = set(current_spin.completed_columns)

        if new_completed - old_completed:
            self.sounds.play("yin_yang_column_complete")

        self.yin_yang_cell_spin_offsets = {}
        self.yin_yang_cell_spin_targets = {}
        self.yin_yang_cell_spin_strips = {}

        self.feature_respin_animating = False
        self.feature_waiting_for_input = True
        self.feature_pending_spin_result = None

    def prepare_yin_yang_respin_animation(self, current_spin) -> None:
        if self.feature_display_grid is None:
            return

        self.yin_yang_cell_spin_offsets = {}
        self.yin_yang_cell_spin_targets = {}
        self.yin_yang_cell_spin_strips = {}

        spin_pool = [
            symbol
            for symbol in ALL_SYMBOLS
            if symbol.name
            in {
                "nine",
                "ten",
                "jack",
                "queen",
                "king",
                "gong",
                "house",
                "lantern",
                "vase",
                "yin_yang",
            }
        ]

        miss_pool = [symbol for symbol in spin_pool if symbol.name != "yin_yang"]

        symbol_step = CELL_HEIGHT + CELL_GAP_VERTICAL
        self.yin_yang_cell_spin_start_time = pygame.time.get_ticks()

        for row_index in range(GRID_ROWS):
            for col_index in range(GRID_COLS):
                # Bereits gelandete Yins bleiben fix
                if self.feature_display_grid[row_index][col_index] is not None:
                    continue

                # Nur leere Felder spinnen
                pos = (row_index, col_index)

                # Wenn auf diesem Feld im nächsten Spin ein Yin landet,
                # soll die Animation auch auf YIN_YANG enden.
                target_symbol = (
                    YIN_YANG
                    if current_spin.grid_values[row_index][col_index] is not None
                    else random.choice(miss_pool)
                )

                strip = spin_pool.copy()

                if target_symbol not in strip:
                    strip.append(target_symbol)

                target_index = strip.index(target_symbol)
                loops = 3 + col_index
                target_steps = loops * len(strip) + (
                    (len(strip) - target_index) % len(strip)
                )

                self.yin_yang_visible_symbols[row_index][col_index] = target_symbol

                self.yin_yang_cell_spin_strips[pos] = strip
                self.yin_yang_cell_spin_offsets[pos] = 0.0
                self.yin_yang_cell_spin_targets[pos] = target_steps * symbol_step

                self.current_grid[row_index][col_index] = None

    def start_bull_feature_final_spin(self) -> None:
        if (
            self.bull_feature_result is None
            or self.bull_feature_display_multiplier_grid is None
        ):
            return

        self.bull_feature_phase = "spinning"

        self.last_winning_line_results = []

        self.close_overlay()

        self.final_grid = make_nullable_grid(self.bull_feature_result.final_symbol_grid)

        self.bull_feature_cell_spin_offsets = {}
        self.bull_feature_cell_spin_targets = {}
        self.bull_feature_cell_spin_strips = {}

        symbol_pool = [
            symbol
            for symbol in ALL_SYMBOLS
            if symbol.name
            in {
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

        symbol_step = CELL_HEIGHT + CELL_GAP_VERTICAL
        start_time = pygame.time.get_ticks()
        self.bull_feature_cell_spin_start_time = start_time

        for row_index in range(GRID_ROWS):
            for col_index in range(GRID_COLS):
                if self.bull_feature_display_multiplier_grid[row_index][col_index] > 0:
                    # Bull bleibt fix
                    self.current_grid[row_index][col_index] = BULL
                    continue

                target_symbol = self.bull_feature_result.final_symbol_grid[row_index][
                    col_index
                ]

                strip = symbol_pool.copy()

                if target_symbol not in strip:
                    strip.append(target_symbol)

                target_index = strip.index(target_symbol)
                loops = 4 + col_index

                target_steps = loops * len(strip) + (
                    (len(strip) - target_index) % len(strip)
                )
                pos = (row_index, col_index)
                self.bull_feature_cell_spin_strips[pos] = strip
                self.bull_feature_cell_spin_offsets[pos] = 0.0
                self.bull_feature_cell_spin_targets[pos] = target_steps * symbol_step
                self.current_grid[row_index][col_index] = None

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
                self.bull_feature_phase = "ready_to_spin"
                self.show_overlay(
                    "PRESS SPIN / SPACE",
                    (255, 200, 120),
                    subtext="to start Bull Feature Spin",
                    wait_for_input=True,
                    action="start_bull_feature_final_spin",
                )
                return

            self.bull_feature_drop_index = next_index
            current_drop = self.bull_feature_result.drops[self.bull_feature_drop_index]

            row_index, col_index = current_drop.landing_position

            old_multiplier = self.bull_feature_display_multiplier_grid[row_index][
                col_index
            ]

            self.bull_feature_display_multiplier_grid[row_index][
                col_index
            ] = current_drop.multiplier_after

            self.current_grid[row_index][col_index] = BULL
            self.sounds.play("bull_collect_or_drop")

            if old_multiplier > 0:
                self.bull_feature_bump_cell = (row_index, col_index)
                self.bull_feature_bump_start_time = pygame.time.get_ticks()

            self.bull_feature_next_drop_time = current_time + 500
            return

        if self.bull_feature_phase == "spinning":
            elapsed = current_time - self.bull_feature_cell_spin_start_time
            progress = min(1.0, elapsed / self.bull_feature_cell_spin_duration)
            eased = self.ease_out_cubic(progress)

            for pos, target in self.bull_feature_cell_spin_targets.items():
                self.bull_feature_cell_spin_offsets[pos] = target * eased

            if progress >= 1.0:
                self.current_grid = make_nullable_grid(
                    self.bull_feature_result.final_symbol_grid
                )

                self.last_winning_line_results = [
                    {
                        "line_index": line_win.line_index,
                        "payline": PAYLINES[line_win.line_index - 1],
                        "win": line_win.win,
                        "match_count": line_win.match_count,
                        "target_symbol": line_win.matched_symbol_name,
                    }
                    for line_win in self.bull_feature_result.line_wins
                ]

                self.active_line_win_index = 0
                self.active_line_win_start_time = pygame.time.get_ticks()

                self.bull_feature_phase = "countup"
                self.sounds.play_loop("countup")
                self.bull_feature_countup_start_time = pygame.time.get_ticks()
                self.bull_feature_countup_target = self.bull_feature_result.total_win

            return

        if self.bull_feature_phase == "countup":
            elapsed = current_time - self.bull_feature_countup_start_time
            progress = min(1.0, elapsed / self.bull_feature_countup_duration_ms)

            self.bull_feature_countup_value = int(
                self.bull_feature_countup_target * progress
            )

            if progress >= 1.0:
                self.bull_feature_phase = "done"
                self.sounds.stop("countup")
                self.bull_feature_countup_value = self.bull_feature_countup_target

                if not self.bull_feature_win_applied:
                    apply_win(self.state, self.bull_feature_result.total_win)
                    self.last_total_win = self.bull_feature_result.total_win
                    self.bull_feature_win_applied = True
            return

    def update_info_message_display(self) -> None:
        current_time = pygame.time.get_ticks()

        if current_time - self.info_message_start_time >= self.info_message_duration_ms:
            self.info_message_index = (self.info_message_index + 1) % len(
                self.info_messages
            )
            self.info_message_start_time = current_time

    def refresh_info_messages(self) -> None:
        self.info_messages = [
            f"{len(PAYLINES)} Gewinnlinien",
            f"Credits per Line: {int(self.state.credits_bet/len(PAYLINES))}",
        ]

    def try_spin(self) -> None:
        if self.is_spinning:
            return

        if not can_spin(self.state):
            return

        self.last_credit_values = {}

        self.last_winning_line_results = []
        self.pending_winning_line_results = []
        self.active_line_win_index = 0
        self.active_line_win_start_time = 0

        free_spin_mode = is_free_spin(self.state)
        self.pending_free_spin_mode = free_spin_mode

        self.pending_free_spin_bull_count = 0

        if free_spin_mode:
            consume_free_spin(self.state)

            spin_result = spin_free_spins_with_stops()
            result_grid = spin_result.grid
            self.final_grid = make_nullable_grid(result_grid)
            self.reel_animation_strips = spin_result.strips

            self.pending_free_spin_bull_count += count_bulls(result_grid)
        else:
            if self.state.collected_bulls != 0:
                self.state.collected_bulls = 0
            apply_bet(self.state)

            spin_result = spin_reels_with_stops(self.state.credits_bet)
            result_grid = spin_result.grid
            self.final_grid = make_nullable_grid(result_grid)
            self.reel_animation_strips = spin_result.strips

        win_result = evaluate_total_win(
            result_grid,
            self.state.current_bet,
            self.state.credits_bet,
            free_spin_mode,
        )

        self.pending_winning_line_results = [
            result for result in win_result["line_results"] if result["win"] > 0
        ]
        self.pending_total_line_win = win_result["line_win"]

        total_win = win_result["total_win"]
        yin_yang_feature_result = win_result["yin_yang_feature_result"]
        instant_win = win_result["instant_win"]
        credit_values = win_result["credit_values"]

        self.pending_total_win = total_win
        self.pending_yin_yang_count = win_result["yin_yang_count"]
        self.pending_awarded_free_spins = win_result["awarded_free_spins"]
        self.pending_yin_yang_feature_result = yin_yang_feature_result
        self.pending_instant_win = instant_win
        self.pending_credit_values = credit_values

        self.current_grid = make_nullable_grid(spin_reels(self.state.credits_bet))

        self.is_spinning = True
        self.locked_reels = [False, False, False, False, False]

        spin_start_time = pygame.time.get_ticks()

        symbol_step = CELL_HEIGHT + CELL_GAP_VERTICAL

        for reel_index in range(GRID_COLS):
            strip_len = len(self.reel_animation_strips[reel_index])
            stop_index = spin_result.stop_indices[reel_index]

            extra_loops = 3 + reel_index
            target_symbol_steps = extra_loops * strip_len + (
                (strip_len - stop_index) % strip_len
            )

            self.reel_animation_start_offsets[reel_index] = 0.0
            self.reel_animation_target_offsets[reel_index] = (
                target_symbol_steps * symbol_step
            )
            self.reel_animation_offsets[reel_index] = 0.0
            self.reel_animation_start_times[reel_index] = spin_start_time
            self.reel_animation_durations[reel_index] = 1800 + reel_index * 400

    def start_bull_feature(self) -> None:
        collected_bulls = self.state.collected_bulls

        if collected_bulls <= 0:
            return

        self.last_winning_line_results = []
        self.active_line_win_index = 0
        self.state.free_spins_remaining = 0

        self.bull_feature_result = play_bull_feature(
            collected_bulls=collected_bulls,
            bet=self.state.current_bet,
            paylines=PAYLINES,
        )

        self.bull_feature_mode = True
        self.bull_feature_phase = "drops"

        self.bull_feature_display_multiplier_grid = [
            [0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)
        ]

        self.current_grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        self.bull_feature_drop_index = -1
        self.bull_feature_next_drop_time = pygame.time.get_ticks() + 1000

        self.bull_feature_countup_value = 0
        self.bull_feature_countup_target = self.bull_feature_result.total_win
        self.bull_feature_countup_start_time = 0
        self.bull_feature_win_applied = False

        self.show_overlay(
            "DROPPING BULLS",
            (255, 200, 120),
            700,
            subtext=f"Collected Bulls: {collected_bulls}",
        )

    def close_bull_feature(self) -> None:
        self.bull_feature_mode = False
        self.bull_feature_result = None
        self.bull_feature_phase = "idle"

        self.bull_feature_display_multiplier_grid = None
        self.bull_feature_drop_index = -1
        self.bull_feature_next_drop_time = 0

        self.bull_feature_countup_value = 0
        self.bull_feature_countup_target = 0
        self.bull_feature_countup_start_time = 0

        self.bull_feature_win_applied = False

        self.pending_free_spin_mode = False

    def debug_trigger_free_spins(self) -> None:
        if self.is_spinning:
            return

        awarded = 8
        add_free_spins(self.state, awarded)

        self.last_total_win = 0
        self.pending_awarded_free_spins = 0
        self.pending_free_spin_mode = False

        self.sounds.play("feature_trigger")
        self.show_overlay(
            f"{awarded} FREE SPINS WON!",
            (255, 215, 80),
            wait_for_input=True,
            subtext="Press Spin/Space to start feature",
            action="start_free_spin_feature",
        )

    def debug_trigger_yin_yang(self) -> None:
        if self.is_spinning:
            return

        result = trigger_debug_yin_yang_feature(self.state.current_bet)

        self.pending_yin_yang_feature_result = result["yin_yang_feature_result"]

        self.sounds.play("feature_trigger")
        self.show_overlay(
            "YIN-YANG FEATURE!",
            (210, 160, 255),
            wait_for_input=True,
            subtext="Press Spin/Space to start feature",
            action="start_yin_yang_feature",
        )

    def debug_trigger_instant_win(self) -> None:
        free_spin_mode = is_free_spin(self.state)

        if (
            self.is_spinning
            or self.feature_mode
            or self.bull_feature_mode
            or free_spin_mode
            or not can_spin(self.state)
        ):
            return

        apply_bet(self.state)

        self.pending_free_spin_mode = False
        self.pending_free_spin_bull_count = 0
        self.pending_winning_line_results = []

        self.last_winning_line_results = []
        self.active_line_win_index = 0
        self.active_line_win_start_time = 0

        non_special_symbols = [
            symbol
            for symbol in ALL_SYMBOLS
            if symbol.name not in {"coin", "credit", "collector", "yin_yang"}
        ]

        debug_grid = [
            [
                random.choice(non_special_symbols),
                random.choice(non_special_symbols),
                random.choice(non_special_symbols),
                random.choice(non_special_symbols),
                random.choice(non_special_symbols),
            ]
            for _ in range(3)
        ]

        debug_grid[0][0] = CREDIT
        debug_grid[1][2] = CREDIT
        debug_grid[2][4] = COLLECTOR

        self.final_grid = make_nullable_grid(debug_grid)
        win_result = evaluate_total_win(
            debug_grid, self.state.current_bet, self.state.credits_bet
        )

        total_win = win_result["total_win"]
        instant_win = win_result["instant_win"]
        yin_yang_feature_result = win_result["yin_yang_feature_result"]
        credit_values = win_result["credit_values"]

        self.pending_total_win = total_win
        self.pending_instant_win = instant_win
        self.pending_yin_yang_count = win_result["yin_yang_count"]
        self.pending_awarded_free_spins = win_result["awarded_free_spins"]
        self.pending_yin_yang_feature_result = yin_yang_feature_result
        self.pending_credit_values = credit_values

        self.current_grid = make_nullable_grid(spin_reels(self.state.credits_bet))

        self.is_spinning = True
        self.locked_reels = [False for _ in range(GRID_COLS)]

        spin_start_time = pygame.time.get_ticks()
        symbol_step = CELL_HEIGHT + CELL_GAP_VERTICAL

        spin_result = spin_reels_with_stops(self.state.credits_bet)
        self.reel_animation_strips = spin_result.strips

        for reel_index in range(GRID_COLS):
            strip = self.reel_animation_strips[reel_index]

            target_column = [
                debug_grid[row_index][reel_index] for row_index in range(GRID_ROWS)
            ]

            # Zielspalte vorne in den Strip setzen,
            # damit draw_spinning_reel bei stop_index 0 exakt row 0,1,2 zeigt.
            strip = target_column + [
                symbol for symbol in strip if symbol not in target_column
            ]

            self.reel_animation_strips[reel_index] = strip

            strip_len = len(strip)
            stop_index = 0

            extra_loops = 3 + reel_index
            target_symbol_steps = extra_loops * strip_len + (
                (strip_len - stop_index) % strip_len
            )

            self.reel_animation_start_offsets[reel_index] = 0.0
            self.reel_animation_target_offsets[reel_index] = (
                target_symbol_steps * symbol_step
            )
            self.reel_animation_offsets[reel_index] = 0.0
            self.reel_animation_start_times[reel_index] = spin_start_time
            self.reel_animation_durations[reel_index] = 1800 + reel_index * 400

    def finish_spin(self) -> None:
        if (
            self.bull_feature_mode
            and self.bull_feature_phase == "spinning"
            and self.bull_feature_result is not None
        ):
            self.is_spinning = False
            self.current_grid = make_nullable_grid(
                self.bull_feature_result.final_symbol_grid
            )

            self.bull_feature_phase = "countup"
            self.sounds.play_loop("countup")
            self.bull_feature_countup_start_time = pygame.time.get_ticks()
            return

        self.is_spinning = False

        if self.pending_free_spin_mode and self.pending_free_spin_bull_count > 0:
            self.state.collected_bulls += self.pending_free_spin_bull_count

        if self.pending_awarded_free_spins > 0:
            add_free_spins(self.state, self.pending_awarded_free_spins)

        apply_win(self.state, self.pending_total_win)

        self.last_total_win = self.pending_total_win
        self.last_credit_values = self.pending_credit_values.copy()
        self.last_winning_line_results = self.pending_winning_line_results.copy()
        self.last_total_line_win = self.pending_total_line_win
        self.active_line_win_index = 0
        self.active_line_win_start_time = pygame.time.get_ticks()

        if self.last_total_line_win:
            self.sounds.play_line_win(self.last_total_line_win, self.state.current_bet)

        if self.pending_awarded_free_spins > 0:
            self.sounds.play("feature_trigger")
            self.show_overlay(
                f"{self.pending_awarded_free_spins} FREE SPINS WON!",
                (255, 215, 80),
                wait_for_input=True,
                subtext="Press Spin/Space to start feature",
                action="start_free_spin_feature",
            )

        if (
            self.pending_yin_yang_count >= 3
            and self.pending_yin_yang_feature_result is not None
        ):
            self.sounds.play("feature_trigger")
            self.show_overlay(
                "YIN-YANG FEATURE!",
                (210, 160, 255),
                wait_for_input=True,
                subtext="Press Spin/Space to start feature",
                action="start_yin_yang_feature",
            )
        elif self.pending_instant_win > 0:
            self.sounds.play("instant_win")
            self.show_overlay(
                f"INSTANT WIN {self.pending_instant_win}",
                (255, 190, 90),
                subtext="Collector paid all Credit symbols",
                wait_for_input=True,
            )

        # Freispiele beendet → Bull Feature starten
        if self.pending_free_spin_mode and self.state.free_spins_remaining == 1:

            if self.state.collected_bulls > 0:
                self.bull_feature_mode = True
                self.bull_feature_phase = "armed"
            else:
                self.state.free_spins_remaining = 0

    def draw(self) -> None:
        self.draw_background()
        self.draw_grid()
        self.draw_yin_yang_spins_left()
        self.draw_yin_yang_column_values()
        self.draw_yin_yang_feature_grid_values()
        self.draw_yin_yang_completed_column_highlights()
        self.draw_yin_yang_countup_popup()
        self.draw_bottom_panel()
        self.draw_free_spin_status()
        self.draw_spin_button()
        self.draw_bet_selection_buttons()
        self.draw_selection_popup()
        self.draw_line_win_text()
        self.draw_overlay()
        self.draw_bull_feature_countup_popup()
        self.draw_deposit_popup()
        self.draw_info_text()

    def draw_background(self) -> None:
        if self.feature_mode:
            background = self.yin_yang_background_image
        elif is_free_spin(self.state) or self.pending_free_spin_mode:
            background = self.free_spin_background_image
        else:
            background = self.background_image

        scaled_background = pygame.transform.smoothscale(
            background,
            (BASE_WIDTH, BASE_HEIGHT),
        )
        self.canvas.blit(scaled_background, (0, 0))

    def draw_grid(self) -> None:
        if self.bull_feature_mode and self.bull_feature_phase not in ["idle", "armed"]:
            highlight_rect = pygame.Rect(
                GRID_X - 14,
                GRID_Y - 14,
                GRID_COLS * CELL_WIDTH + (GRID_COLS - 1) * CELL_GAP_HORIZONTAL + 28,
                GRID_ROWS * CELL_HEIGHT + (GRID_ROWS - 1) * CELL_GAP_VERTICAL + 28,
            )

            pygame.draw.rect(
                self.canvas,
                (210, 170, 60),
                highlight_rect,
                border_radius=18,
                width=14,
            )

            if self.bull_feature_phase == "spinning":
                self.draw_bull_feature_spinning_cells()

        if self.feature_mode and self.feature_respin_animating:
            self.draw_yin_yang_spinning_cells()

        winning_positions = (
            [] if self.feature_mode else self.get_active_winning_positions()
        )

        for col_index in range(GRID_COLS):
            if self.is_spinning and not self.locked_reels[col_index]:
                self.draw_spinning_reel(col_index)

        for row_index, row in enumerate(self.current_grid):
            for col_index, symbol in enumerate(row):

                if symbol is None:
                    continue

                if self.is_spinning and not self.locked_reels[col_index]:
                    continue

                x = GRID_X + col_index * (CELL_WIDTH + CELL_GAP_HORIZONTAL)
                y = GRID_Y + row_index * (CELL_HEIGHT + CELL_GAP_VERTICAL)

                cell_rect = pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)

                is_winning = (row_index, col_index) in winning_positions

                scale_bonus = (
                    6 if is_winning and (pygame.time.get_ticks() // 250) % 2 == 0 else 0
                )
                cell_rect = pygame.Rect(
                    x - scale_bonus // 2,
                    y - scale_bonus // 2,
                    CELL_WIDTH + scale_bonus,
                    CELL_HEIGHT + scale_bonus,
                )

                if is_winning:
                    pygame.draw.rect(
                        self.canvas,
                        (255, 230, 120),
                        cell_rect,
                        width=5,
                        border_radius=12,
                    )

                if symbol.is_credit_value_symbol:
                    grid_position = (row_index, col_index)
                    value_text = ""

                    if self.is_spinning:
                        if grid_position in self.pending_credit_values:
                            value_obj = self.pending_credit_values[grid_position]
                            value_text = value_obj.label
                    else:
                        if grid_position in self.last_credit_values:
                            value_obj = self.last_credit_values[grid_position]
                            value_text = value_obj.label

                    image = self.symbol_images.get(symbol.name)
                    if image:
                        self.canvas.blit(
                            image,
                            (
                                x + CELL_WIDTH // 2 - image.get_width() // 2,
                                y + CELL_HEIGHT // 2 - image.get_height() // 2,
                            ),
                        )
                    else:
                        symbol_surface = self.small_font.render(
                            symbol.display, True, (30, 30, 40)
                        )
                        self.canvas.blit(
                            symbol_surface,
                            (
                                x + CELL_WIDTH // 2 - symbol_surface.get_width() // 2,
                                y + 28,
                            ),
                        )

                    if value_text:
                        value_surface = self.credit_font.render(
                            value_text, True, GOLD_COLOR
                        )
                        self.canvas.blit(
                            value_surface,
                            (
                                x + CELL_WIDTH // 2 - value_surface.get_width() // 2,
                                y + CELL_HEIGHT // 2 - value_surface.get_height() // 2,
                            ),
                        )
                else:
                    is_bull_highlight = (
                        not self.bull_feature_mode
                        and (is_free_spin(self.state) or self.pending_free_spin_mode)
                        and symbol.name == "bull"
                        and not self.is_spinning
                    )

                    pulse_scale = 1.0

                    if is_bull_highlight:
                        t = pygame.time.get_ticks() / 200  # Geschwindigkeit
                        pulse_scale = 1.0 + 0.08 * (1 + math.sin(t))  # 1.0 → 1.16 → 1.0

                    symbol_scale = 1.0

                    if self.bull_feature_mode and self.bull_feature_bump_cell == (
                        row_index,
                        col_index,
                    ):
                        elapsed = (
                            pygame.time.get_ticks() - self.bull_feature_bump_start_time
                        )
                        progress = min(
                            1.0, elapsed / self.bull_feature_bump_duration_ms
                        )

                        if progress < 1.0:
                            symbol_scale = 1.0 + 0.18 * (1 - progress)
                        else:
                            self.bull_feature_bump_cell = None

                    image = self.symbol_images.get(symbol.name)

                    if image:
                        if is_bull_highlight:
                            scaled_w = int(image.get_width() * pulse_scale)
                            scaled_h = int(image.get_height() * pulse_scale)

                            scaled_image = pygame.transform.smoothscale(
                                image,
                                (scaled_w, scaled_h),
                            )

                            draw_x = x + CELL_WIDTH // 2 - scaled_w // 2
                            draw_y = y + CELL_HEIGHT // 2 - scaled_h // 2

                            self.canvas.blit(scaled_image, (draw_x, draw_y))

                        elif symbol_scale != 1.0:
                            scaled_w = int(image.get_width() * symbol_scale)
                            scaled_h = int(image.get_height() * symbol_scale)
                            scaled_image = pygame.transform.smoothscale(
                                image, (scaled_w, scaled_h)
                            )

                            self.canvas.blit(
                                scaled_image,
                                (
                                    x + CELL_WIDTH // 2 - scaled_w // 2,
                                    y + CELL_HEIGHT // 2 - scaled_h // 2,
                                ),
                            )
                        else:
                            self.canvas.blit(
                                image,
                                (
                                    x + CELL_WIDTH // 2 - image.get_width() // 2,
                                    y + CELL_HEIGHT // 2 - image.get_height() // 2,
                                ),
                            )
                    else:
                        symbol_surface = self.symbol_font.render(
                            symbol.display, True, (30, 30, 40)
                        )
                        self.canvas.blit(
                            symbol_surface,
                            (
                                x + CELL_WIDTH // 2 - symbol_surface.get_width() // 2,
                                y + CELL_HEIGHT // 2 - symbol_surface.get_height() // 2,
                            ),
                        )
                if (
                    self.bull_feature_mode
                    and self.bull_feature_display_multiplier_grid is not None
                    and symbol.name == "bull"
                ):
                    multiplier = self.bull_feature_display_multiplier_grid[row_index][
                        col_index
                    ]

                    if multiplier >= 2:
                        multi_surface = self.symbol_font.render(
                            f"x{multiplier}",
                            True,
                            GOLD_COLOR,
                        )

                        self.canvas.blit(
                            multi_surface,
                            (
                                x + CELL_WIDTH - multi_surface.get_width() - 18,
                                y + CELL_HEIGHT - multi_surface.get_height() - 14,
                            ),
                        )

    def draw_spinning_reel(self, reel_index: int) -> None:
        if not self.reel_animation_strips:
            return

        strip = self.reel_animation_strips[reel_index]
        strip_len = len(strip)

        symbol_step = CELL_HEIGHT + CELL_GAP_VERTICAL
        offset = self.reel_animation_offsets[reel_index]

        current_symbol_index = int(offset // symbol_step)
        pixel_offset = offset % symbol_step

        current_symbol_index = (-current_symbol_index) % strip_len

        x = GRID_X + reel_index * (CELL_WIDTH + CELL_GAP_HORIZONTAL)

        clip_rect = pygame.Rect(
            x,
            GRID_Y,
            CELL_WIDTH,
            GRID_ROWS * CELL_HEIGHT + (GRID_ROWS - 1) * CELL_GAP_VERTICAL,
        )

        old_clip = self.canvas.get_clip()
        self.canvas.set_clip(clip_rect)

        for draw_row in range(-1, GRID_ROWS + 1):
            symbol_index = (current_symbol_index + draw_row) % strip_len
            symbol = strip[symbol_index]

            y = GRID_Y + draw_row * symbol_step + pixel_offset

            image = self.symbol_images.get(symbol.name)

            if image:
                self.canvas.blit(
                    image,
                    (
                        x + CELL_WIDTH // 2 - image.get_width() // 2,
                        y + CELL_HEIGHT // 2 - image.get_height() // 2,
                    ),
                )
            else:
                symbol_surface = self.symbol_font.render(
                    symbol.display,
                    True,
                    (30, 30, 40),
                )
                self.canvas.blit(
                    symbol_surface,
                    (
                        x + CELL_WIDTH // 2 - symbol_surface.get_width() // 2,
                        y + CELL_HEIGHT // 2 - symbol_surface.get_height() // 2,
                    ),
                )

        self.canvas.set_clip(old_clip)

    def draw_bull_feature_spinning_cells(self) -> None:
        symbol_step = CELL_HEIGHT + CELL_GAP_VERTICAL

        for (row_index, col_index), strip in self.bull_feature_cell_spin_strips.items():
            offset = self.bull_feature_cell_spin_offsets.get((row_index, col_index), 0)
            strip_len = len(strip)

            current_symbol_index = int(offset // symbol_step)
            pixel_offset = offset % symbol_step

            current_symbol_index = (-current_symbol_index) % strip_len

            x = GRID_X + col_index * (CELL_WIDTH + CELL_GAP_HORIZONTAL)
            y = GRID_Y + row_index * (CELL_HEIGHT + CELL_GAP_VERTICAL)

            clip_rect = pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)

            old_clip = self.canvas.get_clip()
            self.canvas.set_clip(clip_rect)

            for draw_offset in range(-1, 2):
                symbol_index = (current_symbol_index + draw_offset) % strip_len
                symbol = strip[symbol_index]

                draw_y = y + draw_offset * symbol_step + pixel_offset

                image = self.symbol_images.get(symbol.name)

                if image:
                    self.canvas.blit(
                        image,
                        (
                            x + CELL_WIDTH // 2 - image.get_width() // 2,
                            draw_y + CELL_HEIGHT // 2 - image.get_height() // 2,
                        ),
                    )

            self.canvas.set_clip(old_clip)

    def draw_bottom_panel(self) -> None:
        balance_surface = self.title_font.render(
            f"{self.state.balance:.2f}", True, TEXT_COLOR
        )
        bet_surface = self.title_font.render(
            f"{self.state.current_bet:.2f}", True, TEXT_COLOR
        )
        win_surface = self.title_font.render(
            f"{self.last_total_win:.2f}", True, TEXT_COLOR
        )

        self.canvas.blit(balance_surface, (450, 817))
        self.canvas.blit(bet_surface, (800, 817))
        self.canvas.blit(win_surface, (1200, 817))

    def draw_line_win_text(self) -> None:
        if not self.last_winning_line_results:
            return

        result = self.last_winning_line_results[self.active_line_win_index]

        text = f"Line {result['line_index']}: {result['win']:.2f}"

        surface = self.small_font.render(text, True, TEXT_COLOR)
        self.canvas.blit(surface, (1300, 875))

    @staticmethod
    def draw_transparent_rect(
        surface: pygame.Surface,
        color: tuple[int, int, int, int],
        rect: pygame.Rect,
        border_radius: int = 0,
    ):
        temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        pygame.draw.rect(
            temp_surface,
            color,  # RGBA
            (0, 0, rect.width, rect.height),
            border_radius=border_radius,
        )

        surface.blit(temp_surface, (rect.x, rect.y))

    def draw_spin_button(self) -> None:
        mouse_pos = self.get_canvas_mouse_pos()
        hovered = mouse_pos is not None and self.spin_button_rect.collidepoint(
            mouse_pos
        )
        enabled = (
            self.has_skippable_animation()
            or self.feature_mode
            or self.bull_feature_mode
            or (not self.is_spinning and can_spin(self.state))
        )

        if not enabled:
            color = BUTTON_DISABLED_COLOR
        elif hovered:
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        self.draw_transparent_rect(
            self.canvas,
            color,
            self.spin_button_rect,
            border_radius=0,
        )

        button_text = "SKIP" if self.has_skippable_animation() else "SPIN"
        text_surface = self.button_font.render(button_text, True, GOLD_COLOR)
        self.canvas.blit(
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

    def draw_small_button(
        self, rect: pygame.Rect, text: str, enabled: bool, border_radius: int = 0
    ) -> None:
        mouse_pos = self.get_canvas_mouse_pos()
        hovered = mouse_pos is not None and rect.collidepoint(mouse_pos)

        if not enabled:
            color = BUTTON_DISABLED_COLOR
        elif hovered:
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        self.draw_transparent_rect(
            self.canvas,
            color,
            rect,
            border_radius=border_radius,
        )

        text_surface = self.title_font.render(text, True, TEXT_COLOR)
        self.canvas.blit(
            text_surface,
            (
                rect.x + rect.width // 2 - text_surface.get_width() // 2,
                rect.y + rect.height // 2 - text_surface.get_height() // 2,
            ),
        )

    def draw_bet_selection_buttons(self) -> None:
        self.draw_small_button(
            self.denom_button_rect,
            f"{self.state.denom:.2f}",
            enabled=not self.is_spinning
            and not is_free_spin(self.state)
            and not self.feature_mode,
        )

        if (
            not is_free_spin(self.state)
            and not self.bull_feature_mode
            and not self.feature_mode
        ):
            self.draw_small_button(
                self.credits_button_rect,
                f"{self.state.credits_bet}",
                enabled=not self.is_spinning
                and not is_free_spin(self.state)
                and not self.feature_mode,
            )

    def draw_selection_popup(self) -> None:
        if not self.selection_popup_open:
            return

        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.canvas.blit(overlay, (0, 0))

        box_rect = pygame.Rect(BASE_WIDTH // 2 - 420, BASE_HEIGHT // 2 - 120, 840, 240)
        pygame.draw.rect(self.canvas, (30, 30, 45), box_rect, border_radius=20)
        pygame.draw.rect(self.canvas, ACCENT_COLOR, box_rect, width=4, border_radius=20)

        title = (
            "Denom auswählen"
            if self.selection_popup_type == "denom"
            else "Credits auswählen"
        )
        title_surface = self.label_font.render(title, True, TEXT_COLOR)
        self.canvas.blit(
            title_surface,
            (box_rect.centerx - title_surface.get_width() // 2, box_rect.y + 35),
        )

        for rect, value in self.selection_popup_buttons:
            label = (
                f"{value:.2f}" if self.selection_popup_type == "denom" else str(value)
            )
            enabled = (
                can_set_denom(self.state, value)
                if self.selection_popup_type == "denom"
                else can_set_credits(self.state, value)
            )
            self.draw_small_button(rect, label, enabled=enabled, border_radius=5)
            pygame.draw.rect(self.canvas, ACCENT_COLOR, rect, width=4, border_radius=5)

    def draw_overlay(self) -> None:
        current_time = pygame.time.get_ticks()

        if not self.overlay_text:
            return

        if (
            not self.overlay_waiting_for_input
            and self.overlay_end_time > 0
            and current_time > self.overlay_end_time
        ):
            self.close_overlay()
            return

        overlay_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 110))
        self.canvas.blit(overlay_surface, (0, 0))

        box_rect = pygame.Rect(
            BASE_WIDTH // 2 - 320,
            BASE_HEIGHT // 2 - 70,
            640,
            140,
        )
        pygame.draw.rect(self.canvas, (25, 25, 35), box_rect, border_radius=18)
        pygame.draw.rect(
            self.canvas, self.overlay_color, box_rect, width=4, border_radius=18
        )

        text_surface = self.title_font.render(
            self.overlay_text, True, self.overlay_color
        )

        self.canvas.blit(
            text_surface,
            (
                box_rect.x + box_rect.width // 2 - text_surface.get_width() // 2,
                (
                    box_rect.y + box_rect.height // 2 - text_surface.get_height() // 2
                    if self.overlay_subtext == ""
                    else box_rect.y + 25
                ),
            ),
        )

        if self.overlay_subtext:
            subtext_surface = self.label_font.render(
                self.overlay_subtext, True, TEXT_COLOR
            )
            self.canvas.blit(
                subtext_surface,
                (
                    box_rect.x + box_rect.width // 2 - subtext_surface.get_width() // 2,
                    box_rect.y + 82,
                ),
            )

    def draw_yin_yang_feature_grid_values(self) -> None:
        if not self.feature_mode or self.feature_display_grid is None:
            return

        for row_index in range(GRID_ROWS):
            for col_index in range(GRID_COLS):
                value = self.feature_display_grid[row_index][col_index]

                if value is None:
                    continue

                x = GRID_X + col_index * (CELL_WIDTH + CELL_GAP_HORIZONTAL)
                y = GRID_Y + row_index * (CELL_HEIGHT + CELL_GAP_VERTICAL)

                value_surface = self.credit_font.render(
                    str(value),
                    True,
                    GOLD_COLOR,
                )

                self.canvas.blit(
                    value_surface,
                    (
                        x + CELL_WIDTH // 2 - value_surface.get_width() // 2,
                        y + CELL_HEIGHT // 2 - value_surface.get_height() // 2,
                    ),
                )

    def draw_yin_yang_spins_left(self) -> None:
        if not self.feature_mode:
            return

        values = [3, 2, 1]

        center_x = 73
        start_y = 657
        gap_y = 80

        for index, value in enumerate(values):
            color = (
                GOLD_COLOR if value == self.feature_display_spins_left else TEXT_COLOR
            )

            surface = self.credit_font.render(str(value), True, color)
            rect = surface.get_rect(center=(center_x, start_y + index * gap_y))
            self.canvas.blit(surface, rect)

    def draw_yin_yang_column_values(self) -> None:
        if not self.feature_mode or self.feature_display_columns is None:
            return

        y = 50

        for col_index, value in enumerate(self.feature_display_columns):
            x = (
                GRID_X
                + col_index * (CELL_WIDTH + CELL_GAP_HORIZONTAL)
                + CELL_WIDTH // 2
            )

            color = (
                GOLD_COLOR
                if col_index in self.feature_current_completed_columns
                else TEXT_COLOR
            )

            surface = self.title_font.render(str(value), True, color)
            rect = surface.get_rect(center=(x, y))
            self.canvas.blit(surface, rect)

    def draw_yin_yang_completed_column_highlights(self) -> None:
        if not self.feature_mode:
            return

        for col_index in self.feature_current_completed_columns:
            x = GRID_X + col_index * (CELL_WIDTH + CELL_GAP_HORIZONTAL)

            lower_rect = pygame.Rect(
                x - 8,
                GRID_Y - 8,
                CELL_WIDTH + 16,
                GRID_ROWS * CELL_HEIGHT + (GRID_ROWS - 1) * CELL_GAP_VERTICAL + 16,
            )

            upper_rect = pygame.Rect(
                x - 8,
                GRID_Y - 70,
                CELL_WIDTH + 16,
                70,
            )

            pygame.draw.rect(
                self.canvas,
                GOLD_COLOR,
                lower_rect,
                width=6,
            )

            pygame.draw.rect(
                self.canvas,
                GOLD_COLOR,
                upper_rect,
                width=6,
            )

    def draw_yin_yang_countup_popup(self) -> None:
        if not self.feature_mode:
            return

        if self.feature_phase not in {"countup", "done"}:
            return

        overlay_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 150))
        self.canvas.blit(overlay_surface, (0, 0))

        box_rect = pygame.Rect(
            BASE_WIDTH // 2 - 360,
            BASE_HEIGHT // 2 - 130,
            720,
            260,
        )

        pygame.draw.rect(self.canvas, (28, 24, 40), box_rect, border_radius=24)
        pygame.draw.rect(
            self.canvas, (210, 160, 255), box_rect, width=5, border_radius=24
        )

        title_surface = self.title_font.render(
            "YIN-YANG FEATURE WIN",
            True,
            (220, 180, 255),
        )

        win_surface = self.credit_font.render(
            f"{self.feature_countup_value:.2f}",
            True,
            GOLD_COLOR,
        )

        self.canvas.blit(
            title_surface,
            (
                box_rect.centerx - title_surface.get_width() // 2,
                box_rect.y + 45,
            ),
        )

        self.canvas.blit(
            win_surface,
            (
                box_rect.centerx - win_surface.get_width() // 2,
                box_rect.y + 125,
            ),
        )

        if self.feature_phase == "done":
            close_surface = self.label_font.render(
                "SPACE / SPIN zum Schließen",
                True,
                TEXT_COLOR,
            )

            self.canvas.blit(
                close_surface,
                (
                    box_rect.centerx - close_surface.get_width() // 2,
                    box_rect.y + 210,
                ),
            )

    def draw_yin_yang_spinning_cells(self) -> None:
        if not self.feature_mode or not self.feature_respin_animating:
            return

        symbol_step = CELL_HEIGHT + CELL_GAP_VERTICAL

        for (row_index, col_index), strip in self.yin_yang_cell_spin_strips.items():
            offset = self.yin_yang_cell_spin_offsets.get((row_index, col_index), 0)
            strip_len = len(strip)

            current_symbol_index = int(offset // symbol_step)
            pixel_offset = offset % symbol_step

            current_symbol_index = (-current_symbol_index) % strip_len

            x = GRID_X + col_index * (CELL_WIDTH + CELL_GAP_HORIZONTAL)
            y = GRID_Y + row_index * (CELL_HEIGHT + CELL_GAP_VERTICAL)

            clip_rect = pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)

            old_clip = self.canvas.get_clip()
            self.canvas.set_clip(clip_rect)

            for draw_offset in range(-1, 2):
                symbol_index = (current_symbol_index + draw_offset) % strip_len
                symbol = strip[symbol_index]

                draw_y = y + draw_offset * symbol_step + pixel_offset

                image = self.symbol_images.get(symbol.name)

                if image:
                    self.canvas.blit(
                        image,
                        (
                            x + CELL_WIDTH // 2 - image.get_width() // 2,
                            draw_y + CELL_HEIGHT // 2 - image.get_height() // 2,
                        ),
                    )

            self.canvas.set_clip(old_clip)

    def draw_free_spin_status(self) -> None:
        if self.feature_mode:
            return

        if (
            not is_free_spin(self.state)
            and not self.pending_free_spin_mode
            and not self.bull_feature_mode
        ):
            return

        spins_text = f"{self.state.free_spins_remaining}"
        bulls_text = f"{self.state.collected_bulls}"

        spins_surface = self.title_font.render(spins_text, True, TEXT_COLOR)
        bulls_surface = self.title_font.render(bulls_text, True, TEXT_COLOR)

        # Koordinaten-Zentren an deine eingezeichneten Plätze anpassen
        spins_pos = (73, 838)
        bulls_pos = (73, 675)

        spins_rect = spins_surface.get_rect(center=spins_pos)
        bulls_rect = bulls_surface.get_rect(center=bulls_pos)

        self.canvas.blit(spins_surface, spins_rect)
        self.canvas.blit(bulls_surface, bulls_rect)

    def draw_bull_feature_countup_popup(self) -> None:
        if not self.bull_feature_mode:
            return

        if self.bull_feature_phase not in {"countup", "done"}:
            return

        overlay_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 150))
        self.canvas.blit(overlay_surface, (0, 0))

        box_rect = pygame.Rect(
            BASE_WIDTH // 2 - 360,
            BASE_HEIGHT // 2 - 130,
            720,
            260,
        )

        pygame.draw.rect(self.canvas, (35, 22, 14), box_rect, border_radius=24)
        pygame.draw.rect(
            self.canvas, (255, 200, 120), box_rect, width=5, border_radius=24
        )

        title_surface = self.title_font.render(
            "BULL FEATURE WIN",
            True,
            (255, 220, 140),
        )

        win_surface = self.credit_font.render(
            f"{self.bull_feature_countup_value:.2f}",
            True,
            GOLD_COLOR,
        )

        self.canvas.blit(
            title_surface,
            (
                box_rect.centerx - title_surface.get_width() // 2,
                box_rect.y + 45,
            ),
        )

        self.canvas.blit(
            win_surface,
            (
                box_rect.centerx - win_surface.get_width() // 2,
                box_rect.y + 125,
            ),
        )

        if self.bull_feature_phase == "done":
            close_surface = self.label_font.render(
                "SPACE / SPIN zum Schließen",
                True,
                TEXT_COLOR,
            )

            self.canvas.blit(
                close_surface,
                (
                    box_rect.centerx - close_surface.get_width() // 2,
                    box_rect.y + 210,
                ),
            )

    def draw_deposit_popup(self) -> None:
        if not self.deposit_popup_open:
            return

        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.canvas.blit(overlay, (0, 0))

        box_rect = pygame.Rect(
            BASE_WIDTH // 2 - 360,
            BASE_HEIGHT // 2 - 150,
            720,
            300,
        )

        pygame.draw.rect(self.canvas, (25, 25, 35), box_rect, border_radius=20)
        pygame.draw.rect(self.canvas, GOLD_COLOR, box_rect, width=4, border_radius=20)

        title_surface = self.title_font.render(
            "GELD EINZAHLEN",
            True,
            GOLD_COLOR,
        )
        self.canvas.blit(
            title_surface,
            (
                box_rect.centerx - title_surface.get_width() // 2,
                box_rect.y + 35,
            ),
        )

        label_surface = self.label_font.render(
            "Betrag eingeben:",
            True,
            TEXT_COLOR,
        )
        self.canvas.blit(label_surface, (box_rect.x + 80, box_rect.y + 105))

        input_rect = pygame.Rect(
            box_rect.x + 80, box_rect.y + 145, box_rect.width - 160, 60
        )

        pygame.draw.rect(self.canvas, (10, 10, 18), input_rect, border_radius=10)
        pygame.draw.rect(
            self.canvas, ACCENT_COLOR, input_rect, width=3, border_radius=10
        )

        input_text = self.deposit_input_text or "0.00"

        input_surface = self.title_font.render(
            input_text,
            True,
            TEXT_COLOR,
        )
        self.canvas.blit(
            input_surface,
            (
                input_rect.x + 20,
                input_rect.y + input_rect.height // 2 - input_surface.get_height() // 2,
            ),
        )

        help_surface = self.small_font.render(
            "ENTER = einzahlen | ESC = abbrechen",
            True,
            TEXT_COLOR,
        )
        self.canvas.blit(
            help_surface,
            (
                box_rect.centerx - help_surface.get_width() // 2,
                box_rect.y + 235,
            ),
        )

    def draw_info_text(self) -> None:
        help_text = "SPACE = Spin | F = Freispiele | Y = Yin-Yang | I = Instant Win | M = Ton an/aus | C = Einzahlen"
        help_surface = self.small_font.render(help_text, True, TEXT_COLOR)
        self.canvas.blit(
            help_surface,
            (BASE_WIDTH // 2 - help_surface.get_width() // 2, 875),
        )

        info_text = self.info_messages[self.info_message_index]
        info_surface = self.small_font.render(info_text, True, TEXT_COLOR)
        self.canvas.blit(info_surface, (205, 875))
