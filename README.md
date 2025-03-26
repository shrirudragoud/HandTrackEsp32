# HandTrackEsp32_OpenCV

A real-time hand tracking system that controls ESP32 LEDs based on finger states using computer vision.

## Features

- Real-time hand detection and tracking using OpenCV and MediaPipe
- Individual finger state detection (open/closed)
- ESP32 LED control based on finger states
- Visual feedback with landmarks and state indicators
- Serial communication between Python and ESP32
- Debug mode for troubleshooting

## System Architecture

1. Python application detects hand and fingers using OpenCV and MediaPipe
2. Finger states are converted to binary format (e.g., "10110")
3. Data is sent to ESP32 via serial communication
4. ESP32 controls 5 LEDs based on received finger states
5. Real-time visual feedback and status monitoring

## Hardware Requirements

- ESP32 Development Board
- 5 LEDs
- 5 Resistors (220Ω - 330Ω)
- USB Cable
- Webcam
- Jumper Wires
- Breadboard

## Software Requirements

- Python 3.x
- OpenCV
- MediaPipe
- PySerial
- Arduino IDE

## Project Structure

```
HandTrackEsp32/
├── src/                    # Python source code
│   ├── main.py            # Main application
│   ├── hand_tracker.py    # Hand tracking implementation
│   ├── visualizer.py      # Visualization utilities
│   └── check_ports.py     # Serial port utilities
├── esp32_firmware/        # ESP32 code
│   ├── led_control.ino    # ESP32 firmware
│   └── README.md          # ESP32 setup guide
└── requirements.txt       # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/shrirudragoud/HandTrackEsp32.git
cd HandTrackEsp32
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Upload ESP32 firmware:
   - Open `esp32_firmware/led_control.ino` in Arduino IDE
   - Install ESP32 board support if needed
   - Select your board and port
   - Upload the code

4. Connect hardware:
   - Follow wiring guide in esp32_firmware/README.md
   - Connect LEDs to specified GPIO pins

## Usage

1. Run the Python application:
```bash
python src/main.py --port COM8  # Replace COM8 with your ESP32's port
```

2. Controls:
   - Press 'q' to quit
   - Press 'r' to reconnect to ESP32
   - Press 'd' to toggle debug information
   - Press 't' to test LED communication

## Hardware Setup

Connect LEDs to ESP32 as follows:
- LED 1 (Thumb) → GPIO 5
- LED 2 (Index) → GPIO 18
- LED 3 (Middle) → GPIO 19
- LED 4 (Ring) → GPIO 21
- LED 5 (Pinky) → GPIO 22

Each LED should be connected with a 220Ω-330Ω resistor to ground.

## Finger State Format

The binary string format represents finger states as follows:
```
[Thumb][Index][Middle][Ring][Pinky]

Example:
"10110" means:
- Thumb: Open (1)
- Index: Open (1)
- Middle: Closed (0)
- Ring: Open (1)
- Pinky: Closed (0)
```

## Troubleshooting

1. Serial Port Issues:
   - Use `python src/check_ports.py` to list available ports
   - Close Arduino IDE's Serial Monitor before running
   - Try unplugging and reconnecting ESP32

2. LED Control:
   - Verify LED connections and resistors
   - Check GPIO pin assignments
   - Use debug mode ('d' key) to monitor communication

3. Hand Detection:
   - Ensure good lighting conditions
   - Keep hand within camera frame
   - Adjust camera position if needed

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
