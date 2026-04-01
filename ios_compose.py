#!/usr/bin/env python3
"""
Apple App Store Screenshot Composer
Composites headline text, device frame template, and app screenshot
into pixel-perfect images for App Store Connect.

Follows Apple App Store screenshot guidelines:
  - iPhone 6.7"  → 1290×2796 (required for iPhone 16 Pro Max / 15 Pro Max)
  - iPhone 6.5"  → 1242×2688 (iPhone 11 Pro Max / XS Max)
  - iPhone 5.5"  → 1242×2208 (iPhone 8 Plus — legacy)
  - iPhone SE    → 750×1334  (iPhone SE 3rd gen / 8)
  - iPad 12.9"   → 2048×2732 (iPad Pro 12.9" — required for iPad)
  - iPad 11"     → 1668×2388 (iPad Pro 11" / Air)

Apple requires at least one screenshot for the 6.7" slot (or 6.5" as fallback).
iPad screenshots are separate and required if the app supports iPad.
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops

# ── Font — SF Pro Display Black (Apple's native typeface) ───────────
_FONT_CANDIDATES = [
    "/Library/Fonts/SF-Pro-Display-Black.otf",
    "/Library/Fonts/SF-Pro-Display-Bold.otf",
    "/System/Library/Fonts/Helvetica.ttc",
]
FONT_PATH = next((f for f in _FONT_CANDIDATES if os.path.exists(f)), _FONT_CANDIDATES[-1])

# ── Typography constants ─────────────────────────────────────────────
VERB_SIZE_MAX = 256
VERB_SIZE_MIN = 140
DESC_SIZE_RATIO = 0.48   # desc font is ~48% of verb font size
VERB_DESC_GAP = 24
DESC_LINE_GAP = 20
TEXT_TOP = 200           # y-offset for text block start
MAX_TEXT_W_RATIO = 0.88  # text stays within 88% of canvas width


# ── iOS device profiles ──────────────────────────────────────────────
# Each profile defines canvas size, device frame dimensions, and frame asset.
# Apple App Store Connect accepted dimensions (portrait):
#   6.7"  → 1290×2796  (iPhone 16 Pro Max, 15 Pro Max — primary required slot)
#   6.5"  → 1242×2688  (iPhone 11 Pro Max, XS Max)
#   5.5"  → 1242×2208  (iPhone 8 Plus — legacy, still accepted)
#   SE    → 750×1334   (iPhone SE 3rd gen / iPhone 8)
#   iPad 12.9" → 2048×2732
#   iPad 11"   → 1668×2388
IOS_DEVICE_PROFILES = {
    "iphone_67": {
        "canvas_w": 1290,
        "canvas_h": 2796,
        "device_w": 1030,
        "device_y": 720,
        "bezel": 15,
        "screen_corner_r": 62,
        "frame_path": "assets/ios_device_frame_iphone.png",
        "store_slot": "iPhone 6.7\" (required — iPhone 16 Pro Max / 15 Pro Max)",
    },
    "iphone_65": {
        "canvas_w": 1242,
        "canvas_h": 2688,
        "device_w": 990,
        "device_y": 700,
        "bezel": 15,
        "screen_corner_r": 58,
        "frame_path": "assets/ios_device_frame_iphone.png",
        "store_slot": "iPhone 6.5\" (iPhone 11 Pro Max / XS Max)",
    },
    "iphone_55": {
        "canvas_w": 1242,
        "canvas_h": 2208,
        "device_w": 990,
        "device_y": 620,
        "bezel": 15,
        "screen_corner_r": 50,
        "frame_path": "assets/ios_device_frame_iphone.png",
        "store_slot": "iPhone 5.5\" (iPhone 8 Plus — legacy)",
    },
    "iphone_se": {
        "canvas_w": 750,
        "canvas_h": 1334,
        "device_w": 580,
        "device_y": 380,
        "bezel": 14,
        "screen_corner_r": 8,
        "frame_path": "assets/ios_device_frame_iphone_se.png",
        "store_slot": "iPhone 4.7\" SE (iPhone SE 3rd gen / iPhone 8)",
    },
    "ipad_129": {
        "canvas_w": 2048,
        "canvas_h": 2732,
        "device_w": 1640,
        "device_y": 680,
        "bezel": 18,
        "screen_corner_r": 18,
        "frame_path": "assets/ios_device_frame_ipad.png",
        "store_slot": "iPad 12.9\" Pro (required for iPad apps)",
    },
    "ipad_11": {
        "canvas_w": 1668,
        "canvas_h": 2388,
        "device_w": 1340,
        "device_y": 600,
        "bezel": 16,
        "screen_corner_r": 16,
        "frame_path": "assets/ios_device_frame_ipad.png",
        "store_slot": "iPad 11\" Pro / Air",
    },
}


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i: i + 2], 16) for i in (0, 2, 4))


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


def fit_font(text, max_w, size_max, size_min):
    """Return the largest font size where text fits within max_w."""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for size in range(size_max, size_min - 1, -4):
        font = ImageFont.truetype(FONT_PATH, size)
        bbox = dummy.textbbox((0, 0), text, font=font)
        if (bbox[2] - bbox[0]) <= max_w:
            return font
    return ImageFont.truetype(FONT_PATH, size_min)


def draw_centered(draw, y, text, font, canvas_w, max_w=None):
    lines = word_wrap(draw, text, font, max_w) if max_w else [text]
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        draw.text((canvas_w // 2, y - bbox[1]), line, fill="white", font=font, anchor="mt")
        y += h + DESC_LINE_GAP
    return y


def compose(bg_hex, verb, desc, screenshot_path, output_path, device_type="iphone_67"):
    if device_type not in IOS_DEVICE_PROFILES:
        raise ValueError(f"Unknown iOS device type '{device_type}'. "
                         f"Choose from: {', '.join(IOS_DEVICE_PROFILES)}")

    profile = IOS_DEVICE_PROFILES[device_type]
    canvas_w = profile["canvas_w"]
    canvas_h = profile["canvas_h"]
    device_w = profile["device_w"]
    device_y = profile["device_y"]
    bezel = profile["bezel"]
    screen_corner_r = profile["screen_corner_r"]
    screen_w = device_w - 2 * bezel

    # Scale typography proportionally to canvas width
    scale = canvas_w / 1290
    verb_size_max = round(VERB_SIZE_MAX * scale)
    verb_size_min = round(VERB_SIZE_MIN * scale)
    max_verb_w = int(canvas_w * MAX_TEXT_W_RATIO)
    max_text_w = int(canvas_w * MAX_TEXT_W_RATIO)

    frame_path = os.path.join(os.path.dirname(__file__), profile["frame_path"])
    if not os.path.exists(frame_path):
        raise FileNotFoundError(
            f"Device frame not found: {frame_path}\n"
            f"Run: python3 generate_frame.py --type {_frame_type_for(device_type)}"
        )

    bg = hex_to_rgb(bg_hex)

    # ── 1. Canvas ────────────────────────────────────────────────────
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (*bg, 255))
    draw = ImageDraw.Draw(canvas)

    # ── 2. Fonts ─────────────────────────────────────────────────────
    verb_font = fit_font(verb.upper(), max_verb_w, verb_size_max, verb_size_min)
    # Derive desc size from verb font size
    verb_actual_size = verb_font.size
    desc_size = max(round(verb_actual_size * DESC_SIZE_RATIO), round(80 * scale))
    desc_font = ImageFont.truetype(FONT_PATH, desc_size)

    # ── 3. Draw text ─────────────────────────────────────────────────
    y = TEXT_TOP
    y = draw_centered(draw, y, verb.upper(), verb_font, canvas_w)
    y += VERB_DESC_GAP
    draw_centered(draw, y, desc.upper(), desc_font, canvas_w, max_w=max_text_w)

    device_x = (canvas_w - device_w) // 2
    screen_x = device_x + bezel
    screen_y = device_y + bezel

    # ── 4. Screenshot into screen area ───────────────────────────────
    shot = Image.open(screenshot_path).convert("RGBA")
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
    # Scale frame to match device_w if needed
    if frame_template.width != device_w:
        ratio = device_w / frame_template.width
        frame_template = frame_template.resize(
            (device_w, int(frame_template.height * ratio)), Image.LANCZOS
        )

    frame_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    frame_layer.paste(frame_template, (device_x, device_y))
    canvas = Image.alpha_composite(canvas, frame_layer)

    # ── 6. Save ───────────────────────────────────────────────────────
    canvas.convert("RGB").save(output_path, "PNG")
    print(f"✓ {output_path} ({canvas_w}×{canvas_h}) — {profile['store_slot']}")


def _frame_type_for(device_type):
    """Map device profile key to generate_frame.py --type argument."""
    mapping = {
        "iphone_67": "iphone",
        "iphone_65": "iphone",
        "iphone_55": "iphone",
        "iphone_se": "iphone_se",
        "ipad_129": "ipad",
        "ipad_11": "ipad",
    }
    return mapping.get(device_type, "iphone")


def main():
    p = argparse.ArgumentParser(
        description="Compose Apple App Store screenshot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(
            f"  {k:12s} → {v['store_slot']}"
            for k, v in IOS_DEVICE_PROFILES.items()
        ),
    )
    p.add_argument("--bg", required=True, help="Background hex colour (#007AFF)")
    p.add_argument("--verb", required=True, help="Action verb headline (TRACK)")
    p.add_argument("--desc", required=True, help="Benefit descriptor (YOUR CARD PRICES)")
    p.add_argument("--screenshot", required=True, help="iOS Simulator screenshot path")
    p.add_argument("--output", required=True, help="Output file path")
    p.add_argument(
        "--device-type",
        choices=list(IOS_DEVICE_PROFILES.keys()),
        default="iphone_67",
        help="iOS device slot (default: iphone_67 — 1290×2796)",
    )
    args = p.parse_args()
    compose(args.bg, args.verb, args.desc, args.screenshot, args.output, args.device_type)


if __name__ == "__main__":
    main()
