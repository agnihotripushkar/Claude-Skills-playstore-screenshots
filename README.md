# Play Store Screenshots

A Claude Code skill that generates high-converting Google Play Store screenshots for your Android app. It analyzes your codebase, identifies core benefits, and creates professional screenshot images using AI.

## What It Does

1. **Benefit Discovery** — Analyzes your app's codebase to identify the 3–5 core benefits that drive downloads
2. **Screenshot Pairing** — Reviews your emulator screenshots, rates them, and pairs each with the best benefit
3. **Generation** — Creates polished Play Store screenshots using a two-stage process: deterministic scaffolding (`compose.py`) + AI enhancement (Nano Banana Pro via Gemini MCP)
4. **Foldable Variants** — Optionally generates additional screenshots for foldable inner and cover screens
5. **Showcase** — Generates a preview image with all screenshots side-by-side

## Installation

### 1. Add the skill to Claude Code

```bash
claude install-skill github.com/YOUR_USERNAME/claude-skill-aso-playstore-screenshots
```

### 2. Install Python dependencies

```bash
pip install Pillow
```

### 3. Font setup

The skill uses **Google Sans Bold** for headline text, with fallbacks to Roboto Black and Helvetica.

To install Google Sans on macOS:
- Download from [Google Fonts](https://fonts.google.com/specimen/Google+Sans) and copy to `/Library/Fonts/`

If neither Google Sans nor Roboto is found, the skill falls back to the system Helvetica automatically.

### 4. Generate device frame assets

Run this once to create the device frame PNG templates:

```bash
# Standard Android phone frame
python generate_frame.py --type phone

# Foldable frames (optional)
python generate_frame.py --type foldable_cover
python generate_frame.py --type foldable_inner
```

### 5. Set up Gemini MCP (for AI enhancement)

The generation phase requires [@houtini/gemini-mcp](https://www.npmjs.com/package/@houtini/gemini-mcp) configured as an MCP server in Claude Code:

```bash
npm install -g @houtini/gemini-mcp
```

Then add it to your Claude Code MCP config (`~/.claude/settings.json` or project `.mcp.json`).

## Usage

From within your Android app's project directory, run:

```
/aso-playstore-screenshots
```

The skill guides you through each phase interactively. Progress is saved to Claude Code's memory system so you can resume across conversations.

## How It Works

### Scaffold → Enhance Pipeline

Rather than generating screenshots from scratch (which produces inconsistent results), the skill uses a two-stage approach:

1. **`compose.py`** creates a deterministic scaffold with exact text positioning, an Android device frame, and your emulator screenshot composited inside the screen cutout
2. **Nano Banana Pro** (via Gemini MCP) enhances the scaffold — adding a photorealistic Android device mockup, breakout elements, Material You visual polish, and a clean background

This ensures consistent layout across all screenshots while letting AI handle the creative enhancement.

### Device Types

| Type | Canvas Size | Use Case |
|------|------------|----------|
| `phone` (default) | 1080×1920 px | Standard phone listing |
| `foldable_cover` | 1080×2092 px | Foldable cover screen |
| `foldable_inner` | 2208×1840 px | Foldable inner (unfolded) screen |

### Output

Screenshots are saved to a `screenshots/` directory in your project:

```
screenshots/
  01-benefit-slug/          ← working versions
    scaffold.png            ← deterministic compose.py output
    v1.png, v2.png, v3.png  ← AI-enhanced versions
  final/                    ← approved screenshots, ready to upload
    01-benefit-slug.png
    02-benefit-slug.png
  foldable/                 ← foldable variants (if generated)
    01-benefit-slug-cover.png
    01-benefit-slug-inner.png
  showcase.png              ← side-by-side preview
```

## Google Play Console Screenshot Requirements

| Screen type | Required size |
|-------------|--------------|
| Phone portrait | min 320px, max 3840px — 9:16 recommended (1080×1920) |
| Phone landscape | 1920×1080 px |
| 7" tablet portrait | 1200×1920 px |
| 10" tablet portrait | 1600×2560 px |
| Foldable cover | 1080×2092 px |
| Foldable inner (unfolded) | 2208×1840 px |
| Feature graphic | 1024×500 px |

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | The skill prompt — defines the multi-phase workflow |
| `compose.py` | Deterministic scaffold generator (Pillow-based) |
| `generate_frame.py` | Generates Android device frame templates (phone + foldable variants) |
| `showcase.py` | Generates the side-by-side showcase image |
| `assets/device_frame.png` | Pre-rendered standard Android phone frame |
| `assets/device_frame_foldable_cover.png` | Pre-rendered foldable cover screen frame |
| `assets/device_frame_foldable_inner.png` | Pre-rendered foldable inner screen frame |

## Capturing Screenshots from Android

**Android Studio emulator:**
- Use the camera icon in the emulator toolbar, or
- `adb exec-out screencap -p > screenshot.png`

**Enable demo mode for clean status bars:**
```bash
adb shell settings put global sysui_demo_allowed 1
adb shell am broadcast -a com.android.systemui.demo -e command enter
adb shell am broadcast -a com.android.systemui.demo -e command clock -e hhmm 1200
adb shell am broadcast -a com.android.systemui.demo -e command battery -e level 100 -e plugged false
adb shell am broadcast -a com.android.systemui.demo -e command network -e wifi show -e level 4
```

## License

MIT
