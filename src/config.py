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
MIN_BET = 0.5

AVAILABLE_DENOMS = [0.01, 0.02, 0.05, 0.10, 1.00]
AVAILABLE_CREDITS = [50, 100, 150, 250, 500]

DEFAULT_DENOM = 0.01
DEFAULT_CREDITS_BET = 100

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

INSTANT_WIN_CREDIT_MULTIPLIERS = [2, 3, 4, 5, 8, 10, 20, 50, 100, 200]

JACKPOT_VALUES = {
    "mini": 10,
    "minor": 50,
    "maxi": 500,  # Progressive
    "major": 1000,  # Progressive
    "grand": 10000,  # Progressive
}

YIN_YANG_VALUE_MULTIPLIERS = [1, 2, 3, 5, 10, 15, 20, 25, 50]

YIN_YANG_PRIZE_TABLES = {
    "table_1": {
        "pool_1": [2, 5, 7, 10, 12, 18, 20, 22, 25],
        "pool_2": [3, 6, 8, 12, 18, 22, 25, 30, 50, 100],
        "pool_3": [1, 3, 5, 8, 10, 15, 22, 25, 30, 50],
        "pool_4": [5, 8, 10, 15, 20, 25, 30, 50, 75, 125],
        "pool_5a": [2, 3, 5, 7, "Grand"],
        "pool_5b": [3, 7, 10, 12, 15, "Grand"],
        "pool_5c": [5, 10, 15, 25, 50, 100, "Grand"],
    },
    "table_2": {
        "pool_1": [5, 10, 15, 20, 25],
        "pool_2": [6, 12, 18, 30, 50, 80, 100],
        "pool_3": [3, 8, 10, 15, 30, 50],
        "pool_4": [8, 15, 20, 40, 80, 125, 150],
        "pool_5a": [5, 10, 15, 25, "Grand"],
        "pool_5b": [5, 10, 15, 25, 50, "Grand"],
        "pool_5c": [5, 10, 15, 25, 50, 100, "Grand"],
    },
}

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
BASE_REEL_STRIPS_50 = [
    [
        NINE,
        TEN,
        JACK,
        NINE,
        QUEEN,
        TEN,
        KING,
        NINE,
        GONG,
        TEN,
        JACK,
        NINE,
        HOUSE,
        TEN,
        QUEEN,
        NINE,
        LANTERN,
        TEN,
        JACK,
        NINE,
        VASE,
        TEN,
        KING,
        NINE,
        TEN,
        JACK,
        QUEEN,
        TEN,
        NINE,
        CREDIT,
        TEN,
        NINE,
        COIN,
        YIN_YANG,
    ],
    [
        TEN,
        JACK,
        NINE,
        QUEEN,
        TEN,
        KING,
        NINE,
        JACK,
        GONG,
        TEN,
        NINE,
        HOUSE,
        YIN_YANG,
        QUEEN,
        TEN,
        BULL,
        NINE,
        LANTERN,
        JACK,
        TEN,
        NINE,
        KING,
        COIN,
        TEN,
        VASE,
        NINE,
        JACK,
        BULL,
        TEN,
        QUEEN,
        CREDIT,
        NINE,
        TEN,
    ],
    [
        JACK,
        NINE,
        TEN,
        QUEEN,
        KING,
        NINE,
        JACK,
        TEN,
        GONG,
        NINE,
        HOUSE,
        TEN,
        QUEEN,
        JACK,
        BULL,
        NINE,
        COIN,
        CREDIT,
        TEN,
        LANTERN,
        NINE,
        VASE,
        JACK,
        TEN,
        BULL,
        NINE,
        KING,
        TEN,
        QUEEN,
        JACK,
        NINE,
        TEN,
        YIN_YANG,
    ],
    [
        QUEEN,
        TEN,
        JACK,
        NINE,
        KING,
        TEN,
        QUEEN,
        JACK,
        GONG,
        NINE,
        HOUSE,
        TEN,
        BULL,
        JACK,
        YIN_YANG,
        NINE,
        LANTERN,
        TEN,
        QUEEN,
        NINE,
        VASE,
        JACK,
        COIN,
        TEN,
        KING,
        NINE,
        BULL,
        JACK,
        TEN,
        QUEEN,
        CREDIT,
        NINE,
        TEN,
    ],
    [
        KING,
        NINE,
        TEN,
        JACK,
        QUEEN,
        NINE,
        KING,
        TEN,
        GONG,
        JACK,
        HOUSE,
        NINE,
        BULL,
        TEN,
        QUEEN,
        JACK,
        LANTERN,
        NINE,
        VASE,
        TEN,
        COIN,
        JACK,
        NINE,
        YIN_YANG,
        KING,
        TEN,
        BULL,
        QUEEN,
        JACK,
        NINE,
        TEN,
        COLLECTOR,
    ],
]

