import math
import random
import struct
import pygame

# ==========================================================
# SINTETIZADOR DE AUDIO RETRO PROCEDURAL (Sin archivos externos)
# ==========================================================
class SoundFX:
    def __init__(self):
        self.enabled = False
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
            self.snd_blip = self._create_beep(freq=420, duration=0.035, volume=0.18)
            self.snd_save = self._create_arpeggio([523, 659, 784, 1046], duration=0.12, volume=0.25)
            self.snd_select = self._create_beep(freq=660, duration=0.05, volume=0.20)
            self.snd_chest = self._create_arpeggio([392, 523, 659], duration=0.09, volume=0.22)
            self.snd_door = self._create_arpeggio([349, 440, 523, 698], duration=0.15, volume=0.25)
            # Efectos de combate estilo Deltarune
            self.snd_encounter = self._create_sweep(200, 780, duration=0.22, volume=0.28)
            self.snd_hurt = self._create_noise(duration=0.18, volume=0.32)
            self.snd_enemy_hit = self._create_noise(duration=0.12, volume=0.26)
            self.snd_slash = self._create_sweep(1050, 260, duration=0.14, volume=0.24)
            self.snd_crit = self._create_arpeggio([440, 880, 1320], duration=0.08, volume=0.30)
            self.snd_graze = self._create_beep(freq=1350, duration=0.03, volume=0.15)
            self.snd_heal = self._create_arpeggio([440, 554, 659, 880], duration=0.09, volume=0.22)
            self.snd_spare = self._create_arpeggio([523, 659, 784, 1046, 1318], duration=0.10, volume=0.26)
            self.snd_shatter = self._create_noise(duration=0.35, volume=0.35)
            self.snd_warning = self._create_beep(freq=880, duration=0.08, volume=0.22)
            self.snd_parry = self._create_arpeggio([880, 1320, 1760], duration=0.12, volume=0.34)
            self.snd_parry_ready = self._create_beep(freq=1050, duration=0.06, volume=0.20)
        except Exception as e:
            print(f"Audio no disponible ({e}), continuando en modo silencioso.")

    def _create_beep(self, freq, duration, volume=0.2):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            env = 1.0 - (i / n_samples)
            val = int(volume * 32767 * math.sin(2 * math.pi * freq * t) * env)
            buf.extend(struct.pack('<h', max(-32768, min(32767, val))))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _create_arpeggio(self, freqs, duration, volume=0.2):
        sample_rate = 22050
        buf = bytearray()
        note_samples = int(sample_rate * duration)
        for freq in freqs:
            for i in range(note_samples):
                t = i / sample_rate
                env = 1.0 - (i / note_samples) * 0.7
                val = int(volume * 32767 * math.sin(2 * math.pi * freq * t) * env)
                buf.extend(struct.pack('<h', max(-32768, min(32767, val))))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _create_noise(self, duration=0.15, volume=0.25):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(n_samples):
            env = 1.0 - (i / n_samples)
            val = int(volume * 32767 * random.uniform(-1, 1) * env)
            buf.extend(struct.pack('<h', max(-32768, min(32767, val))))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _create_sweep(self, start_freq, end_freq, duration=0.2, volume=0.22):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            env = 1.0 - (i / n_samples) * 0.4
            freq = start_freq + (end_freq - start_freq) * (i / n_samples)
            val = int(volume * 32767 * math.sin(2 * math.pi * freq * t) * env)
            buf.extend(struct.pack('<h', max(-32768, min(32767, val))))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def play_blip(self):
        if self.enabled:
            self.snd_blip.play()

    def play_save(self):
        if self.enabled:
            self.snd_save.play()

    def play_select(self):
        if self.enabled:
            self.snd_select.play()

    def play_move(self):
        if self.enabled:
            self.snd_blip.play()

    def play_chest(self):
        if self.enabled:
            self.snd_chest.play()

    def play_door(self):
        if self.enabled:
            self.snd_door.play()

    def play_encounter(self):
        if self.enabled:
            self.snd_encounter.play()

    def play_hurt(self):
        if self.enabled:
            self.snd_hurt.play()

    def play_enemy_hit(self):
        if self.enabled:
            self.snd_enemy_hit.play()

    def play_slash(self):
        if self.enabled:
            self.snd_slash.play()

    def play_crit(self):
        if self.enabled:
            self.snd_crit.play()

    def play_graze(self):
        if self.enabled:
            self.snd_graze.play()

    def play_heal(self):
        if self.enabled:
            self.snd_heal.play()

    def play_spare(self):
        if self.enabled:
            self.snd_spare.play()

    def play_shatter(self):
        if self.enabled:
            self.snd_shatter.play()

    def play_warning(self):
        if self.enabled:
            self.snd_warning.play()

    def play_parry(self):
        if self.enabled:
            self.snd_parry.play()

    def play_parry_ready(self):
        if self.enabled:
            self.snd_parry_ready.play()



