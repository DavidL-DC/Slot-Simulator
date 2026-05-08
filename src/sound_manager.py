from pathlib import Path
import pygame


class SoundManager:
    def __init__(self, base_dir: Path) -> None:
        pygame.mixer.init()

        self.enabled = True
        self.master_volume = 0.8

        sound_dir = base_dir / "assets" / "sounds"

        self.sounds: dict[str, pygame.mixer.Sound] = {
            "spin": pygame.mixer.Sound(sound_dir / "spin.wav"),
            "line_low": pygame.mixer.Sound(sound_dir / "line_low.wav"),
            "line_mid": pygame.mixer.Sound(sound_dir / "line_mid.wav"),
            "line_high": pygame.mixer.Sound(sound_dir / "line_high.wav"),
            "instant_win": pygame.mixer.Sound(sound_dir / "instant_win.wav"),
            "countup": pygame.mixer.Sound(sound_dir / "countup.wav"),
            "yin_yang_drop": pygame.mixer.Sound(sound_dir / "yin.wav"),
            "yin_yang_column_step": pygame.mixer.Sound(
                sound_dir / "column_increase.wav"
            ),
            "yin_yang_column_complete": pygame.mixer.Sound(
                sound_dir / "column_complete.wav"
            ),
            "grand_activated": pygame.mixer.Sound(sound_dir / "grand.wav"),
            "feature_trigger": pygame.mixer.Sound(sound_dir / "trigger.wav"),
            "bull_collect_or_drop": pygame.mixer.Sound(sound_dir / "bull.wav"),
        }

        for sound in self.sounds.values():
            sound.set_volume(self.master_volume)

    def play(self, name: str) -> None:
        if not self.enabled:
            return

        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    def play_loop(self, name: str) -> None:
        if not self.enabled:
            return

        sound = self.sounds.get(name)
        if sound is not None:
            sound.play(loops=-1)

    def stop(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound is not None:
            sound.stop()

    def play_line_win(self, win: float, bet: float) -> None:
        if bet <= 0:
            self.play("line_low")
            return

        multiplier = win / bet

        if multiplier < 5:
            self.play("line_low")
        elif multiplier < 20:
            self.play("line_mid")
        else:
            self.play("line_high")
