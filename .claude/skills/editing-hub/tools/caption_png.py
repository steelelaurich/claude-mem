"""Render one caption as a 1080x1920 transparent PNG, per Steele's rule 1.

TikTok Sans 550, 52 px, pure white, one line centred at y 1055.
Soft shadow only: black 20% opacity, blur 13 px. No box, no outline.
"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
Y_CENTRE = 1055
SIZE = 52
SHADOW_ALPHA = int(255 * 0.20)
SHADOW_BLUR = 13  # CSS-style blur radius; Gaussian sigma = radius / 2


def render(text, out_path, font_path):
    font = ImageFont.truetype(font_path, SIZE)
    l, t, r, b = font.getbbox(text, anchor="mm")
    width = r - l
    # Rule 7: below y 960 nothing may cross x 900, so a centred line must be <= 720 px wide.
    if width > 720:
        raise SystemExit(f"caption too wide ({width}px): {text!r}")

    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).text((W // 2, Y_CENTRE), text, font=font, fill=255, anchor="mm")
    shadow = shadow.filter(ImageFilter.GaussianBlur(SHADOW_BLUR / 2))
    shadow = shadow.point(lambda v: v * SHADOW_ALPHA // 255)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.putalpha(shadow)
    ImageDraw.Draw(img).text((W // 2, Y_CENTRE), text, font=font, fill=(255, 255, 255, 255), anchor="mm")
    img.save(out_path)
    return width


if __name__ == "__main__":
    print(render(sys.argv[1], sys.argv[2], sys.argv[3]))
