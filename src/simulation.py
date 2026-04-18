from dataclasses import dataclass, field

from game import (
    GameState,
    add_free_spins,
    apply_bet,
    apply_win,
    consume_free_spin,
    is_free_spin,
)
from slot_machine import evaluate_total_win, spin_reels

import random


@dataclass
class SimulationStats:
    total_spins: int = 0
    base_game_spins: int = 0
    free_spins_played: int = 0

    total_bet: int = 0
    total_win: int = 0

    total_line_win: int = 0
    total_scatter_win: int = 0

    base_game_win: int = 0
    free_spin_win: int = 0

    base_game_line_win: int = 0
    free_spin_line_win: int = 0

    base_game_scatter_win: int = 0
    free_spin_scatter_win: int = 0

    winning_spins: int = 0

    scatter_triggers: int = 0
    total_free_spins_awarded: int = 0

    line_hit_counts: dict[str, int] = field(default_factory=dict)
    line_hit_wins: dict[str, int] = field(default_factory=dict)
    scatter_count_distribution: dict[int, int] = field(default_factory=dict)

    total_yin_yang_win: int = 0
    base_game_yin_yang_win: int = 0
    free_spin_yin_yang_win: int = 0

    def rtp(self) -> float:
        if self.total_bet == 0:
            return 0.0
        return self.total_win / self.total_bet * 100

    def hit_rate(self) -> float:
        if self.total_spins == 0:
            return 0.0
        return self.winning_spins / self.total_spins * 100

    def line_rtp(self) -> float:
        if self.total_bet == 0:
            return 0.0
        return self.total_line_win / self.total_bet * 100

    def scatter_rtp(self) -> float:
        if self.total_bet == 0:
            return 0.0
        return self.total_scatter_win / self.total_bet * 100

    def yin_yang_rtp(self) -> float:
        if self.total_bet == 0:
            return 0.0
        return self.total_yin_yang_win / self.total_bet * 100

    def base_game_rtp(self) -> float:
        if self.total_bet == 0:
            return 0.0
        return self.base_game_win / self.total_bet * 100

    def free_spin_rtp(self) -> float:
        if self.total_bet == 0:
            return 0.0
        return self.free_spin_win / self.total_bet * 100


def record_line_hits(stats: SimulationStats, line_results: list[dict]) -> None:
    for result in line_results:
        if result["win"] <= 0:
            continue

        target_symbol = result["target_symbol"]
        match_count = result["match_count"]

        if target_symbol is None or match_count < 3:
            continue

        key = f"{target_symbol.name}_{match_count}"

        stats.line_hit_counts[key] = stats.line_hit_counts.get(key, 0) + 1
        stats.line_hit_wins[key] = stats.line_hit_wins.get(key, 0) + result["win"]


def record_scatter_distribution(stats: SimulationStats, scatter_count: int) -> None:
    stats.scatter_count_distribution[scatter_count] = (
        stats.scatter_count_distribution.get(scatter_count, 0) + 1
    )


def simulate_single_spin(state: GameState, stats: SimulationStats) -> None:
    free_spin_mode = is_free_spin(state)

    if free_spin_mode:
        consume_free_spin(state)
        stats.free_spins_played += 1
    else:
        apply_bet(state)
        stats.total_bet += state.current_bet
        stats.base_game_spins += 1

    stats.total_spins += 1

    grid = spin_reels()
    win_result = evaluate_total_win(grid, state.current_bet)

    total_win = win_result["total_win"]
    line_win = win_result["line_win"]
    scatter_win = win_result["scatter_win"]
    yin_yang_win = win_result["yin_yang_win"]
    awarded_free_spins = win_result["awarded_free_spins"]
    scatter_count = win_result["scatter_count"]

    if free_spin_mode:
        total_win *= 3
        line_win *= 3
        scatter_win *= 3

    record_line_hits(stats, win_result["line_results"])
    record_scatter_distribution(stats, scatter_count)

    if total_win > 0:
        stats.winning_spins += 1

    if awarded_free_spins > 0:
        stats.scatter_triggers += 1
        stats.total_free_spins_awarded += awarded_free_spins
        add_free_spins(state, awarded_free_spins)

    apply_win(state, total_win)

    stats.total_win += total_win
    stats.total_line_win += line_win
    stats.total_scatter_win += scatter_win
    stats.total_yin_yang_win += yin_yang_win

    if free_spin_mode:
        stats.free_spin_win += total_win
        stats.free_spin_line_win += line_win
        stats.free_spin_scatter_win += scatter_win
        stats.free_spin_yin_yang_win += yin_yang_win
    else:
        stats.base_game_win += total_win
        stats.base_game_line_win += line_win
        stats.base_game_scatter_win += scatter_win
        stats.base_game_yin_yang_win += yin_yang_win


