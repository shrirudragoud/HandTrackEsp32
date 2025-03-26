#include <Arduino.h>

// Pin definitions for LEDs
#define LED_THUMB  5   // GPIO 5  - Thumb
#define LED_INDEX  18  // GPIO 18 - Index finger
#define LED_MIDDLE 19  // GPIO 19 - Middle finger
#define LED_RING   21  // GPIO 21 - Ring finger
#define LED_PINKY  22  // GPIO 22 - Pinky finger

// Array of LED pins for easier iteration
const int LED_PINS[] = {LED_THUMB, LED_INDEX, LED_MIDDLE, LED_RING, LED_PINKY};
const int NUM_LEDS = 5;

// Buffer for incoming serial data
const int BUFFER_SIZE = 32;
char serialBuffer[BUFFER_SIZE];
int bufferIndex = 0;

// Timer for connection monitoring
unsigned long lastMessageTime = 0;
const unsigned long CONNECTION_TIMEOUT = 5000; // 5 seconds
bool connectionTimedOut = false;

// Statistics
unsigned long messagesReceived = 0;
unsigned long errorCount = 0;

void setup() {
  // Initialize serial communication with a higher timeout
  Serial.begin(115200);
  Serial.setTimeout(50);  // 50ms timeout for serial operations
  
  // Configure LED pins as outputs
  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);  // Start with all LEDs off
  }
  
  // Signal ready state with LED sequence
  startupSequence();
  
  // Print initialization message
  Serial.println("ESP32 LED Control Ready");
  printStatus();
}

void loop() {
  // Check for incoming serial data
  while (Serial.available() > 0) {
    char c = Serial.read();
    
    // Process on newline
    if (c == '\n' || c == '\r') {
      if (bufferIndex > 0) {  // Only process non-empty messages
        // Null terminate the string
        serialBuffer[bufferIndex] = '\0';
        
        // Process the complete message
        processMessage(serialBuffer);
        
        // Update last message time
        lastMessageTime = millis();
        connectionTimedOut = false;
        
        // Reset buffer
        bufferIndex = 0;
      }
    }
    // Add character to buffer if there's space
    else if (bufferIndex < BUFFER_SIZE - 1) {
      serialBuffer[bufferIndex++] = c;
    }
    // Buffer overflow protection
    else {
      Serial.println("Error: Buffer overflow");
      bufferIndex = 0;
      errorCount++;
    }
  }
  
  // Check for connection timeout
  if (!connectionTimedOut && millis() - lastMessageTime > CONNECTION_TIMEOUT) {
    Serial.println("Warning: Connection timed out");
    // Turn off all LEDs
    for (int i = 0; i < NUM_LEDS; i++) {
      digitalWrite(LED_PINS[i], LOW);
    }
    connectionTimedOut = true;
    printStatus();
  }
}

void processMessage(const char* message) {
  // Debug output
  Serial.print("Received: ");
  Serial.println(message);
  
  // Verify message length
  if (strlen(message) != 5) {
    Serial.print("Error: Invalid message length (");
    Serial.print(strlen(message));
    Serial.println(" chars)");
    errorCount++;
    return;
  }
  
  // Verify message format (only 0s and 1s)
  for (int i = 0; i < 5; i++) {
    if (message[i] != '0' && message[i] != '1') {
      Serial.print("Error: Invalid character at position ");
      Serial.print(i);
      Serial.print(": '");
      Serial.print(message[i]);
      Serial.println("'");
      errorCount++;
      return;
    }
  }
  
  // Update LED states
  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_PINS[i], message[i] == '1' ? HIGH : LOW);
  }
  
  // Increment message counter
  messagesReceived++;
  
  // Send confirmation with current state
  Serial.print("OK: LEDs updated [");
  for (int i = 0; i < 5; i++) {
    Serial.print(digitalRead(LED_PINS[i]) == HIGH ? "1" : "0");
  }
  Serial.println("]");
  
  // Periodically print status
  if (messagesReceived % 100 == 0) {
    printStatus();
  }
}

void startupSequence() {
  Serial.println("Running startup sequence...");
  
  // Light up LEDs in sequence
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], HIGH);
    delay(100);
    digitalWrite(LED_PINS[i], LOW);
    Serial.print("LED ");
    Serial.print(i + 1);
    Serial.println(" tested");
  }
  
  // Light up all LEDs briefly
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], HIGH);
  }
  delay(200);
  
  // Turn off all LEDs
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], LOW);
  }
  
  Serial.println("Startup sequence complete");
}

void printStatus() {
  Serial.println("\n=== Status ===");
  Serial.print("Messages received: ");
  Serial.println(messagesReceived);
  Serial.print("Errors: ");
  Serial.println(errorCount);
  Serial.print("Connection status: ");
  Serial.println(connectionTimedOut ? "Timed out" : "Active");
  
  Serial.print("LED states: ");
  for (int i = 0; i < NUM_LEDS; i++) {
    Serial.print(digitalRead(LED_PINS[i]) == HIGH ? "1" : "0");
  }
  Serial.println("\n============");
}

void checkLEDs() {
  Serial.println("\nTesting LEDs...");
  bool ledStatus[NUM_LEDS];
  bool hasError = false;
  
  // Check each LED
  for (int i = 0; i < NUM_LEDS; i++) {
    // Turn on LED
    digitalWrite(LED_PINS[i], HIGH);
    delay(10);  // Short delay for stability
    
    // Read pin state
    ledStatus[i] = digitalRead(LED_PINS[i]) == HIGH;
    
    // Turn off LED
    digitalWrite(LED_PINS[i], LOW);
    
    if (!ledStatus[i]) {
      hasError = true;
      Serial.print("Error: LED on pin ");
      Serial.print(LED_PINS[i]);
      Serial.println(" not responding");
    }
  }
  
  if (!hasError) {
    Serial.println("All LEDs functioning properly");
  }
}

void resetCommunication() {
  Serial.flush();  // Clear serial buffer
  bufferIndex = 0;  // Reset buffer index
  errorCount = 0;   // Reset error count
  messagesReceived = 0;  // Reset message counter
  
  // Turn off all LEDs
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], LOW);
  }
  
  Serial.println("Communication reset complete");
  printStatus();
}