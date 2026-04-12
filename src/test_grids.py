from symbols import BULL, COIN, GONG, KING, LANTERN, YIN_YANG, Symbol


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
            [GONG, KING, LANTERN, COIN, GONG],
            [BULL, BULL, BULL, GONG, COIN],
            [KING, GONG, COIN, LANTERN, KING],
        ),
        "expected_win": 200,
    },
    {
        "name": "4 gleiche BULL mit WILD in mittlerer Reihe",
        "grid": build_grid(
            [GONG, KING, LANTERN, COIN, GONG],
            [BULL, YIN_YANG, BULL, BULL, KING],
            [KING, GONG, COIN, LANTERN, KING],
        ),
        "expected_win": 500,
    },
    {
        "name": "5 gleiche LANTERN mit 2 WILD am Anfang in mittlerer Reihe",
        "grid": build_grid(
            [GONG, KING, LANTERN, COIN, GONG],
            [YIN_YANG, YIN_YANG, LANTERN, LANTERN, LANTERN],
            [KING, GONG, COIN, LANTERN, KING],
        ),
        "expected_win": 400,
    },
    {
        "name": "Kein Gewinn wegen Unterbrechung in mittlerer Reihe",
        "grid": build_grid(
            [GONG, KING, LANTERN, COIN, GONG],
            [BULL, BULL, GONG, BULL, BULL],
            [KING, GONG, COIN, LANTERN, KING],
        ),
        "expected_win": 0,
    },
    {
        "name": "Scatter am Anfang zahlt nicht auf mittlerer Linie",
        "grid": build_grid(
            [GONG, KING, LANTERN, COIN, GONG],
            [COIN, COIN, COIN, COIN, COIN],
            [KING, GONG, COIN, LANTERN, KING],
        ),
        "expected_win": 0,
    },
    {
        "name": "Nur 2 gleiche Symbole in mittlerer Reihe",
        "grid": build_grid(
            [GONG, KING, LANTERN, COIN, GONG],
            [LANTERN, LANTERN, GONG, COIN, KING],
            [KING, GONG, COIN, LANTERN, KING],
        ),
        "expected_win": 0,
    },
]


PAYLINE_TEST_CASES = [
    {
        "name": "Obere Reihe zahlt 3x BULL",
        "grid": build_grid(
            [BULL, BULL, BULL, GONG, COIN],
            [GONG, KING, LANTERN, COIN, GONG],
            [KING, GONG, COIN, LANTERN, KING],
        ),
        "payline": [0, 0, 0, 0, 0],
        "expected_win": 200,
    },
    {
        "name": "Untere Reihe zahlt 4x GONG mit WILD",
        "grid": build_grid(
            [KING, GONG, COIN, LANTERN, KING],
            [GONG, KING, LANTERN, COIN, GONG],
            [GONG, YIN_YANG, GONG, GONG, COIN],
        ),
        "payline": [2, 2, 2, 2, 2],
        "expected_win": 160,
    },
    {
        "name": "V-Form zahlt 5x LANTERN",
        "grid": build_grid(
            [LANTERN, GONG, COIN, KING, LANTERN],
            [GONG, LANTERN, GONG, LANTERN, GONG],
            [KING, COIN, LANTERN, COIN, KING],
        ),
        "payline": [0, 1, 2, 1, 0],
        "expected_win": 400,
    },
    {
        "name": "Umgedrehte V-Form zahlt 5x BULL mit WILD",
        "grid": build_grid(
            [GONG, COIN, BULL, KING, GONG],
            [COIN, BULL, GONG, BULL, COIN],
            [BULL, KING, GONG, LANTERN, YIN_YANG],
        ),
        "payline": [2, 1, 0, 1, 2],
        "expected_win": 1000,
    },
    {
        "name": "Scatter auf Linie unterbricht",
        "grid": build_grid(
            [BULL, BULL, COIN, BULL, BULL],
            [GONG, KING, LANTERN, COIN, GONG],
            [KING, GONG, COIN, LANTERN, KING],
        ),
        "payline": [0, 0, 0, 0, 0],
        "expected_win": 0,
    },
]


ALL_PAYLINES_TEST_CASES = [
    {
        "name": "Zwei gewinnende Reihen gleichzeitig",
        "grid": build_grid(
            [BULL, BULL, BULL, GONG, COIN],
            [LANTERN, LANTERN, LANTERN, LANTERN, GONG],
            [KING, GONG, COIN, LANTERN, KING],
        ),
        "expected_total_win": 200 + 200,
    },
    {
        "name": "Nur V-Form gewinnt",
        "grid": build_grid(
            [LANTERN, GONG, COIN, KING, LANTERN],
            [GONG, LANTERN, GONG, LANTERN, GONG],
            [KING, COIN, LANTERN, COIN, KING],
        ),
        "expected_total_win": 400,
    },
    {
        "name": "Keine Linie gewinnt",
        "grid": build_grid(
            [BULL, GONG, COIN, KING, LANTERN],
            [GONG, KING, LANTERN, COIN, GONG],
            [KING, COIN, GONG, LANTERN, BULL],
        ),
        "expected_total_win": 0,
    },
]

SCATTER_TEST_CASES = [
    {
        "name": "3 Scatter irgendwo im Grid",
        "grid": build_grid(
            [COIN, BULL, GONG, KING, LANTERN],
            [GONG, COIN, LANTERN, BULL, GONG],
            [KING, GONG, COIN, LANTERN, KING],
        ),
        "expected_scatter_count": 3,
        "expected_scatter_win": 50,
        "expected_free_spins": 5,
    },
    {
        "name": "4 Scatter irgendwo im Grid",
        "grid": build_grid(
            [COIN, BULL, GONG, COIN, LANTERN],
            [GONG, COIN, LANTERN, BULL, GONG],
            [KING, GONG, COIN, LANTERN, KING],
        ),
        "expected_scatter_count": 4,
        "expected_scatter_win": 200,
        "expected_free_spins": 8,
    },
    {
        "name": "2 Scatter geben noch keinen Gewinn",
        "grid": build_grid(
            [COIN, BULL, GONG, KING, LANTERN],
            [GONG, COIN, LANTERN, BULL, GONG],
            [KING, GONG, BULL, LANTERN, KING],
        ),
        "expected_scatter_count": 2,
        "expected_scatter_win": 0,
        "expected_free_spins": 0,
    },
]