import random

from config import (
    FREE_SPINS_AWARDED,
    FREE_SPIN_REEL_STRIPS,
    PAYLINES,
    REELS,
    REEL_STRIPS,
    ROWS,
    SCATTER_PAYOUTS,
    FREE_SPIN_PAYOUTS,
)

from symbols import Symbol
from yin_yang_feature import YinYangFeatureResult, play_yin_yang_feature


def get_visible_symbols(
    strip: list[Symbol], stop_index: int, window_size: int
) -> list[Symbol]:
    visible_symbols: list[Symbol] = []
    strip_length = len(strip)

    for offset in range(window_size):
        symbol_index = (stop_index + offset) % strip_length
        visible_symbols.append(strip[symbol_index])

    return visible_symbols


def get_reel_set_key_for_bet(total_bet: float) -> str:
    if total_bet < 1:
        return "low"
    if total_bet < 5:
        return "mid"
    return "high"


def get_line_bet(total_bet: int | float) -> float:
    return total_bet / len(PAYLINES)


def spin_reels(total_bet: float = 1.0) -> list[list[Symbol]]:
    reel_set_key = get_reel_set_key_for_bet(total_bet)

    columns: list[list[Symbol]] = []

    for reel_index in range(REELS):
        strip = REEL_STRIPS[reel_index]

        if reel_index == 4:
            filtered_strip = [
                symbol for symbol in strip if not symbol.is_credit_value_symbol
            ]
        else:
            filtered_strip = [symbol for symbol in strip if not symbol.is_collector]

        stop_index = random.randint(0, len(filtered_strip) - 1)
        visible_column = get_visible_symbols(filtered_strip, stop_index, ROWS)
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


def analyze_line_symbols(line_symbols: list[Symbol]) -> dict:
    first_symbol = line_symbols[0]

    if first_symbol.is_scatter or first_symbol.name == "yin_yang":
        return {
            "target_symbol": None,
            "match_count": 0,
            "win": 0,
        }

    if first_symbol.is_wild:
        target_symbol = None
        for symbol in line_symbols[1:]:
            if (
                not symbol.is_wild
                and not symbol.is_scatter
                and not symbol.name == "yin_yang"
            ):
                target_symbol = symbol
                break

        if target_symbol is None:
            return {
                "target_symbol": None,
                "match_count": 0,
                "win": 0,
            }
    else:
        target_symbol = first_symbol

    match_count = 0

    for symbol in line_symbols:
        if symbol.is_scatter or symbol.name == "yin_yang":
            break

        if symbol.name == target_symbol.name or symbol.is_wild:
            match_count += 1
        else:
            break

    if match_count < 3:
        return {
            "target_symbol": target_symbol,
            "match_count": match_count,
            "win": 0,
        }

    return {
        "target_symbol": target_symbol,
        "match_count": match_count,
        "win": 0,
    }


def evaluate_line_symbols(
    line_symbols: list[Symbol], bet: int | float, free_spin_mode: bool = False
) -> float:
    analysis = analyze_line_symbols(line_symbols)

    target_symbol = analysis["target_symbol"]
    match_count = analysis["match_count"]

    if target_symbol is None or match_count < 3:
        return 0.0

    if free_spin_mode:
        payouts = FREE_SPIN_PAYOUTS.get(target_symbol.name)
    else:
        payouts = target_symbol.payouts

    if payouts is None:
        return 0.0

    line_bet = get_line_bet(bet)
    multiplier = payouts.get(match_count, 0)
    return line_bet * multiplier


def evaluate_middle_row(grid: list[list[Symbol]], bet: int | float) -> float:
    middle_payline = [1, 1, 1, 1, 1]
    line_symbols = get_line_symbols(grid, middle_payline)
    return evaluate_line_symbols(line_symbols, bet)


def evaluate_all_paylines(
    grid: list[list[Symbol]], bet: int | float, free_spin_mode: bool = False
) -> tuple[float, list[dict]]:
    total_win = 0.0
    line_results: list[dict] = []

    for line_index, payline in enumerate(PAYLINES, start=1):
        line_symbols = get_line_symbols(grid, payline)
        analysis = analyze_line_symbols(line_symbols)
        win = evaluate_line_symbols(line_symbols, bet, free_spin_mode)

        line_results.append(
            {
                "line_index": line_index,
                "payline": payline,
                "symbols": line_symbols,
                "win": win,
                "target_symbol": analysis["target_symbol"],
                "match_count": analysis["match_count"],
            }
        )

        total_win += win

    return total_win, line_results


