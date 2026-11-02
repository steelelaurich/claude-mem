"""Rule 2 check: count silent frames in the finished edit.

Dead = 11 dB under speaking level. A frame (1/30 s) is silent when it sits wholly inside
a dead run longer than a word fade. The allowed exceptions are a word's own fade (rule 4, <= 60 ms, so
never a whole frame on its own) and deliberate serious-line pauses passed with --allow.

usage: check_dead.py edit.mp4 [--allow start-end ...]
"""
import subprocess, sys
import numpy as np

SR, FPS = 48000, 30
path = sys.argv[1]
allow = [tuple(map(float, a.split("-"))) for a in sys.argv[3::2]] if "--allow" in sys.argv else []
raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                      "-f", "s16le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
HOP, WIN = 0.005, 0.020  # same windows as the cutter


def frame_db(s):
    hop, win = int(HOP * SR), int(WIN * SR)
    m = max(1, (len(s) - win) // hop + 1)
    idx = np.arange(m)[:, None] * hop + np.arange(win)[None, :]
    return 20 * np.log10(np.sqrt(np.mean(s[np.clip(idx, 0, len(s) - 1)] ** 2, axis=1) + 1e-12))


db = frame_db(x)
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from level import live_mask, preemph  # noqa: E402
pe = frame_db(preemph(x))
live, level, level_pe = live_mask(db, pe)
dead = ~live

# A dead run up to 90 ms is a word's own fade (<= 60 ms, rule 4) plus the next
# word's lead-in and the 20 ms join. Anything longer is air.
MAX_FADE = 0.09
air = np.zeros(len(dead), bool)
i = 0
while i < len(dead):
    if dead[i]:
        j = i
        while j < len(dead) and dead[j]:
            j += 1
        if (j - i) * HOP > MAX_FADE:
            air[i:j] = True
        i = j
    else:
        i += 1
silent = []
for f in range(int(len(x) / SR * FPS)):
    t0 = f / FPS
    a, b = int(t0 / HOP), int((t0 + 1 / FPS) / HOP)
    if b <= len(air) and air[a:b].all() and not any(s <= t0 < e for s, e in allow):
        silent.append(t0)
print(f"speaking level {level:.1f} dB (tilted {level_pe:.1f} dB), dead 11 dB below either")
print(f"silent frames: {len(silent)}")
runs = []
for t in silent:
    if runs and t - runs[-1][1] <= 1.01 / FPS:
        runs[-1][1] = t
    else:
        runs.append([t, t])
for s, e in runs:
    print(f"  {s:7.3f}-{e + 1 / FPS:7.3f}  ({round((e - s) * FPS) + 1} frames)")
sys.exit(0 if not silent else 1)
