# Air Canvas AI — Real-Time Touchless Drawing System

A production-quality computer vision desktop application built with Python, OpenCV, and MediaPipe. Air Canvas AI enables users to draw, erase, select colors, and save virtual artwork in real time using intuitive hand and finger movements captured via a webcam.

---

## 1. Project Overview

**Air Canvas AI** transforms hand movements captured through a standard webcam into a virtual digital paint canvas. By using 21 3D hand landmarks provided by MediaPipe and coordinate smoothing algorithms, the application delivers fluid, low-latency, and anti-jitter touchless drawing.

### Architecture Data Flow
```text
                         USER
                          │
                          │ Hand Movement
                          ▼
                     WEBCAM STREAM
                          │
                          ▼
                    CAMERA MANAGER
                          │ (BGR Frame Capture & Mirroring)
                          ▼
                 MEDIAPIPE HAND MODEL
                          │
                          ▼
                  21 HAND LANDMARKS
                          │
                          ▼
                 GESTURE ENGINE RECOGNITION
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
        DRAW           ERASER          CONTROL (Toolbar/Clear/Save)
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                 COORDINATE SMOOTHING (EMA)
                          │
                          ▼
                    DRAWING ENGINE
                          │ (Separate Layer)
                          ▼
                   VIRTUAL CANVAS
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
     DISPLAY WINDOW                  SAVE IMAGE (.png)
```

---

## 2. Key Features

- **Touchless Real-Time Drawing**: Draw continuously in mid-air using index finger movements.
- **21 Hand Landmark Tracking**: High-precision hand detection using MediaPipe.
- **Coordinate Smoothing Engine**: Exponential Moving Average (EMA) filtering eliminates jitter while maintaining instant responsiveness.
- **Dedicated Layer Compositing**: Draws on an independent layer without permanently modifying or degrading the camera stream.
- **Interactive UI Toolbar**: Glassmorphic top navigation bar with visual touchless button collision detection.
- **Multiple Colors & Brush Sizes**: Quick palette selection (Red, Green, Blue, Yellow, Magenta, White) and key controls for brush sizing.
- **Dedicated Eraser Tool**: Precise scissors gesture or button toggle for removing unwanted lines.
- **One-Gesture Clear & Save**: Clear canvas with open palm or save high-resolution PNG artwork to `saved_drawings/`.
- **Heads-Up Display (HUD)**: Real-time FPS tracker, active mode badge, color preview, and shortcut legend.
- **Automated Test Suite**: 22 passing unit tests covering gestures, coordinate smoothing, canvas operations, and FPS calculations.

---

## 3. Technology Stack

- **Core**: Python 3.11+
- **Computer Vision**: OpenCV (`opencv-python`)
- **Hand Tracking**: MediaPipe (`mediapipe`)
- **Array Processing**: NumPy (`numpy`)
- **Configuration & Utilities**: `python-dotenv`
- **Testing**: PyTest (`pytest`)

---

## 4. Project Structure

```text
air-canvas-ai/
│
├── app.py                     # Main application entrypoint & loop
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive documentation
├── .gitignore                 # Git ignore rules
├── .env.example               # Environment variables template
│
├── config/
│   ├── __init__.py
│   └── settings.py            # Centralized settings & environment loader
│
├── camera/
│   ├── __init__.py
│   └── camera_manager.py      # OpenCV webcam capture, mirroring, and resizing
│
├── hand_tracking/
│   ├── __init__.py
│   ├── hand_detector.py       # MediaPipe Hands detector & custom landmark renderer
│   └── landmarks.py           # Landmark ID enums and HandLandmarks models
│
├── gestures/
│   ├── __init__.py
│   ├── gesture_detector.py    # Finger state solver & gesture recognition logic
│   └── gesture_types.py       # Gesture result dataclass & GestureType enum
│
├── drawing/
│   ├── __init__.py
│   ├── canvas.py              # Virtual canvas layer management & compositing
│   ├── brush.py               # Anti-aliased line brush
│   ├── eraser.py              # Dedicated eraser tool
│   └── smoothing.py           # Exponential moving average coordinate filter
│
├── ui/
│   ├── __init__.py
│   ├── toolbar.py             # Top interactive glassmorphic toolbar
│   ├── colors.py              # BGR color palette definitions
│   └── controls.py            # HUD status bar, badges, and shortcut legend
│
├── storage/
│   ├── __init__.py
│   └── drawing_saver.py       # Timestamped PNG artwork exporter
│
├── utils/
│   ├── __init__.py
│   ├── fps.py                 # Real-time FPS monitor with windowed averaging
│   └── logger.py              # Logging setup
│
├── tests/
│   ├── test_gestures.py       # Unit tests for gesture recognition
│   ├── test_smoothing.py      # Unit tests for EMA smoothing
│   ├── test_canvas.py        # Unit tests for canvas drawing & saving
│   └── test_fps.py           # Unit tests for FPS calculations
│
└── saved_drawings/
    └── .gitkeep               # Output folder for saved drawings
```

