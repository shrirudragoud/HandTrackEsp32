# ESP32 LED Control Setup

This guide explains how to set up and upload the LED control firmware to your ESP32.

## Hardware Setup

1. Connect 5 LEDs to your ESP32 as follows:
   - LED 1 (Thumb) → GPIO 5
   - LED 2 (Index) → GPIO 18
   - LED 3 (Middle) → GPIO 19
   - LED 4 (Ring) → GPIO 21
   - LED 5 (Pinky) → GPIO 22

2. For each LED:
   - Connect the LED's anode (longer leg, +) to the GPIO pin
   - Connect the LED's cathode (shorter leg, -) to a 220Ω-330Ω resistor
   - Connect the other end of the resistor to GND

## Software Setup

1. Install Arduino IDE:
   - Download from [Arduino's official website](https://www.arduino.cc/en/software)
   - Install the IDE

2. Install ESP32 Board Support:
   - Open Arduino IDE
   - Go to File → Preferences
   - Add this URL to Additional Board Manager URLs:
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Go to Tools → Board → Boards Manager
   - Search for "esp32"
   - Install "ESP32 by Espressif Systems"

3. Configure Arduino IDE:
   - Select your board: Tools → Board → ESP32 Arduino → ESP32 Dev Module
   - Select the correct port: Tools → Port → (your ESP32 port)
   - Set Upload Speed: Tools → Upload Speed → 115200

## Upload Instructions

1. Open `led_control.ino` in Arduino IDE
2. Click Verify/Compile (✓) to check for errors
3. Click Upload (→) to flash the ESP32
4. Open Serial Monitor (Tools → Serial Monitor) and set baud rate to 115200
5. You should see "ESP32 LED Control Ready" message

## Testing

1. The ESP32 will perform a startup sequence:
   - LEDs will light up one by one
   - All LEDs will flash briefly
   - All LEDs will turn off

2. Expected behavior:
   - Receives 5-character binary strings (e.g., "10110")
   - Controls LEDs based on received data
   - Sends feedback through Serial Monitor
   - Auto-turns off LEDs if no data received for 5 seconds

## Troubleshooting

1. LEDs not responding:
   - Check LED polarity
   - Verify resistor connections
   - Confirm GPIO pin numbers
   - Test LEDs with `checkLEDs()` function

2. Communication issues:
   - Verify correct COM port selection
   - Confirm baud rate matches (115200)
   - Check USB cable connection
   - Try `resetCommunication()` function

3. Upload fails:
   - Hold BOOT button while uploading
   - Release after upload starts
   - If still failing, try:
     1. Press and hold BOOT
     2. Press and release EN/RST
     3. Release BOOT
     4. Upload sketch

## Pin Reference

```
ESP32 Pins:
GPIO 5  → LED 1 (Thumb)  + 220Ω → GND
GPIO 18 → LED 2 (Index)  + 220Ω → GND
GPIO 19 → LED 3 (Middle) + 220Ω → GND
GPIO 21 → LED 4 (Ring)   + 220Ω → GND
GPIO 22 → LED 5 (Pinky)  + 220Ω → GND
```

## Communication Protocol

- Baud Rate: 115200
- Data Format: "XXXXX\n" where X is '0' or '1'
- Example: "10110\n" → Thumb, Index, and Ring fingers ON