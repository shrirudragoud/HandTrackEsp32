import serial.tools.list_ports
import sys

def check_ports():
    """Check available serial ports and their status."""
    print("\nChecking available serial ports...")
    
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("No serial ports found!")
        return
    
    print("\nAvailable ports:")
    print("---------------")
    
    for port in ports:
        print(f"\nPort: {port.device}")
        print(f"Description: {port.description}")
        print(f"Hardware ID: {port.hwid}")
        
        # Try to open the port to check if it's in use
        try:
            ser = serial.Serial(port.device, 115200, timeout=1)
            print("Status: Available")
            ser.close()
        except serial.SerialException as e:
            print(f"Status: In use or unavailable ({str(e)})")
        except Exception as e:
            print(f"Status: Error checking port ({str(e)})")

if __name__ == "__main__":
    try:
        check_ports()
    except Exception as e:
        print(f"Error: {e}")
    
    if sys.platform == 'win32':
        print("\nNote: On Windows, if Arduino IDE is open, it may block access to the COM port.")
        print("Close Arduino IDE's Serial Monitor before running the Python application.")