---

## 5. Installation & Setup

### Requirements
- Operating System: Windows, macOS, or Linux
- Python: Version 3.11 or higher
- Webcam: Any standard USB or built-in webcam

### Step 1: Clone or Navigate to Directory
```bash
cd "Air AI"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 6. Running the Application

Start the application using:

```bash
python app.py
```

Press `q` or `ESC` in the application window to quit cleanly.

---

## 7. Gesture Controls & Interaction

| Gesture | Finger Posture | Action |
| :--- | :--- | :--- |
| **DRAW** | Only Index Finger Extended Up | Freehand air drawing with active color |
| **ERASER** | Index + Middle Fingers Extended Up (Scissors pose) | Erase content along finger path |
| **COLOR SELECT** | Index Finger inside Top Toolbar Area | Select color / trigger hover buttons |
| **CLEAR** | Open Palm (All 5 Fingers Extended Up) | Clear drawing canvas |
| **SAVE** | Closed Fist (Held for ~1 sec) | Save drawing to `saved_drawings/` as PNG |
| **IDLE** | Hand closed or posture unrecognized | Pause drawing |

### Keyboard Shortcuts

- **`C`**: Clear canvas layer
- **`S`**: Save current drawing to `saved_drawings/`
- **`E`**: Toggle Eraser mode on/off
- **`+` / `=`**: Increase brush / eraser size
- **`-` / `_`**: Decrease brush / eraser size
- **`1` - `6`**: Quick pick colors (1: Red, 2: Green, 3: Blue, 4: Yellow, 5: Magenta, 6: White)
- **`Q` / `ESC`**: Quit application

---

## 8. Configuration

Central configuration parameters are managed in `config/settings.py` and can be overridden via a `.env` file:

```env
CAMERA_INDEX=0
FRAME_WIDTH=1280
FRAME_HEIGHT=720
MAX_HANDS=1
DETECTION_CONFIDENCE=0.7
TRACKING_CONFIDENCE=0.7
SMOOTHING_FACTOR=0.5
BRUSH_SIZE=8
ERASER_SIZE=30
SAVED_DRAWINGS_DIR=saved_drawings
```

---

## 9. Running Tests

Run the unit test suite using `pytest`:

```bash
pytest -v
```

Output:
```text
tests/test_canvas.py PASSED
tests/test_fps.py PASSED
tests/test_gestures.py PASSED
tests/test_smoothing.py PASSED

22 passed in 1.65s
```

---

## 10. Troubleshooting

1. **Camera Not Opening**:
   - Ensure no other application (Zoom, Teams, Skype) is using the webcam.
   - Change `CAMERA_INDEX=1` in `.env` if using an external USB camera.

2. **Low FPS or Lag**:
   - Reduce `FRAME_WIDTH` and `FRAME_HEIGHT` in `.env` (e.g. `640`x`480`).
   - Ensure adequate lighting for fast MediaPipe tracking.

3. **Jittery Drawing**:
   - Adjust `SMOOTHING_FACTOR` in `.env` (lower values like `0.3` increase smoothing).

---

## 11. Future Improvements

- **Undo / Redo Stack**: State history management for drawing operations.
- **Shape Tools**: Air gestures for drawing straight lines, rectangles, and circles.
- **Handwriting Recognition**: AI text extraction from drawn air strokes.
- **Multi-Hand Support**: Multi-user collaboration on a single screen.
