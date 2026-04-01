#!/usr/bin/env python3
"""
Generate Android and iOS device frame template PNGs.
Outputs standalone device images (not positioned on canvas).
compose.py / ios_compose.py positions these dynamically based on text height.

Android frame types:
  phone           → assets/device_frame.png
  foldable_inner  → assets/device_frame_foldable_inner.png
  foldable_cover  → assets/device_frame_foldable_cover.png

iOS frame types:
  iphone          → assets/ios_device_frame_iphone.png   (Dynamic Island, 6.7")
  iphone_se       → assets/ios_device_frame_iphone_se.png (Home button, 4.7")
  ipad            → assets/ios_device_frame_ipad.png      (iPad Pro 12.9")
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


# ────────────────────────────────────────────────────────────────────
# iOS iPhone frame (Dynamic Island — iPhone 15 Pro / 16 Pro style)
# Canvas: 1290×2796 (6.7" App Store slot)
# ────────────────────────────────────────────────────────────────────
def generate_iphone():
    DEVICE_W = 1030
    DEVICE_H = 2800
    DEVICE_CORNER_R = 77
    BEZEL = 15
    SCREEN_CORNER_R = 62

    # Dynamic Island
    DI_W = 130
    DI_H = 38
    DI_TOP = 14   # offset from top of screen

    SCREEN_W = DEVICE_W - 2 * BEZEL
    SCREEN_H = DEVICE_H - 2 * BEZEL

    frame = Image.new("RGBA", (DEVICE_W, DEVICE_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # ── Device body ─────────────────────────────────────────────────
    fd.rounded_rectangle(
        [0, 0, DEVICE_W - 1, DEVICE_H - 1],
        radius=DEVICE_CORNER_R,
        fill=(30, 30, 30, 255),
    )
    fd.rounded_rectangle(
        [1, 1, DEVICE_W - 2, DEVICE_H - 2],
        radius=DEVICE_CORNER_R - 1,
        fill=(20, 20, 20, 255),
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

    # ── Dynamic Island ───────────────────────────────────────────────
    di_x = (DEVICE_W - DI_W) // 2
    di_y = screen_y + DI_TOP
    ImageDraw.Draw(frame).rounded_rectangle(
        [di_x, di_y, di_x + DI_W, di_y + DI_H],
        radius=DI_H // 2,
        fill=(0, 0, 0, 255),
    )

    # ── Side buttons ────────────────────────────────────────────────
    btn_color = (25, 25, 25, 255)
    fd2 = ImageDraw.Draw(frame)
    # Power (right)
    fd2.rounded_rectangle([DEVICE_W, 340, DEVICE_W + 4, 460], radius=2, fill=btn_color)
    # Volume up (left)
    fd2.rounded_rectangle([-4, 280, 0, 360], radius=2, fill=btn_color)
    # Volume down (left)
    fd2.rounded_rectangle([-4, 380, 0, 460], radius=2, fill=btn_color)
    # Silent switch (left)
    fd2.rounded_rectangle([-4, 180, 0, 220], radius=2, fill=btn_color)

    out = "assets/ios_device_frame_iphone.png"
    os.makedirs("assets", exist_ok=True)
    frame.save(out, "PNG")
    print(f"✓ {out} ({DEVICE_W}×{DEVICE_H})")
    print(f"  BEZEL={BEZEL}, SCREEN_W={SCREEN_W}, SCREEN_H={SCREEN_H}")
    print(f"  SCREEN_CORNER_R={SCREEN_CORNER_R}, Dynamic Island={DI_W}×{DI_H}")


# ────────────────────────────────────────────────────────────────────
# iOS iPhone SE frame (Home button — 4.7" / 750×1334 slot)
# ────────────────────────────────────────────────────────────────────
def generate_iphone_se():
    DEVICE_W = 600
    DEVICE_H = 1800
    DEVICE_CORNER_R = 55
    BEZEL = 14
    SCREEN_CORNER_R = 8   # SE has nearly square corners on screen

    # Home button
    HOME_D = 80
    HOME_BOTTOM_OFFSET = 30  # from bottom of device

    SCREEN_W = DEVICE_W - 2 * BEZEL
    # SE has top/bottom bezels (no edge-to-edge)
    TOP_BEZEL = 100
    BOTTOM_BEZEL = 140
    SCREEN_H = DEVICE_H - TOP_BEZEL - BOTTOM_BEZEL

    frame = Image.new("RGBA", (DEVICE_W, DEVICE_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # ── Device body ─────────────────────────────────────────────────
    fd.rounded_rectangle(
        [0, 0, DEVICE_W - 1, DEVICE_H - 1],
        radius=DEVICE_CORNER_R,
        fill=(30, 30, 30, 255),
    )
    fd.rounded_rectangle(
        [1, 1, DEVICE_W - 2, DEVICE_H - 2],
        radius=DEVICE_CORNER_R - 1,
        fill=(20, 20, 20, 255),
    )

    # ── Screen cutout ────────────────────────────────────────────────
    screen_x = BEZEL
    screen_y = TOP_BEZEL
    cutout = Image.new("L", (DEVICE_W, DEVICE_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + SCREEN_W, screen_y + SCREEN_H],
        radius=SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # ── Front camera (top center, small circle) ──────────────────────
    cam_r = 12
    cam_cx = DEVICE_W // 2
    cam_cy = TOP_BEZEL // 2
    ImageDraw.Draw(frame).ellipse(
        [cam_cx - cam_r, cam_cy - cam_r, cam_cx + cam_r, cam_cy + cam_r],
        fill=(0, 0, 0, 255),
    )

    # ── Home button ──────────────────────────────────────────────────
    hb_cx = DEVICE_W // 2
    hb_cy = DEVICE_H - HOME_BOTTOM_OFFSET - HOME_D // 2
    hb_r = HOME_D // 2
    ImageDraw.Draw(frame).ellipse(
        [hb_cx - hb_r, hb_cy - hb_r, hb_cx + hb_r, hb_cy + hb_r],
        fill=(35, 35, 35, 255),
        outline=(50, 50, 50, 255),
        width=2,
    )

    # ── Side buttons ────────────────────────────────────────────────
    btn_color = (25, 25, 25, 255)
    fd2 = ImageDraw.Draw(frame)
    # Power (right side, top area)
    fd2.rounded_rectangle([DEVICE_W, 200, DEVICE_W + 4, 300], radius=2, fill=btn_color)
    # Volume up (left)
    fd2.rounded_rectangle([-4, 260, 0, 330], radius=2, fill=btn_color)
    # Volume down (left)
    fd2.rounded_rectangle([-4, 350, 0, 420], radius=2, fill=btn_color)
    # Silent switch (left)
    fd2.rounded_rectangle([-4, 170, 0, 210], radius=2, fill=btn_color)

    out = "assets/ios_device_frame_iphone_se.png"
    os.makedirs("assets", exist_ok=True)
    frame.save(out, "PNG")
    print(f"✓ {out} ({DEVICE_W}×{DEVICE_H})")
    print(f"  TOP_BEZEL={TOP_BEZEL}, SCREEN_W={SCREEN_W}, SCREEN_H={SCREEN_H}")


# ────────────────────────────────────────────────────────────────────
# iOS iPad Pro frame (12.9" — 2048×2732 App Store slot)
# ────────────────────────────────────────────────────────────────────
def generate_ipad():
    DEVICE_W = 1640
    DEVICE_H = 2200
    DEVICE_CORNER_R = 40
    BEZEL = 18
    SCREEN_CORNER_R = 18

    # iPad Pro has Face ID camera bar at top (landscape pill)
    CAM_W = 60
    CAM_H = 14
    CAM_TOP = 10

    SCREEN_W = DEVICE_W - 2 * BEZEL
    SCREEN_H = DEVICE_H - 2 * BEZEL

    frame = Image.new("RGBA", (DEVICE_W, DEVICE_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # ── Device body ─────────────────────────────────────────────────
    fd.rounded_rectangle(
        [0, 0, DEVICE_W - 1, DEVICE_H - 1],
        radius=DEVICE_CORNER_R,
        fill=(30, 30, 30, 255),
    )
    fd.rounded_rectangle(
        [1, 1, DEVICE_W - 2, DEVICE_H - 2],
        radius=DEVICE_CORNER_R - 1,
        fill=(20, 20, 20, 255),
    )

    # ── Screen cutout ────────────────────────────────────────────────
    screen_x = BEZEL
    screen_y = BEZEL
    cutout = Image.new("L", (DEVICE_W, DEVICE_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + SCREEN_W, screen_y + SCREEN_H],
        radius=SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # ── Front camera pill (top center) ───────────────────────────────
    cam_x = (DEVICE_W - CAM_W) // 2
    cam_y = screen_y + CAM_TOP
    ImageDraw.Draw(frame).rounded_rectangle(
        [cam_x, cam_y, cam_x + CAM_W, cam_y + CAM_H],
        radius=CAM_H // 2,
        fill=(0, 0, 0, 255),
    )

    # ── Side buttons ────────────────────────────────────────────────
    btn_color = (25, 25, 25, 255)
    fd2 = ImageDraw.Draw(frame)
    # Power / Touch ID (top edge, right of center)
    fd2.rounded_rectangle([DEVICE_W - 200, -4, DEVICE_W - 100, 0], radius=2, fill=btn_color)
    # Volume up (right side)
    fd2.rounded_rectangle([DEVICE_W, 300, DEVICE_W + 4, 400], radius=2, fill=btn_color)
    # Volume down (right side)
    fd2.rounded_rectangle([DEVICE_W, 420, DEVICE_W + 4, 520], radius=2, fill=btn_color)

    out = "assets/ios_device_frame_ipad.png"
    os.makedirs("assets", exist_ok=True)
    frame.save(out, "PNG")
    print(f"✓ {out} ({DEVICE_W}×{DEVICE_H})")
    print(f"  BEZEL={BEZEL}, SCREEN_W={SCREEN_W}, SCREEN_H={SCREEN_H}")


def main():
    p = argparse.ArgumentParser(
        description="Generate Android/iOS device frame template PNG(s)"
    )
    p.add_argument(
        "--type",
        choices=["phone", "foldable_inner", "foldable_cover", "iphone", "iphone_se", "ipad"],
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
    elif args.type == "iphone":
        generate_iphone()
    elif args.type == "iphone_se":
        generate_iphone_se()
    elif args.type == "ipad":
        generate_ipad()


if __name__ == "__main__":
    main()