def count_scatters(grid: list[list[Symbol]]) -> int:
    scatter_count = 0

    for row in grid:
        for symbol in row:
            if symbol.is_scatter:
                scatter_count += 1

    return scatter_count


def evaluate_scatters(grid: list[list[Symbol]], bet: float) -> tuple[int, float]:
    scatter_count = count_scatters(grid)
    capped_count = min(scatter_count, max(SCATTER_PAYOUTS))
    multiplier = SCATTER_PAYOUTS.get(capped_count, 0)
    scatter_win = round(bet * multiplier, 2)
    return scatter_count, scatter_win


def get_awarded_free_spins(scatter_count: int) -> int:
    capped_count = min(scatter_count, max(FREE_SPINS_AWARDED))
    return FREE_SPINS_AWARDED.get(capped_count, 0)


def get_random_credit_multiplier() -> int:
    return random.choice([2, 3, 4, 5, 8, 10, 10, 50, 100, 200])


def spin_reels_free_spins() -> list[list[Symbol]]:
    columns: list[list[Symbol]] = []

    for reel_index in range(REELS):
        strip = FREE_SPIN_REEL_STRIPS[reel_index]
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


def count_bulls(grid: list[list[Symbol]]) -> int:
    count = 0
    for row in grid:
        for symbol in row:
            if symbol.name == "bull":
                count += 1
    return count


def count_yin_yang_symbols(grid: list[list[Symbol]]) -> int:
    yin_yang_count = 0

    for row in grid:
        for symbol in row:
            if symbol.name == "yin_yang":
                yin_yang_count += 1

    return yin_yang_count


def evaluate_yin_yang_feature(
    grid: list[list[Symbol]],
    bet: float,
) -> tuple[int, float, YinYangFeatureResult | None]:
    trigger_positions = get_yin_yang_positions(grid)
    yin_yang_count = len(trigger_positions)

    if yin_yang_count < 3:
        return yin_yang_count, 0, None

    feature_result = play_yin_yang_feature(bet, trigger_positions)

    return yin_yang_count, round(feature_result.total_win, 2), feature_result


def get_yin_yang_positions(grid: list[list[Symbol]]) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []

    for row_index, row in enumerate(grid):
        for col_index, symbol in enumerate(row):
            if symbol.name == "yin_yang":
                positions.append((row_index, col_index))

    return positions


def get_credit_positions(grid: list[list[Symbol]]) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []

    for row_index, row in enumerate(grid):
        for col_index, symbol in enumerate(row):
            if symbol.is_credit_value_symbol and col_index < 4:
                positions.append((row_index, col_index))

    return positions


def get_collector_positions(grid: list[list[Symbol]]) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []

    for row_index, row in enumerate(grid):
        for col_index, symbol in enumerate(row):
            if symbol.is_collector and col_index == 4:
                positions.append((row_index, col_index))

    return positions


def evaluate_total_win(
    grid: list[list[Symbol]], bet: float, free_spin_mode: bool = False
) -> dict:
    line_win, line_results = evaluate_all_paylines(grid, bet, free_spin_mode)

    if free_spin_mode:
        scatter_count = 0
        scatter_win = 0
        awarded_free_spins = 0
        instant_win = 0
        credit_values = {}
        credit_positions = []
        collector_positions = []
    else:
        scatter_count, scatter_win = evaluate_scatters(grid, bet)
        awarded_free_spins = get_awarded_free_spins(scatter_count)
        instant_win, credit_values, credit_positions, collector_positions = (
            evaluate_instant_win_feature(grid, bet)
        )

    yin_yang_count, yin_yang_win, yin_yang_feature_result = evaluate_yin_yang_feature(
        grid, bet
    )

    total_win = line_win + scatter_win + yin_yang_win + instant_win

    return {
        "line_win": line_win,
        "line_results": line_results,
        "scatter_count": scatter_count,
        "scatter_win": scatter_win,
        "awarded_free_spins": awarded_free_spins,
        "yin_yang_count": yin_yang_count,
        "yin_yang_win": yin_yang_win,
        "yin_yang_feature_result": yin_yang_feature_result,
        "instant_win": instant_win,
        "credit_values": credit_values,
        "credit_positions": credit_positions,
        "collector_positions": collector_positions,
        "total_win": total_win,
    }


