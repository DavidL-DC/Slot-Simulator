import random

from config import PAYLINES, REELS, REEL_STRIPS, ROWS
from symbols import Symbol


def get_visible_symbols(strip: list[Symbol], stop_index: int, window_size: int) -> list[Symbol]:
    visible_symbols: list[Symbol] = []
    strip_length = len(strip)

    for offset in range(window_size):
        symbol_index = (stop_index + offset) % strip_length
        visible_symbols.append(strip[symbol_index])

    return visible_symbols


def spin_reels() -> list[list[Symbol]]:
    columns: list[list[Symbol]] = []

    for reel_index in range(REELS):
        strip = REEL_STRIPS[reel_index]
        stop_index = random.randint(0, len(strip) - 1)
        visible_column = get_visible_symbols(strip, stop_index, ROWS)
        columns.append(visible_column)

    grid: list[list[Symbol]] = []

    for row_index in range(ROWS):
        row: list[Symbol] = []
        for reel_index in range(REELS):
            row.append(columns[reel_index][row_index])
        grid.append(row)

    return grid


def print_grid(grid: list[list[Symbol]]) -> None:
    print("=== SPIN RESULT ===")
    for row in grid:
        formatted_row = " | ".join(f"{symbol.display:^5}" for symbol in row)
        print(formatted_row)


def get_line_symbols(grid: list[list[Symbol]], payline: list[int]) -> list[Symbol]:
    line_symbols: list[Symbol] = []

    for reel_index, row_index in enumerate(payline):
        line_symbols.append(grid[row_index][reel_index])

    return line_symbols


def evaluate_line_symbols(line_symbols: list[Symbol], bet: int) -> int:
    first_symbol = line_symbols[0]

    if first_symbol.is_scatter:
        return 0

    if first_symbol.is_wild:
        target_symbol = None
        for symbol in line_symbols[1:]:
            if not symbol.is_wild and not symbol.is_scatter:
                target_symbol = symbol
                break

        if target_symbol is None:
            return 0
    else:
        target_symbol = first_symbol

    match_count = 0

    for symbol in line_symbols:
        if symbol.is_scatter:
            break

        if symbol.name == target_symbol.name or symbol.is_wild:
            match_count += 1
        else:
            break

    if match_count < 3:
        return 0

    multiplier = target_symbol.payouts.get(match_count, 0)
    return bet * multiplier


def evaluate_middle_row(grid: list[list[Symbol]], bet: int) -> int:
    middle_payline = [1, 1, 1, 1, 1]
    line_symbols = get_line_symbols(grid, middle_payline)
    return evaluate_line_symbols(line_symbols, bet)


def evaluate_all_paylines(grid: list[list[Symbol]], bet: int) -> tuple[int, list[dict]]:
    total_win = 0
    line_results: list[dict] = []

    for line_index, payline in enumerate(PAYLINES, start=1):
        line_symbols = get_line_symbols(grid, payline)
        win = evaluate_line_symbols(line_symbols, bet)

        line_results.append(
            {
                "line_index": line_index,
                "payline": payline,
                "symbols": line_symbols,
                "win": win,
            }
        )

        total_win += win

    return total_win, line_results


def print_line_results(line_results: list[dict]) -> None:
    print("=== LINIENAUSWERTUNG ===")

    for result in line_results:
        formatted_symbols = " - ".join(symbol.display for symbol in result["symbols"])
        print(
            f"Linie {result['line_index']}: "
            f"{formatted_symbols} | Gewinn: {result['win']}"
        )

def run_middle_row_test_case(name: str, grid: list[list[Symbol]], bet: int, expected_win: int) -> bool:
    print(f"=== TEST MITTLERE REIHE: {name} ===")
    print_grid(grid)
    actual_win = evaluate_middle_row(grid, bet)
    print(f"Erwarteter Gewinn: {expected_win}")
    print(f"Tatsächlicher Gewinn: {actual_win}")

    passed = actual_win == expected_win

    if passed:
        print("Ergebnis: OK")
    else:
        print("Ergebnis: FEHLER")

    print()
    return passed


def run_payline_test_case(
    name: str,
    grid: list[list[Symbol]],
    payline: list[int],
    bet: int,
    expected_win: int,
) -> bool:
    print(f"=== TEST EINZELNE LINIE: {name} ===")
    print_grid(grid)
    print(f"Payline: {payline}")

    line_symbols = get_line_symbols(grid, payline)
    actual_win = evaluate_line_symbols(line_symbols, bet)

    print(f"Linien-Symbole: {' - '.join(symbol.display for symbol in line_symbols)}")
    print(f"Erwarteter Gewinn: {expected_win}")
    print(f"Tatsächlicher Gewinn: {actual_win}")

    passed = actual_win == expected_win

    if passed:
        print("Ergebnis: OK")
    else:
        print("Ergebnis: FEHLER")

    print()
    return passed


def run_all_paylines_test_case(
    name: str,
    grid: list[list[Symbol]],
    bet: int,
    expected_total_win: int,
) -> bool:
    print(f"=== TEST ALLE LINIEN: {name} ===")
    print_grid(grid)

    actual_total_win, line_results = evaluate_all_paylines(grid, bet)
    print_line_results(line_results)
    print(f"Erwarteter Gesamtgewinn: {expected_total_win}")
    print(f"Tatsächlicher Gesamtgewinn: {actual_total_win}")

    passed = actual_total_win == expected_total_win

    if passed:
        print("Ergebnis: OK")
    else:
        print("Ergebnis: FEHLER")

    print()
    return passed