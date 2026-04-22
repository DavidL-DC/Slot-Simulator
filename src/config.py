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

START_BALANCE = 100
DEFAULT_BET = 1

PAYLINES = [
    [1, 1, 1, 1, 1],  # 1
    [0, 0, 0, 0, 0],  # 2
    [2, 2, 2, 2, 2],  # 3
    [0, 1, 2, 1, 0],  # 4
    [2, 1, 0, 1, 2],  # 5
    [0, 0, 1, 0, 0],  # 6
    [2, 2, 1, 2, 2],  # 7
    [1, 2, 2, 2, 1],  # 8
    [1, 0, 0, 0, 1],  # 9
    [0, 1, 1, 1, 0],  # 10
    [2, 1, 1, 1, 2],  # 11
    [0, 1, 0, 1, 0],  # 12
    [2, 1, 2, 1, 2],  # 13
    [1, 0, 1, 0, 1],  # 14
    [1, 2, 1, 2, 1],  # 15
    [1, 1, 0, 1, 1],  # 16
    [1, 1, 2, 1, 1],  # 17
    [0, 2, 0, 2, 0],  # 18
    [2, 0, 2, 0, 2],  # 19
    [1, 0, 2, 0, 1],  # 20
    [1, 2, 0, 2, 1],  # 21
    [0, 0, 2, 0, 0],  # 22
    [2, 2, 0, 2, 2],  # 23
    [0, 2, 2, 2, 0],  # 24
    [2, 0, 0, 0, 2],  # 25
    [0, 1, 2, 2, 2],  # 26
    [2, 1, 0, 0, 0],  # 27
    [0, 1, 1, 1, 2],  # 28
    [0, 0, 1, 2, 2],  # 29
    [2, 2, 1, 0, 0],  # 30
    [0, 2, 1, 2, 0],  # 31
    [2, 0, 1, 0, 2],  # 32
    [0, 2, 1, 0, 2],  # 33
    [1, 0, 1, 2, 1],  # 34
    [1, 2, 1, 0, 1],  # 35
    [2, 0, 1, 2, 0],  # 36
    [1, 0, 0, 0, 0],  # 37
    [1, 2, 2, 2, 2],  # 38
    [0, 2, 2, 2, 2],  # 39
    [2, 0, 0, 0, 0],  # 40
    [0, 0, 0, 0, 1],  # 41
    [2, 2, 2, 2, 1],  # 42
    [0, 1, 1, 1, 1],  # 43
    [2, 1, 1, 1, 1],  # 44
    [2, 2, 2, 2, 0],  # 45
    [0, 0, 0, 0, 2],  # 46
    [1, 1, 1, 1, 0],  # 47
    [1, 1, 1, 1, 2],  # 48
    [2, 2, 2, 1, 0],  # 49
    [2, 1, 1, 1, 0],  # 50
]

FREE_SPIN_PAYOUTS = {
    "nine": {3: 5, 4: 8, 5: 25},
    "ten": {3: 5, 4: 8, 5: 30},
    "jack": {3: 5, 4: 8, 5: 30},
    "queen": {3: 5, 4: 8, 5: 30},
    "king": {3: 5, 4: 10, 5: 50},
    "gong": {3: 5, 4: 10, 5: 50},
    "lantern": {3: 5, 4: 10, 5: 50},
    "vase": {3: 5, 4: 10, 5: 50},
    "house": {3: 5, 4: 15, 5: 75},
}

SCATTER_PAYOUTS = {
    3: 1,
    4: 10,
    5: 100,
}

FREE_SPINS_AWARDED = {
    3: 8,
    4: 8,
    5: 8,
}

YIN_YANG_FEATURE_PAYOUTS = {
    3: (10, 30),
    4: (25, 60),
    5: (50, 120),
}

