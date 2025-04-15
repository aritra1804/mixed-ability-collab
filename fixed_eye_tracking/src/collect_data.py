import os
import time
import csv
from datetime import datetime
import tobii_research as tr


def collect_gaze_data(duration=10):
    """
    Connects to the Tobii eye tracker and collects gaze data for a fixed duration (in seconds).
    Saves the data as CSV (timestamp, readable time, x, y) and returns the file path.
    """
    gaze_data_list = []

    def to_human(ts):
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

    def gaze_data_callback(gaze_data):
        left_eye = gaze_data.get('left_gaze_point_on_display_area')
        right_eye = gaze_data.get('right_gaze_point_on_display_area')
        if left_eye and right_eye:
            # Average the left and right eye coordinates
            avg_x = (left_eye[0] + right_eye[0]) / 2
            avg_y = (left_eye[1] + right_eye[1]) / 2
            timestamp = time.time()
            readable_time = to_human(timestamp)
            gaze_data_list.append((timestamp, readable_time, avg_x, avg_y))
            print("Gaze point recorded:", (timestamp, avg_x, avg_y))

    # Connect to the eye tracker
    eyetrackers = tr.find_all_eyetrackers()
    if not eyetrackers:
        raise Exception("No eye tracker found.")
    my_eyetracker = eyetrackers[0]
    print("Connected to:", my_eyetracker)

    # Subscribe to gaze data stream
    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

    print(f"Collecting gaze data for {duration} seconds...")
    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(0.1)

    # Stop listening
    my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

    # Save to CSV
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    gaze_csv_path = os.path.join(data_dir, "gaze_data.csv")
    with open(gaze_csv_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["timestamp", "time_readable", "x", "y"])
        writer.writerows(gaze_data_list)

    print("Gaze data saved to:", gaze_csv_path)
    return gaze_csv_path


if __name__ == "__main__":
    collect_gaze_data()
