"""Edit #1: safety razor / Movember. Keeper lines in output order.

Each line: (clip, first word start, last word start, caption text, options).
Caption text is Steele's exact words, spelling fixed (see voice.md).
"""
import json, sys

LINES = [
    ("a", 2.62, 5.10, "You know what time of the year it is? Movember, baby.", {"zoom": 1.25, "face": [560, 880]}),
    ("a", 12.16, 14.84, "I've got new products, right?", {}),
    ("a", 25.70, 27.34, "This is the King C. Gillette.", {}),
    ("a", 16.56, 23.66, "I've never used a safety razor before, so I'm gonna be teaching myself how to use this thing", {}),
    ("a", 28.54, 33.02, "I've been told by a few people on here, I've asked, and they said this is probably the best one for a beginner.", {}),
    ("a", 41.70, 44.60, "But we need a bit of a shave, so let's get it.", {}),
    ("a", 49.20, 51.60, "They come in a little packet like this", {}),
    ("a", 94.66, 95.96, "New one out of the sleeve", {}),
    ("a", 139.26, 143.10, "Because if you put it on the wrong way, your razor's not gonna come through", {}),
    ("c", 30.44, 38.94, "We have got a new shaving kit with our brush and our paste.", {}),
    ("c", 47.16, 50.80, "I'll dab a little bit in hot water, make it nice and warm.", {}),
    ("c", 77.82, 85.32, "The mo's going because it's Movember. That's why. Support all my bros out there, right?", {"gap": 6, "extend": 0.55}),
    ("c", 116.82, 120.28, "You want to keep it on the edge. We start from the top.", {}),
    ("c", 124.08, 125.96, "Have one pass, not too bad.", {}),
    ("c", 138.38, 141.50, "Dang. I actually really enjoy this thing.", {"zoom": 1.25, "face": [380, 1000]}),
    ("c", 145.02, 145.86, "You gotta be careful.", {}),
    ("c", 192.44, 197.08, "My mum would be proud. You look so good with a nice face with no mo.", {}),
    ("c", 199.78, 200.46, "Shut up, Mum.", {}),
    ("c", 208.68, 210.68, "Honestly, I don't know why I didn't start using these things earlier.", {}),
    ("c", 216.06, 217.80, "Gives you such a clean shave, too.", {}),
    ("c", 225.98, 227.80, "Instead of all those shitty razor bumps.", {}),
    # joke: cut mid-word on "once", straight into the undercut (rule 3)
    ("c", 285.32, 287.22, "I don't even think I'll cut myself once.", {"cut_mid_last": True}),
    ("c", 299.14, 299.90, "Nah, I've cut myself.", {"zoom": 1.25, "face": [200, 880]}),
    ("c", 430.18, 432.12, "Fucking perfect, mate. Perfect.", {"zoom": 1.25, "face": [460, 1080]}),
    ("c", 525.24, 528.30, "Now, a bit of aftershave. Just gonna fucking sting.", {}),
    ("c", 540.02, 547.52, "Voila. Nice clean shave, first of November. I'm gonna update you guys on my moustache growth.", {}),
    ("b", 1.60, 2.84, "Yeah, yeah, yeah, yeah!", {"zoom": 1.25, "face": [380, 880]}),
]


def build(words_dir):
    words = {c: [w for s in json.load(open(f"{words_dir}/{c}.json")) for w in s["words"]] for c in "abc"}
    out = []
    for clip, s0, s1, text, opt in LINES:
        ws = words[clip]
        i0 = min(range(len(ws)), key=lambda i: abs(ws[i]["s"] - s0))
        i1 = min(range(len(ws)), key=lambda i: abs(ws[i]["s"] - s1))
        prev_end = ws[i0 - 1]["e"] if i0 > 0 else 0.0
        next_start = ws[i1 + 1]["s"] if i1 + 1 < len(ws) else ws[i1]["e"] + 1.0
        a = max(prev_end, ws[i0]["s"] - 0.15)
        if opt.get("cut_mid_last"):
            b = ws[i1]["s"] + 0.6 * (ws[i1]["e"] - ws[i1]["s"])
        else:
            b = min(next_start, ws[i1]["e"] + 0.15 + opt.get("extend", 0))
        out.append({"clip": clip, "a": round(a, 3), "b": round(b, 3), "label": text,
                    "zoom": opt.get("zoom", 1.0), "face": opt.get("face"), "gap": opt.get("gap", 0)})
    return out


if __name__ == "__main__":
    lines = build(sys.argv[1])
    face = {"a": [440, 900], "b": [540, 860], "c": [540, 860]}
    json.dump({"face": face, "lines": lines}, open(sys.argv[2], "w"), indent=1)
    print(len(lines), "lines")
