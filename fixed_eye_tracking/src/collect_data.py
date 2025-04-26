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



# import os
# import time
# import csv
# from datetime import datetime
# import tobii_research as tr

# def to_human(ts):
#     return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

# def collect_gaze_data(timestamp):
#     """
#     Collect gaze data until CTRL+C, then save to
#     data/gaze_data_<timestamp>.csv
#     """
#     gaze_data_list = []

#     def gaze_data_callback(gaze_data):
#         left = gaze_data.get('left_gaze_point_on_display_area')
#         right = gaze_data.get('right_gaze_point_on_display_area')
#         left_3d = gaze_data.get('left_gaze_point_in_user_coordinate_system')
#         right_3d = gaze_data.get('right_gaze_point_in_user_coordinate_system')

#         # extract z
#         left_z  = left_3d[2] if left_3d else None
#         right_z = right_3d[2] if right_3d else None

#         avg_x = avg_y = avg_z = None
#         source = None

#         if left and right:
#             avg_x = (left[0] + right[0]) / 2
#             avg_y = (left[1] + right[1]) / 2
#             if left_z is not None and right_z is not None:
#                 avg_z = (left_z + right_z) / 2
#             else:
#                 avg_z = left_z or right_z
#             source = 'both'
#         elif left:
#             avg_x, avg_y = left
#             avg_z = left_z
#             source = 'left'
#         elif right:
#             avg_x, avg_y = right
#             avg_z = right_z
#             source = 'right'
#         else:
#             return  # no data

#         ts = time.time()
#         gaze_data_list.append((ts, to_human(ts), avg_x, avg_y, avg_z, source))
#         print(f"Gaze recorded: {ts:.3f}, x={avg_x:.3f}, y={avg_y:.3f}, z={avg_z:.3f}, src={source}")

#     # connect and subscribe
#     eyetrackers = tr.find_all_eyetrackers()
#     if not eyetrackers:
#         raise RuntimeError("No eye tracker found.")
#     et = eyetrackers[0]
#     print("Connected to:", et)
#     et.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
#     print("Collecting gaze data... Press CTRL+C to stop")

#     try:
#         while True:
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("\nStopped by user")
#     finally:
#         et.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

#     # write CSV
#     data_dir = os.path.join(os.getcwd(), "data")
#     os.makedirs(data_dir, exist_ok=True)
#     out_file = os.path.join(data_dir, f"gaze_data_{timestamp}.csv")
#     with open(out_file, 'w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow(['timestamp','time_readable','x','y','z','eye_source'])
#         writer.writerows(gaze_data_list)

#     print("Saved gaze data to:", out_file)
#     return out_file

# if __name__ == "__main__":
#     ts = datetime.now().strftime("%Y%m%d_%H%M%S")
#     collect_gaze_data(ts)


import os
import time
import csv
from datetime import datetime
import tobii_research as tr

def to_human(ts):
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def collect_gaze_data(dominant_eye, timestamp):
    """
    Collects until CTRL+C, using only the user-chosen eye or both.
    Saves to data/gaze_data_<timestamp>.csv
    """
    gaze_data_list = []

    def gaze_data_callback(gaze_data):
        # 2D normalized display points
        left_2d  = gaze_data.get('left_gaze_point_on_display_area')
        right_2d = gaze_data.get('right_gaze_point_on_display_area')
        # 3D intersection points (for z)
        left_3d  = gaze_data.get('left_gaze_point_in_user_coordinate_system')
        right_3d = gaze_data.get('right_gaze_point_in_user_coordinate_system')

        # extract z
        left_z  = left_3d[2]  if left_3d  else None
        right_z = right_3d[2] if right_3d else None

        avg_x = avg_y = avg_z = None
        source = None

        if dominant_eye == 'left':
            if not left_2d: return
            avg_x, avg_y = left_2d
            avg_z = left_z
            source = 'left'
        elif dominant_eye == 'right':
            if not right_2d: return
            avg_x, avg_y = right_2d
            avg_z = right_z
            source = 'right'
        else:  # both
            if left_2d and right_2d:
                avg_x = (left_2d[0] + right_2d[0]) / 2
                avg_y = (left_2d[1] + right_2d[1]) / 2
                if left_z is not None and right_z is not None:
                    avg_z = (left_z + right_z) / 2
                else:
                    avg_z = left_z or right_z
                source = 'both'
            else:
                # fallback: if one eye only, use that
                if left_2d:
                    avg_x, avg_y = left_2d; avg_z = left_z; source = 'left'
                elif right_2d:
                    avg_x, avg_y = right_2d; avg_z = right_z; source = 'right'
                else:
                    return

        ts = time.time()
        gaze_data_list.append((ts, to_human(ts), avg_x, avg_y, avg_z, source))
        print(f"Gaze recorded: {ts:.3f}, x={avg_x:.3f}, y={avg_y:.3f}, z={avg_z:.3f}, src={source}")

    # connect & subscribe
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
    finally:
        et.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

    # save CSV
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    out_csv = os.path.join(data_dir, f"gaze_data_{timestamp}.csv")
    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp','time_readable','x','y','z','eye_source'])
        writer.writerows(gaze_data_list)

    print("Gaze data saved to:", out_csv)
    return out_csv


if __name__ == "__main__":
    # fallback for standalone run
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    collect_gaze_data('both', ts)