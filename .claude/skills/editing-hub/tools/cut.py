"""Cut keeper lines down to zero dead space and render the assembled edit.

Implements Steele's rules 2-4 and 14-15:
  - dead = 11 dB under speaking level; every dead run is removed
  - keep 15 ms before each word and up to 50 ms of its fade (rule 4: <= 60 ms)
  - every join is a 10 ms fade out + 10 ms fade in (<= 20 ms, rule 2)
  - 2-frame J-cut at each line join (rule 4: 1-3 frames)
  - "gap": frames of held pause after a line (rule 3: serious = 6)
  - "zoom": 1.25 punch-in centred on the face (rule 14)
  - voice +6 dB with a limiter (rule 15)

usage: cut.py plan.json words_dir sdr_dir out_dir
plan.json: {"face": {"a": [x, y], ...}, "lines": [{"clip","a","b","label","gap","zoom"}...]}
"""
import glob, json, os, subprocess, sys, wave
import numpy as np

FPS = 30
SR = 48000
HOP = 0.005
WIN = 0.020
HEAD = 0.010
TAIL = 0.030
JOIN_FADE = 0.010
MIN_DEAD = 0.090   # shorter dips are a word fade or a t/p/k closure, not air
JCUT_FRAMES = 2
DEAD_DB = 11.0

plan_path, words_dir, src_dir, out_dir = sys.argv[1:5]
out_dir = os.path.abspath(out_dir)
REUSE = os.environ.get("REUSE") == "1"  # keep already-rendered pieces
TONEMAP = ("zscale=w=1080:h=1920:f=lanczos,zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
           "tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,fps=30")


def src(clip):
    return glob.glob(os.path.join(src_dir, f"clip-{clip}-*.mov"))[0]

plan = json.load(open(plan_path))
os.makedirs(out_dir, exist_ok=True)


def load_audio(clip):
    path = os.path.join(out_dir, f"{clip}_48k.wav")
    if not os.path.exists(path):
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src(clip),
                        "-map", "0:a:0", "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", path], check=True)
    w = wave.open(path)
    return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0