def run_simulation(
    start_balance: int, bet: int, base_game_spins: int
) -> SimulationStats:
    state = GameState(balance=start_balance, current_bet=bet)
    stats = SimulationStats()

    completed_base_spins = 0

    while completed_base_spins < base_game_spins:
        if not is_free_spin(state):
            print(f"{completed_base_spins}/{base_game_spins}")
            if state.balance < state.current_bet:
                break
            completed_base_spins += 1

        simulate_single_spin(state, stats)

    while is_free_spin(state):
        simulate_single_spin(state, stats)

    return stats


def print_line_hit_stats(stats: SimulationStats) -> None:
    print("=== LINIENTREFFER NACH SYMBOL ===")

    if not stats.line_hit_counts:
        print("Keine gewinnenden Linien registriert.")
        return

    for key in sorted(stats.line_hit_counts):
        count = stats.line_hit_counts[key]
        total_win = stats.line_hit_wins.get(key, 0)
        print(f"{key}: Treffer={count}, Auszahlungswert gesamt={total_win}")


def print_scatter_distribution(stats: SimulationStats) -> None:
    print("=== SCATTER-VERTEILUNG ===")

    for scatter_count in sorted(stats.scatter_count_distribution):
        occurrences = stats.scatter_count_distribution[scatter_count]
        print(f"{scatter_count} Scatter: {occurrences}")


def print_simulation_stats(stats: SimulationStats) -> None:
    print("=== SIMULATIONSERGEBNIS ===")
    print(f"Gesamtanzahl Spins: {stats.total_spins}")
    print(f"Basis-Spiel-Spins: {stats.base_game_spins}")
    print(f"Gespielte Freispiele: {stats.free_spins_played}")
    print()
    print(f"Gesamteinsatz: {stats.total_bet}")
    print(f"Gesamtauszahlung: {stats.total_win}")
    print(f"RTP: {stats.rtp():.2f}%")
    print()
    print("=== RTP AUFSCHLÜSSELUNG ===")
    print(f"Linien RTP: {stats.line_rtp():.2f}%")
    print(f"Scatter RTP: {stats.scatter_rtp():.2f}%")
    print(f"Yin-Yang RTP: {stats.yin_yang_rtp():.2f}%")
    print()
    print(f"Basis-Spiel RTP: {stats.base_game_rtp():.2f}%")
    print(f"Freispiel RTP: {stats.free_spin_rtp():.2f}%")
    print()
    print()
    print(f"Gewinnspins: {stats.winning_spins}")
    print(f"Hit Rate: {stats.hit_rate():.2f}%")
    print()
    print(f"Basis-Spiel-Gewinn: {stats.base_game_win}")
    print(f"Freispiel-Gewinn: {stats.free_spin_win}")
    print()
    print(f"Scatter-Trigger: {stats.scatter_triggers}")
    print(f"Gewonnene Freispiele gesamt: {stats.total_free_spins_awarded}")
    print()
    print("=== DETAIL GEWINNE ===")
    print(f"Liniengewinn gesamt: {stats.total_line_win}")
    print(f"Scattergewinn gesamt: {stats.total_scatter_win}")
    print(f"Yin-Yang-Gewinn gesamt: {stats.total_yin_yang_win}")
    print()
    print(f"Basis-Spiel Liniengewinn: {stats.base_game_line_win}")
    print(f"Freispiel Liniengewinn: {stats.free_spin_line_win}")
    print()
    print(f"Basis-Spiel Scattergewinn: {stats.base_game_scatter_win}")
    print(f"Freispiel Scattergewinn: {stats.free_spin_scatter_win}")
    print()
    print(f"Basis-Spiel Yin-Yang-Gewinn: {stats.base_game_yin_yang_win}")
    print(f"Freispiel Yin-Yang-Gewinn: {stats.free_spin_yin_yang_win}")
    print()
    print_line_hit_stats(stats)
    print()
    print_scatter_distribution(stats)
