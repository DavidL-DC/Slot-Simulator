from dataclasses import dataclass
import random

from config import (
    MIN_BET,
    JACKPOT_VALUES,
    YIN_YANG_PRIZE_TABLES,
    YIN_YANG_VALUE_MULTIPLIERS,
)

ROWS = 3
REELS = 5

GRAND_COLUMN_HIT_CHANCE_MULTIPLIER = 0.15


@dataclass
class YinYangFeatureSpin:
    grid_values: list[list[float | None]]
    column_values: list[str]
    new_positions: list[tuple[int, int]]
    spins_left_after: int
    completed_columns: list[int]
    grand_column_index: int | None
    grand_activated: bool


@dataclass
class YinYangFeatureResult:
    trigger_positions: list[tuple[int, int]]
    start_grid_values: list[list[float | None]]
    start_column_values: list[str]
    spins: list[YinYangFeatureSpin]
    final_grid_values: list[list[float | None]]
    final_column_values: list[str]
    completed_columns: list[int]
    grand_column_index: int | None
    symbol_total: float
    column_bonus_total: float
    total_win: float
    selected_table_key: str
    column_pool_keys: list[str]
    column_step_indexes: list[int]


def copy_grid(grid: list[list[float | None]]) -> list[list[float | None]]:
    return [row.copy() for row in grid]


def create_empty_grid() -> list[list[float | None]]:
    return [[None for _ in range(REELS)] for _ in range(ROWS)]


def get_progressive_factor_for_bet(bet: float) -> int:
    # weiche Skalierung für MINI/MINOR-Chance
    if bet <= 1:
        return 1
    if bet <= 2.5:
        return 2
    if bet <= 5:
        return 3
    if bet <= 10:
        return 4
    return 5


def get_random_yin_value(bet: float) -> float:
    pool: list[float] = []

    for multiplier in YIN_YANG_VALUE_MULTIPLIERS:
        pool.append(round(bet * multiplier, 2))

    progressive_factor = get_progressive_factor_for_bet(bet)

    pool.extend([JACKPOT_VALUES["mini"]] * progressive_factor)
    pool.extend([JACKPOT_VALUES["minor"]] * progressive_factor)

    return round(random.choice(pool), 2)


def choose_prize_table_key() -> str:
    return random.choice(["table_1", "table_2"])


def choose_column_pool_keys() -> list[str]:
    base_pools = ["pool_1", "pool_2", "pool_3", "pool_4"]

    pool_5_variant = random.choice(["pool_5a", "pool_5b", "pool_5c"])
    all_pools = base_pools + [pool_5_variant]
    random.shuffle(all_pools)

    return all_pools


def build_column_display_values(
    bet: float,
    table_key: str,
    column_pool_keys: list[str],
    column_step_indexes: list[int],
) -> list[str]:
    table = YIN_YANG_PRIZE_TABLES[table_key]
    display_values: list[str] = []

    for col_index, pool_key in enumerate(column_pool_keys):
        steps = table[pool_key]
        step_index = column_step_indexes[col_index]
        raw_value = steps[step_index]

        if raw_value == "Grand":
            display_values.append("GRAND")
        else:
            display_values.append(str(round(bet * raw_value, 2)))

    return display_values


def get_completed_columns(grid: list[list[float | None]]) -> list[int]:
    completed_columns: list[int] = []

    for col_index in range(REELS):
        if all(grid[row_index][col_index] is not None for row_index in range(ROWS)):
            completed_columns.append(col_index)

    return completed_columns


def advance_column_steps(
    column_step_indexes: list[int],
    completed_columns: list[int],
    table_key: str,
    column_pool_keys: list[str],
) -> list[int]:
    table = YIN_YANG_PRIZE_TABLES[table_key]
    new_indexes: list[int] = []

    for col_index, current_index in enumerate(column_step_indexes):
        if col_index in completed_columns:
            new_indexes.append(current_index)
            continue

        steps = table[column_pool_keys[col_index]]
        if current_index < len(steps) - 1:
            new_indexes.append(current_index + 1)
        else:
            new_indexes.append(current_index)

    return new_indexes


def calculate_symbol_total(grid: list[list[float | None]]) -> float:
    total = 0.0

    for row in grid:
        for value in row:
            if value is not None:
                total += value

    return round(total, 2)


