import os
import time
import csv
from datetime import datetime
import tobii_research as tr


def collect_gaze_data():
    """
    Collect gaze data until user manually stops (Ctrl+C).
    Saves data to CSV with both raw timestamp and human-readable time.
    """
    gaze_data_list = []

    def to_human(ts):
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

    def gaze_data_callback(gaze_data):
        left_eye = gaze_data.get('left_gaze_point_on_display_area')
        right_eye = gaze_data.get('right_gaze_point_on_display_area')
        if left_eye and right_eye:
            avg_x = (left_eye[0] + right_eye[0]) / 2
            avg_y = (left_eye[1] + right_eye[1]) / 2
            timestamp = time.time()
            readable_time = to_human(timestamp)
            gaze_data_list.append((timestamp, readable_time, avg_x, avg_y))
            print("Gaze recorded:", (timestamp, avg_x, avg_y))

    # Connect to Eye Tracker
    eyetrackers = tr.find_all_eyetrackers()
    if not eyetrackers:
        raise Exception("No eye tracker found.")
    my_eyetracker = eyetrackers[0]
    print("Connected to:", my_eyetracker)

    # Subscribe
    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

    print("Collecting gaze data... Press CTRL+C to stop.")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nData collection stopped by user.")

    # Unsubscribe
    my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

    # Save to CSV
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gaze_csv_path = os.path.join(data_dir, f"gaze_data_{timestamp}.csv")

    with open(gaze_csv_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["timestamp", "time_readable", "x", "y"])
        writer.writerows(gaze_data_list)

    print("Gaze data saved to:", gaze_csv_path)
    return gaze_csv_path


if __name__ == "__main__":
    collect_gaze_data()
