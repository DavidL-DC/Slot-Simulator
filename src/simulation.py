from dataclasses import dataclass, field

from game import (
    GameState,
    add_free_spins,
    apply_bet,
    apply_win,
    consume_free_spin,
    is_free_spin,
)
from slot_machine import (
    count_bulls,
    evaluate_total_win,
    spin_reels,
    spin_reels_free_spins,
)
from bull_feature import play_bull_feature
from config import PAYLINES


@dataclass
class SimulationStats:
    total_spins: int = 0
    base_game_spins: int = 0
    free_spins_played: int = 0

    total_bet: float = 0
    total_win: float = 0

    total_line_win: int = 0
    total_scatter_win: int = 0

    base_game_win: int = 0
    free_spin_win: float = 0

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

    total_instant_win: int = 0
    base_game_instant_win: int = 0
    free_spin_instant_win: int = 0

    total_bull_feature_win: float = 0
    bull_feature_triggers: int = 0
    total_bulls_collected: int = 0

    base_game_yin_yang_triggers: int = 0
    free_spin_yin_yang_triggers: int = 0

    base_game_instant_win_triggers: int = 0
    free_spin_instant_win_triggers: int = 0

    free_spin_sessions: int = 0
    completed_free_spin_sessions: int = 0
    total_free_spin_session_win: float = 0

    total_bull_feature_trigger_bulls: int = 0

    total_yin_yang_triggers: int = 0
    grand_activations: int = 0
    grand_wins: int = 0
    total_grand_win: int = 0

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

    def bull_feature_rtp(self) -> float:
        if self.total_bet == 0:
            return 0.0
        return self.total_bull_feature_win / self.total_bet * 100

    def avg_free_spins_per_trigger(self) -> float:
        if self.scatter_triggers == 0:
            return 0.0
        return self.total_free_spins_awarded / self.scatter_triggers

    def avg_free_spin_session_win(self) -> float:
        if self.completed_free_spin_sessions == 0:
            return 0.0
        return self.total_free_spin_session_win / self.completed_free_spin_sessions

    def avg_bulls_per_bull_feature(self) -> float:
        if self.bull_feature_triggers == 0:
            return 0.0
        return self.total_bull_feature_trigger_bulls / self.bull_feature_triggers

    def avg_bull_feature_win(self) -> float:
        if self.bull_feature_triggers == 0:
            return 0.0
        return self.total_bull_feature_win / self.bull_feature_triggers

    def grand_activation_rate_per_yin_yang(self) -> float:
        if self.total_yin_yang_triggers == 0:
            return 0.0
        return self.grand_activations / self.total_yin_yang_triggers * 100

    def grand_win_rate_per_activation(self) -> float:
        if self.grand_activations == 0:
            return 0.0
        return self.grand_wins / self.grand_activations * 100

    def grand_rtp(self) -> float:
        if self.total_bet == 0:
            return 0.0
        return self.total_grand_win / self.total_bet * 100


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
        if state.free_spins_remaining == 1:
            state.free_spins_remaining = 0

            if state.collected_bulls > 0:
                bull_feature_result = play_bull_feature(
                    collected_bulls=state.collected_bulls,
                    bet=state.current_bet,
                    paylines=PAYLINES,
                )

                bull_feature_win = bull_feature_result.total_win

                apply_win(state, bull_feature_win)

                stats.total_win += bull_feature_win
                stats.free_spin_win += bull_feature_win
                stats.total_bull_feature_win += bull_feature_win
                stats.bull_feature_triggers += 1
                stats.total_bull_feature_trigger_bulls += state.collected_bulls

                state.collected_bulls = 0

            return

        consume_free_spin(state)
        stats.free_spins_played += 1
    else:
        apply_bet(state)
        stats.total_bet += state.current_bet
        stats.base_game_spins += 1

    stats.total_spins += 1

    if free_spin_mode:
        grid = spin_reels_free_spins()
        bulls_this_spin = count_bulls(grid)
        state.collected_bulls += bulls_this_spin
        stats.total_bulls_collected += bulls_this_spin
    else:
        grid = spin_reels(state.credits_bet)

    win_result = evaluate_total_win(grid, state.current_bet, free_spin_mode)

    total_win = win_result["total_win"]
    line_win = win_result["line_win"]
    scatter_win = win_result["scatter_win"]
    yin_yang_win = win_result["yin_yang_win"]
    instant_win = win_result["instant_win"]
    awarded_free_spins = win_result["awarded_free_spins"]
    scatter_count = win_result["scatter_count"]
    yin_yang_triggered = win_result["yin_yang_feature_result"] is not None
    instant_win_triggered = instant_win > 0

    grand_activated = False
    grand_won = False
    grand_win_amount = 0

    if yin_yang_triggered:
        feature_result = win_result["yin_yang_feature_result"]
        if feature_result is not None and feature_result.grand_column_index is not None:
            grand_activated = True

            if feature_result.grand_column_index in feature_result.completed_columns:
                grand_won = True
                grand_win_amount = 10000

    record_line_hits(stats, win_result["line_results"])
    record_scatter_distribution(stats, scatter_count)

    if total_win > 0:
        stats.winning_spins += 1

    if awarded_free_spins > 0:
        stats.scatter_triggers += 1
        stats.total_free_spins_awarded += awarded_free_spins
        add_free_spins(state, awarded_free_spins)

    if yin_yang_triggered:
        if free_spin_mode:
            stats.free_spin_yin_yang_triggers += 1
        else:
            stats.base_game_yin_yang_triggers += 1

        stats.total_yin_yang_triggers += 1

        if grand_activated:
            stats.grand_activations += 1

        if grand_won:
            stats.grand_wins += 1
            stats.total_grand_win += grand_win_amount

    if instant_win_triggered:
        if free_spin_mode:
            stats.free_spin_instant_win_triggers += 1
        else:
            stats.base_game_instant_win_triggers += 1

    apply_win(state, total_win)

    stats.total_win += total_win
    stats.total_line_win += line_win
    stats.total_scatter_win += scatter_win
    stats.total_yin_yang_win += yin_yang_win
    stats.total_instant_win += instant_win

    if free_spin_mode:
        stats.free_spin_win += total_win
        stats.free_spin_line_win += line_win
        stats.free_spin_scatter_win += scatter_win
        stats.free_spin_yin_yang_win += yin_yang_win
        stats.free_spin_instant_win += instant_win
    else:
        stats.base_game_win += line_win + scatter_win + instant_win
        stats.base_game_line_win += line_win
        stats.base_game_scatter_win += scatter_win
        stats.base_game_yin_yang_win += yin_yang_win
        stats.base_game_instant_win += instant_win


