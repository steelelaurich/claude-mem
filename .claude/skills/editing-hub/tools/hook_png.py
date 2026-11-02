"""Render the text hook: black text on white boxes, top of frame, as a 1080x1920 PNG.

Placement follows rules 7 and 8: nothing above y 288 (TikTok's top 15%), and the card
sits in the band above the head. Each line gets its own white box, like TikTok's own
text style. No animation (rule 9): it is on screen full size from frame 1.

usage: hook_png.py out.png font.ttf "line one" ["line two" ...]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
TOP = 300          # first box starts just under the y 288 safe line
SIZE = 56
PAD_X, PAD_Y = 26, 14
GAP = 6            # boxes touch-ish, like stacked TikTok text
RADIUS = 18
MAX_W = 1080 - 2 * 60


def render(out_path, font_path, lines, size=SIZE, top=TOP):
    font = ImageFont.truetype(font_path, size)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    asc, desc = font.getmetrics()
    line_h = asc + desc
    y = top
    for text in lines:
        l, _, r, _ = font.getbbox(text)
        tw = r - l
        bw = tw + 2 * PAD_X
        if bw > MAX_W:
            raise SystemExit(f"hook line too wide ({bw}px): {text!r}")
        x0 = (W - bw) // 2
        d.rounded_rectangle([x0, y, x0 + bw, y + line_h + 2 * PAD_Y], RADIUS, fill=(255, 255, 255, 255))
        d.text((x0 + PAD_X - l, y + PAD_Y), text, font=font, fill=(0, 0, 0, 255))
        y += line_h + 2 * PAD_Y + GAP
    img.save(out_path)
    return y - GAP  # bottom edge


if __name__ == "__main__":
    print(render(sys.argv[1], sys.argv[2], sys.argv[3:]))