def evaluate_instant_win_feature(
    grid: list[list[Symbol]],
    bet: float,
) -> tuple[
    float, dict[tuple[int, int], float], list[tuple[int, int]], list[tuple[int, int]]
]:
    credit_positions = get_credit_positions(grid)
    collector_positions = get_collector_positions(grid)

    credit_values: dict[tuple[int, int], float] = {}

    high_values_used = {
        100: False,
        200: False,
    }

    for position in credit_positions:
        while True:
            multiplier = get_random_credit_multiplier()

            if multiplier in {100, 200} and high_values_used[multiplier]:
                continue

            if multiplier in {100, 200}:
                high_values_used[multiplier] = True

            credit_values[position] = round(bet * multiplier, 2)
            break

    if not credit_positions or not collector_positions:
        return 0, credit_values, credit_positions, collector_positions

    instant_win = round(sum(credit_values.values()), 2)

    return instant_win, credit_values, credit_positions, collector_positions


def print_line_results(line_results: list[dict]) -> None:
    print("=== LINIENAUSWERTUNG ===")

    for result in line_results:
        formatted_symbols = " - ".join(symbol.display for symbol in result["symbols"])
        print(
            f"Linie {result['line_index']}: "
            f"{formatted_symbols} | Gewinn: {result['win']}"
        )


def print_scatter_result(
    scatter_count: int, scatter_win: int, awarded_free_spins: int
) -> None:
    print("=== SCATTER-AUSWERTUNG ===")
    print(f"Scatter-Anzahl: {scatter_count}")
    print(f"Scatter-Gewinn: {scatter_win}")
    print(f"Gewonnene Freispiele: {awarded_free_spins}")


def print_yin_yang_result(yin_yang_count: int, yin_yang_win: int) -> None:
    print("=== YIN-YANG-AUSWERTUNG ===")
    print(f"Yin-Yang-Anzahl: {yin_yang_count}")
    print(f"Yin-Yang-Gewinn: {yin_yang_win}")


def run_middle_row_test_case(
    name: str, grid: list[list[Symbol]], bet: int, expected_win: int
) -> bool:
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


def run_scatter_test_case(
    name: str,
    grid: list[list[Symbol]],
    bet: int,
    expected_scatter_count: int,
    expected_scatter_win: int,
    expected_free_spins: int,
) -> bool:
    print(f"=== TEST SCATTER: {name} ===")
    print_grid(grid)

    actual_scatter_count, actual_scatter_win = evaluate_scatters(grid, bet)
    actual_free_spins = get_awarded_free_spins(actual_scatter_count)

    print(f"Erwartete Scatter-Anzahl: {expected_scatter_count}")
    print(f"Tatsächliche Scatter-Anzahl: {actual_scatter_count}")
    print(f"Erwarteter Scatter-Gewinn: {expected_scatter_win}")
    print(f"Tatsächlicher Scatter-Gewinn: {actual_scatter_win}")
    print(f"Erwartete Freispiele: {expected_free_spins}")
    print(f"Tatsächliche Freispiele: {actual_free_spins}")

    passed = (
        actual_scatter_count == expected_scatter_count
        and actual_scatter_win == expected_scatter_win
        and actual_free_spins == expected_free_spins
    )

    if passed:
        print("Ergebnis: OK")
    else:
        print("Ergebnis: FEHLER")

    print()
    return passed


def trigger_debug_yin_yang_feature(bet: float) -> dict:
    trigger_positions = [(0, 0), (1, 2), (2, 4)]
    feature_result = play_yin_yang_feature(bet, trigger_positions)

    return {
        "yin_yang_count": len(trigger_positions),
        "yin_yang_win": feature_result.total_win,
        "yin_yang_feature_result": feature_result,
        "total_win": feature_result.total_win,
    }