def run_simulation(
    start_balance: float, bet: float, base_game_spins: int
) -> SimulationStats:
    state = GameState(balance=start_balance, current_bet=bet)
    stats = SimulationStats()

    completed_base_spins = 0
    free_spin_session_active = False
    free_spin_session_start_win = 0

    while completed_base_spins < base_game_spins:
        if not is_free_spin(state):
            if completed_base_spins % 10000 == 0:
                print(f"{completed_base_spins}/{base_game_spins}")
            if state.balance < state.current_bet:
                break
            completed_base_spins += 1

        if is_free_spin(state) and not free_spin_session_active:
            free_spin_session_active = True
            free_spin_session_start_win = stats.free_spin_win
            stats.free_spin_sessions += 1

        simulate_single_spin(state, stats)

        if free_spin_session_active and not is_free_spin(state):
            session_win = stats.free_spin_win - free_spin_session_start_win
            stats.total_free_spin_session_win += session_win
            stats.completed_free_spin_sessions += 1
            free_spin_session_active = False

    while is_free_spin(state):
        if not free_spin_session_active:
            free_spin_session_active = True
            free_spin_session_start_win = stats.free_spin_win
            stats.free_spin_sessions += 1

        simulate_single_spin(state, stats)

        if free_spin_session_active and not is_free_spin(state):
            session_win = stats.free_spin_win - free_spin_session_start_win
            stats.total_free_spin_session_win += session_win
            stats.completed_free_spin_sessions += 1
            free_spin_session_active = False

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
    print(f"Bull Feature RTP: {stats.bull_feature_rtp():.2f}%")
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
    print(f"Ø Freispiele pro Trigger: {stats.avg_free_spins_per_trigger():.2f}")
    print(f"Freispiele-Sessions: {stats.free_spin_sessions}")
    print(f"Abgeschlossene Freispiele-Sessions: {stats.completed_free_spin_sessions}")
    print(
        f"Ø Freispiele-Gesamtgewinn pro Session: {stats.avg_free_spin_session_win():.2f}"
    )
    print()
    print(f"Bull-Feature Trigger: {stats.bull_feature_triggers}")
    print(f"Gesammelte Bulls gesamt: {stats.total_bulls_collected}")
    print(f"Ø Bulls pro Bull-Feature: {stats.avg_bulls_per_bull_feature():.2f}")
    print(f"Ø Bull-Feature Gewinn: {stats.avg_bull_feature_win():.2f}")
    print()
    print("=== FEATURE TRIGGER ===")
    print(f"Base Game Yin-Yang Trigger: {stats.base_game_yin_yang_triggers}")
    print(f"Freispiel Yin-Yang Trigger: {stats.free_spin_yin_yang_triggers}")
    print(f"Base Game Instant-Win Trigger: {stats.base_game_instant_win_triggers}")
    print(f"Freispiel Instant-Win Trigger: {stats.free_spin_instant_win_triggers}")
    print(f"Yin-Yang Trigger gesamt: {stats.total_yin_yang_triggers}")
    print(f"Grand Aktivierungen: {stats.grand_activations}")
    print(f"Grand Gewinne: {stats.grand_wins}")
    print(
        f"Grand Aktivierungsrate pro Yin-Yang: {stats.grand_activation_rate_per_yin_yang():.2f}%"
    )
    print(
        f"Grand Gewinnrate pro Aktivierung: {stats.grand_win_rate_per_activation():.2f}%"
    )
    print(f"Grand Gewinn gesamt: {stats.total_grand_win}")
    print(f"Grand RTP: {stats.grand_rtp():.2f}%")
    print()
    print()
    print("=== DETAIL GEWINNE ===")
    print(f"Liniengewinn gesamt: {stats.total_line_win}")
    print(f"Scattergewinn gesamt: {stats.total_scatter_win}")
    print(f"Yin-Yang-Gewinn gesamt: {stats.total_yin_yang_win}")
    print(f"Instant-Win gesamt: {stats.total_instant_win}")
    print(f"Bull-Feature Gewinn gesamt: {stats.total_bull_feature_win}")
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
    print(f"Basis-Spiel Instant-Win: {stats.base_game_instant_win}")
    print(f"Freispiel Instant-Win: {stats.free_spin_instant_win}")
    print()
    print_line_hit_stats(stats)
    print()
    print_scatter_distribution(stats)


