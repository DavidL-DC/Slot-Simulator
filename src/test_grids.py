from symbols import BULL, COIN, DRUM, INGOT, LANTERN, YIN_YANG, Symbol


def build_grid(
    top_row: list[Symbol],
    middle_row: list[Symbol],
    bottom_row: list[Symbol],
) -> list[list[Symbol]]:
    return [top_row, middle_row, bottom_row]


MIDDLE_ROW_TEST_CASES = [
    {
        "name": "3 gleiche BULL in mittlerer Reihe",
        "grid": build_grid(
            [DRUM, INGOT, LANTERN, COIN, DRUM],
            [BULL, BULL, BULL, DRUM, COIN],
            [INGOT, DRUM, COIN, LANTERN, INGOT],
        ),
        "expected_win": 200,
    },
    {
        "name": "4 gleiche BULL mit WILD in mittlerer Reihe",
        "grid": build_grid(
            [DRUM, INGOT, LANTERN, COIN, DRUM],
            [BULL, YIN_YANG, BULL, BULL, INGOT],
            [INGOT, DRUM, COIN, LANTERN, INGOT],
        ),
        "expected_win": 500,
    },
    {
        "name": "5 gleiche LANTERN mit 2 WILD am Anfang in mittlerer Reihe",
        "grid": build_grid(
            [DRUM, INGOT, LANTERN, COIN, DRUM],
            [YIN_YANG, YIN_YANG, LANTERN, LANTERN, LANTERN],
            [INGOT, DRUM, COIN, LANTERN, INGOT],
        ),
        "expected_win": 400,
    },
    {
        "name": "Kein Gewinn wegen Unterbrechung in mittlerer Reihe",
        "grid": build_grid(
            [DRUM, INGOT, LANTERN, COIN, DRUM],
            [BULL, BULL, DRUM, BULL, BULL],
            [INGOT, DRUM, COIN, LANTERN, INGOT],
        ),
        "expected_win": 0,
    },
    {
        "name": "Scatter am Anfang zahlt nicht auf mittlerer Linie",
        "grid": build_grid(
            [DRUM, INGOT, LANTERN, COIN, DRUM],
            [COIN, COIN, COIN, COIN, COIN],
            [INGOT, DRUM, COIN, LANTERN, INGOT],
        ),
        "expected_win": 0,
    },
    {
        "name": "Nur 2 gleiche Symbole in mittlerer Reihe",
        "grid": build_grid(
            [DRUM, INGOT, LANTERN, COIN, DRUM],
            [LANTERN, LANTERN, DRUM, COIN, INGOT],
            [INGOT, DRUM, COIN, LANTERN, INGOT],
        ),
        "expected_win": 0,
    },
]


PAYLINE_TEST_CASES = [
    {
        "name": "Obere Reihe zahlt 3x BULL",
        "grid": build_grid(
            [BULL, BULL, BULL, DRUM, COIN],
            [DRUM, INGOT, LANTERN, COIN, DRUM],
            [INGOT, DRUM, COIN, LANTERN, INGOT],
        ),
        "payline": [0, 0, 0, 0, 0],
        "expected_win": 200,
    },
    {
        "name": "Untere Reihe zahlt 4x DRUM mit WILD",
        "grid": build_grid(
            [INGOT, DRUM, COIN, LANTERN, INGOT],
            [DRUM, INGOT, LANTERN, COIN, DRUM],
            [DRUM, YIN_YANG, DRUM, DRUM, COIN],
        ),
        "payline": [2, 2, 2, 2, 2],
        "expected_win": 160,
    },
    {
        "name": "V-Form zahlt 5x LANTERN",
        "grid": build_grid(
            [LANTERN, DRUM, COIN, INGOT, LANTERN],
            [DRUM, LANTERN, DRUM, LANTERN, DRUM],
            [INGOT, COIN, LANTERN, COIN, INGOT],
        ),
        "payline": [0, 1, 2, 1, 0],
        "expected_win": 400,
    },
    {
        "name": "Umgedrehte V-Form zahlt 5x BULL mit WILD",
        "grid": build_grid(
            [DRUM, COIN, BULL, INGOT, DRUM],
            [COIN, BULL, DRUM, BULL, COIN],
            [BULL, INGOT, DRUM, LANTERN, YIN_YANG],
        ),
        "payline": [2, 1, 0, 1, 2],
        "expected_win": 1000,
    },
    {
        "name": "Scatter auf Linie unterbricht",
        "grid": build_grid(
            [BULL, BULL, COIN, BULL, BULL],
            [DRUM, INGOT, LANTERN, COIN, DRUM],
            [INGOT, DRUM, COIN, LANTERN, INGOT],
        ),
        "payline": [0, 0, 0, 0, 0],
        "expected_win": 0,
    },
]


ALL_PAYLINES_TEST_CASES = [
    {
        "name": "Zwei gewinnende Reihen gleichzeitig",
        "grid": build_grid(
            [BULL, BULL, BULL, DRUM, COIN],
            [LANTERN, LANTERN, LANTERN, LANTERN, DRUM],
            [INGOT, DRUM, COIN, LANTERN, INGOT],
        ),
        "expected_total_win": 200 + 200,
    },
    {
        "name": "Nur V-Form gewinnt",
        "grid": build_grid(
            [LANTERN, DRUM, COIN, INGOT, LANTERN],
            [DRUM, LANTERN, DRUM, LANTERN, DRUM],
            [INGOT, COIN, LANTERN, COIN, INGOT],
        ),
        "expected_total_win": 400,
    },
    {
        "name": "Keine Linie gewinnt",
        "grid": build_grid(
            [BULL, DRUM, COIN, INGOT, LANTERN],
            [DRUM, INGOT, LANTERN, COIN, DRUM],
            [INGOT, COIN, DRUM, LANTERN, BULL],
        ),
        "expected_total_win": 0,
    },
]

SCATTER_TEST_CASES = [
    {
        "name": "3 Scatter irgendwo im Grid",
        "grid": build_grid(
            [COIN, BULL, DRUM, INGOT, LANTERN],
            [DRUM, COIN, LANTERN, BULL, DRUM],
            [INGOT, DRUM, COIN, LANTERN, INGOT],
        ),
        "expected_scatter_count": 3,
        "expected_scatter_win": 50,
        "expected_free_spins": 5,
    },
    {
        "name": "4 Scatter irgendwo im Grid",
        "grid": build_grid(
            [COIN, BULL, DRUM, COIN, LANTERN],
            [DRUM, COIN, LANTERN, BULL, DRUM],
            [INGOT, DRUM, COIN, LANTERN, INGOT],
        ),
        "expected_scatter_count": 4,
        "expected_scatter_win": 200,
        "expected_free_spins": 8,
    },
    {
        "name": "2 Scatter geben noch keinen Gewinn",
        "grid": build_grid(
            [COIN, BULL, DRUM, INGOT, LANTERN],
            [DRUM, COIN, LANTERN, BULL, DRUM],
            [INGOT, DRUM, BULL, LANTERN, INGOT],
        ),
        "expected_scatter_count": 2,
        "expected_scatter_win": 0,
        "expected_free_spins": 0,
    },
]