import cv2
import mediapipe as mp
import numpy as np
import time
import os
from datetime import datetime

class HandGestureReader:
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Gesture names for teaching
        self.gesture_name = "Unknown"
        self.gesture_history = []
        self.gesture_shortcuts_enabled = True
        
        # Virtual drawing board
        self.drawing_canvas = None
        self.prev_x, self.prev_y = None, None
        self.drawing_mode = False
        self.drawing_color = (0, 255, 0)  # Green
        self.eraser_mode = False
        self.brush_size = 5
        self.shape_mode = None  # None, 'line', 'circle', 'rectangle'
        self.shape_start = None
        
        # UI and interaction
        self.show_landmarks = True
        self.show_finger_status = True
        self.show_help = False
        self.last_gesture = None
        self.gesture_stable_frames = 0
        
        # Drawing colors palette
        self.colors = {
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'red': (0, 0, 255),
            'yellow': (0, 255, 255),
            'white': (255, 255, 255),
            'purple': (255, 0, 255),
            'orange': (0, 165, 255),
            'black': (0, 0, 0)
        }
        
        # Screenshot directory
        self.screenshot_dir = "hand_gesture_screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # UI interaction
        self.hover_item = None  # Track which button is being hovered
        
    def count_fingers(self, hand_landmarks, handedness):
        """Count the number of extended fingers"""
        # Finger tip and pip landmark indices
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        finger_pips = [3, 6, 10, 14, 18]
        
        fingers_up = []
        
        # Check if hand is left or right
        is_right_hand = handedness == "Right"
        
        # Thumb (different logic - check horizontal position)
        if is_right_hand:
            if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[finger_pips[0]].x:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        else:
            if hand_landmarks.landmark[finger_tips[0]].x > hand_landmarks.landmark[finger_pips[0]].x:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        # Other four fingers (check vertical position)
        for i in range(1, 5):
            if hand_landmarks.landmark[finger_tips[i]].y < hand_landmarks.landmark[finger_pips[i]].y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        return fingers_up
    
    def recognize_gesture(self, fingers_up, hand_landmarks):
        """Recognize specific hand gestures"""
        finger_count = sum(fingers_up)
        
        # Gesture shortcuts for drawing mode
        if self.drawing_mode and self.gesture_shortcuts_enabled:
            # Open palm (5 fingers) = Clear canvas
            if finger_count == 5:
                if self.last_gesture != "clear" or self.gesture_stable_frames > 20:
                    self.drawing_canvas = None
                    self.prev_x, self.prev_y = None, None
                    print("✨ Canvas cleared by gesture!")
                    self.last_gesture = "clear"
                    self.gesture_stable_frames = 0
                return "CLEAR CANVAS (5 fingers)"
            
            # Peace sign (2 fingers) = Toggle eraser
            elif finger_count == 2 and fingers_up[1] == 1 and fingers_up[2] == 1:
                if self.last_gesture != "eraser" or self.gesture_stable_frames > 20:
                    self.eraser_mode = not self.eraser_mode
                    print(f"🖌️ Eraser: {'ON' if self.eraser_mode else 'OFF'}")
                    self.last_gesture = "eraser"
                    self.gesture_stable_frames = 0
                return f"ERASER {'ON' if self.eraser_mode else 'OFF'}"
        
        self.gesture_stable_frames += 1
        
        # Number gestures (0-5)
        if finger_count == 0:
            return f"Number: 0 (Fist)"
        elif finger_count == 1:
            if fingers_up[1] == 1:  # Index finger
                return "Number: 1 (Pointing)"
            elif fingers_up[0] == 1:  # Thumb
                return "Thumbs Up!"
        elif finger_count == 2:
            if fingers_up[1] == 1 and fingers_up[2] == 1:
                return "Number: 2 (Peace/Victory)"
            elif fingers_up[0] == 1 and fingers_up[4] == 1:
                return "Call Me (Shaka)"
            elif fingers_up[0] == 1 and fingers_up[1] == 1:
                return "Number: 2 (L-Shape)"
        elif finger_count == 3:
            if fingers_up[1] == 1 and fingers_up[2] == 1 and fingers_up[3] == 1:
                return "Number: 3"
            elif fingers_up[0] == 1 and fingers_up[1] == 1 and fingers_up[4] == 1:
                return "I Love You"
        elif finger_count == 4:
            if fingers_up[0] == 0:
                return "Number: 4"
            else:
                return "Number: 4 (with thumb)"
        elif finger_count == 5:
            return "Number: 5 (Open Palm)"
        
        return f"Fingers: {finger_count}"
    
    def calculate_hand_distance(self, hand_landmarks):
        """Calculate approximate distance of hand from camera"""
        # Use wrist to middle finger tip distance as reference
        wrist = hand_landmarks.landmark[0]
        middle_tip = hand_landmarks.landmark[12]
        
        distance = np.sqrt(
            (wrist.x - middle_tip.x)**2 + 
            (wrist.y - middle_tip.y)**2
        )
        return distance
    
    def save_screenshot(self):
        """Save current drawing to file"""
        if self.drawing_canvas is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.screenshot_dir, f"drawing_{timestamp}.png")
            cv2.imwrite(filename, self.drawing_canvas)
            print(f"✅ Drawing saved: {filename}")
            return True
        return False
    
    def draw_help_overlay(self, frame):
        """Draw help overlay with controls"""
        h, w = frame.shape[:2]
        overlay = frame.copy()
        
        # Semi-transparent background
        cv2.rectangle(overlay, (50, 50), (w - 50, h - 50), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        
        # Title
        cv2.putText(frame, "CONTROLS & SHORTCUTS", (w//2 - 220, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        y_start = 130
        controls = [
            "KEYBOARD CONTROLS:",
            "  D - Toggle Drawing Mode",
            "  C - Clear Canvas",
            "  S - Save Screenshot",
            "  L - Toggle Landmarks",
            "  F - Toggle Finger Status",
            "  H - Toggle This Help",
            "  +/= - Increase Brush Size",
            "  - - Decrease Brush Size",
            "  G - Toggle Gesture Shortcuts",
            "  Q - Quit Application",
            "",
            "GESTURE SHORTCUTS (Drawing Mode):",
            "  Point (1 finger) - Draw/Write",
            "  Fist (0 fingers) - Stop Drawing",
            "  Peace (2 fingers) - Toggle Eraser",
            "  Open Palm (5 fingers) - Clear Canvas",
            "",
            "DRAWING TIPS:",
            "  - Click color boxes to change color",
            "  - Use shapes for precise drawings",
            "  - Drawings auto-save in folder"
        ]
        
        for i, text in enumerate(controls):
            color = (255, 255, 0) if text.endswith(":") else (255, 255, 255)
            size = 0.65 if text.endswith(":") else 0.55
            cv2.putText(frame, text, (80, y_start + i * 28),
                       cv2.FONT_HERSHEY_SIMPLEX, size, color, 1 if text.endswith(":") else 1)
        
        cv2.putText(frame, "Press H to close", (w//2 - 110, h - 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    def draw_color_palette(self, frame):
        """Draw color palette on the frame"""
        palette_x = frame.shape[1] - 260
        palette_y = 10
        color_list = ['green', 'blue', 'red', 'yellow', 'white', 'purple', 'orange']
        
        # Drawing tools section background
        cv2.rectangle(frame, (palette_x - 5, palette_y - 5), 
                     (frame.shape[1] - 5, palette_y + 500), (40, 40, 40), -1)
        cv2.putText(frame, "TOOLS", (palette_x + 65, palette_y + 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        palette_y += 30
        
        # Color palette
        for i, color_name in enumerate(color_list):
            y_pos = palette_y + (i * 35)
            color = self.colors[color_name]
            
            # Draw color box
            cv2.rectangle(frame, (palette_x, y_pos), (palette_x + 35, y_pos + 30), color, -1)
            cv2.rectangle(frame, (palette_x, y_pos), (palette_x + 35, y_pos + 30), (255, 255, 255), 2)
            
            # Highlight selected color
            if self.drawing_color == color:
                cv2.rectangle(frame, (palette_x - 3, y_pos - 3), (palette_x + 38, y_pos + 33), (0, 255, 255), 4)
                cv2.putText(frame, "✓", (palette_x + 42, y_pos + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Hover effect
            if self.hover_item == f"color_{i}":
                cv2.rectangle(frame, (palette_x - 2, y_pos - 2), (palette_x + 37, y_pos + 32), (255, 255, 0), 2)
            
            # Color name
            cv2.putText(frame, color_name[:3].upper(), (palette_x + 40, y_pos + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        
        # Tools section
        tools_y = palette_y + (len(color_list) * 35) + 15
        
        # Eraser
        eraser_color = (180, 180, 180) if self.eraser_mode else (80, 80, 80)
        cv2.rectangle(frame, (palette_x, tools_y), (palette_x + 70, tools_y + 30), eraser_color, -1)
        cv2.rectangle(frame, (palette_x, tools_y), (palette_x + 70, tools_y + 30), (255, 255, 255), 2)
        if self.eraser_mode:
            cv2.rectangle(frame, (palette_x - 3, tools_y - 3), (palette_x + 73, tools_y + 33), (0, 255, 255), 4)
            cv2.putText(frame, "✓", (palette_x + 73, tools_y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        if self.hover_item == "eraser":
            cv2.rectangle(frame, (palette_x - 2, tools_y - 2), (palette_x + 72, tools_y + 32), (255, 255, 0), 2)
        cv2.putText(frame, "ERASE", (palette_x + 8, tools_y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0) if self.eraser_mode else (255, 255, 255), 1)
        
        # Clear
        clear_y = tools_y + 35
        cv2.rectangle(frame, (palette_x, clear_y), (palette_x + 70, clear_y + 30), (0, 0, 180), -1)
        cv2.rectangle(frame, (palette_x, clear_y), (palette_x + 70, clear_y + 30), (255, 255, 255), 2)
        if self.hover_item == "clear":
            cv2.rectangle(frame, (palette_x - 2, clear_y - 2), (palette_x + 72, clear_y + 32), (255, 255, 0), 2)
        cv2.putText(frame, "CLEAR", (palette_x + 8, clear_y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        
        # Save
        save_y = clear_y + 35
        cv2.rectangle(frame, (palette_x, save_y), (palette_x + 70, save_y + 30), (0, 180, 0), -1)
        cv2.rectangle(frame, (palette_x, save_y), (palette_x + 70, save_y + 30), (255, 255, 255), 2)
        if self.hover_item == "save":
            cv2.rectangle(frame, (palette_x - 2, save_y - 2), (palette_x + 72, save_y + 32), (255, 255, 0), 2)
        cv2.putText(frame, "SAVE", (palette_x + 12, save_y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        
        # Shapes section
        shapes_y = save_y + 45
        cv2.putText(frame, "SHAPES:", (palette_x, shapes_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        
        shape_types = [('line', 'LINE'), ('circle', 'CIRC'), ('rectangle', 'RECT')]
        for i, (shape, label) in enumerate(shape_types):
            s_y = shapes_y + 10 + (i * 32)
            shape_color = (0, 220, 220) if self.shape_mode == shape else (70, 70, 70)
            cv2.rectangle(frame, (palette_x, s_y), (palette_x + 70, s_y + 27), shape_color, -1)
            cv2.rectangle(frame, (palette_x, s_y), (palette_x + 70, s_y + 27), (255, 255, 255), 2)
            if self.shape_mode == shape:
                cv2.rectangle(frame, (palette_x - 2, s_y - 2), (palette_x + 72, s_y + 29), (0, 255, 255), 3)
                cv2.putText(frame, "✓", (palette_x + 73, s_y + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            if self.hover_item == f"shape_{i}":
                cv2.rectangle(frame, (palette_x - 2, s_y - 2), (palette_x + 72, s_y + 29), (255, 255, 0), 2)
            cv2.putText(frame, label, (palette_x + 10, s_y + 18),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
        
        # Brush size
        brush_y = shapes_y + 115
        cv2.putText(frame, f"SIZE: {self.brush_size}", (palette_x, brush_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.circle(frame, (palette_x + 35, brush_y + 20), self.brush_size, self.drawing_color, -1)
        cv2.circle(frame, (palette_x + 35, brush_y + 20), self.brush_size, (255, 255, 255), 1)
    
    def check_palette_click(self, x, y, frame_width, frame_height, is_clicking=False):
        """Check if finger is clicking or hovering on color palette"""
        palette_x = frame_width - 260
        palette_y = 40
        color_list = ['green', 'blue', 'red', 'yellow', 'white', 'purple', 'orange']
        
        # Check color boxes
        for i, color_name in enumerate(color_list):
            y_pos = palette_y + (i * 35)
            if palette_x <= x <= palette_x + 35 and y_pos <= y <= y_pos + 30:
                self.hover_item = f"color_{i}"
                if is_clicking:
                    self.drawing_color = self.colors[color_name]
                    self.eraser_mode = False
                    self.shape_mode = None
                    print(f"🎨 Color: {color_name}")
                return True
        
        tools_y = palette_y + (len(color_list) * 35) + 15
        
        # Eraser
        if palette_x <= x <= palette_x + 70 and tools_y <= y <= tools_y + 30:
            self.hover_item = "eraser"
            if is_clicking:
                self.eraser_mode = not self.eraser_mode
                self.shape_mode = None
                print(f"🖌️ Eraser: {'ON' if self.eraser_mode else 'OFF'}")
            return True
        
        # Clear
        clear_y = tools_y + 35
        if palette_x <= x <= palette_x + 70 and clear_y <= y <= clear_y + 30:
            self.hover_item = "clear"
            if is_clicking:
                self.drawing_canvas = None
                self.prev_x, self.prev_y = None, None
                self.shape_start = None
                print("🗑️ Canvas cleared!")
            return True
        
        # Save
        save_y = clear_y + 35
        if palette_x <= x <= palette_x + 70 and save_y <= y <= save_y + 30:
            self.hover_item = "save"
            if is_clicking:
                self.save_screenshot()
            return True
        
        # Shapes
        shapes_y = save_y + 55
        shape_types = ['line', 'circle', 'rectangle']
        for i, shape in enumerate(shape_types):
            s_y = shapes_y + (i * 32)
            if palette_x <= x <= palette_x + 70 and s_y <= y <= s_y + 27:
                self.hover_item = f"shape_{i}"
                if is_clicking:
                    self.shape_mode = shape if self.shape_mode != shape else None
                    self.eraser_mode = False
                    print(f"📐 Shape: {self.shape_mode if self.shape_mode else 'Free draw'}")
                return True
        
        self.hover_item = None
        return False
    
    def draw_info_panel(self, frame, gesture, hand_type, fps):
        """Draw information panel on frame"""
        height, width, _ = frame.shape
        
        # Semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (500, 210), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Display information
        cv2.putText(frame, f"Gesture: {gesture[:30]}", (20, 45), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        cv2.putText(frame, f"Hand: {hand_type}", (20, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2)
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 115), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        
        # Drawing mode indicator
        mode_text = "🎨 DRAWING MODE" if self.drawing_mode else "👋 GESTURE MODE"
        mode_color = (0, 255, 0) if self.drawing_mode else (150, 150, 150)
        cv2.putText(frame, f"Mode: {mode_text}", (20, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2)
        
        # Quick tips
        if self.drawing_mode:
            tip = "Point to draw | Fist to stop | Peace for eraser"
        else:
            tip = "Press 'H' for help | 'D' for drawing mode"
        cv2.putText(frame, tip, (20, 180), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        
        cv2.putText(frame, "Press 'Q' to quit", (20, 200), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
    
    def run(self, camera_index=None):
        """Main loop to capture and process video"""
        # Try to find available cameras
        print("\n" + "="*60)
        print("Checking available cameras...")
        print("="*60)
        
        available_cameras = []
        for i in range(5):  # Check first 5 camera indices
            test_cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if test_cap.isOpened():
                ret, _ = test_cap.read()
                if ret:
                    backend = test_cap.getBackendName()
                    width = int(test_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(test_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    available_cameras.append((i, backend, width, height))
                    print(f"Camera {i}: Available ({backend}) - {width}x{height}")
                test_cap.release()
        
        if not available_cameras:
            print("\n❌ No cameras found!")
            print("Please check your camera connection.")
            input("Press Enter to exit...")
            return
        
        print("\n" + "="*60)
        
        # If camera_index is provided, use it
        if camera_index is not None and 0 <= camera_index < 5:
            # Check if the specified camera is available
            if any(cam[0] == camera_index for cam in available_cameras):
                print(f"Using specified Camera {camera_index}")
            else:
                print(f"⚠️  Camera {camera_index} not available, choosing from available cameras...")
                camera_index = None
        
        # If no camera specified or invalid, prompt user
        if camera_index is None:
            if len(available_cameras) > 1:
                print(f"Found {len(available_cameras)} cameras!")
                for idx, backend, w, h in available_cameras:
                    cam_type = "Phone/Smart Connect" if idx == 0 else "PC Built-in Camera"
                    print(f"  - Camera {idx}: {cam_type} ({backend}) - {w}x{h}")
                
                while True:
                    try:
                        choice = input(f"\n👉 Enter camera number to use (0-{available_cameras[-1][0]}): ")
                        camera_index = int(choice)
                        if any(cam[0] == camera_index for cam in available_cameras):
                            break
                        else:
                            print(f"❌ Camera {camera_index} is not available. Please choose from the list.")
                    except ValueError:
                        print("❌ Please enter a valid number.")
            else:
                camera_index = available_cameras[0][0]
                print(f"Using Camera {camera_index}")
        
        print("="*60)
        print(f"Opening Camera {camera_index}...")
        
        # Open camera with DirectShow backend for Windows
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print(f"\n❌ Failed to open camera {camera_index}")
            print("Trying alternative method...")
            cap = cv2.VideoCapture(camera_index)
            
        if not cap.isOpened():
            print(f"\n❌ Still cannot open camera {camera_index}")
            input("Press Enter to exit...")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Verify camera is working
        ret, test_frame = cap.read()
        if not ret or test_frame is None:
            print(f"\n❌ Camera {camera_index} opened but cannot read frames")
            cap.release()
            input("Press Enter to exit...")
            return
        
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"✅ Camera ready! Resolution: {actual_width}x{actual_height}")
        
        prev_time = 0
        
        print("\n✅ Hand Gesture Reader Started!")
        print("Show your hand gestures to the camera")
        print("Controls:")
        print("  - Press 'd' to toggle drawing mode")
        print("  - Press 'c' to clear drawing")
        print("  - Press '+' to increase brush size")
        print("  - Press '-' to decrease brush size")
        print("  - Press 'q' to quit\n")
        print("Drawing Tips:")
        print("  - Point with INDEX finger only to draw")
        print("  - Make a FIST to stop drawing")
        print("  - Click color boxes on right to change color\n")
        
        # Initialize drawing canvas
        if self.drawing_canvas is None:
            self.drawing_canvas = np.zeros((actual_height, actual_width, 3), dtype=np.uint8)
        
        while True:
            success, frame = cap.read()
            if not success:
                print("Failed to capture frame")
                break
            
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # Ensure canvas matches frame size
            if self.drawing_canvas is None or self.drawing_canvas.shape[:2] != (h, w):
                self.drawing_canvas = np.zeros((h, w, 3), dtype=np.uint8)
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.hands.process(rgb_frame)
            
            gesture = "No hand detected"
            hand_type = "N/A"
            
            # Draw hand landmarks and recognize gestures
            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, 
                                                       results.multi_handedness):
                    # Draw hand landmarks (if enabled)
                    if self.show_landmarks:
                        self.mp_draw.draw_landmarks(
                            frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.mp_drawing_styles.get_default_hand_connections_style()
                        )
                    
                    # Get hand type
                    hand_type = handedness.classification[0].label
                    
                    # Count fingers and recognize gesture
                    fingers_up = self.count_fingers(hand_landmarks, hand_type)
                    gesture = self.recognize_gesture(fingers_up, hand_landmarks)
                    
                    # Get index finger tip position for drawing
                    index_tip = hand_landmarks.landmark[8]
                    x = int(index_tip.x * w)
                    y = int(index_tip.y * h)
                    
                    # Drawing mode logic
                    if self.drawing_mode:
                        # Get number of fingers up
                        num_fingers = sum(fingers_up)
                        
                        # Always check for hover on palette
                        on_palette = self.check_palette_click(x, y, w, h, is_clicking=False)
                        
                        # Check if clicking on palette (thumb + index or just index)
                        if num_fingers == 1 and fingers_up[1] == 1 and on_palette:
                            self.check_palette_click(x, y, w, h, is_clicking=True)
                            self.prev_x, self.prev_y = None, None
                        # Eraser mode: Index finger only for precise erasing
                        elif self.eraser_mode and num_fingers == 1 and fingers_up[1] == 1:
                            # Show eraser circle
                            eraser_size = self.brush_size * 2
                            cv2.circle(frame, (x, y), eraser_size, (100, 100, 100), 2)
                            cv2.circle(frame, (x, y), eraser_size, (50, 50, 50), -1)
                            cv2.putText(frame, "ERASING", (x + 15, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                            
                            if self.prev_x is not None and self.prev_y is not None:
                                cv2.line(self.drawing_canvas, (self.prev_x, self.prev_y), 
                                       (x, y), (0, 0, 0), eraser_size)
                            self.prev_x, self.prev_y = x, y
                        # Shape drawing: Use TWO fingers (index + middle)
                        elif self.shape_mode and num_fingers >= 2 and fingers_up[1] == 1 and fingers_up[2] == 1:
                            # Show two-finger indicator
                            cv2.circle(frame, (x, y), 12, (255, 0, 255), 2)
                            cv2.putText(frame, "SHAPE MODE", (x + 15, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                            
                            if self.shape_mode:
                                # Shape drawing mode
                                if self.prev_x is None:
                                    # Starting point for shape
                                    self.prev_x, self.prev_y = x, y
                                else:
                                    # Draw shape preview on frame
                                    if self.shape_mode == 'line':
                                        cv2.line(frame, (self.prev_x, self.prev_y), (x, y), 
                                               self.drawing_color, self.brush_size)
                                    elif self.shape_mode == 'circle':
                                        radius = int(((x - self.prev_x)**2 + (y - self.prev_y)**2)**0.5)
                                        cv2.circle(frame, (self.prev_x, self.prev_y), radius, 
                                                 self.drawing_color, self.brush_size)
                                    elif self.shape_mode == 'rectangle':
                                        cv2.rectangle(frame, (self.prev_x, self.prev_y), (x, y), 
                                                    self.drawing_color, self.brush_size)
                        # Free-hand drawing: Only index finger up (not in eraser or shape mode)
                        elif not self.eraser_mode and not self.shape_mode and num_fingers == 1 and fingers_up[1] == 1:
                            # Show drawing indicator
                            cv2.circle(frame, (x, y), 8, self.drawing_color, -1)
                            cv2.circle(frame, (x, y), 10, (255, 255, 255), 2)
                            
                            if self.prev_x is not None and self.prev_y is not None:
                                cv2.line(self.drawing_canvas, (self.prev_x, self.prev_y), 
                                       (x, y), self.drawing_color, self.brush_size)
                            
                            self.prev_x, self.prev_y = x, y
                        else:
                            # Finalize shape when two fingers are released
                            if self.shape_mode and self.prev_x is not None:
                                # Get current fingertip position
                                if len(hand_landmarks.landmark) > 8:
                                    h, w, _ = frame.shape
                                    curr_x = int(hand_landmarks.landmark[8].x * w)
                                    curr_y = int(hand_landmarks.landmark[8].y * h)
                                    
                                    # Draw final shape on canvas
                                    if self.shape_mode == 'line':
                                        cv2.line(self.drawing_canvas, (self.prev_x, self.prev_y), 
                                               (curr_x, curr_y), self.drawing_color, self.brush_size)
                                        print(f"✏️ Line drawn from ({self.prev_x},{self.prev_y}) to ({curr_x},{curr_y})")
                                    elif self.shape_mode == 'circle':
                                        radius = int(((curr_x - self.prev_x)**2 + (curr_y - self.prev_y)**2)**0.5)
                                        if radius > 5:  # Minimum radius
                                            cv2.circle(self.drawing_canvas, (self.prev_x, self.prev_y), 
                                                     radius, self.drawing_color, self.brush_size)
                                            print(f"⭕ Circle drawn at ({self.prev_x},{self.prev_y}) radius {radius}")
                                    elif self.shape_mode == 'rectangle':
                                        cv2.rectangle(self.drawing_canvas, (self.prev_x, self.prev_y), 
                                                    (curr_x, curr_y), self.drawing_color, self.brush_size)
                                        print(f"▭ Rectangle drawn from ({self.prev_x},{self.prev_y}) to ({curr_x},{curr_y})")
                            
                            # Reset when gesture changes
                            self.prev_x, self.prev_y = None, None
                    
                    # Calculate and display hand distance
                    distance = self.calculate_hand_distance(hand_landmarks)
                    
                    # Draw finger status (only in gesture mode and if enabled)
                    if not self.drawing_mode and self.show_finger_status:
                        finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
                        y_offset = 230
                        for i, (finger, status) in enumerate(zip(finger_names, fingers_up)):
                            color = (0, 255, 0) if status == 1 else (0, 0, 255)
                            cv2.putText(frame, f"{finger}: {'UP' if status == 1 else 'DOWN'}", 
                                      (20, y_offset + i * 30), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            else:
                # Reset drawing position when hand not detected
                self.prev_x, self.prev_y = None, None
            
            # Merge drawing canvas with frame (if canvas exists)
            if self.drawing_canvas is not None:
                mask = cv2.cvtColor(self.drawing_canvas, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
                mask_inv = cv2.bitwise_not(mask)
                
                frame_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
                canvas_fg = cv2.bitwise_and(self.drawing_canvas, self.drawing_canvas, mask=mask)
                frame = cv2.add(frame_bg, canvas_fg)
            
            # Calculate FPS
            current_time = time.time()
            fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
            prev_time = current_time
            
            # Draw color palette in drawing mode
            if self.drawing_mode:
                self.draw_color_palette(frame)
            
            # Draw help overlay if enabled
            if self.show_help:
                self.draw_help_overlay(frame)
            
            # Draw info panel
            if not self.show_help:
                self.draw_info_panel(frame, gesture, hand_type, fps)
            
            # Display the frame
            cv2.imshow("Hand Gesture Reader - Interactive Teaching Tool", frame)
            
            # Keyboard controls with better handling
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == ord('Q'):
                print("\n🛑 Quitting application...")
                break
            elif key == ord('d') or key == ord('D'):
                self.drawing_mode = not self.drawing_mode
                print(f"✏️  Drawing mode: {'ON' if self.drawing_mode else 'OFF'}")
            elif key == ord('c') or key == ord('C'):
                if self.drawing_canvas is not None:
                    self.drawing_canvas = np.zeros((h, w, 3), dtype=np.uint8)
                    self.prev_x, self.prev_y = None, None
                    self.shape_start = None
                    print("🗑️  Canvas cleared!")
            elif key == ord('s') or key == ord('S'):
                self.save_screenshot()
            elif key == ord('h') or key == ord('H'):
                self.show_help = not self.show_help
                print(f"❓ Help: {'Shown' if self.show_help else 'Hidden'}")
            elif key == ord('l') or key == ord('L'):
                self.show_landmarks = not self.show_landmarks
                print(f"🔵 Landmarks: {'Shown' if self.show_landmarks else 'Hidden'}")
            elif key == ord('f') or key == ord('F'):
                self.show_finger_status = not self.show_finger_status
                print(f"👆 Finger status: {'Shown' if self.show_finger_status else 'Hidden'}")
            elif key == ord('g') or key == ord('G'):
                self.gesture_shortcuts_enabled = not self.gesture_shortcuts_enabled
                print(f"🎯 Gesture shortcuts: {'ON' if self.gesture_shortcuts_enabled else 'OFF'}")
            elif key == ord('+') or key == ord('='):
                self.brush_size = min(25, self.brush_size + 2)
                print(f"🖌️  Brush size: {self.brush_size}")
            elif key == ord('-') or key == ord('_'):
                self.brush_size = max(1, self.brush_size - 2)
                print(f"🖌️  Brush size: {self.brush_size}")
            elif key == 27:  # ESC key
                print("\n🛑 ESC pressed - Quitting...")
                break
        
        # Cleanup
        print("\n🧹 Cleaning up resources...")
        cap.release()
        cv2.destroyAllWindows()
        self.hands.close()
        print("✅ Application closed successfully!")


if __name__ == "__main__":
    import sys
    try:
        print("\n" + "="*60)
        print("🎨 HAND GESTURE READER - Interactive Teaching Tool")
        print("="*60)
        reader = HandGestureReader()
        # Use camera 1 by default (PC camera), or specify via command line
        camera_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
        reader.run(camera_id) if camera_id is not None else reader.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your webcam is connected and accessible")
        import traceback
        traceback.print_exc()
