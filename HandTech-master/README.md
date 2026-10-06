# Hand Gesture Reader - Interactive Teaching Tool 

A real-time hand gesture recognition system using OpenCV and MediaPipe, designed specifically for teaching and presentations. This tool combines gesture recognition with a virtual drawing canvas, making it perfect for interactive teaching sessions, virtual whiteboards, and hands-free presentations.

## Features

### **Gesture Recognition Mode**
- **Real-time Hand Detection**: Detects and tracks hands using MediaPipe
- **Multiple Gesture Recognition**: Recognizes 10+ gestures including:
  - Numbers 0-5 with fingers
  - Peace sign / Victory sign
  - Thumbs up
  - Pointing gesture
  - Open palm
  - Fist
  - Call me / Shaka sign
  - I Love You sign
- **Live Feedback**: Shows finger status (up/down) for each finger
- **Hand Distance Calculation**: Displays hand size/distance from camera

**Virtual Drawing Mode**
- **Free-hand Drawing**: Draw smooth lines with single index finger
- **7 Color Palette**: Green, Blue, Red, Yellow, White, Purple, Orange
- **Easy Selection System**: 
  - Hover effects with yellow borders
  - Visual confirmation with cyan borders + checkmarks
  - Point and click with index finger
- **Drawing Tools**:
  - **Precise Eraser**: Erase only what you point at (not everything!)
  - Clear canvas button
  - Save screenshots to folder
- **Two-Finger Shape Drawing**: Perfect geometric shapes
  - Line tool (index + middle fingers)
  - Circle tool (index + middle fingers)
  - Rectangle tool (index + middle fingers)
  - Real-time preview while drawing
- **Adjustable Brush Size**: Increase/decrease with +/- keys (1-25 pixels)

### **Interactive Controls**
- **Keyboard Shortcuts**:
  - `D`: Toggle drawing mode
  - `C`: Clear canvas
  - `S`: Save screenshot
  - `H`: Toggle help overlay
  - `L`: Toggle hand landmarks display
  - `F`: Toggle finger status display
  - `G`: Toggle gesture shortcuts
  - `+/-`: Adjust brush size
  - `Q` or `ESC`: Quit application

- **Finger Gestures** (in drawing mode):
  -  **Index finger only**: Free-hand drawing or precise erasing
  -  **Index + Middle fingers**: Shape drawing mode
  -  **Peace sign**: Toggle eraser mode (gesture shortcut)
  -  **Open palm**: Clear canvas (gesture shortcut)

###  **UI Features**
- Real-time FPS counter
- Mode indicators (Gesture/Drawing)
- Status displays (eraser, shape mode, brush size)
- Comprehensive help overlay
- Smooth visual feedback
- Toggleable UI elements for clean view

## Installation

### Prerequisites
- **Python 3.12** (Required for MediaPipe compatibility)
- Webcam connected to your computer
- Windows/Linux/Mac OS

### Setup

1. **Install required packages**:
```cmd
pip install -r requirements.txt
```

2. **Verify installation**:
```cmd
python -c "import cv2, mediapipe; print('All packages installed successfully!')"
```

## Usage

### Run the Interactive Gesture Reader

Run the main application:

```cmd
python hand_gesture_reader.py
```

### Getting Started

1. **Camera Selection**: 
   - On first run, the program will list all available cameras
   - Enter the camera number you want to use (usually 0 or 1)
   - Your PC webcam is typically a different number than phone cameras

2. **Gesture Mode** (Default):
   - Hold your hand in front of the camera
   - System will recognize and display the gesture name
   - See finger status for each finger (UP/DOWN)
   - View hand distance/size information

3. **Drawing Mode** (Press `D`):
   - Point with only your index finger to draw
   - Click on colors in the right panel to change color
   - Use shape tools for perfect geometric shapes:
     - **Line**: Click shape, set start point (index finger), move to end point, release
     - **Circle**: Click shape, set center, move out for radius, release
     - **Rectangle**: Click shape, set corner, drag to opposite corner, release
   - Use gesture shortcuts:
     - Peace sign toggles eraser
     -  Open palm clears canvas

