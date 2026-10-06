import cv2
import mediapipe as mp
import numpy as np
import json
import os
from datetime import datetime

class GestureTrainer:
    """Advanced gesture trainer for creating custom teaching gestures"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.custom_gestures = {}
        self.gesture_file = "custom_gestures.json"
        self.load_gestures()
        
    def load_gestures(self):
        """Load saved custom gestures"""
        if os.path.exists(self.gesture_file):
            with open(self.gesture_file, 'r') as f:
                self.custom_gestures = json.load(f)
            print(f"Loaded {len(self.custom_gestures)} custom gestures")
    
    def save_gestures(self):
        """Save custom gestures to file"""
        with open(self.gesture_file, 'w') as f:
            json.dump(self.custom_gestures, f, indent=2)
        print(f"Saved {len(self.custom_gestures)} custom gestures")
    
    def extract_hand_features(self, hand_landmarks):
        """Extract key features from hand landmarks"""
        features = {}
        
        # Finger tip positions relative to wrist
        finger_tips = [4, 8, 12, 16, 20]
        wrist = hand_landmarks.landmark[0]
        
        features['finger_positions'] = []
        for tip_idx in finger_tips:
            tip = hand_landmarks.landmark[tip_idx]
            features['finger_positions'].append({
                'x': tip.x - wrist.x,
                'y': tip.y - wrist.y,
                'z': tip.z - wrist.z
            })
        
        # Palm center
        palm_center = hand_landmarks.landmark[9]
        features['palm_center'] = {
            'x': palm_center.x - wrist.x,
            'y': palm_center.y - wrist.y,
            'z': palm_center.z - wrist.z
        }
        
        # Hand orientation
        index_mcp = hand_landmarks.landmark[5]
        pinky_mcp = hand_landmarks.landmark[17]
        
        features['hand_width'] = abs(index_mcp.x - pinky_mcp.x)
        features['hand_height'] = abs(wrist.y - palm_center.y)
        
        return features
    
    def train_gesture(self, gesture_name):
        """Train a new custom gesture"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        samples = []
        max_samples = 30
        recording = False
        
        print(f"\nTraining gesture: {gesture_name}")
        print("Press 's' to start recording samples")
        print("Press 'q' to finish and save")
        
        while True:
            success, frame = cap.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Draw instructions
            status_color = (0, 255, 0) if recording else (0, 0, 255)
            status_text = "RECORDING" if recording else "Ready - Press 's' to start"
            
            cv2.putText(frame, f"Gesture: {gesture_name}", (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, status_text, (20, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
            cv2.putText(frame, f"Samples: {len(samples)}/{max_samples}", (20, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, "Press 'q' when done", (20, 160),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            
            # Process hand
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # Record sample if recording
                    if recording and len(samples) < max_samples:
                        features = self.extract_hand_features(hand_landmarks)
                        samples.append(features)
                        
                        # Visual feedback
                        cv2.circle(frame, (frame.shape[1] - 50, 50), 20, (0, 255, 0), -1)
                    
                    if len(samples) >= max_samples:
                        recording = False
                        cv2.putText(frame, "Max samples reached! Press 'q' to save", 
                                  (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Gesture Trainer", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                recording = not recording
            elif key == ord('q'):
                if len(samples) >= 5:
                    break
                else:
                    print("Need at least 5 samples! Keep recording...")
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Save the gesture
        if len(samples) >= 5:
            self.custom_gestures[gesture_name] = {
                'samples': samples,
                'created': datetime.now().isoformat(),
                'num_samples': len(samples)
            }
            self.save_gestures()
            print(f"Successfully saved gesture '{gesture_name}' with {len(samples)} samples")
        else:
            print("Not enough samples. Gesture not saved.")
    
    def list_gestures(self):
        """List all trained gestures"""
        if not self.custom_gestures:
            print("No custom gestures trained yet.")
            return
        
        print("\n=== Trained Gestures ===")
        for name, data in self.custom_gestures.items():
            print(f"- {name}: {data['num_samples']} samples (created: {data['created']})")
    
    def delete_gesture(self, gesture_name):
        """Delete a trained gesture"""
        if gesture_name in self.custom_gestures:
            del self.custom_gestures[gesture_name]
            self.save_gestures()
            print(f"Deleted gesture: {gesture_name}")
        else:
            print(f"Gesture '{gesture_name}' not found")
    
    def menu(self):
        """Interactive menu"""
        while True:
            print("\n=== Hand Gesture Trainer ===")
            print("1. Train new gesture")
            print("2. List trained gestures")
            print("3. Delete gesture")
            print("4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                name = input("Enter gesture name: ").strip()
                if name:
                    self.train_gesture(name)
            elif choice == '2':
                self.list_gestures()
            elif choice == '3':
                name = input("Enter gesture name to delete: ").strip()
                self.delete_gesture(name)
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice!")


if __name__ == "__main__":
    trainer = GestureTrainer()
    trainer.menu()
