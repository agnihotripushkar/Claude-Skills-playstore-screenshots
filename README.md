# App Store & Play Store Screenshots

A Claude Code skill that generates high-converting screenshots for both **Google Play Store** (Android) and **Apple App Store** (iOS). It analyzes your app's codebase, identifies core benefits, and creates professional screenshot images using AI.

The skill auto-detects your platform from the project structure and runs the appropriate workflow.

## What It Does

1. **Platform Detection** — Detects Android, iOS, or cross-platform (React Native / Flutter) from your codebase
2. **Benefit Discovery** — Analyzes your app to identify the 3–5 core benefits that drive downloads
3. **Screenshot Pairing** — Reviews your device screenshots, rates them, and pairs each with the best benefit
4. **Generation** — Creates polished screenshots using a two-stage process: deterministic scaffolding + AI enhancement (Nano Banana Pro via Gemini MCP)
5. **Device Variants** — Android: foldable cover/inner screens. iOS: iPad, iPhone SE, multiple size slots
6. **Showcase** — Generates a side-by-side preview image of the full set

## Installation

### 1. Add the skill to Claude Code

```bash
claude install-skill github.com/agnihotripushkar/claude-skill-aso-playstore-screenshots
```

### 2. Install Python dependencies

```bash
pip install Pillow
```

### 3. Font setup