4. **Keyboard Controls**:
   - `D`: Switch between drawing and gesture modes
   - `C`: Clear the entire canvas
   - `S`: Save current drawing as screenshot (saved to `hand_gesture_screenshots/`)
   - `H`: Show/hide help overlay
   - `L`: Show/hide hand landmarks (skeleton)
   - `F`: Show/hide finger status display
   - `G`: Enable/disable gesture shortcuts
   - `+`: Increase brush size
   - `-`: Decrease brush size
   - `Q` or `ESC`: Exit application safely

### What You'll See

**In Gesture Mode**:
- Live camera feed with hand landmark overlays (toggleable with `L`)
- Current gesture name at the top
- Hand type identification (Left/Right)
- Finger status display (toggleable with `F`)
- Real-time FPS counter
- Info panel with mode and tips

**In Drawing Mode**:
- Camera feed with your drawing overlay
- Color palette panel (right side):
  - 7 colors (green, blue, red, yellow, white, purple, orange)
  - Eraser button
  - Clear button
  - Save button
  - 3 shape tools (line, circle, rectangle)
- Yellow circle at your index fingertip when drawing
- Current mode, brush size, and active tool indicators
- Help overlay (press `H`)

### Custom Gesture Trainer

Train your own custom gestures for specialized teaching needs:

```cmd
python gesture_trainer.py
```

**Menu Options**:
1. **Train new gesture**: Create a custom gesture
   - Enter a name for your gesture
   - Press `s` to start recording samples
   - Hold your hand in the desired position
   - The system will capture 30 samples automatically
   - Press `q` when done

2. **List trained gestures**: View all saved custom gestures

3. **Delete gesture**: Remove a trained gesture

4. **Exit**: Close the trainer

## Recognized Gestures

| Gesture | Description | Teaching Use |
|---------|-------------|--------------|
| Number 0 (Fist) | Closed fist | Attention, Stop |
| Number 1 (Pointing) | Index finger up | Highlighting points |
| Thumbs Up | Thumb extended | Approval, Good job |
| Number 2 (Peace) | Index + Middle fingers | Two items, Peace |
| Number 3 | Three fingers up | Three points/items |
| Number 4 | Four fingers up | Four items |
| Number 5 (Open Palm) | All fingers extended | Five items, Stop, Pause |
| Call Me | Thumb + Pinky | Informal communication |
| I Love You | Thumb + Index + Pinky | Positive reinforcement |

## Teaching Applications

This tool is perfect for:

- **Online Teaching**: Recognize gestures during virtual classes
-  **Presentations**: Interactive demonstrations
-  **Math Classes**: Show numbers with hands
-  **Sign Language**: Basic gesture communication
-  **Interactive Learning**: Gamified lessons
-  **Group Activities**: Gesture-based responses

## Technical Details

### Hand Detection
- Uses MediaPipe Hands for accurate hand landmark detection
- Tracks 21 hand landmarks in real-time
- Supports detection of both hands simultaneously

### Gesture Recognition Algorithm
- Analyzes finger positions relative to palm
- Considers hand orientation (left/right)
- Uses vertical and horizontal position checks
- Distinguishes between similar gestures

### Performance
- Runs at 30+ FPS on most modern computers
- Low latency for real-time interaction
- Optimized for teaching scenarios

## Troubleshooting

### Camera not detected
```cmd
# Check available cameras
python -c "import cv2; print(f'Camera available: {cv2.VideoCapture(0).isOpened()}')"
```

### Low FPS
- Close other applications using the camera
- Reduce video resolution in the code (line 82)
- Ensure good lighting conditions

### Hand not detected
- Ensure proper lighting
- Keep hand within camera frame
- Adjust `min_detection_confidence` in code (line 11)
- Move hand closer to camera

### Installation issues
```cmd
# Update pip
python -m pip install --upgrade pip

# Reinstall packages
pip install --force-reinstall -r requirements.txt
```

## Customization

### Adjust Detection Sensitivity
In `hand_gesture_reader.py`, modify these parameters (lines 10-13):

```python
self.hands = self.mp_hands.Hands(
    max_num_hands=2,              # Number of hands to detect (1 or 2)
    min_detection_confidence=0.7,  # Lower = more sensitive (0.5-0.9)
    min_tracking_confidence=0.7    # Lower = more tracking (0.5-0.9)
)
```

### Add New Gestures
Add your own gesture recognition in the `recognize_gesture` method (line 51):

```python
# Example: Add "OK" sign detection
elif fingers_up[0] == 1 and fingers_up[1] == 1 and sum(fingers_up[2:]) == 0:
    return "OK Sign"
```

