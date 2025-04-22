# import os
# import time
# import csv
# from datetime import datetime
# import tobii_research as tr


# def collect_gaze_data(timestamp):
#     """
#     Collect gaze data until user manually stops (Ctrl+C).
#     Saves to CSV with both raw timestamp and human-readable time.
#     """
#     gaze_data_list = []

#     def to_human(ts):
#         return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

#     def gaze_data_callback(gaze_data):
#         left_eye = gaze_data.get('left_gaze_point_on_display_area')
#         right_eye = gaze_data.get('right_gaze_point_on_display_area')
#         if left_eye and right_eye:
#             avg_x = (left_eye[0] + right_eye[0]) / 2
#             avg_y = (left_eye[1] + right_eye[1]) / 2
#             timestamp_now = time.time()
#             readable_time = to_human(timestamp_now)
#             gaze_data_list.append((timestamp_now, readable_time, avg_x, avg_y))
#             print("Gaze recorded:", (timestamp_now, avg_x, avg_y))

#     # Connect to Eye Tracker
#     eyetrackers = tr.find_all_eyetrackers()
#     if not eyetrackers:
#         raise Exception("No eye tracker found.")
#     my_eyetracker = eyetrackers[0]
#     print("Connected to:", my_eyetracker)

#     # Start Collecting
#     my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

#     print("Collecting gaze data... Press CTRL+C to stop")

#     try:
#         while True:
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("\nData collection stopped by user.")

#     my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

#     # Save to CSV
#     data_dir = os.path.join(os.getcwd(), "data")
#     os.makedirs(data_dir, exist_ok=True)
#     gaze_csv_path = os.path.join(data_dir, f"gaze_data_{timestamp}.csv")

#     with open(gaze_csv_path, "w", newline="") as csv_file:
#         writer = csv.writer(csv_file)
#         writer.writerow(["timestamp", "time_readable", "x", "y"])
#         writer.writerows(gaze_data_list)

#     print("Gaze data saved to:", gaze_csv_path)
#     return gaze_csv_path


# if __name__ == "__main__":
#     # fallback if you want to run directly (testing)
#     ts = datetime.now().strftime("%Y%m%d_%H%M%S")
#     collect_gaze_data(ts)


# collect_data.py

import os
import time
import csv
from datetime import datetime
import tobii_research as tr

def to_human(ts):
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def collect_gaze_data():
    """
    Continuously collects gaze data until user presses CTRL+C.
    Records raw timestamp, human-readable time, x, y, z, and eye source.
    Saves to data/gaze_data_<timestamp>.csv and returns the file path.
    """
    gaze_data_list = []

    def gaze_data_callback(gaze_data):
        left = gaze_data.get('left_gaze_point_on_display_area')
        right = gaze_data.get('right_gaze_point_on_display_area')
        left_origin = gaze_data.get('left_gaze_origin_in_user_coordinate_system')
        right_origin = gaze_data.get('right_gaze_origin_in_user_coordinate_system')

        left_z = left_origin[2] if left_origin else None
        right_z = right_origin[2] if right_origin else None

        avg_x = avg_y = avg_z = None
        source = None

        if left and right:
            avg_x = (left[0] + right[0]) / 2
            avg_y = (left[1] + right[1]) / 2
            if left_z is not None and right_z is not None:
                avg_z = (left_z + right_z) / 2
            else:
                avg_z = left_z or right_z
            source = 'both'
        elif left:
            avg_x, avg_y = left
            avg_z = left_z
            source = 'left'
        elif right:
            avg_x, avg_y = right
            avg_z = right_z
            source = 'right'
        else:
            return  # No valid gaze data

        ts = time.time()
        gaze_data_list.append((ts, to_human(ts), avg_x, avg_y, avg_z, source))
        print(f"Gaze recorded: ts={ts:.3f}, x={avg_x:.3f}, y={avg_y:.3f}, z={avg_z:.3f}, source={source}")

    # Connect to Tobii eye tracker
    trackers = tr.find_all_eyetrackers()
    if not trackers:
        raise RuntimeError("No eye tracker found.")
    et = trackers[0]
    print("Connected to:", et)

    et.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    print("Collecting gaze data... Press CTRL+C to stop.")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nData collection stopped by user.")

    et.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

    # Save collected data to CSV
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(data_dir, f"gaze_data_{timestamp_str}.csv")
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'time_readable', 'x', 'y', 'z', 'eye_source'])
        writer.writerows(gaze_data_list)

    print("Gaze data saved to:", out_path)
    return out_path

if __name__ == "__main__":
    collect_gaze_data()
