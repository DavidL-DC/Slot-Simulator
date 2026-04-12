from symbols import (
    BULL,
    COIN,
    COLLECTOR,
    CREDIT,
    GONG,
    HOUSE,
    JACK,
    KING,
    LANTERN,
    NINE,
    QUEEN,
    TEN,
    VASE,
    YIN_YANG,
)

ROWS = 3
REELS = 5

START_BALANCE = 1000
DEFAULT_BET = 10

PAYLINES = [
    [0, 0, 0, 0, 0],  # 1
    [1, 1, 1, 1, 1],  # 2
    [2, 2, 2, 2, 2],  # 3
    [0, 1, 2, 1, 0],  # 4
    [2, 1, 0, 1, 2],  # 5
    [0, 0, 1, 0, 0],  # 6
    [2, 2, 1, 2, 2],  # 7
    [1, 0, 0, 0, 1],  # 8
    [1, 2, 2, 2, 1],  # 9
    [0, 1, 1, 1, 0],  # 10
    [2, 1, 1, 1, 2],  # 11
    [1, 0, 1, 2, 1],  # 12
    [1, 2, 1, 0, 1],  # 13
    [0, 1, 0, 1, 0],  # 14
    [2, 1, 2, 1, 2],  # 15
    [0, 2, 0, 2, 0],  # 16
    [2, 0, 2, 0, 2],  # 17
    [1, 0, 2, 0, 1],  # 18
    [1, 2, 0, 2, 1],  # 19
    [0, 1, 2, 2, 1],  # 20
    [2, 1, 0, 0, 1],  # 21
    [0, 2, 1, 0, 2],  # 22
    [2, 0, 1, 2, 0],  # 23
    [1, 1, 0, 1, 1],  # 24
    [1, 1, 2, 1, 1],  # 25
]

SCATTER_PAYOUTS = {
    3: 2,
    4: 10,
    5: 50,
}

FREE_SPINS_AWARDED = {
    3: 8,
    4: 10,
    5: 12,
}

REEL_STRIPS = [
    [
        NINE, TEN, JACK, QUEEN, KING,
        NINE, TEN, JACK, QUEEN, KING,
        GONG, HOUSE, LANTERN, VASE,
        NINE, TEN, JACK, QUEEN,
        BULL,
        CREDIT,
        COIN,
        NINE, TEN, JACK,
    ],
    [
        NINE, TEN, JACK, QUEEN, KING,
        NINE, TEN, JACK, QUEEN, KING,
        GONG, HOUSE, LANTERN, VASE,
        NINE, TEN, JACK, QUEEN,
        BULL,
        CREDIT,
        YIN_YANG,
        NINE, TEN, JACK,
    ],
    [
        NINE, TEN, JACK, QUEEN, KING,
        NINE, TEN, JACK, QUEEN, KING,
        GONG, HOUSE, LANTERN, VASE,
        NINE, TEN, JACK, QUEEN,
        BULL,
        CREDIT,
        COIN,
        YIN_YANG,
        NINE, TEN, JACK,
    ],
    [
        NINE, TEN, JACK, QUEEN, KING,
        NINE, TEN, JACK, QUEEN, KING,
        GONG, HOUSE, LANTERN, VASE,
        NINE, TEN, JACK, QUEEN,
        BULL,
        CREDIT,
        YIN_YANG,
        NINE, TEN, JACK,
    ],
    [
        NINE, TEN, JACK, QUEEN, KING,
        NINE, TEN, JACK, QUEEN, KING,
        GONG, HOUSE, LANTERN, VASE,
        NINE, TEN, JACK, QUEEN,
        BULL,
        COIN,
        COLLECTOR,
        NINE, TEN, JACK,
    ],
]