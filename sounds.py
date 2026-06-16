import array
import math
import random
import pygame

from settings import settings


def play_synth_sound(freq_list, duration, wav_type='square', volume=0.08, sample_rate=22050):
    try:
        if not pygame.mixer or not pygame.mixer.get_init():
            return None

        vol = volume * settings.effective_sfx()
        if vol <= 0.0:
            return None

        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)

        for i in range(num_samples):
            t = i / sample_rate
            if len(freq_list) == 1:
                freq = freq_list[0]
            else:
                progress = t / duration
                idx = min(int(progress * (len(freq_list) - 1)), len(freq_list) - 2)
                t_sub = (progress * (len(freq_list) - 1)) - idx
                freq = freq_list[idx] * (1 - t_sub) + freq_list[idx + 1] * t_sub

            if wav_type == 'square':
                val = 1.0 if (t * freq) % 1.0 < 0.5 else -1.0
            elif wav_type == 'sine':
                val = math.sin(2 * math.pi * freq * t)
            elif wav_type == 'triangle':
                val = 2.0 * abs(2.0 * ((t * freq) % 1.0 - 0.5)) - 1.0
            elif wav_type == 'noise':
                val = random.uniform(-1.0, 1.0)
            else:
                val = 0.0

            decay = 1.0 - (t / duration)
            val_int = int(max(-32768, min(32767, val * decay * vol * 32767)))
            buf[i] = val_int

        sound = pygame.mixer.Sound(buffer=buf)
        sound.play()
        return sound
    except Exception:
        return None


def sfx_jump():
    play_synth_sound(_jump_profile, 0.18, _jump_wave, volume=0.08)


# The currently equipped character's jump sound. Characters override this via
# set_jump_profile() so each one sounds distinct.
_jump_profile = [160, 680, 820]
_jump_wave = 'square'


def set_jump_profile(freqs, wave='square'):
    global _jump_profile, _jump_wave
    if freqs:
        _jump_profile = list(freqs)
    _jump_wave = wave

def sfx_coin():
    play_synth_sound([988], 0.07, 'sine', volume=0.1)
    pygame.time.set_timer(pygame.USEREVENT + 10, 80)

def play_coin_second_tone():
    play_synth_sound([1318], 0.2, 'sine', volume=0.1)

def sfx_stomp():
    play_synth_sound([180, 50], 0.12, 'noise', volume=0.18)

def sfx_shrink():
    play_synth_sound([600, 400, 200, 100], 0.25, 'triangle', volume=0.15)

def sfx_powerup_spawn():
    play_synth_sound([330, 440, 550, 660], 0.22, 'square', volume=0.07)

def sfx_powerup():
    play_synth_sound([330, 550, 660, 880, 1100], 0.3, 'square', volume=0.08)

def sfx_block_bump():
    play_synth_sound([120, 60], 0.1, 'square', volume=0.15)

def sfx_block_break():
    play_synth_sound([100, 40], 0.15, 'noise', volume=0.2)

def sfx_die():
    play_synth_sound([500, 400, 300, 200, 100, 50], 0.5, 'square', volume=0.15)

def sfx_clear():
    play_synth_sound([523, 659, 784, 1046, 784, 1046], 0.6, 'sine', volume=0.1)

def sfx_menu_move():
    play_synth_sound([440, 660], 0.06, 'square', volume=0.08)

def sfx_menu_select():
    play_synth_sound([660, 880, 1100], 0.14, 'square', volume=0.1)

def sfx_pause():
    play_synth_sound([880, 440], 0.12, 'sine', volume=0.1)

def sfx_unpause():
    play_synth_sound([440, 880], 0.12, 'sine', volume=0.1)

def sfx_level_start():
    play_synth_sound([523, 659, 784, 1046], 0.4, 'square', volume=0.09)

def sfx_hazard():
    play_synth_sound([300, 120, 60], 0.2, 'noise', volume=0.16)

def sfx_firework():
    play_synth_sound([200, 1200], 0.18, 'noise', volume=0.1)


_NOTE_FREQ = {
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00,
    'A3': 220.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00,
    'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99,
    'A5': 880.00, 'B5': 987.77,
    'R': 0.0,
}

_MELODIES = [
    ['E4', 'E4', 'R', 'E4', 'R', 'C4', 'E4', 'R',
     'G4', 'R', 'R', 'R', 'G3', 'R', 'R', 'R',
     'C4', 'R', 'R', 'G3', 'R', 'R', 'E3', 'R',
     'A3', 'R', 'B3', 'R', 'A3', 'R', 'G3', 'R'],
    ['A3', 'C4', 'E4', 'A4', 'G4', 'E4', 'C4', 'E4',
     'F4', 'A4', 'C5', 'A4', 'G4', 'E4', 'C4', 'R',
     'D4', 'F4', 'A4', 'D5', 'C5', 'A4', 'F4', 'A4',
     'E4', 'G4', 'B4', 'E5', 'D5', 'B4', 'G4', 'R'],
    ['E3', 'R', 'G3', 'R', 'B3', 'R', 'E4', 'R',
     'D4', 'R', 'B3', 'R', 'G3', 'R', 'E3', 'R',
     'A3', 'R', 'C4', 'R', 'E4', 'R', 'A4', 'R',
     'G4', 'R', 'E4', 'R', 'C4', 'R', 'A3', 'R'],
    ['C3', 'E3', 'G3', 'C4', 'B3', 'G3', 'E3', 'C3',
     'D3', 'F3', 'A3', 'D4', 'C4', 'A3', 'F3', 'D3',
     'E3', 'G3', 'B3', 'E4', 'D4', 'B3', 'G3', 'E3',
     'F3', 'A3', 'C4', 'F4', 'E4', 'C4', 'A3', 'F3'],
]

