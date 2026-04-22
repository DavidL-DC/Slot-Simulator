from dataclasses import dataclass
import random


ROWS = 3
REELS = 5

GRAND_COLUMN_HIT_CHANCE_MULTIPLIER = 0.15


@dataclass
class YinYangFeatureSpin:
    grid_values: list[list[int | None]]
    column_values: list[int]
    new_positions: list[tuple[int, int]]
    spins_left_after: int
    completed_columns: list[int]
    grand_column_index: int | None
    grand_activated: bool


@dataclass
class YinYangFeatureResult:
    trigger_positions: list[tuple[int, int]]
    start_grid_values: list[list[int | None]]
    start_column_values: list[int]
    spins: list[YinYangFeatureSpin]
    final_grid_values: list[list[int | None]]
    final_column_values: list[int]
    completed_columns: list[int]
    grand_column_index: int | None
    symbol_total: int
    column_bonus_total: int
    total_win: int


def copy_grid(grid: list[list[int | None]]) -> list[list[int | None]]:
    return [row.copy() for row in grid]


def create_empty_grid() -> list[list[int | None]]:
    return [[None for _ in range(REELS)] for _ in range(ROWS)]


def get_random_yin_value(bet: int) -> int:
    multiplier = random.choice(
        [
            1,
            1,
            1,
            2,
            2,
            2,
            2,
            3,
            3,
            4,
        ]
    )
    return multiplier * bet


def get_random_column_multiplier() -> int:
    return random.choice(
        [
            1,
            1,
            2,
            2,
            2,
            3,
            3,
            3,
            4,
        ]
    )


def create_initial_column_values(bet: int) -> list[int]:
    return [get_random_column_multiplier() * bet for _ in range(REELS)]


def get_completed_columns(grid: list[list[int | None]]) -> list[int]:
    completed_columns: list[int] = []

    for col_index in range(REELS):
        if all(grid[row_index][col_index] is not None for row_index in range(ROWS)):
            completed_columns.append(col_index)

    return completed_columns


def get_random_column_increase_factor() -> float:
    return random.choice([1.25, 1.5, 1.75, 2.0])


def increase_column_values(
    column_values: list[int],
    completed_columns: list[int],
) -> list[int]:
    new_values: list[int] = []
    factor = get_random_column_increase_factor()

    for col_index, value in enumerate(column_values):
        if col_index in completed_columns:
            new_values.append(value)
        else:
            new_value = int(round(value * factor))
            new_values.append(new_value)

    return new_values


def calculate_symbol_total(grid: list[list[int | None]]) -> int:
    total = 0

    for row in grid:
        for value in row:
            if value is not None:
                total += value

    return total


def count_filled_positions(grid: list[list[int | None]]) -> int:
    filled = 0

    for row in grid:
        for value in row:
            if value is not None:
                filled += 1

    return filled


def maybe_activate_grand(
    grid: list[list[int | None]],
    current_grand_column_index: int | None,
) -> int | None:
    if current_grand_column_index is not None:
        return current_grand_column_index

    filled_count = count_filled_positions(grid)

    if filled_count < 10:
        return None

    completed_columns = get_completed_columns(grid)
    available_columns = [
        col_index for col_index in range(REELS) if col_index not in completed_columns
    ]

    if not available_columns:
        return None

    return random.choice(available_columns)


def play_yin_yang_feature(
    bet: int,
    trigger_positions: list[tuple[int, int]],
    hit_chance: float = 0.05,
) -> YinYangFeatureResult:
    grid = create_empty_grid()

    for row_index, col_index in trigger_positions:
        grid[row_index][col_index] = get_random_yin_value(bet)

    start_grid_values = copy_grid(grid)
    column_values = create_initial_column_values(bet)
    start_column_values = column_values.copy()

    spins_left = 3
    spins: list[YinYangFeatureSpin] = []
    grand_column_index: int | None = None

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

            column_values = increase_column_values(column_values, completed_columns)

            previous_grand = grand_column_index
            grand_column_index = maybe_activate_grand(grid, grand_column_index)
            grand_activated = previous_grand is None and grand_column_index is not None
        else:
            spins_left -= 1

        spins.append(
            YinYangFeatureSpin(
                grid_values=copy_grid(grid),
                column_values=column_values.copy(),
                new_positions=new_positions.copy(),
                spins_left_after=spins_left,
                completed_columns=completed_columns.copy(),
                grand_column_index=grand_column_index,
                grand_activated=grand_activated,
            )
        )

    completed_columns = get_completed_columns(grid)
    symbol_total = calculate_symbol_total(grid)

    column_bonus_total = 0
    for col_index in completed_columns:
        if grand_column_index == col_index:
            column_bonus_total += 10000
        else:
            column_bonus_total += column_values[col_index]

    total_win = symbol_total + column_bonus_total

    return YinYangFeatureResult(
        trigger_positions=trigger_positions.copy(),
        start_grid_values=start_grid_values,
        start_column_values=start_column_values,
        spins=spins,
        final_grid_values=copy_grid(grid),
        final_column_values=column_values.copy(),
        completed_columns=completed_columns,
        grand_column_index=grand_column_index,
        symbol_total=symbol_total,
        column_bonus_total=column_bonus_total,
        total_win=total_win,
    )
