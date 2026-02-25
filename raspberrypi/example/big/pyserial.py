import serial
import time

SERIAL_PORT_NAME = "COM7"  # Change this to your serial port name
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for the connection to initialize
    print(f"Connected to {SERIAL_PORT_NAME} at {BAUD_RATE} baud.")

    SWEEPING_DELAY = 0.01

    while True:
        for angle in range(0, 181):  # Example: Send angles from 0 to 180 degrees
            data = f"{angle}\n"  # Add newline for Arduino to recognize end of message
            ser.write(data.encode('utf-8'))  # Send data to the serial port
            ser.flush()  # Ensure data is sent immediately
            print(f"Sent data: '{data.strip()}'")

            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print(f"Received from Arduino: '{line}'")

            time.sleep(SWEEPING_DELAY)  # Wait before sending the next command

except serial.SerialException as e:
    print(f"Serial error: {e}")

except KeyboardInterrupt:
    print("Exiting program.")
finally:
    if ser and ser.is_open:
        ser.close()
        print(f"Closed serial connection to {SERIAL_PORT_NAME}.")            