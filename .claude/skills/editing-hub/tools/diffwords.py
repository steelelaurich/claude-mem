"""Compare the re-transcribed edit with the caption script; print words that went missing."""
import difflib, json, re, sys
norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
plan = json.load(open(sys.argv[1]))
heard = [norm(w["w"]) for s in json.load(open(sys.argv[2])) for w in s["words"]]
for li, l in enumerate(plan["lines"]):
    want = [norm(t) for t in l["label"].split()]
    best = max((difflib.SequenceMatcher(a=want, b=heard[i:i + len(want) + 4], autojunk=False).ratio(), i)
               for i in range(max(1, len(heard) - len(want) + 1)))
    seg = heard[best[1]:best[1] + len(want) + 4]
    sm = difflib.SequenceMatcher(a=want, b=seg, autojunk=False)
    miss = [want[i] for op, i1, i2, j1, j2 in sm.get_opcodes() if op in ("delete", "replace") for i in range(i1, i2)]
    flag = "  " if not miss else "!!"
    print(f"{flag} {li:2d} {best[0]:.2f} {l['label'][:60]:60s} missing: {' '.join(miss)}")
