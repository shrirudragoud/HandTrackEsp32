import cv2
import numpy as np
from typing import Tuple, List
from hand_tracker import FingerState

class HandVisualizer:
    """Handles visualization of hand tracking results."""
    
    def __init__(self):
        """Initialize colors and text parameters."""
        self.colors = {
            'landmark': (0, 255, 0),    # Green
            'connection': (255, 0, 0),   # Blue
            'text': (255, 255, 255),    # White
            'open': (0, 255, 0),        # Green
            'closed': (0, 0, 255)       # Red
        }
        
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.6
        self.thickness = 2
        
    def draw_finger_states(self, frame: np.ndarray, 
                          finger_state: FingerState,
                          position: Tuple[float, float]) -> np.ndarray:
        """Draw finger state indicators on the frame.
        
        Args:
            frame (np.ndarray): Input frame
            finger_state (FingerState): Current finger states
            position (Tuple[float, float]): Hand position (x, y)
            
        Returns:
            np.ndarray: Frame with finger state visualization
        """
        h, w = frame.shape[:2]
        x, y = int(position[0] * w), int(position[1] * h)
        
        # Draw finger state indicators
        fingers = ['thumb', 'index', 'middle', 'ring', 'pinky']
        spacing = 30
        
        for i, finger in enumerate(fingers):
            state = getattr(finger_state, finger)
            color = self.colors['open'] if state else self.colors['closed']
            pos = (20, 50 + i * spacing)
            
            # Draw circle indicator
            cv2.circle(frame, (pos[0], pos[1]), 8, color, -1)
            
            # Draw finger name
            cv2.putText(frame, finger.capitalize(), 
                       (pos[0] + 20, pos[1] + 5),
                       self.font, self.font_scale, self.colors['text'], 
                       self.thickness)
        
        return frame
    
    def draw_binary_state(self, frame: np.ndarray, 
                         finger_state: FingerState) -> np.ndarray:
        """Draw binary representation of finger states.
        
        Args:
            frame (np.ndarray): Input frame
            finger_state (FingerState): Current finger states
            
        Returns:
            np.ndarray: Frame with binary state visualization
        """
        binary = finger_state.to_binary()
        text_pos = (20, frame.shape[0] - 30)
        
        cv2.putText(frame, f"State: {binary}", text_pos,
                   self.font, self.font_scale, self.colors['text'], 
                   self.thickness)
        
        return frame
    
    def draw_angles(self, frame: np.ndarray, 
                   angles: List[float],
                   position: Tuple[float, float]) -> np.ndarray:
        """Draw finger angles on the frame.
        
        Args:
            frame (np.ndarray): Input frame
            angles (List[float]): List of finger angles
            position (Tuple[float, float]): Hand position
            
        Returns:
            np.ndarray: Frame with angle visualization
        """
        h, w = frame.shape[:2]
        x, y = int(position[0] * w), int(position[1] * h)
        
        # Draw angle values
        for i, angle in enumerate(angles):
            pos = (w - 150, 50 + i * 30)
            cv2.putText(frame, f"Angle {i+1}: {angle:.1f}°",
                       pos, self.font, self.font_scale,
                       self.colors['text'], self.thickness)
        
        return frame
    
    def draw_hand_position(self, frame: np.ndarray,
                          position: Tuple[float, float]) -> np.ndarray:
        """Draw hand position indicator on frame.
        
        Args:
            frame (np.ndarray): Input frame
            position (Tuple[float, float]): Normalized hand position (x, y)
            
        Returns:
            np.ndarray: Frame with position visualization
        """
        h, w = frame.shape[:2]
        x, y = int(position[0] * w), int(position[1] * h)
        
        # Draw crosshair at hand position
        size = 20
        cv2.line(frame, (x - size, y), (x + size, y),
                self.colors['landmark'], self.thickness)
        cv2.line(frame, (x, y - size), (x, y + size),
                self.colors['landmark'], self.thickness)
        
        # Draw coordinates
        cv2.putText(frame, f"({position[0]:.2f}, {position[1]:.2f})",
                   (x + 10, y + 20), self.font, self.font_scale,
                   self.colors['text'], self.thickness)
        
        return frame
    
    def create_visualization(self, frame: np.ndarray,
                           finger_state: FingerState,
                           angles: List[float],
                           position: Tuple[float, float]) -> np.ndarray:
        """Create complete visualization with all components.
        
        Args:
            frame (np.ndarray): Input frame
            finger_state (FingerState): Current finger states
            angles (List[float]): List of finger angles
            position (Tuple[float, float]): Hand position
            
        Returns:
            np.ndarray: Frame with complete visualization
        """
        # Draw each component
        frame = self.draw_finger_states(frame, finger_state, position)
        frame = self.draw_binary_state(frame, finger_state)
        frame = self.draw_angles(frame, angles, position)
        frame = self.draw_hand_position(frame, position)
        
        # Add title
        cv2.putText(frame, "Hand Tracking Visualization",
                   (20, 30), self.font, 1.0,
                   self.colors['text'], self.thickness)
        
        return frame