_music_channel = None
_music_sounds  = {}

# Tense, faster melodies used for boss battles. Each PvP boss cycles through
# these so consecutive fights sound different; the final boss gets the last,
# most menacing one.
_BOSS_MELODIES = [
    # 0 - driving minor march (classic beast)
    ['E3', 'E3', 'G3', 'E3', 'A3', 'G3', 'E3', 'D3',
     'E3', 'G3', 'B3', 'A3', 'G3', 'E3', 'B3', 'E3',
     'C4', 'B3', 'G3', 'E3', 'A3', 'G3', 'E3', 'D3',
     'E3', 'B3', 'G3', 'B3', 'E4', 'D4', 'B3', 'G3'],
    # 1 - mechanical pulse (mech)
    ['A3', 'A3', 'E4', 'A3', 'C4', 'A3', 'E4', 'A3',
     'G3', 'G3', 'D4', 'G3', 'B3', 'G3', 'D4', 'G3',
     'F3', 'F3', 'C4', 'F3', 'A3', 'F3', 'C4', 'F3',
     'E3', 'B3', 'E4', 'G4', 'B4', 'A4', 'G4', 'E4'],
    # 2 - frantic chase
    ['D4', 'E4', 'F4', 'E4', 'D4', 'C4', 'D4', 'A3',
     'D4', 'F4', 'A4', 'F4', 'E4', 'D4', 'C4', 'A3',
     'B3', 'C4', 'D4', 'C4', 'B3', 'A3', 'G3', 'E3',
     'A3', 'C4', 'E4', 'A4', 'G4', 'E4', 'C4', 'A3'],
    # 3 - heavy stomp
    ['C3', 'C3', 'R', 'C3', 'E3', 'R', 'G3', 'R',
     'C3', 'C3', 'R', 'D3', 'F3', 'R', 'A3', 'R',
     'B3', 'B3', 'R', 'D3', 'G3', 'R', 'B3', 'R',
     'C3', 'E3', 'G3', 'C4', 'B3', 'G3', 'E3', 'C3'],
    # 4 - final boss: relentless and dark
    ['E3', 'F3', 'E3', 'D3', 'E3', 'G3', 'A3', 'B3',
     'C4', 'B3', 'A3', 'G3', 'A3', 'B3', 'C4', 'D4',
     'E4', 'D4', 'C4', 'B3', 'C4', 'A3', 'G3', 'E3',
     'A3', 'C4', 'E4', 'G4', 'A4', 'G4', 'E4', 'C4'],
]


def _build_music_sound(theme_index, sample_rate=22050):
    return _build_music_from(_MELODIES[theme_index % len(_MELODIES)],
                             note_dur=0.16, sample_rate=sample_rate)


def _build_music_from(melody, note_dur=0.16, sample_rate=22050):
    total_samples = int(sample_rate * note_dur * len(melody))
    buf = array.array('h', [0] * total_samples)

    for n, note in enumerate(melody):
        freq = _NOTE_FREQ.get(note, 0.0)
        bass = freq / 2.0 if freq > 0 else 0.0
        start = int(n * note_dur * sample_rate)
        end   = int((n + 1) * note_dur * sample_rate)
        for i in range(start, end):
            t  = (i - start) / sample_rate
            td = note_dur
            val = 0.0
            if freq > 0:
                lead = 1.0 if (t * freq) % 1.0 < 0.5 else -1.0
                bwave = 2.0 * abs(2.0 * ((t * bass) % 1.0 - 0.5)) - 1.0
                env = min(1.0, (t / 0.02)) * (1.0 - (t / td) * 0.7)
                val = (lead * 0.5 + bwave * 0.5) * env
            sample = int(max(-32768, min(32767, val * 0.18 * 32767)))
            buf[i] = sample

    return pygame.mixer.Sound(buffer=buf)


def _play_cached(key, builder):
    global _music_channel
    try:
        if not pygame.mixer or not pygame.mixer.get_init():
            return
        if not settings.music_enabled:
            stop_music()
            return
        if key not in _music_sounds:
            _music_sounds[key] = builder()
        snd = _music_sounds[key]
        if _music_channel is None:
            _music_channel = pygame.mixer.Channel(0)
        _music_channel.stop()
        _music_channel.set_volume(settings.effective_music())
        _music_channel.play(snd, loops=-1)
    except Exception:
        pass


def start_music(theme_index=0):
    _play_cached(theme_index, lambda: _build_music_sound(theme_index))


def start_boss_music(boss_index=0):
    """Play a boss battle theme. boss_index picks (and caches) one of the
    tense boss melodies; it's played faster than overworld music."""
    key = ('boss', boss_index % len(_BOSS_MELODIES))
    _play_cached(key, lambda: _build_music_from(
        _BOSS_MELODIES[boss_index % len(_BOSS_MELODIES)], note_dur=0.13))


def stop_music():
    global _music_channel
    try:
        if _music_channel is not None:
            _music_channel.stop()
    except Exception:
        pass


def update_music_volume():
    try:
        if _music_channel is not None:
            _music_channel.set_volume(settings.effective_music() if settings.music_enabled else 0.0)
    except Exception:
        pass
