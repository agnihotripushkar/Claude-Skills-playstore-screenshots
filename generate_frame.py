#!/usr/bin/env python3
"""
Generate Android device frame template PNGs.
Outputs standalone device images (not positioned on canvas).
compose.py positions these dynamically based on text height.

Supported frame types:
  phone           → assets/device_frame.png
  foldable_inner  → assets/device_frame_foldable_inner.png
  foldable_cover  → assets/device_frame_foldable_cover.png
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageChops


# ────────────────────────────────────────────────────────────────────
# Standard Android Phone frame
# ────────────────────────────────────────────────────────────────────
def generate_phone():
    DEVICE_W = 900
    DEVICE_H = 2600
    DEVICE_CORNER_R = 55
    BEZEL = 12
    SCREEN_CORNER_R = 40

    # Punch-hole camera
    PH_DIAMETER = 52
    PH_TOP_OFFSET = 16   # from top of screen

    SCREEN_W = DEVICE_W - 2 * BEZEL
    SCREEN_H = DEVICE_H - 2 * BEZEL

    frame = Image.new("RGBA", (DEVICE_W, DEVICE_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # ── Device body ─────────────────────────────────────────────────
    fd.rounded_rectangle(
        [0, 0, DEVICE_W - 1, DEVICE_H - 1],
        radius=DEVICE_CORNER_R,
        fill=(28, 28, 28, 255),
    )
    fd.rounded_rectangle(
        [1, 1, DEVICE_W - 2, DEVICE_H - 2],
        radius=DEVICE_CORNER_R - 1,
        fill=(18, 18, 18, 255),
    )

    # ── Screen cutout (transparent) ─────────────────────────────────
    screen_x = BEZEL
    screen_y = BEZEL

    cutout = Image.new("L", (DEVICE_W, DEVICE_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + SCREEN_W, screen_y + SCREEN_H],
        radius=SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # ── Punch-hole camera (top-center of screen) ─────────────────────
    ph_cx = DEVICE_W // 2
    ph_cy = screen_y + PH_TOP_OFFSET + PH_DIAMETER // 2
    ph_r = PH_DIAMETER // 2
    ImageDraw.Draw(frame).ellipse(
        [ph_cx - ph_r, ph_cy - ph_r, ph_cx + ph_r, ph_cy + ph_r],
        fill=(0, 0, 0, 255),
    )

    # ── Side buttons (Android — all on RIGHT side) ───────────────────
    btn_color = (22, 22, 22, 255)
    fd2 = ImageDraw.Draw(frame)

    # Power button (right side)
    fd2.rounded_rectangle(
        [DEVICE_W, 380, DEVICE_W + 4, 520],
        radius=2, fill=btn_color,
    )
    # Volume up (right side)
    fd2.rounded_rectangle(
        [DEVICE_W, 280, DEVICE_W + 4, 370],
        radius=2, fill=btn_color,
    )
    # Volume down (right side)
    fd2.rounded_rectangle(
        [DEVICE_W, 385, DEVICE_W + 4, 475],
        radius=2, fill=btn_color,
    )

    out = "assets/device_frame.png"
    os.makedirs("assets", exist_ok=True)
    frame.save(out, "PNG")
    print(f"✓ {out} ({DEVICE_W}×{DEVICE_H})")
    print(f"  BEZEL={BEZEL}, SCREEN_W={SCREEN_W}, SCREEN_H={SCREEN_H}")
    print(f"  SCREEN_CORNER_R={SCREEN_CORNER_R}")


# ────────────────────────────────────────────────────────────────────
# Foldable inner screen frame (landscape-ish unfolded display)
# ────────────────────────────────────────────────────────────────────
def generate_foldable_inner():
    DEVICE_W = 1600
    DEVICE_H = 1400
    DEVICE_CORNER_R = 30
    BEZEL = 14
    SCREEN_CORNER_R = 20

    # Punch-hole camera
    PH_DIAMETER = 48
    PH_TOP_OFFSET = 14

    SCREEN_W = DEVICE_W - 2 * BEZEL
    SCREEN_H = DEVICE_H - 2 * BEZEL

    frame = Image.new("RGBA", (DEVICE_W, DEVICE_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # ── Device body ─────────────────────────────────────────────────
    fd.rounded_rectangle(
        [0, 0, DEVICE_W - 1, DEVICE_H - 1],
        radius=DEVICE_CORNER_R,
        fill=(28, 28, 28, 255),
    )
    fd.rounded_rectangle(
        [1, 1, DEVICE_W - 2, DEVICE_H - 2],
        radius=DEVICE_CORNER_R - 1,
        fill=(18, 18, 18, 255),
    )

    # ── Screen cutout (transparent) ─────────────────────────────────
    screen_x = BEZEL
    screen_y = BEZEL

    cutout = Image.new("L", (DEVICE_W, DEVICE_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + SCREEN_W, screen_y + SCREEN_H],
        radius=SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # ── Vertical crease line (subtle, down center of screen) ─────────
    crease_x = DEVICE_W // 2
    crease_layer = Image.new("RGBA", (DEVICE_W, DEVICE_H), (0, 0, 0, 0))
    ImageDraw.Draw(crease_layer).rectangle(
        [crease_x - 1, screen_y, crease_x + 1, screen_y + SCREEN_H],
        fill=(80, 80, 80, 40),
    )
    frame = Image.alpha_composite(frame, crease_layer)

    # ── Punch-hole camera (top-center of screen) ─────────────────────
    ph_cx = DEVICE_W // 2
    ph_cy = screen_y + PH_TOP_OFFSET + PH_DIAMETER // 2
    ph_r = PH_DIAMETER // 2
    ImageDraw.Draw(frame).ellipse(
        [ph_cx - ph_r, ph_cy - ph_r, ph_cx + ph_r, ph_cy + ph_r],
        fill=(0, 0, 0, 255),
    )

    # ── Side buttons (right side) ────────────────────────────────────
    btn_color = (22, 22, 22, 255)
    fd2 = ImageDraw.Draw(frame)

    # Power button
    fd2.rounded_rectangle(
        [DEVICE_W, 300, DEVICE_W + 4, 420],
        radius=2, fill=btn_color,
    )
    # Volume up
    fd2.rounded_rectangle(
        [DEVICE_W, 200, DEVICE_W + 4, 280],
        radius=2, fill=btn_color,
    )
    # Volume down
    fd2.rounded_rectangle(
        [DEVICE_W, 295, DEVICE_W + 4, 375],
        radius=2, fill=btn_color,
    )

    out = "assets/device_frame_foldable_inner.png"
    os.makedirs("assets", exist_ok=True)
    frame.save(out, "PNG")
    print(f"✓ {out} ({DEVICE_W}×{DEVICE_H})")
    print(f"  BEZEL={BEZEL}, SCREEN_W={SCREEN_W}, SCREEN_H={SCREEN_H}")
    print(f"  SCREEN_CORNER_R={SCREEN_CORNER_R}")


# ────────────────────────────────────────────────────────────────────
# Foldable cover screen frame (tall, narrower outer display)
# ────────────────────────────────────────────────────────────────────
def generate_foldable_cover():
    DEVICE_W = 860
    DEVICE_H = 2200
    DEVICE_CORNER_R = 60
    BEZEL = 12
    SCREEN_CORNER_R = 48

    # Punch-hole camera
    PH_DIAMETER = 46
    PH_TOP_OFFSET = 15

    SCREEN_W = DEVICE_W - 2 * BEZEL
    SCREEN_H = DEVICE_H - 2 * BEZEL

    frame = Image.new("RGBA", (DEVICE_W, DEVICE_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # ── Device body ─────────────────────────────────────────────────
    fd.rounded_rectangle(
        [0, 0, DEVICE_W - 1, DEVICE_H - 1],
        radius=DEVICE_CORNER_R,
        fill=(28, 28, 28, 255),
    )
    fd.rounded_rectangle(
        [1, 1, DEVICE_W - 2, DEVICE_H - 2],
        radius=DEVICE_CORNER_R - 1,
        fill=(18, 18, 18, 255),
    )

    # ── Screen cutout (transparent) ─────────────────────────────────
    screen_x = BEZEL
    screen_y = BEZEL

    cutout = Image.new("L", (DEVICE_W, DEVICE_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + SCREEN_W, screen_y + SCREEN_H],
        radius=SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # ── Punch-hole camera (top-center of screen) ─────────────────────
    ph_cx = DEVICE_W // 2
    ph_cy = screen_y + PH_TOP_OFFSET + PH_DIAMETER // 2
    ph_r = PH_DIAMETER // 2
    ImageDraw.Draw(frame).ellipse(
        [ph_cx - ph_r, ph_cy - ph_r, ph_cx + ph_r, ph_cy + ph_r],
        fill=(0, 0, 0, 255),
    )

    # ── Side buttons (right side) ────────────────────────────────────
    btn_color = (22, 22, 22, 255)
    fd2 = ImageDraw.Draw(frame)

    # Power button
    fd2.rounded_rectangle(
        [DEVICE_W, 360, DEVICE_W + 4, 490],
        radius=2, fill=btn_color,
    )
    # Volume up
    fd2.rounded_rectangle(
        [DEVICE_W, 260, DEVICE_W + 4, 345],
        radius=2, fill=btn_color,
    )
    # Volume down
    fd2.rounded_rectangle(
        [DEVICE_W, 360, DEVICE_W + 4, 445],
        radius=2, fill=btn_color,
    )

    out = "assets/device_frame_foldable_cover.png"
    os.makedirs("assets", exist_ok=True)
    frame.save(out, "PNG")
    print(f"✓ {out} ({DEVICE_W}×{DEVICE_H})")
    print(f"  BEZEL={BEZEL}, SCREEN_W={SCREEN_W}, SCREEN_H={SCREEN_H}")
    print(f"  SCREEN_CORNER_R={SCREEN_CORNER_R}")


def main():
    p = argparse.ArgumentParser(
        description="Generate Android device frame template PNG(s)"
    )
    p.add_argument(
        "--type",
        choices=["phone", "foldable_inner", "foldable_cover"],
        default="phone",
        help="Frame type to generate (default: phone)",
    )
    args = p.parse_args()

    if args.type == "phone":
        generate_phone()
    elif args.type == "foldable_inner":
        generate_foldable_inner()
    elif args.type == "foldable_cover":
        generate_foldable_cover()


if __name__ == "__main__":
    main()
