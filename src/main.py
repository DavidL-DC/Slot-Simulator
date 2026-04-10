from config import DEFAULT_BET, REELS, ROWS, START_BALANCE
from slot_machine import evaluate_middle_row, print_grid, spin_reels
from symbols import ALL_SYMBOLS


def print_game_info() -> None:
    print("=== Slot Simulator ===")
    print(f"Walzen: {REELS}")
    print(f"Reihen: {ROWS}")
    print(f"Startguthaben: {START_BALANCE}")
    print(f"Standard-Einsatz: {DEFAULT_BET}")
    print()
    print("Symbole:")
    for symbol in ALL_SYMBOLS:
        flags = []
        if symbol.is_wild:
            flags.append("WILD")
        if symbol.is_scatter:
            flags.append("SCATTER")

        extra = f" ({', '.join(flags)})" if flags else ""
        print(f"- {symbol.display}: payouts={symbol.payouts}{extra}")


def main() -> None:
    print_game_info()
    print()

    grid = spin_reels()
    print_grid(grid)
    print()

    win = evaluate_middle_row(grid, DEFAULT_BET)
    print(f"Gewinn mittlere Reihe: {win}")


if __name__ == "__main__":
    main()