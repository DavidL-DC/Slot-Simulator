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
BUTTON_COLOR = (70, 120, 200)
BUTTON_DISABLED_COLOR = (90, 90, 90)


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

        self.state = state

        self.current_grid = spin_reels()
        self.last_total_win = 0
        self.last_line_win = 0
        self.last_scatter_win = 0
        self.last_yin_yang_win = 0
        self.last_scatter_count = 0
        self.last_yin_yang_count = 0
        self.last_awarded_free_spins = 0
        self.status_text = "Drücke LEERTASTE für Spin"

        self.running = True

    def run(self) -> None:
        while self.running:
            self.handle_events()
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

    def change_bet(self, delta: int) -> None:
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
        if not can_spin(self.state):
            self.status_text = "Nicht genug Guthaben für einen Spin."
            return

        free_spin_mode = is_free_spin(self.state)

        if free_spin_mode:
            consume_free_spin(self.state)
        else:
            apply_bet(self.state)

        self.current_grid = spin_reels()
        win_result = evaluate_total_win(self.current_grid, self.state.current_bet)

        total_win = win_result["total_win"]
        line_win = win_result["line_win"]
        scatter_win = win_result["scatter_win"]
        yin_yang_win = win_result["yin_yang_win"]

        if free_spin_mode:
            total_win *= 3
            line_win *= 3
            scatter_win *= 3
            yin_yang_win *= 3

        if win_result["awarded_free_spins"] > 0:
            add_free_spins(self.state, win_result["awarded_free_spins"])

        apply_win(self.state, total_win)

        self.last_total_win = total_win
        self.last_line_win = line_win
        self.last_scatter_win = scatter_win
        self.last_yin_yang_win = yin_yang_win
        self.last_scatter_count = win_result["scatter_count"]
        self.last_yin_yang_count = win_result["yin_yang_count"]
        self.last_awarded_free_spins = win_result["awarded_free_spins"]

        if free_spin_mode:
            self.status_text = f"Freispiel gespielt. Gewinn: {total_win}"
        else:
            self.status_text = f"Spin gespielt. Gewinn: {total_win}"

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)

        self.draw_title()
        self.draw_top_panel()
        self.draw_grid()
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
                pygame.draw.rect(self.screen, CELL_COLOR, cell_rect, border_radius=12)
                pygame.draw.rect(
                    self.screen, PANEL_COLOR, cell_rect, width=3, border_radius=12
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
        row_2_surface = self.small_font.render(row_2, True, TEXT_COLOR)

        self.screen.blit(row_1_surface, (80, 585))
        self.screen.blit(row_2_surface, (80, 620))

    def draw_help_text(self) -> None:
        help_text = "SPACE = Spin | Pfeil hoch/runter = Einsatz ändern | ESC = Beenden"
        help_surface = self.small_font.render(help_text, True, TEXT_COLOR)
        self.screen.blit(
            help_surface,
            (WINDOW_WIDTH // 2 - help_surface.get_width() // 2, 675),
        )
