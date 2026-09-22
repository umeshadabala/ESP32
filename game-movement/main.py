import serial
import keyboard
import time

# macOS serial port
PORT = "/dev/tty.usbserial-0001"
BAUD_RATE = 115200

KEY_MAP = {
    "UP": "up",
    "DOWN": "down",
    "LEFT": "left",
    "RIGHT": "right",
    "NONE": None
}


def main():
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Give Arduino time to reset

        print("Connected!")
        print("Start tilting your sensor.")
        print("Press Ctrl+C to stop.")

        current_key = None

        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

            if not line:
                continue

            print("Received:", line)

            # Ignore anything that isn't a valid command
            if line not in KEY_MAP:
                continue

            new_key = KEY_MAP[line]

            # If the key changed, release the previous key
            if current_key is not None and current_key != new_key:
                keyboard.release(current_key)
                current_key = None

            # Press the new key if needed
            if new_key is not None:
                if current_key != new_key:
                    keyboard.press(new_key)
                    current_key = new_key

            # No movement command
            else:
                if current_key is not None:
                    keyboard.release(current_key)
                    current_key = None

            time.sleep(0.05)

    except serial.SerialException as e:
        print("Serial connection error:")
        print(e)

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        # Make sure any held key is released
        if 'current_key' in locals() and current_key is not None:
            keyboard.release(current_key)

        if 'ser' in locals() and ser.is_open:
            ser.close()

        print("Serial connection closed.")


if __name__ == "__main__":
    main()