def frame_db(x):
    hop, win = int(HOP * SR), int(WIN * SR)
    n = max(1, (len(x) - win) // hop + 1)
    idx = np.arange(n)[:, None] * hop + np.arange(win)[None, :]
    rms = np.sqrt(np.mean(x[np.clip(idx, 0, len(x) - 1)] ** 2, axis=1) + 1e-12)
    return 20 * np.log10(rms)


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from level import live_mask, preemph, speaking_level  # noqa: E402

audio = {c: load_audio(c) for c in sorted({l["clip"] for l in plan["lines"]})}
dbs = {c: frame_db(x) for c, x in audio.items()}
pes = {c: frame_db(preemph(x)) for c, x in audio.items()}

# One speaking level for the whole edit (same mic, same session), measured over the
# kept lines only. The checker measures the finished edit the same way.
sel = {c: [slice(int(l["a"] / HOP), int(l["b"] / HOP)) for l in plan["lines"] if l["clip"] == c] for c in audio}
all_db = np.concatenate([dbs[c][s] for c in audio for s in sel[c]])
all_pe = np.concatenate([pes[c][s] for c in audio for s in sel[c]])
lvl_all, lvl_pe_all = speaking_level(all_db, DEAD_DB), speaking_level(all_pe, DEAD_DB)
level = {c: lvl_all for c in audio}
level_pe = {c: lvl_pe_all for c in audio}


def voiced_regions(clip, a, b):
    sl = slice(int(a / HOP), int(b / HOP))
    live, _, _ = live_mask(dbs[clip][sl], pes[clip][sl], DEAD_DB, level[clip], level_pe[clip])
    regions, i, n = [], 0, len(live)
    while i < n:
        if live[i]:
            j = i
            while j < n and live[j]:
                j += 1
            regions.append([a + i * HOP + WIN / 2, a + (j - 1) * HOP + WIN / 2])
            i = j
        else:
            i += 1
    merged = []
    for r in regions:
        if merged and r[0] - merged[-1][1] < MIN_DEAD:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    merged = [r for r in merged if r[1] - r[0] >= 0.06]  # drop clicks and breaths
    out = []
    for s, e in merged:
        s, e = max(a, s - HEAD), min(b, e + TAIL)
        if out and s <= out[-1][1]:
            out[-1][1] = e
        else:
            out.append([s, e])
    return out


# Build pieces on the 30 fps grid so picture and sound stay locked.
pieces = []  # {clip, s, e, line, zoom, hold}
for li, l in enumerate(plan["lines"]):
    regs = voiced_regions(l["clip"], l["a"], l["b"])
    for ri, (s, e) in enumerate(regs):
        # round toward the speech so frame rounding never adds air
        fs, fe = int(np.ceil(s * FPS - 0.3)), int(np.floor(e * FPS + 0.3))
        if fe <= fs:
            continue
        pieces.append({"clip": l["clip"], "fs": fs, "fe": fe, "line": li, "zoom": l.get("zoom", 1.0), "face": l.get("face"),
                       "label": l["label"]})
    gap = int(l.get("gap", 0))
    if gap and pieces:
        pieces[-1]["fe"] += gap  # hold the picture and room tone after a serious line

# Audio: concatenate with 10 ms fades at each join.
fade = int(JOIN_FADE * SR)
ramp_in = np.linspace(0, 1, fade, dtype=np.float32)
chunks = []
for p in pieces:
    x = audio[p["clip"]][p["fs"] * SR // FPS:p["fe"] * SR // FPS].copy()
    need = (p["fe"] - p["fs"]) * SR // FPS
    if len(x) < need:
        x = np.pad(x, (0, need - len(x)))
    x[:fade] *= ramp_in
    x[-fade:] *= ramp_in[::-1]
    chunks.append(x)
voice = np.concatenate(chunks) * 2.0  # +6 dB
peak = np.max(np.abs(voice))
if peak > 0.97:
    # soft limiter: compress only the peaks above 0.9
    over = np.abs(voice) > 0.9
    voice[over] = np.sign(voice[over]) * (0.9 + 0.07 * np.tanh((np.abs(voice[over]) - 0.9) / 0.07))
with wave.open(os.path.join(out_dir, "voice.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(voice, -1, 1) * 32767).astype(np.int16).tobytes())

# Timeline map for captions: every kept word, in output seconds.
words_out, t = [], 0
for p in pieces:
    segs = json.load(open(os.path.join(words_dir, f"{p['clip']}.json")))
    s0, e0 = p["fs"] / FPS, p["fe"] / FPS
    for sg in segs:
        for w in sg["words"]:
            mid = (w["s"] + w["e"]) / 2
            if s0 <= mid < e0:
                words_out.append({"w": w["w"].strip(), "s": t + max(w["s"], s0) - s0,
                                  "e": t + min(w["e"], e0) - s0, "line": p["line"]})
    t += e0 - s0
json.dump({"pieces": pieces, "words": words_out, "level": level, "duration": t},
          open(os.path.join(out_dir, "timeline.json"), "w"), indent=1)
print(f"{len(pieces)} pieces, {t:.2f}s, levels {level}")

if os.environ.get("AUDIO_ONLY") == "1":
    print(f"{len(pieces)} pieces, {sum(p['fe'] - p['fs'] for p in pieces) / FPS:.2f}s, level {lvl_all:.1f} dB, tilted {lvl_pe_all:.1f} dB")
    sys.exit(0)

# Video pieces: shift by the J-cut at each line join (picture changes 2 frames after the sound).
vpieces = [dict(p) for p in pieces]
for i in range(1, len(vpieces)):
    if vpieces[i]["line"] != vpieces[i - 1]["line"] and vpieces[i]["fe"] - vpieces[i]["fs"] > JCUT_FRAMES + 2:
        vpieces[i - 1]["fe"] += JCUT_FRAMES
        vpieces[i]["fs"] += JCUT_FRAMES

face = plan.get("face", {})
listfile = os.path.join(out_dir, "concat.txt")
with open(listfile, "w") as lf:
    for i, p in enumerate(vpieces):
        seg = os.path.join(out_dir, f"v{i:04d}.mp4")
        n = p["fe"] - p["fs"]
        vf = TONEMAP + ",setpts=PTS-STARTPTS"
        if p["zoom"] != 1.0:
            fx, fy = p.get("face") or face.get(p["clip"], [540, 860])
            cw, ch = int(1080 / p["zoom"]) // 2 * 2, int(1920 / p["zoom"]) // 2 * 2
            cx = min(max(fx - cw // 2, 0), 1080 - cw)
            cy = min(max(fy - ch // 2, 0), 1920 - ch)
            vf = TONEMAP + f",crop={cw}:{ch}:{cx}:{cy},scale=1080:1920:flags=lanczos,setpts=PTS-STARTPTS"
        if REUSE and os.path.exists(seg):
            lf.write(f"file '{seg}'\n")
            continue
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{p['fs'] / FPS:.6f}",
                        "-i", src(p["clip"]), "-frames:v", str(n), "-an",
                        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                        "-pix_fmt", "yuv420p", seg], check=True)
        lf.write(f"file '{seg}'\n")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", listfile,
                "-c", "copy", os.path.join(out_dir, "picture.mp4")], check=True)

