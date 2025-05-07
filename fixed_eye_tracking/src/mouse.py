from pynput import mouse, keyboard
import csv
from datetime import datetime

# File to store the mouse log
csv_file = "mouse/mouse_log_" + datetime.now().strftime("%Y%m%d %H%M%S") + ".csv"

# Create and write headers to the CSV file
with open(csv_file, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "X Coordinate", "Y Coordinate"])

# Flag to stop the listener
stop_logging = False

def on_move(x, y):
    global stop_logging
    if stop_logging:
        return False  # Stop the listener
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp}, Mouse moved to ({x}, {y})")
    with open(csv_file, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, x, y])

def on_press(key):
    global stop_logging
    if key == keyboard.Key.esc:
        print("Logging stopped.")
        stop_logging = True
        return False  # Stop the keyboard listener

# Start mouse and keyboard listeners
with mouse.Listener(on_move=on_move) as mouse_listener, \
        keyboard.Listener(on_press=on_press) as keyboard_listener:
    mouse_listener.join()
    keyboard_listener.join()
