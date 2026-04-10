from config import DEFAULT_BET, REELS, ROWS, START_BALANCE
from slot_machine import print_grid, run_test_case, spin_reels
from symbols import ALL_SYMBOLS
from test_grids import TEST_CASES


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


def run_all_tests() -> None:
    print("=== TESTS ===")
    print()

    passed_tests = 0
    total_tests = len(TEST_CASES)

    for test_case in TEST_CASES:
        passed = run_test_case(
            name=test_case["name"],
            grid=test_case["grid"],
            bet=DEFAULT_BET,
            expected_win=test_case["expected_win"],
        )

        if passed:
            passed_tests += 1

    print("=== ZUSAMMENFASSUNG ===")
    print(f"{passed_tests}/{total_tests} Tests bestanden")

def main() -> None:
    print_game_info()
    print()

    grid = spin_reels()
    print_grid(grid)
    print()

    run_all_tests()


if __name__ == "__main__":
    main()