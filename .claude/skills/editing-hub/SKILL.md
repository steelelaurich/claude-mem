---
name: editing-hub
description: Steele's personal short-form video editing style. 15 locked rules (captions, cutting, placement, proof, B-roll, sound), the prompts Steele types, the "save that as a rule" loop, and where footage lives in Drive. Use for ANY request to edit, cut, caption, add B-roll, add music or review one of Steele's videos, and whenever Steele says "save that as a rule".
---

# Editing Hub: edit like Steele

Every edit starts from this file. These rules are not suggestions. If a rule and a
generic editing skill disagree, **this file wins**.

Frame is **1080 x 1920** (9:16). All pixel numbers below are in that frame. If the
source is 4K (2160 x 3840), scale down to 1080 x 1920 first, then apply the numbers.

---

## Captions & cutting

### 1. Captions are for reading.
- **2-3 words** at a time. Never end a caption on a weak word (a, the, to, my, and).
- **TikTok Sans, weight 550, 52 px, pure white (#FFFFFF).**
- Soft shadow only: **black at 20% opacity, blur 13 px**.
- No box, no outline, no highlight, no animation. **One line, centred at y 1055**, on the mouth.

### 2. Zero dead space.
- Not a single frame of air. **Every join 20 ms or less.**
- "Dead" = **11 dB under your speaking level**, even a breath or a fading word.
- A script checks every cut: **0 silent frames.**

### 3. Tone decides the gap.
- Normal line: **0 frames**, straight into the next.
- Serious line: **0.2 s (6 frames)** so it lands.
- Joke: **cut mid-word.** The cut is the punchline.

### 4. Tight, never choppy.
- **1-3 frame J-cuts:** you hear the next line just before you see it.
- Keep up to **60 ms** of each word's own fade.
- Never let a sliver of a cut word leak in. It sounds like a stutter.

### 5. Cut words, not just air.
- Cut **repeats, tangents, extra detail, double goodbyes and stumbles.**
- Keep the **best take of every line**. It has to sound like one take.

## Placement & visuals

### 6. Money in full.
- **"$11,500 MRR"**, never "11.5k". Always $ and commas.
- Counts that aren't money stay as spoken: "10k views".

### 7. Stay out of TikTok's way.
- Nothing in the **top 15% (y 0-288)**, the **bottom 20% (y 1536+)** or the
  **button column (x 900+, from y 960 down)**.
- Safe-area check on every frame before it renders.

### 8. Never cover your face.
- Cards go in the band **above your head (y 288 to your hairline)**.
- Lean in? The card gets **smaller, not lower**. One card at a time.
- No punch-in while a card is up.

### 9. Things just appear.
- Cards appear **on their word: full size, final spot, frame 1.**
- No pop, spring, scale, slide, fade or blur-in. They leave on the next jump cut.

### 10. Show the real thing.
- **No emojis.** Anywhere.
- Name an app, article or result? **Show the real one:** real logo, screenshot or UI.

## Proof, B-roll & sound

### 11. Files as files.
- Show folders as a **grid of real thumbnails** with short labels, never word chips.

### 12. Real receipts only.
- Every stat on screen is real. **Never invent a number**, payment, follower count or review.
- No receipt? Keep the line on your face. Label the span ("4 days, Oct 15 - 19").

### 13. Literal B-roll.
- B-roll shows **exactly what you say**, from your own footage. **Never stock.**
- Starts on the first word. A spoken list = **one clip per item, 0.9 s minimum.**
- Darken it to **72%** so the captions read.

### 14. Punch in on your face.
- Most cuts stay at **1.0**. **~1.25x** only on the lines that matter.
- Move your face to the **centre** of the frame. Never while a card is up.

### 15. Voice on top.
- Voice **200% (+6 dB)**. Music **25%** in a quiet intro, **10%** once the drums or lyrics hit.
- Start the song where it gets good, not at 0:00.

---

## The prompts Steele types

Give Claude numbers, not vibes. These are the shorthand. Each one means the full
rule set above applies.

| Steele says | What it means |
|---|---|
| "Caption this. Put a pop-up above my head for each thing I mention, and [song] under it: 25%, then 10% when the drums hit." | Rules 1, 8, 9, 10, 15 in one pass |
| "Cut the dead space and the retakes. Keep the best take of each line. Zero gaps." | Rules 2-5 |
| "Add B-roll from my Drive. When I list things, one clip per item." | Rule 13, pulling from the Drive **B-roll** folder below |
| "Caption 2-3 words at a time. TikTok Sans 550, white, no animation." | Rule 1 |
| "When I name an app or an article, show the real one. Never an emoji." | Rule 10 |
| "Review my hook, find viral hooks like it, then edit this." | Critique the first 3 s, research hooks of the same shape, rewrite or re-cut the hook, then do the full edit |

---

## The loop: make Claude edit like you

Run this on every edit. That's how the 15 rules above were born.

1. **Let Claude edit.** Give it the video and this skill.
2. **Watch it like a viewer.** Where did you get bored, look away or cringe?
3. **Say exactly what's off.** "Autocaps slightly smaller." Not "make it better".
4. **Say "save that as a rule."** Claude writes it into this file, under
   *Rules learned from edits* below, with the date and the number. Every edit after starts from it.

When Steele says "save that as a rule":
- Write it as a short headline plus bullets with exact numbers, like the 15 above.
- Number it 16, 17, ... in order.
- If it changes one of the 15, edit that rule in place and note the date.
- Commit and push the change so the next session has it.

### Rules learned from edits

_None yet. The first one goes here as rule 16._

---

## Where things live

Google Drive, folder **Editing Hub**
(https://drive.google.com/drive/folders/1JzTvviFz4r8xapQi45A7h7vfa_F_lPJZ):

| Folder | Use | Drive ID |
|---|---|---|
| **B-roll** | Steele's own B-roll clips. The only source for rule 13. | `1TUSi0Sa-fL0TG86hADuaqYntJRmkH-7k` |
| **Raw footage** | Unedited takes waiting to be cut | `1MvNEjSqUhoKS5-rFVWyI3bVK8GIkNKDn` |
| **Finished edits** | Rendered videos ready to post | `1VKvaOdNEqw0ZzmbJYqOpRDCd0Frw_Uu0` |

Footage comes in as "Anyone with the link" Drive links. Download the full file with
`https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`.
The environment must allow `drive.google.com` and `drive.usercontent.google.com`.

## Source footage notes

- Shot on iPhone, 2160 x 3840, HEVC, 60 fps. Render the edit at 1080 x 1920.
- Talking to camera, centred, white wall behind, dark t-shirt.

## Steele's voice

See [voice.md](voice.md). Captions use Steele's exact words. Never paraphrase on screen.

---

## How an edit runs (tools/)

Work in a scratch folder, never in the repo. `tools/setup.sh <work>` fetches the
speech model and TikTok Sans 550 once per session.

1. **Download** each Drive link to `<work>/videos/clip-<a|b|c>-<anything>.mov`.
2. **Transcribe**: extract 16 kHz mono audio per clip, then
   `tools/transcribe.py <model> <clip>.wav <clip>.json` (word-level timestamps).
3. **Pick the keepers** (rule 5). Write an edit file like `edits/001-*.py`: one row
   per line in output order with the clip, first-word and last-word times, the exact
   caption text, and options (`zoom` + `face` for a 1.25x punch-in, `gap: 6` for a
   serious line, `cut_mid_last` for a joke). Check unclear words with
   `tools/snippet.py` and fix known mishearings from voice.md.
4. **Cut**: `AUDIO_ONLY=1 tools/cut.py plan.json <work> <work>/videos <out>` builds the
   voice track only. Iterate on this, it takes seconds.
5. **Check, every time** (both must pass before rendering picture):
   - `tools/check_dead.py <out>/voice.wav` must say `silent frames: 0` (rule 2).
   - Re-transcribe `voice.wav` and read it back against the captions
     (`tools/diffwords.py`). A lost or clipped word fails the edit (rule 4).
6. **Render**: `tools/cut.py` without `AUDIO_ONLY`, then `tools/captions.py`, then
   overlay `captions.mov` on `picture.mp4` with `voice.wav`. Run `check_dead.py` on
   the final mp4 too.

What the tools enforce:
- iPhone HDR (HLG) is tone-mapped to SDR (hable) and rendered at 1080 x 1920, 30 fps.
- One speaking level for the whole edit; dead = 11 dB below it on either plain or
  high-frequency-tilted loudness (so s/f/t sounds are never treated as air).
- Dips under 90 ms stay (a word's fade or a t/p/k closure). Each kept word gets 10 ms
  in front and 30 ms of fade; every join is a 10 ms fade out + 10 ms fade in.
- 2-frame J-cut at every line join. Voice +6 dB with a soft limiter.
- Captions: 2-3 words, never ending on a weak word or running across a sentence,
  minimum 4 frames each, held until the next one (no gaps, no animation).
