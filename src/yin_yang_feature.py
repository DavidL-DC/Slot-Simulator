from dataclasses import dataclass
import random


ROWS = 3
REELS = 5


@dataclass
class YinYangFeatureSpin:
    grid_values: list[list[int | None]]
    column_values: list[int]
    new_positions: list[tuple[int, int]]
    spins_left_after: int


@dataclass
class YinYangFeatureResult:
    trigger_positions: list[tuple[int, int]]
    start_grid_values: list[list[int | None]]
    spins: list[YinYangFeatureSpin]
    final_grid_values: list[list[int | None]]
    final_column_values: list[int]
    completed_columns: list[int]
    symbol_total: int
    column_bonus_total: int
    total_win: int


def copy_grid(grid: list[list[int | None]]) -> list[list[int | None]]:
    return [row.copy() for row in grid]


def create_empty_grid() -> list[list[int | None]]:
    return [[None for _ in range(REELS)] for _ in range(ROWS)]


def get_random_initial_value(bet: int) -> int:
    multiplier = random.choice([1, 1, 1, 2, 2, 3])
    return multiplier * bet


def get_random_respin_value(bet: int) -> int:
    multiplier = random.choice([1, 1, 2, 2, 3])
    return multiplier * bet


def increase_column_values(column_values: list[int]) -> list[int]:
    increases = [150, 150, 50, 100, 150]
    return [value + increase for value, increase in zip(column_values, increases)]


def get_completed_columns(grid: list[list[int | None]]) -> list[int]:
    completed_columns: list[int] = []

    for col_index in range(REELS):
        if all(grid[row_index][col_index] is not None for row_index in range(ROWS)):
            completed_columns.append(col_index)

    return completed_columns


def calculate_symbol_total(grid: list[list[int | None]]) -> int:
    total = 0

    for row in grid:
        for value in row:
            if value is not None:
                total += value

    return total


def play_yin_yang_feature(
    bet: int,
    trigger_positions: list[tuple[int, int]],
    hit_chance: float = 0.05,
) -> YinYangFeatureResult:
    grid = create_empty_grid()

    for row_index, col_index in trigger_positions:
        grid[row_index][col_index] = get_random_initial_value(bet)

    start_grid_values = copy_grid(grid)
    column_values = [250, 100, 100, 50, 150]

    spins_left = 3
    spins: list[YinYangFeatureSpin] = []

    while spins_left > 0:
        new_positions: list[tuple[int, int]] = []

        for row_index in range(ROWS):
            for col_index in range(REELS):
                if grid[row_index][col_index] is None:
                    if random.random() < hit_chance:
                        grid[row_index][col_index] = get_random_respin_value(bet)
                        new_positions.append((row_index, col_index))

        if new_positions:
            spins_left = 3

            for _ in new_positions:
                column_values = increase_column_values(column_values)
        else:
            spins_left -= 1

        spins.append(
            YinYangFeatureSpin(
                grid_values=copy_grid(grid),
                column_values=column_values.copy(),
                new_positions=new_positions.copy(),
                spins_left_after=spins_left,
            )
        )

    completed_columns = get_completed_columns(grid)
    symbol_total = calculate_symbol_total(grid)
    column_bonus_total = sum(
        column_values[col_index] for col_index in completed_columns
    )
    total_win = symbol_total + column_bonus_total

    return YinYangFeatureResult(
        trigger_positions=trigger_positions.copy(),
        start_grid_values=start_grid_values,
        spins=spins,
        final_grid_values=copy_grid(grid),
        final_column_values=column_values.copy(),
        completed_columns=completed_columns,
        symbol_total=symbol_total,
        column_bonus_total=column_bonus_total,
        total_win=total_win,
    )