BASE_REEL_STRIPS_100 = [
    BASE_REEL_STRIPS_50[0],
    BASE_REEL_STRIPS_50[1],
    BASE_REEL_STRIPS_50[2],
    BASE_REEL_STRIPS_50[3],
    BASE_REEL_STRIPS_50[4],
]

BASE_REEL_STRIPS_150 = [
    BASE_REEL_STRIPS_50[0],
    BASE_REEL_STRIPS_50[1] + [CREDIT],
    BASE_REEL_STRIPS_50[2],
    BASE_REEL_STRIPS_50[3],
    BASE_REEL_STRIPS_50[4],
]

BASE_REEL_STRIPS_250 = [
    BASE_REEL_STRIPS_50[0],
    BASE_REEL_STRIPS_50[1] + [CREDIT],
    BASE_REEL_STRIPS_50[2],
    BASE_REEL_STRIPS_50[3],
    BASE_REEL_STRIPS_50[4] + [COLLECTOR],
]

BASE_REEL_STRIPS_500 = [
    BASE_REEL_STRIPS_50[0],
    BASE_REEL_STRIPS_50[1] + [CREDIT],
    BASE_REEL_STRIPS_50[2] + [YIN_YANG],
    BASE_REEL_STRIPS_50[3],
    BASE_REEL_STRIPS_50[4] + [COLLECTOR],
]

BASE_REEL_SETS_BY_CREDITS = {
    50: BASE_REEL_STRIPS_50,
    100: BASE_REEL_STRIPS_100,
    150: BASE_REEL_STRIPS_150,
    250: BASE_REEL_STRIPS_250,
    500: BASE_REEL_STRIPS_500,
}

FREE_SPIN_REEL_STRIPS = [
    [
        NINE,
        TEN,
        JACK,
        QUEEN,
        KING,
        NINE,
        TEN,
        JACK,
        GONG,
        NINE,
        HOUSE,
        TEN,
        QUEEN,
        JACK,
        LANTERN,
        NINE,
        VASE,
        TEN,
        JACK,
        YIN_YANG,
    ],
    [
        TEN,
        JACK,
        NINE,
        QUEEN,
        KING,
        TEN,
        JACK,
        NINE,
        GONG,
        HOUSE,
        TEN,
        BULL,
        QUEEN,
        JACK,
        LANTERN,
        NINE,
        VASE,
        TEN,
        YIN_YANG,
    ],
    [
        JACK,
        NINE,
        TEN,
        QUEEN,
        KING,
        JACK,
        TEN,
        NINE,
        GONG,
        HOUSE,
        BULL,
        TEN,
        QUEEN,
        JACK,
        LANTERN,
        VASE,
        TEN,
        BULL,
        YIN_YANG,
    ],
    [
        QUEEN,
        TEN,
        JACK,
        NINE,
        KING,
        QUEEN,
        TEN,
        JACK,
        GONG,
        HOUSE,
        BULL,
        NINE,
        LANTERN,
        TEN,
        VASE,
        JACK,
        QUEEN,
        YIN_YANG,
    ],
    [
        KING,
        NINE,
        TEN,
        JACK,
        QUEEN,
        KING,
        TEN,
        JACK,
        GONG,
        HOUSE,
        BULL,
        NINE,
        LANTERN,
        TEN,
        VASE,
        JACK,
        QUEEN,
        BULL,
    ],
]
