from symbols import BULL, COIN, DRUM, INGOT, LANTERN, YIN_YANG, Symbol


def build_grid(middle_row: list[Symbol]) -> list[list[Symbol]]:
    top_row = [DRUM, INGOT, LANTERN, COIN, DRUM]
    bottom_row = [INGOT, DRUM, COIN, LANTERN, INGOT]
    return [top_row, middle_row, bottom_row]


TEST_CASES = [
    {
        "name": "3 gleiche BULL",
        "grid": build_grid([BULL, BULL, BULL, DRUM, COIN]),
        "expected_win": 200,
    },
    {
        "name": "4 gleiche BULL mit WILD",
        "grid": build_grid([BULL, YIN_YANG, BULL, BULL, INGOT]),
        "expected_win": 500,
    },
    {
        "name": "5 gleiche LANTERN mit 2 WILD am Anfang",
        "grid": build_grid([YIN_YANG, YIN_YANG, LANTERN, LANTERN, LANTERN]),
        "expected_win": 400,
    },
    {
        "name": "Kein Gewinn wegen Unterbrechung",
        "grid": build_grid([BULL, BULL, DRUM, BULL, BULL]),
        "expected_win": 0,
    },
    {
        "name": "Scatter am Anfang zahlt nicht auf Linie",
        "grid": build_grid([COIN, COIN, COIN, COIN, COIN]),
        "expected_win": 0,
    },
    {
        "name": "Scatter an zweiter Position",
        "grid": build_grid([BULL, COIN, BULL, BULL, COIN]),
        "expected_win": 0,
    },
    {
        "name": "Nur 2 gleiche Symbole",
        "grid": build_grid([LANTERN, LANTERN, DRUM, COIN, INGOT]),
        "expected_win": 0,
    },
]