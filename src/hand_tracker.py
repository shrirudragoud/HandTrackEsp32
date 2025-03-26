import numpy as np
from typing import List, Tuple
import mediapipe as mp
from dataclasses import dataclass

@dataclass
class FingerState:
    """Represents the state of all fingers."""
    thumb: bool = False
    index: bool = False
    middle: bool = False
    ring: bool = False
    pinky: bool = False
    
    def to_binary(self) -> str:
        """Convert finger states to binary string.
        
        Returns:
            str: Binary string where 1 = open, 0 = closed
                 Order: thumb, index, middle, ring, pinky
        """
        return "".join(["1" if state else "0" for state in 
                       [self.thumb, self.index, self.middle, self.ring, self.pinky]])
    
    @classmethod
    def from_binary(cls, binary: str) -> 'FingerState':
        """Create FingerState from binary string.
        
        Args:
            binary (str): Binary string (e.g., "10110")
            
        Returns:
            FingerState: New instance with specified states
        """
        if len(binary) != 5 or not all(c in '01' for c in binary):
            raise ValueError("Invalid binary string")
        return cls(
            thumb=binary[0] == '1',
            index=binary[1] == '1',
            middle=binary[2] == '1',
            ring=binary[3] == '1',
            pinky=binary[4] == '1'
        )

class HandLandmarkDetector:
    """Detects and analyzes hand landmarks using MediaPipe."""
    
    def __init__(self):
        """Initialize the MediaPipe hands solution."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
    def detect_finger_states(self, landmarks) -> FingerState:
        """Determine which fingers are open based on hand landmarks.
        
        Args:
            landmarks: MediaPipe hand landmarks
            
        Returns:
            FingerState: Current state of all fingers
        """
        if not landmarks:
            return FingerState()
            
        finger_state = FingerState()
        
        # Thumb: Compare x-coordinates of tip and IP joint
        finger_state.thumb = landmarks[4].x < landmarks[3].x
        
        # Other fingers: Compare y-coordinates of tip and PIP joints
        fingers = {
            'index': (8, 6),   # Tip, PIP
            'middle': (12, 10),
            'ring': (16, 14),
            'pinky': (20, 18)
        }
        
        for finger, (tip_idx, pip_idx) in fingers.items():
            # Finger is considered open if tip is above PIP joint
            is_open = landmarks[tip_idx].y < landmarks[pip_idx].y
            setattr(finger_state, finger, is_open)
            
        return finger_state
    
    def get_hand_position(self, landmarks) -> Tuple[float, float]:
        """Calculate the center position of the hand.
        
        Args:
            landmarks: MediaPipe hand landmarks
            
        Returns:
            Tuple[float, float]: (x, y) coordinates of hand center
        """
        if not landmarks:
            return (0.0, 0.0)
            
        # Calculate average position of all landmarks
        x_coords = [lm.x for lm in landmarks]
        y_coords = [lm.y for lm in landmarks]
        
        return (np.mean(x_coords), np.mean(y_coords))
    
    def get_finger_angles(self, landmarks) -> List[float]:
        """Calculate angles between finger segments.
        
        Args:
            landmarks: MediaPipe hand landmarks
            
        Returns:
            List[float]: Angles in degrees for each finger
        """
        if not landmarks:
            return [0.0] * 5
            
        angles = []
        # Finger triplet points (tip, PIP, MCP)
        finger_points = [
            (4, 3, 2),    # Thumb
            (8, 7, 6),    # Index
            (12, 11, 10), # Middle
            (16, 15, 14), # Ring
            (20, 19, 18)  # Pinky
        ]
        
        for tip, pip, mcp in finger_points:
            # Get vectors
            v1 = np.array([landmarks[pip].x - landmarks[mcp].x,
                          landmarks[pip].y - landmarks[mcp].y])
            v2 = np.array([landmarks[tip].x - landmarks[pip].x,
                          landmarks[tip].y - landmarks[pip].y])
            
            # Calculate angle
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
            angles.append(np.degrees(angle))
            
        return angles
        
    def process_frame(self, frame) -> Tuple[FingerState, List[float], Tuple[float, float]]:
        """Process a frame and return hand analysis results.
        
        Args:
            frame: RGB image frame
            
        Returns:
            Tuple containing:
            - FingerState: Current state of fingers
            - List[float]: Angles of each finger
            - Tuple[float, float]: Hand position (x, y)
        """
        results = self.hands.process(frame)
        
        if not results.multi_hand_landmarks:
            return FingerState(), [0.0] * 5, (0.0, 0.0)
            
        landmarks = results.multi_hand_landmarks[0].landmark
        
        finger_state = self.detect_finger_states(landmarks)
        angles = self.get_finger_angles(landmarks)
        position = self.get_hand_position(landmarks)
        
        return finger_state, angles, position