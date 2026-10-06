# Quick Start Guide 🚀

## Setup (5 minutes)

1. **Install Python 3.12** (if not already installed)
2. **Open terminal** in the project folder
3. **Run**: `pip install -r requirements.txt`
4. **Start**: `python hand_gesture_reader.py`

## First Time Use

### Camera Selection
- Program shows available cameras with resolution
- Enter the number for your PC webcam (usually 0 or 1)
- Smart Connect/phone cameras will be identified

## Two Modes

### 🖐️ Gesture Mode (Default)
**What it does**: Recognizes your hand gestures
**How to use**: 
- Hold hand in front of camera
- System shows gesture name, finger status
- Great for teaching sign language, counting, etc.

**Recognized gestures**:
- Numbers 0-5 (count fingers)
- Peace sign ✌️
- Thumbs up 👍
- Pointing ☝️
- Open palm 🖐️
- Fist ✊

### 🎨 Drawing Mode (Press 'D')
**What it does**: Virtual whiteboard with your finger
**How to draw**:
1. Extend ONLY index finger (keep others closed)
2. Move finger to draw
3. Make fist to stop drawing

**Tools available**:
- 7 colors (click on right panel)
- Eraser (click button or peace sign ✌️)
- Clear all (click button or open palm 🖐️)
- Save drawing (click button or press 'S')
- Shape tools (line, circle, rectangle)

## Essential Keyboard Shortcuts

| Key | What it does |
|-----|-------------|
| `D` | Switch between Drawing/Gesture mode |
| `H` | Show help overlay (all controls) |
| `C` | Clear your drawing |
| `S` | Save screenshot |
| `Q` | Quit safely |

## Tips for Success

### ✅ Good Practice:
- Use plain background
- Good lighting
- Hand 1-2 feet from camera
- Make clear, distinct gestures
- For drawing: extend ONLY index finger

### ❌ Common Issues:
- **Can't draw**: Check if only index finger is up
- **Wrong camera**: Restart and select different camera number
- **Lag**: Close other programs using camera
- **No hand detected**: Improve lighting or move closer

## Quick Drawing Tips

1. **Free draw**: Just point and move
2. **Straight line**: Use line tool from palette
3. **Perfect circle**: Use circle tool from palette
4. **Change color**: Click color box on right
5. **Erase mistake**: Make peace sign ✌️ or click eraser
6. **Start fresh**: Open palm 🖐️ or press 'C'
7. **Save work**: Press 'S' before quitting

## Gesture Shortcuts (Drawing Mode)

- ✌️ **Peace sign** → Toggle eraser
- 🖐️ **Open palm** → Clear canvas
- ☝️ **Index finger** → Draw/Erase

## Where Files Are Saved

Your drawings are saved to: `hand_gesture_screenshots/`
- Filename format: `gesture_YYYYMMDD_HHMMSS.png`
- Full screenshot including UI

## Getting More Help

- Press `H` in the app for full controls
- See `README.md` for detailed documentation
- See `PYTHON_VERSION_HELP.md` for Python issues

---

**You're ready to go! Have fun teaching and drawing! 🎨👋**

