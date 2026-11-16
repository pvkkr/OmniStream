"""
Synthesizes a high-energy, modern tech-house / electronic soundtrack for the OmniStream promo video.
Outputs a 30-second 44.1kHz stereo WAV file.
"""

import math
import wave
import numpy as np

def generate_track(duration=30.0, sr=44100):
    total_samples = int(duration * sr)
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    bpm = 124.0
    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4.0

    # Generate note frequencies dynamically across all octaves
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    NOTE_FREQS = {}
    for midi in range(21, 108):
        octave = (midi // 12) - 1
        name = NOTE_NAMES[midi % 12]
        NOTE_FREQS[f"{name}{octave}"] = 440.0 * (2.0 ** ((midi - 69) / 12.0))
        # Support flat aliases if needed
        if '#' in name:
            pass

    # Chords Progression (Am - F - C - G)
    CHORDS = [
        {'bass': 'A1', 'pluck': ['A3', 'C4', 'E4', 'A4', 'C5', 'E5', 'C5', 'A4']},
        {'bass': 'F1', 'pluck': ['F3', 'A3', 'C4', 'F4', 'A4', 'C5', 'A4', 'F4']},
        {'bass': 'C2', 'pluck': ['C3', 'E3', 'G3', 'C4', 'E4', 'G4', 'E4', 'C4']},
        {'bass': 'G1', 'pluck': ['G2', 'B3', 'D4', 'G4', 'B4', 'D5', 'B4', 'G4']}
    ]

    def add_sound(buf, start_time, audio_arr, pan=0.0):
        start_idx = int(start_time * sr)
        end_idx = min(start_idx + len(audio_arr), total_samples)
        if start_idx >= total_samples or start_idx < 0:
            return
        seg_len = end_idx - start_idx
        p_l = 0.5 * (1.0 - pan)
        p_r = 0.5 * (1.0 + pan)
        buf[0][start_idx:end_idx] += audio_arr[:seg_len] * p_l
        buf[1][start_idx:end_idx] += audio_arr[:seg_len] * p_r

    # Pre-render drum elements
    # 1. Kick Drum (Punchy 130Hz -> 42Hz pitch drop + sub)
    kick_len = int(0.25 * sr)
    t_kick = np.linspace(0, 0.25, kick_len, endpoint=False)
    freq_sweep = 45.0 + (120.0 - 45.0) * np.exp(-t_kick * 30.0)
    phase_kick = 2.0 * np.pi * np.cumsum(freq_sweep) / sr
    kick = np.sin(phase_kick) * np.exp(-t_kick * 14.0)
    # Add subtle punch click
    kick[:int(0.008 * sr)] += (np.random.rand(int(0.008 * sr)) * 2 - 1) * 0.35

    # 2. Snare / Clap
    snare_len = int(0.20 * sr)
    t_snare = np.linspace(0, 0.20, snare_len, endpoint=False)
    noise_snare = (np.random.rand(snare_len) * 2 - 1) * np.exp(-t_snare * 22.0)
    tone_snare = np.sin(2.0 * np.pi * 185.0 * t_snare) * np.exp(-t_snare * 28.0) * 0.5
    snare = noise_snare + tone_snare

    # 3. Closed Hi-Hat
    hh_len = int(0.06 * sr)
    t_hh = np.linspace(0, 0.06, hh_len, endpoint=False)
    hh = (np.random.rand(hh_len) * 2 - 1) * np.exp(-t_hh * 70.0)

    # 4. Open Hi-Hat
    oh_len = int(0.22 * sr)
    t_oh = np.linspace(0, 0.22, oh_len, endpoint=False)
    oh = (np.random.rand(oh_len) * 2 - 1) * np.exp(-t_oh * 18.0)

    buf = [left, right]

    # Render Tracks Over Time
    num_bars = int(duration / bar_dur) + 2
    for bar in range(num_bars):
        bar_start = bar * bar_dur
        chord = CHORDS[bar % len(CHORDS)]

        # --- Scene Transitions / Riser (Bar 2, around 4-6s)
        if bar == 2:
            riser_len = int(2.0 * sr)
            t_r = np.linspace(0, 2.0, riser_len, endpoint=False)
            freq_r = 200.0 + 3000.0 * (t_r / 2.0) ** 2
            riser = (np.random.rand(riser_len) * 2 - 1) * (t_r / 2.0) ** 2 * 0.25
            riser += np.sin(2.0 * np.pi * np.cumsum(freq_r) / sr) * (t_r / 2.0) * 0.15
            add_sound(buf, bar_start, riser, pan=0.0)

        # --- Drums (Drop starts at Bar 3, ~5.8s, until Bar 13, ~25s)
        has_drums = (bar >= 3 and bar <= 13)
        has_open_hh = (bar >= 7 and bar <= 13)

        for beat in range(4):
            beat_time = bar_start + beat * beat_dur

            if has_drums:
                # 4-on-the-floor Kick
                add_sound(buf, beat_time, kick * 0.85, pan=0.0)

                # Snare on 2 and 4
                if beat in [1, 3]:
                    add_sound(buf, beat_time, snare * 0.60, pan=0.05)

                # Hi-Hats on off-beats (8th notes)
                add_sound(buf, beat_time + beat_dur * 0.5, hh * 0.35, pan=-0.2)

                if has_open_hh and beat in [0, 2]:
                    add_sound(buf, beat_time + beat_dur * 0.5, oh * 0.25, pan=0.3)

            # --- Synth Bass (Playing 16th notes with warm drive)
            if bar >= 3 and bar <= 13:
                bass_f = NOTE_FREQS[chord['bass']]
                for step in range(4):
                    b_time = beat_time + step * (beat_dur / 4.0)
                    b_dur = beat_dur * 0.22
                    b_len = int(b_dur * sr)
                    t_b = np.linspace(0, b_dur, b_len, endpoint=False)
                    # Saturated saw + sub sine
                    bass_wave = (np.sin(2 * np.pi * bass_f * t_b) + 
                                 0.5 * np.sin(2 * np.pi * bass_f * 2 * t_b) +
                                 0.3 * np.sin(2 * np.pi * bass_f * 3 * t_b)) * np.exp(-t_b * 12.0)
                    add_sound(buf, b_time, bass_wave * 0.45, pan=0.0)

            # --- Synth Pluck Arpeggio (Wide stereo, active throughout)
            for sub_step in range(2):
                arp_idx = (beat * 2 + sub_step) % len(chord['pluck'])
                arp_note = chord['pluck'][arp_idx]
                note_f = NOTE_FREQS[arp_note]
                p_time = beat_time + sub_step * (beat_dur / 2.0)

                p_dur = beat_dur * 0.45
                p_len = int(p_dur * sr)
                t_p = np.linspace(0, p_dur, p_len, endpoint=False)
                # Bright bell-like FM synth pluck
                mod = np.sin(2 * np.pi * (note_f * 2) * t_p) * np.exp(-t_p * 20.0) * 2.0
                pluck_wave = np.sin(2 * np.pi * note_f * t_p + mod) * np.exp(-t_p * 7.0)

                # Alternating ping-pong stereo pan
                pan_val = 0.55 if (sub_step % 2 == 0) else -0.55
                vol = 0.32 if (bar < 3 or bar > 13) else 0.28
                add_sound(buf, p_time, pluck_wave * vol, pan=pan_val)

    # Master Fade In & Fade Out
    fade_in_len = int(0.5 * sr)
    fade_out_len = int(3.0 * sr)
    t_fi = np.linspace(0, 1, fade_in_len)
    buf[0][:fade_in_len] *= t_fi
    buf[1][:fade_in_len] *= t_fi

    t_fo = np.linspace(1, 0, fade_out_len)
    buf[0][-fade_out_len:] *= t_fo
    buf[1][-fade_out_len:] *= t_fo

    # Normalize audio to -1.0 dB
    max_peak = max(np.max(np.abs(buf[0])), np.max(np.abs(buf[1])))
    if max_peak > 0:
        gain = 0.88 / max_peak
        buf[0] *= gain
        buf[1] *= gain

    # Convert to 16-bit PCM
    audio_interleaved = np.zeros(total_samples * 2, dtype=np.int16)
    audio_interleaved[0::2] = np.int16(np.clip(buf[0], -1.0, 1.0) * 32767)
    audio_interleaved[1::2] = np.int16(np.clip(buf[1], -1.0, 1.0) * 32767)

    return audio_interleaved.tobytes()

def main():
    wav_path = "omnistream_soundtrack.wav"
    print("Synthesizing 30-second energetic tech soundtrack...")
    raw_bytes = generate_track(duration=30.0, sr=44100)

    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(raw_bytes)

    print(f"Soundtrack created: {wav_path} (Size: {len(raw_bytes)} bytes)")

if __name__ == "__main__":
    main()