### Change Display Colors
Modify color values in the code (BGR format):
- `(0, 255, 0)` = Green
- `(255, 0, 0)` = Blue
- `(0, 0, 255)` = Red
- `(255, 255, 0)` = Cyan

## File Structure

```
Hand gesture/
│
├── hand_gesture_reader.py        # Main interactive application
├── gesture_trainer.py             # Custom gesture training tool
├── requirements.txt               # Python dependencies
├── README.md                      # Documentation
├── PYTHON_VERSION_HELP.md        # Python version guide
├── custom_gestures.json          # Saved custom gestures (auto-generated)
└── hand_gesture_screenshots/     # Saved drawings (auto-generated)
```

## Tips for Best Results

### For Gesture Recognition:
1. **Lighting**: Use good, even lighting for better hand detection
2. **Background**: Plain backgrounds work best
3. **Distance**: Keep hand 1-2 feet from camera
4. **Clarity**: Make gestures clear and distinct
5. **Speed**: Hold gestures for a moment for recognition
6. **Camera**: Position camera at chest/face level

### For Drawing Mode:
1. **Drawing Gesture**: Only extend your index finger, keep others closed
2. **Smooth Lines**: Move your hand slowly and steadily
3. **Shape Tools**: 
   - Select shape first from palette
   - Point index finger for start point
   - Move to end point (preview shows in yellow)
   - Release (make fist or change gesture) to finalize
4. **Brush Size**: Start with default (5), adjust with +/- as needed
5. **Clean Canvas**: Use 'C' key or open palm gesture for quick clear
6. **Save Work**: Press 'S' or click Save button before exiting

### Troubleshooting Drawing:
- **Can't draw**: Make sure only index finger is extended
- **Lines appear when not intended**: Keep hand still or make fist between strokes
- **Eraser mode stuck**: Click eraser button again or press peace sign gesture
- **Shape not appearing**: Ensure you release (change gesture) after setting end point

## Keyboard Shortcuts Reference

| Key | Action |
|-----|--------|
| `D` | Toggle Drawing/Gesture mode |
| `C` | Clear canvas |
| `S` | Save screenshot |
| `H` | Toggle help overlay |
| `L` | Toggle hand landmarks |
| `F` | Toggle finger status |
| `G` | Toggle gesture shortcuts |
| `+` | Increase brush size |
| `-` | Decrease brush size |
| `Q` / `ESC` | Quit application |

## Gesture Shortcuts Reference (Drawing Mode)

| Gesture | Action |
|---------|--------|
| Peace Sign | Toggle Eraser Mode |
|  Open Palm | Clear Canvas |
|  Index Finger Only | Draw/Erase |

## Use Cases

### Teaching & Education:
- Interactive math demonstrations (drawing shapes, diagrams)
- Virtual whiteboard for online classes
- Gesture-based presentation control
- Student engagement through interactive activities

### Presentations:
- Annotate slides in real-time
- Highlight key points with drawings
- Hands-free controls for slide navigation
- Create visual explanations on the fly

### Accessibility:
- Touchless interaction for hygiene
- Alternative input method
- Hands-free drawing for users with mobility aids

## Future Enhancements

Potential additions:
- Text recognition and writing
- More shape tools (polygons, arrows, curves)
- Gesture-based controls (volume, slides, zoom)
- Recording gesture sequences as macros
- Multi-language support
- Integration with presentation software (PowerPoint, Google Slides)
- Gesture history tracking and replay
- Collaborative drawing with multiple users
- AI-powered shape recognition and cleanup

## Support

If you encounter any issues:
1. Check the Troubleshooting section
2. Verify all requirements are installed (see `requirements.txt`)
3. Ensure webcam permissions are granted
4. Test with good lighting conditions
5. Make sure you're using Python 3.12 (check `PYTHON_VERSION_HELP.md`)
6. For NumPy errors, run: `py -3.12 -m pip install "numpy<2" --force-reinstall`

## License

Free to use for educational and teaching purposes.

## Credits

Built with:
- [OpenCV](https://opencv.org/) - Computer vision library
- [MediaPipe](https://mediapipe.dev/) - Hand detection framework
- [NumPy](https://numpy.org/) - Numerical computing

---

**Happy Teaching!**

Made for educators, presenters, and anyone who wants to make their sessions more interactive and engaging through gesture-based controls and virtual drawing.