def print_balancing_summary(stats: SimulationStats) -> None:
    print("=== BALANCING SUMMARY ===")
    print(
        f"Spins={stats.total_spins} | "
        f"Base={stats.base_game_spins} | "
        f"FS={stats.free_spins_played}"
    )
    print(
        f"Bet={stats.total_bet} | "
        f"Win={stats.total_win} | "
        f"RTP={stats.rtp():.2f}% | "
        f"Hit Rate={stats.hit_rate():.2f}%"
    )
    print()

    print("RTP Split:")
    print(
        f"  Line={stats.line_rtp():.2f}% | "
        f"Scatter={stats.scatter_rtp():.2f}% | "
        f"Yin-Yang={stats.yin_yang_rtp():.2f}% | "
        f"Bull Feature={stats.bull_feature_rtp():.2f}% | "
        f"Grand RTP={stats.grand_rtp():.2f}%"
    )
    print(
        f"  Base Game={stats.base_game_rtp():.2f}% | "
        f"Free Spins={stats.free_spin_rtp():.2f}%"
    )
    print()

    print("Feature Trigger:")
    print(
        f"  Scatter Trigger={stats.scatter_triggers} | "
        f"FS awarded={stats.total_free_spins_awarded} | "
        f"Avg FS/Trigger={stats.avg_free_spins_per_trigger():.2f}"
    )
    print(
        f"  Yin-Yang Base={stats.base_game_yin_yang_triggers} | "
        f"Yin-Yang FS={stats.free_spin_yin_yang_triggers}"
    )
    print(
        f"  Instant Base={stats.base_game_instant_win_triggers} | "
        f"Instant FS={stats.free_spin_instant_win_triggers}"
    )
    print(
        f"  Bull Feature Trigger={stats.bull_feature_triggers} | "
        f"Avg Bulls/Bull Feature={stats.avg_bulls_per_bull_feature():.2f}"
    )
    print()
    print(
        f"  Grand Activations={stats.grand_activations} | "
        f"Grand Wins={stats.grand_wins} | "
        f"Grand Act/Yin-Yang={stats.grand_activation_rate_per_yin_yang():.2f}% | "
        f"Grand Win/Activation={stats.grand_win_rate_per_activation():.2f}%"
    )
    print()

    print("Free Games:")
    print(
        f"  Sessions={stats.completed_free_spin_sessions} | "
        f"Total FS Win={stats.free_spin_win} | "
        f"Avg FS Total Win/Session={stats.avg_free_spin_session_win():.2f}"
    )
    print()

    print("Feature Wins:")
    print(
        f"  Yin-Yang Total={stats.total_yin_yang_win} | "
        f"Instant Total={stats.total_instant_win} | "
        f"Bull Feature Total={stats.total_bull_feature_win} | "
        f"Grand Total={stats.total_grand_win}"
    )
    print(f"  Avg Bull Feature Win={stats.avg_bull_feature_win():.2f}")