REEL_STRIPS = [
    [
        NINE,
        TEN,
        JACK,
        QUEEN,
        KING,
        GONG,
        NINE,
        TEN,
        JACK,
        HOUSE,
        QUEEN,
        TEN,
        JACK,
        LANTERN,
        NINE,
        VASE,
        TEN,
        JACK,
        BULL,
        CREDIT,
        COIN,
    ],
    [
        TEN,
        JACK,
        QUEEN,
        KING,
        NINE,
        GONG,
        TEN,
        JACK,
        HOUSE,
        COIN,
        QUEEN,
        KING,
        TEN,
        JACK,
        LANTERN,
        QUEEN,
        VASE,
        TEN,
        JACK,
        BULL,
        CREDIT,
        YIN_YANG,
    ],
    [
        JACK,
        QUEEN,
        KING,
        NINE,
        TEN,
        JACK,
        GONG,
        NINE,
        TEN,
        HOUSE,
        COIN,
        JACK,
        QUEEN,
        KING,
        NINE,
        TEN,
        LANTERN,
        JACK,
        QUEEN,
        VASE,
        TEN,
        JACK,
        BULL,
        CREDIT,
        COIN,
        YIN_YANG,
        NINE,
        TEN,
    ],
    [
        QUEEN,
        KING,
        NINE,
        TEN,
        JACK,
        GONG,
        NINE,
        TEN,
        HOUSE,
        JACK,
        QUEEN,
        KING,
        NINE,
        TEN,
        JACK,
        LANTERN,
        QUEEN,
        VASE,
        TEN,
        JACK,
        NINE,
        BULL,
        CREDIT,
        YIN_YANG,
        TEN,
        JACK,
        QUEEN,
    ],
    [
        KING,
        NINE,
        TEN,
        JACK,
        QUEEN,
        GONG,
        NINE,
        TEN,
        HOUSE,
        JACK,
        QUEEN,
        KING,
        NINE,
        TEN,
        JACK,
        LANTERN,
        QUEEN,
        VASE,
        TEN,
        JACK,
        NINE,
        BULL,
        COIN,
        COLLECTOR,
        TEN,
        JACK,
        QUEEN,
    ],
]

FREE_SPIN_REEL_STRIPS = [
    [
        NINE,
        TEN,
        JACK,
        QUEEN,
        KING,
        GONG,
        NINE,
        TEN,
        JACK,
        HOUSE,
        QUEEN,
        TEN,
        JACK,
        LANTERN,
        NINE,
        VASE,
        TEN,
        JACK,
        YIN_YANG,
        NINE,
        TEN,
    ],
    [
        TEN,
        JACK,
        QUEEN,
        KING,
        NINE,
        GONG,
        TEN,
        JACK,
        HOUSE,
        BULL,
        QUEEN,
        KING,
        TEN,
        JACK,
        LANTERN,
        QUEEN,
        VASE,
        TEN,
        JACK,
        BULL,
        YIN_YANG,
        NINE,
    ],
    [
        JACK,
        QUEEN,
        KING,
        NINE,
        TEN,
        JACK,
        GONG,
        NINE,
        TEN,
        HOUSE,
        BULL,
        JACK,
        QUEEN,
        KING,
        NINE,
        TEN,
        LANTERN,
        JACK,
        QUEEN,
        VASE,
        TEN,
        JACK,
        BULL,
        YIN_YANG,
        NINE,
        TEN,
    ],
    [
        QUEEN,
        KING,
        NINE,
        TEN,
        JACK,
        GONG,
        NINE,
        TEN,
        HOUSE,
        JACK,
        QUEEN,
        KING,
        NINE,
        TEN,
        JACK,
        LANTERN,
        QUEEN,
        VASE,
        TEN,
        JACK,
        BULL,
        BULL,
        YIN_YANG,
        TEN,
        JACK,
        QUEEN,
    ],
    [
        KING,
        NINE,
        TEN,
        JACK,
        QUEEN,
        GONG,
        NINE,
        TEN,
        HOUSE,
        JACK,
        QUEEN,
        KING,
        NINE,
        TEN,
        JACK,
        LANTERN,
        QUEEN,
        VASE,
        TEN,
        JACK,
        NINE,
        BULL,
        BULL,
        TEN,
        JACK,
        QUEEN,
    ],
]
