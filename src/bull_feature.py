from dataclasses import dataclass
import random

from symbols import ALL_SYMBOLS, BULL, Symbol


ROWS = 3
REELS = 5


@dataclass
class BullDrop:
    bull_index: int
    landing_position: tuple[int, int]
    multiplier_after: int


@dataclass
class BullLineWin:
    line_index: int
    win: int
    multiplier_used: int
    matched_symbol_name: str | None


@dataclass
class BullFeatureResult:
    collected_bulls: int
    multiplier_grid: list[list[int]]
    drops: list[BullDrop]
    final_symbol_grid: list[list[Symbol]]
    line_wins: list[BullLineWin]
    total_win: int


def create_empty_multiplier_grid() -> list[list[int]]:
    return [[0 for _ in range(REELS)] for _ in range(ROWS)]


def get_bull_feature_symbol_pool() -> list[Symbol]:
    return [
        symbol
        for symbol in ALL_SYMBOLS
        if symbol.name not in {"coin", "credit", "collector"}
    ]


def drop_bulls(collected_bulls: int) -> tuple[list[list[int]], list[BullDrop]]:
    multiplier_grid = create_empty_multiplier_grid()
    drops: list[BullDrop] = []

    for bull_index in range(collected_bulls):
        row_index = random.randint(0, ROWS - 1)
        col_index = random.randint(0, REELS - 1)

        multiplier_grid[row_index][col_index] += 1

        drops.append(
            BullDrop(
                bull_index=bull_index + 1,
                landing_position=(row_index, col_index),
                multiplier_after=multiplier_grid[row_index][col_index],
            )
        )

    return multiplier_grid, drops


def build_final_symbol_grid(multiplier_grid: list[list[int]]) -> list[list[Symbol]]:
    pool = get_bull_feature_symbol_pool()

    final_grid: list[list[Symbol]] = []

    for row_index in range(ROWS):
        row: list[Symbol] = []
        for col_index in range(REELS):
            if multiplier_grid[row_index][col_index] > 0:
                row.append(BULL)
            else:
                row.append(random.choice(pool))
        final_grid.append(row)

    return final_grid


def get_line_symbols(
    grid: list[list[Symbol]],
    payline: list[int],
) -> list[Symbol]:
    line_symbols: list[Symbol] = []

    for reel_index, row_index in enumerate(payline):
        line_symbols.append(grid[row_index][reel_index])

    return line_symbols


def get_line_multipliers(
    multiplier_grid: list[list[int]],
    payline: list[int],
) -> list[int]:
    line_multipliers: list[int] = []

    for reel_index, row_index in enumerate(payline):
        line_multipliers.append(multiplier_grid[row_index][reel_index])

    return line_multipliers


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
            if not symbol.is_wild and not symbol.is_scatter:
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


def evaluate_bull_feature_paylines(
    final_symbol_grid: list[list[Symbol]],
    multiplier_grid: list[list[int]],
    paylines: list[list[int]],
    bet: int,
) -> tuple[int, list[BullLineWin]]:
    total_win = 0
    line_wins: list[BullLineWin] = []

    for line_index, payline in enumerate(paylines, start=1):
        line_symbols = get_line_symbols(final_symbol_grid, payline)
        line_multipliers = get_line_multipliers(multiplier_grid, payline)

        analysis = analyze_line_symbols(line_symbols)
        target_symbol = analysis["target_symbol"]
        match_count = analysis["match_count"]

        if target_symbol is None or match_count < 3:
            continue

        base_multiplier = target_symbol.payouts.get(match_count, 0)
        base_win = bet * base_multiplier

        if base_win <= 0:
            continue

        used_line_multipliers = [
            line_multipliers[index]
            for index in range(match_count)
            if line_multipliers[index] > 0
        ]

        line_multiplier = max(used_line_multipliers, default=1)
        final_win = base_win * line_multiplier

        total_win += final_win
        line_wins.append(
            BullLineWin(
                line_index=line_index,
                win=final_win,
                multiplier_used=line_multiplier,
                matched_symbol_name=target_symbol.name,
            )
        )

    return total_win, line_wins


def play_bull_feature(
    collected_bulls: int,
    bet: int,
    paylines: list[list[int]],
) -> BullFeatureResult:
    multiplier_grid, drops = drop_bulls(collected_bulls)
    final_symbol_grid = build_final_symbol_grid(multiplier_grid)
    total_win, line_wins = evaluate_bull_feature_paylines(
        final_symbol_grid=final_symbol_grid,
        multiplier_grid=multiplier_grid,
        paylines=paylines,
        bet=bet,
    )

    return BullFeatureResult(
        collected_bulls=collected_bulls,
        multiplier_grid=multiplier_grid,
        drops=drops,
        final_symbol_grid=final_symbol_grid,
        line_wins=line_wins,
        total_win=total_win,
    )