**Android** uses Google Sans Bold (falls back to Roboto Black → Helvetica):
- Download from [Google Fonts](https://fonts.google.com/specimen/Google+Sans) and copy to `/Library/Fonts/`

**iOS** uses SF Pro Display Black (falls back to Helvetica):
- Download from [Apple's developer fonts page](https://developer.apple.com/fonts/) and copy to `/Library/Fonts/SF-Pro-Display-Black.otf`

### 4. Generate device frame assets

Run once to create the device frame PNG templates you need:

```bash
# Android
python3 generate_frame.py --type phone
python3 generate_frame.py --type foldable_cover   # optional
python3 generate_frame.py --type foldable_inner   # optional

# iOS
python3 generate_frame.py --type iphone           # iPhone with Dynamic Island
python3 generate_frame.py --type ipad             # iPad Pro (if targeting iPad)
python3 generate_frame.py --type iphone_se        # iPhone SE with home button (optional)
```

### 5. Set up Gemini MCP (for AI enhancement)

The generation phase requires [@houtini/gemini-mcp](https://www.npmjs.com/package/@houtini/gemini-mcp) configured as an MCP server in Claude Code:

```bash
npm install -g @houtini/gemini-mcp
```

Then add it to your Claude Code MCP config (`~/.claude/settings.json` or project `.mcp.json`).

## Usage

From within your app's project directory, run:

```
/aso-playstore-screenshots
```

The skill detects your platform automatically and guides you through each phase interactively. Progress is saved to Claude Code's memory system so you can resume across conversations.

## How It Works

### Scaffold → Enhance Pipeline

Rather than generating screenshots from scratch (which produces inconsistent results), the skill uses a two-stage approach:

1. **`compose.py` / `ios_compose.py`** creates a deterministic scaffold with exact text positioning, a device frame, and your screenshot composited inside the screen cutout
2. **Nano Banana Pro** (via Gemini MCP) enhances the scaffold — adding a photorealistic device mockup, breakout elements, and visual polish

This ensures consistent layout across all screenshots while letting AI handle the creative enhancement.

---

## Android (Google Play Store)

### Device Types

| `--device-type` | Canvas Size | Play Console Slot |
|----------------|------------|-------------------|
| `phone` (default) | 1080×1920 px | Standard phone |
| `foldable_cover` | 1080×2092 px | Foldable cover screen |
| `foldable_inner` | 2208×1840 px | Foldable inner (unfolded) |

### Capturing Screenshots

```bash
# Android Studio emulator
adb exec-out screencap -p > screenshot.png

# Clean status bar (demo mode)
adb shell settings put global sysui_demo_allowed 1
adb shell am broadcast -a com.android.systemui.demo -e command enter
adb shell am broadcast -a com.android.systemui.demo -e command clock -e hhmm 0941
adb shell am broadcast -a com.android.systemui.demo -e command battery -e level 100 -e plugged false
adb shell am broadcast -a com.android.systemui.demo -e command network -e wifi show -e level 4
```

### Play Console Requirements

| Screen type | Dimensions |
|-------------|-----------|
| Phone portrait | 1080×1920 px (9:16) |
| 7" tablet | 1200×1920 px |
| 10" tablet | 1600×2560 px |
| Foldable cover | 1080×2092 px |
| Foldable inner | 2208×1840 px |
| Feature graphic | 1024×500 px |

### Output

```
screenshots/
  01-benefit-slug/
    scaffold.png            ← compose.py output
    v1.png, v2.png, v3.png  ← AI-enhanced versions
  final/                    ← approved, ready to upload
    01-benefit-slug.png
  foldable-cover/final/
  foldable-inner/final/
  showcase.png
```

---

## iOS (Apple App Store)

### Device Types

| `--device-type` | Canvas Size | App Store Slot |
|----------------|------------|----------------|
| `iphone_67` (default) | 1290×2796 px | iPhone 6.7" — **required** (iPhone 16 Pro Max / 15 Pro Max) |
| `iphone_65` | 1242×2688 px | iPhone 6.5" (iPhone 11 Pro Max / XS Max) |
| `iphone_55` | 1242×2208 px | iPhone 5.5" — legacy (iPhone 8 Plus) |
| `iphone_se` | 750×1334 px | iPhone SE / 4.7" (iPhone SE 3rd gen) |
| `ipad_129` | 2048×2732 px | iPad 12.9" Pro — **required** for iPad apps |
| `ipad_11` | 1668×2388 px | iPad 11" Pro / Air |

Apple enforces **exact pixel dimensions** — unlike Play Store, no size ranges are accepted.

### Capturing Screenshots

```bash
# Xcode Simulator — keyboard shortcut
# Device → Take Screenshot (Cmd+S)

# Or via command line
xcrun simctl io booted screenshot screenshot.png

# Clean status bar
xcrun simctl status_bar booted override \
  --time "9:41" \
  --batteryState charged \
  --batteryLevel 100 \
  --wifiBars 3 \
  --cellularBars 4
```

### App Store Connect Requirements

- Up to **10 screenshots** per device slot
- At least one screenshot required for the **6.7" slot** (or 6.5" as fallback)
- **iPad screenshots are a separate required slot** — they don't inherit from iPhone
- Portrait orientation strongly recommended for phone
- No misleading content or simulated iOS UI elements not present in the app

### Output

```
screenshots/
  ios/
    01-benefit-slug/
      scaffold.png            ← ios_compose.py output
      v1.png, v2.png, v3.png  ← AI-enhanced versions
    final/                    ← approved iPhone screenshots, ready to upload
      01-benefit-slug.png     ← exact App Store dimensions
    ipad/final/               ← iPad variants (if generated)
  showcase.png
```

---

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | The skill prompt — defines the full multi-phase workflow for both platforms |
| `compose.py` | Android scaffold generator (Pillow-based) |
| `ios_compose.py` | iOS scaffold generator — handles all App Store size slots |
| `generate_frame.py` | Generates device frame templates (Android + iOS) |
| `showcase.py` | Generates the side-by-side showcase image |
| `assets/device_frame.png` | Android phone frame |
| `assets/device_frame_foldable_cover.png` | Android foldable cover frame |
| `assets/device_frame_foldable_inner.png` | Android foldable inner frame |
| `assets/ios_device_frame_iphone.png` | iPhone frame with Dynamic Island |
| `assets/ios_device_frame_iphone_se.png` | iPhone SE frame with home button |
| `assets/ios_device_frame_ipad.png` | iPad Pro frame |

## License

MIT
