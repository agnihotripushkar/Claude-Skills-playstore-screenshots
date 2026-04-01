#!/usr/bin/env python3
"""
Google Play Store Screenshot Composer
Composites headline text, device frame template, and app screenshot
into a pixel-perfect image for Google Play Console.

The device frame is positioned dynamically based on text height,
matching the proportions seen in professional Play Store screenshots.
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops

# ── Default Canvas (phone 9:16) ──────────────────────────────────────
CANVAS_W = 1080
CANVAS_H = 1920

# ── Device template constants (must match generate_frame.py) ────────
DEVICE_W = 900
BEZEL = 12
SCREEN_W = DEVICE_W - 2 * BEZEL    # 876
SCREEN_CORNER_R = 40

# ── Layout ───────────────────────────────────────────────────────────
DEVICE_Y = 620                       # device top position (fixed)
MIN_TEXT_DEVICE_GAP = 40             # minimum gap between text bottom and device top

# ── Typography ───────────────────────────────────────────────────────
VERB_SIZE_MAX = 180
VERB_SIZE_MIN = 110
DESC_SIZE = 90
VERB_DESC_GAP = 20
DESC_LINE_GAP = 24
MAX_TEXT_W = int(CANVAS_W * 0.92)
MAX_VERB_W = int(CANVAS_W * 0.92)

# Try Google Sans, then Roboto, then system fallback
_FONT_CANDIDATES = [
    "/Library/Fonts/GoogleSans-Bold.ttf",
    "/Library/Fonts/Roboto-Black.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]
FONT_PATH = next((f for f in _FONT_CANDIDATES if os.path.exists(f)), _FONT_CANDIDATES[-1])

FRAME_PATH = os.path.join(os.path.dirname(__file__), "assets", "device_frame.png")


# ── Device type profiles ─────────────────────────────────────────────
DEVICE_PROFILES = {
    "phone": {
        "canvas_w": 1080,
        "canvas_h": 1920,
        "device_w": 900,
        "device_y": 620,
        "bezel": 12,
        "screen_corner_r": 40,
        "frame_path": "assets/device_frame.png",
    },
    "foldable_cover": {
        "canvas_w": 1080,
        "canvas_h": 2092,
        "device_w": 860,
        "device_y": 650,
        "bezel": 12,
        "screen_corner_r": 48,
        "frame_path": "assets/device_frame_foldable_cover.png",
    },
    "foldable_inner": {
        "canvas_w": 2208,
        "canvas_h": 1840,
        "device_w": 1600,
        "device_y": 520,
        "bezel": 14,
        "screen_corner_r": 20,
        "frame_path": "assets/device_frame_foldable_inner.png",
    },
}


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def word_wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(text, max_w, size_max, size_min, font_path):
    """Return the largest font size where text fits within max_w."""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for size in range(size_max, size_min - 1, -4):
        font = ImageFont.truetype(font_path, size)
        bbox = dummy.textbbox((0, 0), text, font=font)
        if (bbox[2] - bbox[0]) <= max_w:
            return font
    return ImageFont.truetype(font_path, size_min)


def draw_centered(draw, y, text, font, canvas_w, max_w=None):
    lines = word_wrap(draw, text, font, max_w) if max_w else [text]
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        draw.text((canvas_w // 2, y - bbox[1]), line, fill="white", font=font, anchor="mt")
        y += h + DESC_LINE_GAP
    return y


def compose(bg_hex, verb, desc, screenshot_path, output_path, device_type="phone"):
    profile = DEVICE_PROFILES[device_type]

    canvas_w = profile["canvas_w"]
    canvas_h = profile["canvas_h"]
    device_w = profile["device_w"]
    device_y = profile["device_y"]
    bezel = profile["bezel"]
    screen_corner_r = profile["screen_corner_r"]
    screen_w = device_w - 2 * bezel

    # Scale typography for non-standard canvas widths
    scale = canvas_w / 1080
    verb_size_max = round(VERB_SIZE_MAX * scale)
    verb_size_min = round(VERB_SIZE_MIN * scale)
    desc_size = round(DESC_SIZE * scale)
    max_verb_w = int(canvas_w * 0.92)
    max_text_w = int(canvas_w * 0.92)

    frame_path = os.path.join(os.path.dirname(__file__), profile["frame_path"])

    bg = hex_to_rgb(bg_hex)

    # ── 1. Canvas ────────────────────────────────────────────────────
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (*bg, 255))
    draw = ImageDraw.Draw(canvas)

    # ── 2. Fonts ─────────────────────────────────────────────────────
    verb_font = fit_font(verb.upper(), max_verb_w, verb_size_max, verb_size_min, FONT_PATH)
    desc_font = ImageFont.truetype(FONT_PATH, desc_size)

    # ── 3. Draw text ─────────────────────────────────────────────────
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    text_top = 200

    y = text_top
    y = draw_centered(draw, y, verb.upper(), verb_font, canvas_w)
    y += VERB_DESC_GAP
    draw_centered(draw, y, desc.upper(), desc_font, canvas_w, max_w=max_text_w)

    device_x = (canvas_w - device_w) // 2
    screen_x = device_x + bezel
    screen_y = device_y + bezel

    # ── 4. Screenshot into screen area ───────────────────────────────
    shot = Image.open(screenshot_path).convert("RGBA")

    # Scale to fill screen width
    scale_factor = screen_w / shot.width
    sc_w = screen_w
    sc_h = int(shot.height * scale_factor)
    shot = shot.resize((sc_w, sc_h), Image.LANCZOS)

    # Screen extends to bottom of canvas + overflow
    screen_h = canvas_h - screen_y + 500

    # Screen mask (rounded rect)
    scr_mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(scr_mask).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=screen_corner_r,
        fill=255,
    )

    # Black screen bg + screenshot on top
    scr_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(scr_layer).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=screen_corner_r,
        fill=(0, 0, 0, 255),
    )
    scr_layer.paste(shot, (screen_x, screen_y))
    scr_layer.putalpha(scr_mask)

    canvas = Image.alpha_composite(canvas, scr_layer)

    # ── 5. Device frame template ──────────────────────────────────────
    frame_template = Image.open(frame_path).convert("RGBA")

    frame_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    frame_layer.paste(frame_template, (device_x, device_y))
    canvas = Image.alpha_composite(canvas, frame_layer)

    # ── 6. Save ───────────────────────────────────────────────────────
    canvas.convert("RGB").save(output_path, "PNG")
    print(f"✓ {output_path} ({canvas_w}×{canvas_h})")


def main():
    p = argparse.ArgumentParser(description="Compose Google Play Store screenshot")
    p.add_argument("--bg", required=True, help="Background hex colour (#E31837)")
    p.add_argument("--verb", required=True, help="Action verb (TRACK)")
    p.add_argument("--desc", required=True, help="Benefit descriptor (TRADING CARD PRICES)")
    p.add_argument("--screenshot", required=True, help="Android emulator screenshot path")
    p.add_argument("--output", required=True, help="Output file path")
    p.add_argument(
        "--device-type",
        choices=["phone", "foldable_cover", "foldable_inner"],
        default="phone",
        help=(
            "Android device type: "
            "phone (1080x1920, default), "
            "foldable_cover (1080x2092), "
            "foldable_inner (2208x1840)"
        ),
    )
    args = p.parse_args()

    compose(args.bg, args.verb, args.desc, args.screenshot, args.output, args.device_type)


if __name__ == "__main__":
    main()
