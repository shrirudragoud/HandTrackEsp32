Here’s a structured **Project Plan** for using **Python OpenCV** to detect a human palm, track five fingers in real-time, and control five LEDs on an ESP32 while displaying received data on the **Serial Monitor**.  

---

# **Project Plan: Palm & Finger Tracking with ESP32 LED Control**
### **Project Overview**
The goal of this project is to use **Python OpenCV** to detect and track a human palm with five fingers, send the detected finger states (open/closed) to an **ESP32** via USB, and use the ESP32 to control five LEDs based on the received data. The ESP32 will also display the received finger states on the **Serial Monitor**.

---

## **1. Hardware Requirements**
- **ESP32 Development Board**
- **5 LEDs**
- **5 Resistors (220Ω - 330Ω)**
- **USB Cable (for ESP32 & PC Communication)**
- **Laptop/PC with Camera**
- **Jumper Wires**
- **Breadboard**

---

## **2. Software Requirements**
- **Python 3.x**
- **OpenCV (`cv2`) for palm & finger tracking**
- **Mediapipe (for hand landmark detection)**
- **PySerial (for serial communication)**
- **Arduino IDE / PlatformIO** (for ESP32 programming)

---

## **3. System Architecture**
1. **Python OpenCV + Mediapipe** detects a **palm & five fingers** in real-time.
2. The number of **open fingers (0-5)** is determined.
3. The detected number (e.g., `10110` for **Thumb, Index open; others closed**) is sent via **USB Serial**.
4. **ESP32 reads serial data** and controls **5 LEDs** based on the received signal.
5. **ESP32 Serial Monitor** prints the received finger states.

---

## **4. Implementation Steps**
### **Step 1: Setup Python Environment**
1. **Install required libraries**  
   ```bash
   pip install opencv-python mediapipe pyserial
   ```
2. **Write Python Code to Detect Hand & Track Fingers**  
   - Use **MediaPipe Hands API** to get **21 landmarks** of a human hand.
   - Determine which fingers are open using landmark positions.
   - Convert the finger states into a **binary string (e.g., "10110")**.
   - Send the binary string over **Serial (USB)** to the ESP32.

---

### **Step 2: Write Python Code to Send Data to ESP32**
```python
import cv2
import mediapipe as mp
import serial
import time

# Initialize Serial Communication with ESP32
ser = serial.Serial('COM3', 115200, timeout=1)  # Change COM port accordingly
time.sleep(2)  # Wait for ESP32 to initialize

# Initialize MediaPipe Hand Detection
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)  # Open webcam

def get_finger_state(landmarks):
    fingers = [0, 0, 0, 0, 0]  # Thumb, Index, Middle, Ring, Pinky
    
    # Thumb
    if landmarks[4].x < landmarks[3].x:  # If thumb tip is to the left of the thumb base
        fingers[0] = 1
    
    # Other fingers (Index, Middle, Ring, Pinky)
    for i, tip in enumerate([8, 12, 16, 20]):  
        if landmarks[tip].y < landmarks[tip - 2].y:  # If tip is above its base
            fingers[i + 1] = 1
    
    return "".join(map(str, fingers))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get finger states (open/closed)
            finger_state = get_finger_state(hand_landmarks.landmark)
            ser.write(finger_state.encode())  # Send to ESP32
            print(f"Sent: {finger_state}")

    cv2.imshow("Palm & Finger Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
```

---

### **Step 3: Setup ESP32 Code to Receive Data & Control LEDs**
1. Connect **5 LEDs** to GPIO pins (e.g., **GPIO 5, 18, 19, 21, 22**).
2. Read **serial data** from Python.
3. Control **LED states** based on the received binary string.

---

### **Step 4: Write ESP32 Code**
```cpp
#define LED1 5   // Thumb
#define LED2 18  // Index
#define LED3 19  // Middle
#define LED4 21  // Ring
#define LED5 22  // Pinky

void setup() {
    Serial.begin(115200);
    pinMode(LED1, OUTPUT);
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);
}

void loop() {
    if (Serial.available()) {
        String data = Serial.readStringUntil('\n');  // Read input
        Serial.println("Received: " + data);

        if (data.length() == 5) {  // Ensure valid input length
            digitalWrite(LED1, data[0] == '1' ? HIGH : LOW);
            digitalWrite(LED2, data[1] == '1' ? HIGH : LOW);
            digitalWrite(LED3, data[2] == '1' ? HIGH : LOW);
            digitalWrite(LED4, data[3] == '1' ? HIGH : LOW);
            digitalWrite(LED5, data[4] == '1' ? HIGH : LOW);
        }
    }
}
```

---

## **5. Hardware Wiring Guide**
| **ESP32 GPIO** | **Component** |
|--------------|------------|
| GPIO 5      | LED 1 (Thumb) |
| GPIO 18     | LED 2 (Index) |
| GPIO 19     | LED 3 (Middle) |
| GPIO 21     | LED 4 (Ring) |
| GPIO 22     | LED 5 (Pinky) |
| GND         | LED Common Ground |

**Wiring Steps:**
1. Connect **each LED’s anode (+)** to ESP32 GPIOs.
2. Connect **each LED’s cathode (-)** through a **220Ω resistor** to **GND**.

---

## **6. Testing & Debugging**
1. **Run Python OpenCV code** to detect palm and track fingers.
2. Check the **Python terminal** for the binary output (`10110` etc.).
3. Ensure ESP32 **Serial Monitor** receives data correctly.
4. Observe **LED behavior**:
   - **"00000"** → All LEDs OFF
   - **"11111"** → All LEDs ON
   - **"10110"** → Only thumb & middle fingers ON

---
