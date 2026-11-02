"""Build the caption track (rule 1) from the cut timeline.

usage: captions.py plan.json render_dir font.ttf
Writes render_dir/captions.mov (PNG codec with alpha, 30 fps) and captions.json.
"""
import difflib, json, os, re, subprocess, sys
from PIL import ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from caption_png import render  # noqa: E402

FPS = 30
# Rule 1's weak words (a, the, to, my, and) plus the same kind of dangling word.
WEAK = {"a", "an", "the", "to", "my", "and", "of", "i", "your", "our", "in", "on", "for", "with"}

plan_path, rdir, font = sys.argv[1:4]
rdir = os.path.abspath(rdir)
plan = json.load(open(plan_path))
tl = json.load(open(os.path.join(rdir, "timeline.json")))
fnt = ImageFont.truetype(font, 52)


def norm(t):
    return re.sub(r"[^a-z0-9']", "", t.lower())


def width(text):
    l, _, r, _ = fnt.getbbox(text)
    return r - l


def chunk(tokens):
    """Split a line into 2-3 word captions, never ending on a weak word."""
    n = len(tokens)
    best = [(0, [])] + [(1e9, None)] * n
    for i in range(1, n + 1):
        for k in (1, 2, 3):
            if i - k < 0 or best[i - k][1] is None:
                continue
            words = tokens[i - k:i]
            cost = {1: 6, 2: 0.5, 3: 0}[k]
            if norm(words[-1]) in WEAK and i != n:
                cost += 20
            if any(w[-1] in ".?!" and len(norm(w)) > 1 for w in words[:-1]):
                cost += 8  # don't run a caption across a sentence break
            if width(" ".join(words)) > 700:
                cost += 100
            c = best[i - k][0] + cost
            if c < best[i][0]:
                best[i] = (c, best[i - k][1] + [(i - k, i)])
    return best[n][1]


# Each line's span on the output timeline, from the cut pieces.
line_span, t = {}, 0.0
for p in tl["pieces"]:
    d = (p["fe"] - p["fs"]) / FPS
    s, e = line_span.get(p["line"], (t, t))
    line_span[p["line"]] = (s, t + d)
    t += d

events = []  # (start, text)
for li, line in enumerate(plan["lines"]):
    heard = [w for w in tl["words"] if w["line"] == li]
    toks = line["label"].split()
    times = [None] * len(toks)
    sm = difflib.SequenceMatcher(a=[norm(w["w"]) for w in heard], b=[norm(t) for t in toks], autojunk=False)
    for blk in sm.get_matching_blocks():
        for j in range(blk.size):
            times[blk.b + j] = heard[blk.a + j]["s"]
    line_start, line_end = line_span[li]
    # interpolate unmatched words between their neighbours
    known = [(i, t) for i, t in enumerate(times) if t is not None]
    for i in range(len(toks)):
        if times[i] is None:
            prev = max([(j, t) for j, t in known if j < i], default=(-1, line_start))
            nxt = min([(j, t) for j, t in known if j > i], default=(len(toks), line_end))
            times[i] = prev[1] + (nxt[1] - prev[1]) * (i - prev[0]) / (nxt[0] - prev[0])
    # keep words in order and give every caption at least 4 frames
    for i in range(1, len(times)):
        times[i] = max(times[i], times[i - 1])
    for s, e in chunk(toks):
        text = " ".join(toks[s:e]).rstrip(".,")
        events.append((times[s], text))

# The first caption starts on frame 1; each holds until the next one (no gaps, no animation).
events[0] = (0.0, events[0][1])
for i in range(1, len(events)):
    if events[i][0] < events[i - 1][0] + 4 / FPS:
        events[i] = (events[i - 1][0] + 4 / FPS, events[i][1])
dur = tl["duration"]
os.makedirs(os.path.join(rdir, "caps"), exist_ok=True)
lst = []
for i, (s, text) in enumerate(events):
    e = events[i + 1][0] if i + 1 < len(events) else dur
    fs, fe = round(s * FPS), round(e * FPS)
    if fe <= fs:
        continue
    png = os.path.join(rdir, "caps", f"c{i:03d}.png")
    render(text, png, font)
    lst.append({"text": text, "s": fs / FPS, "e": fe / FPS, "png": png})
# fix frame-rounding overlaps
for a, b in zip(lst, lst[1:]):
    a["e"] = b["s"]
json.dump(lst, open(os.path.join(rdir, "captions.json"), "w"), indent=1)

with open(os.path.join(rdir, "caps.txt"), "w") as f:
    for c in lst:
        f.write(f"file '{c['png']}'\nduration {c['e'] - c['s']:.6f}\n")
    f.write(f"file '{lst[-1]['png']}'\n")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i",
                os.path.join(rdir, "caps.txt"), "-vf", f"fps={FPS},format=rgba", "-c:v", "png",
                "-t", f"{dur:.6f}", os.path.join(rdir, "captions.mov")], check=True)
print(f"{len(lst)} captions")
for c in lst:
    print(f"{c['s']:6.2f}-{c['e']:6.2f}  {c['text']}")
