#!/usr/bin/env python3
"""Synthesize the transition SFX (whoosh, swoosh, whip, flyby) as 48 kHz stereo WAVs.

    python3 tools/make_sfx.py assets/sfx

Noise is shaped in the STFT domain by a time-varying band-pass (centre frequency and width follow
envelopes), then given an amplitude envelope, a stereo pan sweep and a short room tail.
"""
import sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def stft_shape(x, centre, width, nfft=1024, hop=256):
    """Band-pass noise x with a centre/width (Hz, log-domain width in octaves) that change over time."""
    win = np.hanning(nfft)
    n = len(x)
    pad = np.concatenate([np.zeros(nfft), x, np.zeros(nfft)])
    out = np.zeros_like(pad)
    norm = np.zeros_like(pad)
    freqs = np.fft.rfftfreq(nfft, 1 / SR)
    lf = np.log2(np.maximum(freqs, 20))
    for start in range(0, len(pad) - nfft, hop):
        t = np.clip((start - nfft + nfft / 2) / max(n - 1, 1), 0, 1)
        c, w = np.log2(centre(t)), width(t)
        gain = np.exp(-0.5 * ((lf - c) / w) ** 2)
        seg = np.fft.irfft(np.fft.rfft(pad[start:start + nfft] * win) * gain)
        out[start:start + nfft] += seg * win
        norm[start:start + nfft] += win ** 2
    return (out / np.maximum(norm, 1e-6))[nfft:nfft + n]


def envelope(n, peak_at, attack_pow=2.2, release_pow=1.6):
    t = np.linspace(0, 1, n)
    a = np.where(t < peak_at, (t / peak_at) ** attack_pow, ((1 - t) / (1 - peak_at)) ** release_pow)
    return a


def pan(mono, p):
    """p(t) in [-1, 1] -> constant-power stereo."""
    th = (p + 1) * np.pi / 4
    return np.stack([mono * np.cos(th), mono * np.sin(th)], 1)


def room(st, amount=0.18):
    """Tiny feedback-delay tail so the sound sits in a space instead of feeling dry."""
    out = st.copy()
    for d, g in ((0.031, 0.5), (0.047, 0.4), (0.071, 0.3), (0.113, 0.2)):
        k = int(d * SR)
        out[k:] += st[:-k] * g * amount * 2
    return out


def norm(st, peak_db):
    return st / np.max(np.abs(st)) * 10 ** (peak_db / 20)


def lin(a, b):
    return lambda t: a + (b - a) * t


def whoosh(dur=0.75, f0=250, f1=2600, peak=0.62, peak_db=-3):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    # centre rises to f1 at the peak then falls back a little; band narrows at the peak (more "air")
    centre = lambda u: f0 * (f1 / f0) ** (min(u / peak, 1) ** 1.3) * (1 - 0.45 * max(0, (u - peak) / (1 - peak)))
    width = lambda u: 1.3 - 0.6 * np.exp(-((u - peak) / 0.18) ** 2)
    m = stft_shape(noise, centre, width) * envelope(n, peak)
    st = pan(m, np.tanh(3 * (t - peak)) * 0.7)
    return norm(room(st), peak_db)


def whip(dur=0.32, peak_db=-2):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    centre = lambda u: 400 * (9000 / 400) ** (u ** 2.4)
    m = stft_shape(noise, centre, lambda u: 0.9 - 0.4 * u) * envelope(n, 0.88, 3.0, 4.0)
    # the crack: a 12 ms bright transient right at the end of the sweep
    k = int(0.86 * n)
    crack_len = int(0.012 * SR)
    crack = rng.standard_normal(crack_len) * np.exp(-np.linspace(0, 6, crack_len))
    crack = np.diff(np.concatenate([[0], crack]))  # first difference = high-pass
    m[k:k + crack_len] += crack * np.max(np.abs(m)) * 2.2
    st = pan(m, lin(-0.5, 0.6)(t))
    return norm(room(st, 0.12), peak_db)


def flyby(dur=1.3, peak_db=-3):
    """Object passing the listener: rising then falling level, Doppler pitch drop, pan left to right."""
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    x = (t - 0.5) * 2  # position, closest at the middle
    dist = np.sqrt(x ** 2 + 0.06)
    amp = 1 / dist ** 1.6
    amp /= amp.max()
    doppler = 1 + 0.18 * (-x / dist)  # higher while approaching, lower while leaving
    noise = rng.standard_normal(n)
    centre = lambda u: 900 * (1 + 0.18 * (-(u - 0.5) * 2) / np.sqrt(((u - 0.5) * 2) ** 2 + 0.06)) * (1.6 - 0.9 * abs(u - 0.5) * 2)
    air = stft_shape(noise, centre, lambda u: 0.75 + 0.5 * abs(u - 0.5) * 2)
    # a soft tonal body (two partials) with the Doppler shift, for the "flyby" character
    phase = np.cumsum(2 * np.pi * 240 * doppler / SR)
    body = 0.35 * np.sin(phase) + 0.18 * np.sin(2.01 * phase)
    m = (air + body * np.std(air) * 2.0) * amp
    st = pan(m, np.tanh(2.5 * x) * 0.9)
    return norm(room(st, 0.2), peak_db)


def swoosh(dur=0.5, peak_db=-4):
    """Lighter, shorter whoosh for UI pops and exits."""
    return whoosh(dur, 600, 4200, 0.55, peak_db)


def write(path, st):
    data = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    out = sys.argv[1]
    write(f"{out}/whoosh.wav", whoosh())
    write(f"{out}/swoosh.wav", swoosh())
    write(f"{out}/whip.wav", whip())
    write(f"{out}/flyby.wav", flyby())
    print("ok")
