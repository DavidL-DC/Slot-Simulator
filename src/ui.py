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
from slot_machine import evaluate_total_win, spin_reels
from symbols import ALL_SYMBOLS, Symbol


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
        self.status_text = "Drücke LEERTASTE oder SPIN"

        self.running = True

        self.is_spinning = False
        self.spin_start_time = 0
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

        self.spin_button_rect = pygame.Rect(830, 470, 140, 60)
        self.bet_minus_rect = pygame.Rect(20, 470, 60, 50)
        self.bet_plus_rect = pygame.Rect(90, 470, 60, 50)

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update_animation()
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
                    self.try_spin()
                elif event.key == pygame.K_UP:
                    self.change_bet(10)
                elif event.key == pygame.K_DOWN:
                    self.change_bet(-10)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if self.spin_button_rect.collidepoint(mouse_pos):
                    self.try_spin()
                elif self.bet_minus_rect.collidepoint(mouse_pos):
                    self.change_bet(-10)
                elif self.bet_plus_rect.collidepoint(mouse_pos):
                    self.change_bet(10)

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
        else:
            apply_bet(self.state)
            self.status_text = "Walzen drehen..."

        self.final_grid = spin_reels()
        win_result = evaluate_total_win(self.final_grid, self.state.current_bet)

        total_win = win_result["total_win"]
        line_win = win_result["line_win"]
        scatter_win = win_result["scatter_win"]
        yin_yang_win = win_result["yin_yang_win"]

        if free_spin_mode:
            total_win *= 3
            line_win *= 3
            scatter_win *= 3
            yin_yang_win *= 3

        self.pending_total_win = total_win
        self.pending_line_win = line_win
        self.pending_scatter_win = scatter_win
        self.pending_yin_yang_win = yin_yang_win
        self.pending_scatter_count = win_result["scatter_count"]
        self.pending_yin_yang_count = win_result["yin_yang_count"]
        self.pending_awarded_free_spins = win_result["awarded_free_spins"]

        self.current_grid = self.create_random_grid()

        self.is_spinning = True
        self.spin_start_time = pygame.time.get_ticks()
        self.locked_reels = [False, False, False, False, False]

        base_delay = 700
        reel_delay = 250

        self.reel_stop_times = [
            self.spin_start_time + base_delay + reel_index * reel_delay
            for reel_index in range(GRID_COLS)
        ]

    def finish_spin(self) -> None:
        self.is_spinning = False

        if self.pending_awarded_free_spins > 0:
            add_free_spins(self.state, self.pending_awarded_free_spins)

        apply_win(self.state, self.pending_total_win)

        self.last_total_win = self.pending_total_win
        self.last_line_win = self.pending_line_win
        self.last_scatter_win = self.pending_scatter_win
        self.last_yin_yang_win = self.pending_yin_yang_win
        self.last_scatter_count = self.pending_scatter_count
        self.last_yin_yang_count = self.pending_yin_yang_count
        self.last_awarded_free_spins = self.pending_awarded_free_spins

        if self.pending_free_spin_mode:
            self.status_text = f"Freispiel beendet. Gewinn: {self.pending_total_win}"
        else:
            self.status_text = f"Spin beendet. Gewinn: {self.pending_total_win}"

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)

        self.draw_title()
        self.draw_top_panel()
        self.draw_grid()
        self.draw_controls()
        self.draw_bottom_panel()
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

        text_surface = self.button_font.render("SPIN", True, TEXT_COLOR)
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

    def draw_help_text(self) -> None:
        help_text = "SPACE = Spin | Pfeil hoch/runter = Einsatz ändern | Maus: Buttons klickbar | ESC = Beenden"
        help_surface = self.small_font.render(help_text, True, TEXT_COLOR)
        self.screen.blit(
            help_surface,
            (WINDOW_WIDTH // 2 - help_surface.get_width() // 2, 675),
        )
