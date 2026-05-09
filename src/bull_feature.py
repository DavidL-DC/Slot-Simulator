from dataclasses import dataclass
import random

from symbols import ALL_SYMBOLS, BULL, Symbol, LANTERN, VASE, GONG, HOUSE

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
    win: float
    multiplier_used: int
    matched_symbol_name: str | None
    match_count: int


@dataclass
class BullFeatureResult:
    collected_bulls: int
    multiplier_grid: list[list[int]]
    drops: list[BullDrop]
    final_symbol_grid: list[list[Symbol]]
    line_wins: list[BullLineWin]
    total_win: float


def create_empty_multiplier_grid() -> list[list[int]]:
    return [[0 for _ in range(REELS)] for _ in range(ROWS)]


def get_bull_feature_symbol_pool() -> list[Symbol]:
    pool = [
        symbol
        for symbol in ALL_SYMBOLS
        if symbol.name not in {"coin", "credit", "collector", "bull", "yin_yang"}
    ]
    pool.append(LANTERN)
    pool.append(VASE)
    pool.append(GONG)
    random.shuffle(pool)

    return pool


def get_neighbor_positions(
    row_index: int,
    col_index: int,
) -> list[tuple[int, int]]:
    neighbors: list[tuple[int, int]] = []

    for row_offset in (-1, 0, 1):
        for col_offset in (-1, 0, 1):
            if row_offset == 0 and col_offset == 0:
                continue

            new_row = row_index + row_offset
            new_col = col_index + col_offset

            if 0 <= new_row < ROWS and 0 <= new_col < REELS:
                neighbors.append((new_row, new_col))

    return neighbors


def get_all_positions() -> list[tuple[int, int]]:
    return [
        (row_index, col_index)
        for row_index in range(ROWS)
        for col_index in range(REELS)
    ]


def drop_bulls(collected_bulls: int) -> tuple[list[list[int]], list[BullDrop]]:
    multiplier_grid = create_empty_multiplier_grid()
    drops: list[BullDrop] = []

    all_positions = get_all_positions()

    for bull_index in range(collected_bulls):
        occupied_positions = [
            (row_index, col_index)
            for row_index in range(ROWS)
            for col_index in range(REELS)
            if multiplier_grid[row_index][col_index] > 0
        ]

        empty_positions = [
            position
            for position in all_positions
            if multiplier_grid[position[0]][position[1]] == 0
        ]

        neighbor_empty_positions: list[tuple[int, int]] = []
        if occupied_positions:
            neighbor_set = set()

            for occupied_row, occupied_col in occupied_positions:
                for neighbor_position in get_neighbor_positions(
                    occupied_row, occupied_col
                ):
                    if multiplier_grid[neighbor_position[0]][neighbor_position[1]] == 0:
                        neighbor_set.add(neighbor_position)

            neighbor_empty_positions = list(neighbor_set)

        if not occupied_positions:
            landing_position = random.choice(all_positions)
        else:
            weighted_positions: list[tuple[int, int]] = []

            weighted_positions.extend(neighbor_empty_positions * 4)
            weighted_positions.extend(empty_positions * 5)
            weighted_positions.extend(occupied_positions * 1)

            landing_position = random.choice(weighted_positions)

        row_index, col_index = landing_position
        multiplier_grid[row_index][col_index] = min(
            3, multiplier_grid[row_index][col_index] + 1
        )

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
            if (
                not symbol.is_wild
                and not symbol.is_scatter
                and symbol.name != "yin_yang"
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


def evaluate_bull_feature_paylines(
    final_symbol_grid: list[list[Symbol]],
    multiplier_grid: list[list[int]],
    paylines: list[list[int]],
    bet: float,
) -> tuple[float, list[BullLineWin]]:
    total_win = 0.0
    line_wins: list[BullLineWin] = []

    line_bet = bet / len(paylines)

    for line_index, payline in enumerate(paylines, start=1):
        line_symbols = get_line_symbols(final_symbol_grid, payline)
        line_multipliers = get_line_multipliers(multiplier_grid, payline)

        # SPECIAL: 5 Bulls auf einer Linie zahlen x75
        if all(symbol.name == "bull" for symbol in line_symbols):
            base_win = line_bet * 75

            used_line_multipliers = [value for value in line_multipliers if value > 0]

            line_multiplier = 1
            for value in used_line_multipliers:
                line_multiplier *= value

            line_multiplier = min(line_multiplier, 18)

            final_win = round(base_win * line_multiplier, 2)

            total_win += final_win
            line_wins.append(
                BullLineWin(
                    line_index=line_index,
                    win=final_win,
                    multiplier_used=line_multiplier,
                    matched_symbol_name="bull",
                    match_count=5,
                )
            )
            continue

        analysis = analyze_line_symbols(line_symbols)
        target_symbol = analysis["target_symbol"]
        match_count = analysis["match_count"]

        if target_symbol is None or match_count < 3:
            continue

        base_multiplier = target_symbol.payouts.get(match_count, 0)
        base_win = line_bet * base_multiplier

        if base_win <= 0:
            continue

        used_line_multipliers = [
            line_multipliers[index]
            for index in range(match_count)
            if line_multipliers[index] > 0
        ]

        line_multiplier = 1
        for value in used_line_multipliers:
            line_multiplier *= value

        line_multiplier = min(line_multiplier, 18)

        final_win = base_win * line_multiplier

        total_win += final_win
        line_wins.append(
            BullLineWin(
                line_index=line_index,
                win=final_win,
                multiplier_used=line_multiplier,
                matched_symbol_name=target_symbol.name,
                match_count=match_count,
            )
        )

    return round(total_win, 2), line_wins


def play_bull_feature(
    collected_bulls: int,
    bet: float,
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
