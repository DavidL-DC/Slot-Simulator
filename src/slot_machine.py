import random

from config import REELS, ROWS
from symbols import ALL_SYMBOLS, Symbol


def spin_reels() -> list[list[Symbol]]:
    grid: list[list[Symbol]] = []

    for _ in range(ROWS):
        row: list[Symbol] = []
        for _ in range(REELS):
            symbol = random.choice(ALL_SYMBOLS)
            row.append(symbol)
        grid.append(row)

    return grid


def print_grid(grid: list[list[Symbol]]) -> None:
    print("=== SPIN RESULT ===")
    for row in grid:
        formatted_row = " | ".join(f"{symbol.display:^5}" for symbol in row)
        print(formatted_row)


def get_middle_row(grid: list[list[Symbol]]) -> list[Symbol]:
    middle_row_index = len(grid) // 2
    return grid[middle_row_index]


def evaluate_middle_row(grid: list[list[Symbol]], bet: int) -> int:
    row = get_middle_row(grid)

    first_symbol = row[0]

    if first_symbol.is_scatter:
        return 0

    if first_symbol.is_wild:
        target_symbol = None
        for symbol in row[1:]:
            if not symbol.is_wild and not symbol.is_scatter:
                target_symbol = symbol
                break

        if target_symbol is None:
            return 0
    else:
        target_symbol = first_symbol

    match_count = 0

    for symbol in row:
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


def run_test_case(name: str, grid: list[list[Symbol]], bet: int, expected_win: int) -> bool:
    print(f"=== TEST: {name} ===")
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