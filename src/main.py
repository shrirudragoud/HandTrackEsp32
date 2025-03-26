import cv2
import numpy as np
import serial
import serial.tools.list_ports
import time
import os
from hand_tracker import HandLandmarkDetector
from visualizer import HandVisualizer

class HandTrackingApp:
    def __init__(self, camera_id: int = 0, serial_port: str = 'COM8', baud_rate: int = 115200, retry_count: int = 3):
        """Initialize the hand tracking application.
        
        Args:
            camera_id (int): Camera device ID (default: 0 for primary camera)
            serial_port (str): Serial port for ESP32 communication
            baud_rate (int): Serial communication baud rate
            retry_count (int): Number of connection retries
        """
        # Initialize camera
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera")
            
        # Initialize components
        self.detector = HandLandmarkDetector()
        self.visualizer = HandVisualizer()
        
        # Store serial parameters for reconnection
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.serial = None
        
        # Try to establish serial connection
        self.connect_to_esp32(retry_count)
            
    def connect_to_esp32(self, retry_count: int = 3):
        """Attempt to connect to ESP32 with retries.
        
        Args:
            retry_count (int): Number of connection attempts
        """
        print("\nChecking available ports...")
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            print(f"Found {port.device}: {port.description}")
            
        print(f"\nAttempting to connect to ESP32 on {self.serial_port}...")
        
        for attempt in range(retry_count):
            try:
                # Close existing connection if any
                if self.serial and self.serial.is_open:
                    self.serial.close()
                    time.sleep(1)  # Wait for port to release
                
                print(f"Connection attempt {attempt + 1}/{retry_count}")
                
                # Try to open port
                self.serial = serial.Serial(
                    port=self.serial_port,
                    baudrate=self.baud_rate,
                    timeout=1,
                    write_timeout=1
                )
                
                # Clear buffers
                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()
                
                print("Connected successfully!")
                print("Waiting for ESP32 to initialize...")
                time.sleep(2)
                
                # Test communication
                self.serial.write(b"00000\n")
                response = self.serial.readline().decode().strip()
                print(f"ESP32 response: {response}")
                
                return True
                
            except serial.SerialException as e:
                print(f"Connection attempt failed: {e}")
                if "Access is denied" in str(e):
                    print("\nTroubleshooting steps:")
                    print("1. Close Arduino IDE and its Serial Monitor")
                    print("2. Close any other applications using the serial port")
                    print("3. Check if the correct COM port is selected")
                    print("4. Try unplugging and reconnecting the ESP32")
                time.sleep(2)  # Wait before retry
            
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(2)
        
        print("\nFailed to connect to ESP32")
        print("Running in camera-only mode")
        return False
        
    def send_to_esp32(self, finger_state: str):
        """Send finger state to ESP32.
        
        Args:
            finger_state (str): Binary string of finger states (e.g., "10110")
        """
        if self.serial and self.serial.is_open:
            try:
                # Add newline character for ESP32 parsing
                data = finger_state + '\n'
                bytes_written = self.serial.write(data.encode())
                self.serial.flush()  # Ensure data is sent
                
                print(f"Sent to ESP32: {finger_state} ({bytes_written} bytes)")
                
                # Read ESP32 response with timeout
                if self.serial.in_waiting:
                    response = self.serial.readline().decode().strip()
                    print(f"ESP32 Response: {response}")
                    
            except serial.SerialException as e:
                print(f"Serial communication error: {e}")
                print("Attempting to reconnect...")
                self.connect_to_esp32()
        
    def run(self):
        """Main application loop."""
        try:
            print("\nStarting Hand Tracking Application...")
            print("Controls:")
            print("  - Press 'q' to quit")
            print("  - Press 'r' to reconnect to ESP32")
            print("  - Press 'd' to toggle debug info")
            print("  - Press 't' to test ESP32 communication")
            
            show_debug = False
            last_state = ""
            frame_count = 0
            
            while True:
                # Read frame
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break
                
                # Convert frame to RGB for MediaPipe
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process frame
                finger_state, angles, position = self.detector.process_frame(frame_rgb)
                
                # Get binary state
                binary_state = finger_state.to_binary()
                
                # Only send if state has changed
                if binary_state != last_state:
                    self.send_to_esp32(binary_state)
                    last_state = binary_state
                
                # Create visualization
                output_frame = self.visualizer.create_visualization(
                    frame.copy(),
                    finger_state,
                    angles,
                    position
                )
                
                # Add ESP32 connection status
                status = "ESP32: Connected" if (self.serial and self.serial.is_open) else "ESP32: Disconnected"
                color = (0, 255, 0) if (self.serial and self.serial.is_open) else (0, 0, 255)
                cv2.putText(output_frame, status,
                           (output_frame.shape[1] - 200, output_frame.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Add debug info
                if show_debug:
                    debug_info = [
                        f"Frame: {frame_count}",
                        f"Last State: {last_state}",
                        f"Current State: {binary_state}",
                        f"Serial Port: {self.serial_port}",
                        f"Serial Connected: {bool(self.serial and self.serial.is_open)}"
                    ]
                    for i, info in enumerate(debug_info):
                        cv2.putText(output_frame, info,
                                  (10, output_frame.shape[0] - 120 + i*20),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                  (255, 255, 255), 1)
                
                # Display frame
                cv2.imshow("Hand Tracking", output_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.connect_to_esp32()
                elif key == ord('d'):
                    show_debug = not show_debug
                elif key == ord('t'):
                    print("\nTesting ESP32 communication...")
                    self.send_to_esp32("11111")
                    time.sleep(0.5)
                    self.send_to_esp32("00000")
                    
                frame_count += 1
                    
        finally:
            # Clean up
            self.cleanup()
    
    def cleanup(self):
        """Release resources."""
        print("\nCleaning up...")
        self.cap.release()
        if self.serial:
            self.serial.close()
        cv2.destroyAllWindows()
            
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()

def main():
    """Application entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hand Tracking Application')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera device ID (default: 0)')
    parser.add_argument('--port', type=str, default='COM8',
                       help='Serial port for ESP32 (default: COM8)')
    parser.add_argument('--baud', type=int, default=115200,
                       help='Baud rate for serial communication (default: 115200)')
    parser.add_argument('--retry', type=int, default=3,
                       help='Number of connection retries (default: 3)')
    
    args = parser.parse_args()
    
    try:
        app = HandTrackingApp(
            camera_id=args.camera,
            serial_port=args.port,
            baud_rate=args.baud,
            retry_count=args.retry
        )
        app.run()
        
    except Exception as e:
        print(f"\nError: {e}")
        
    finally:
        print("\nApplication terminated")

if __name__ == "__main__":
    main()