def count_filled_positions(grid: list[list[float | None]]) -> int:
    filled = 0

    for row in grid:
        for value in row:
            if value is not None:
                filled += 1

    return filled


def get_grand_column_index(column_pool_keys: list[str]) -> int | None:
    for col_index, pool_key in enumerate(column_pool_keys):
        if pool_key in {"pool_5a", "pool_5b", "pool_5c"}:
            return col_index
    return None


def play_yin_yang_feature(
    bet: float,
    trigger_positions: list[tuple[int, int]],
    hit_chance: float = 0.06,
) -> YinYangFeatureResult:
    grid = create_empty_grid()

    for row_index, col_index in trigger_positions:
        grid[row_index][col_index] = get_random_yin_value(bet)

    selected_table_key = choose_prize_table_key()
    column_pool_keys = choose_column_pool_keys()
    grand_column_index = get_grand_column_index(column_pool_keys)

    column_step_indexes = [0, 0, 0, 0, 0]
    start_grid_values = copy_grid(grid)
    start_column_values = build_column_display_values(
        bet,
        selected_table_key,
        column_pool_keys,
        column_step_indexes,
    )

    spins_left = 3
    spins: list[YinYangFeatureSpin] = []

    while spins_left > 0:
        new_positions: list[tuple[int, int]] = []

        for row_index in range(ROWS):
            for col_index in range(REELS):
                if grid[row_index][col_index] is None:
                    current_hit_chance = hit_chance

                    if (
                        grand_column_index is not None
                        and col_index == grand_column_index
                    ):
                        current_hit_chance *= GRAND_COLUMN_HIT_CHANCE_MULTIPLIER

                    if random.random() < current_hit_chance:
                        grid[row_index][col_index] = get_random_yin_value(bet)
                        new_positions.append((row_index, col_index))

        completed_columns = get_completed_columns(grid)
        grand_activated = False

        if new_positions:
            spins_left = 3

            previous_display_values = build_column_display_values(
                bet,
                selected_table_key,
                column_pool_keys,
                column_step_indexes,
            )

            column_step_indexes = advance_column_steps(
                column_step_indexes,
                completed_columns,
                selected_table_key,
                column_pool_keys,
            )

            current_display_values = build_column_display_values(
                bet,
                selected_table_key,
                column_pool_keys,
                column_step_indexes,
            )

            if (
                grand_column_index is not None
                and previous_display_values[grand_column_index] != "GRAND"
                and current_display_values[grand_column_index] == "GRAND"
            ):
                grand_activated = True
        else:
            spins_left -= 1

        spins.append(
            YinYangFeatureSpin(
                grid_values=copy_grid(grid),
                column_values=build_column_display_values(
                    bet,
                    selected_table_key,
                    column_pool_keys,
                    column_step_indexes,
                ),
                new_positions=new_positions.copy(),
                spins_left_after=spins_left,
                completed_columns=completed_columns.copy(),
                grand_column_index=grand_column_index,
                grand_activated=grand_activated,
            )
        )

    completed_columns = get_completed_columns(grid)
    symbol_total = calculate_symbol_total(grid)

    final_column_values = build_column_display_values(
        bet,
        selected_table_key,
        column_pool_keys,
        column_step_indexes,
    )

    column_bonus_total = 0.0
    table = YIN_YANG_PRIZE_TABLES[selected_table_key]

    for col_index in completed_columns:
        pool_key = column_pool_keys[col_index]
        step_index = column_step_indexes[col_index]
        raw_value = table[pool_key][step_index]

        if raw_value == "Grand":
            column_bonus_total += JACKPOT_VALUES["grand"]
        else:
            column_bonus_total += round(bet * raw_value, 2)

    column_bonus_total = round(column_bonus_total, 2)
    total_win = round(symbol_total + column_bonus_total, 2)

    return YinYangFeatureResult(
        trigger_positions=trigger_positions.copy(),
        start_grid_values=start_grid_values,
        start_column_values=start_column_values,
        spins=spins,
        final_grid_values=copy_grid(grid),
        final_column_values=final_column_values,
        completed_columns=completed_columns,
        grand_column_index=grand_column_index,
        symbol_total=symbol_total,
        column_bonus_total=column_bonus_total,
        total_win=total_win,
        selected_table_key=selected_table_key,
        column_pool_keys=column_pool_keys,
        column_step_indexes=column_step_indexes.copy(),
    )
