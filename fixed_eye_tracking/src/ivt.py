# import os
# import pandas as pd
# import numpy as np
# from datetime import datetime

# def compute_centroid(points):
#     if not points:
#         return None
#     points_array = np.array(points)
#     return tuple(points_array.mean(axis=0))

# def to_human(ts):
#     return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

# def process_gaze_data(gaze_csv_path, timestamp):
#     df = pd.read_csv(gaze_csv_path)

#     # Calculate differences
#     df['dx'] = df['x'].diff()
#     df['dy'] = df['y'].diff()
#     df['dt'] = df['timestamp'].diff()

#     # Compute velocity
#     df['velocity'] = np.sqrt(df['dx']**2 + df['dy']**2) / df['dt']
#     df['velocity'].fillna(0, inplace=True)

#     # Threshold for fixation
#     velocity_threshold = 0.15
#     df['fixation'] = df['velocity'] < velocity_threshold

#     fixations = []
#     fixation_points = []
#     start_time = None
#     end_time = None

#     for _, row in df.iterrows():
#         if row['fixation']:
#             if start_time is None:
#                 start_time = row['timestamp']
#             fixation_points.append((row['x'], row['y']))
#             end_time = row['timestamp']
#         else:
#             if fixation_points:
#                 centroid = compute_centroid(fixation_points)
#                 fixations.append({
#                     'start_timestamp': start_time,
#                     'end_timestamp': end_time,
#                     'start_time_readable': to_human(start_time),
#                     'end_time_readable': to_human(end_time),
#                     'x': centroid[0],
#                     'y': centroid[1]
#                 })
#                 fixation_points = []
#                 start_time = None

#     if fixation_points:
#         centroid = compute_centroid(fixation_points)
#         fixations.append({
#             'start_timestamp': start_time,
#             'end_timestamp': end_time,
#             'start_time_readable': to_human(start_time),
#             'end_time_readable': to_human(end_time),
#             'x': centroid[0],
#             'y': centroid[1]
#         })

#     output_dir = os.path.join(os.getcwd(), "output")
#     os.makedirs(output_dir, exist_ok=True)
#     fixation_csv_path = os.path.join(output_dir, f"fixation_centroids_{timestamp}.csv")

#     fixation_df = pd.DataFrame(fixations)
#     fixation_df.to_csv(fixation_csv_path, index=False)

#     print("Fixation centroids saved to:", fixation_csv_path)
#     return fixation_csv_path


# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) < 3:
#         print("python ivt.py <gaze_csv_path> <timestamp>")
#     else:
#         process_gaze_data(sys.argv[1], sys.argv[2])


import os
import pandas as pd
import numpy as np
from datetime import datetime

def to_human(ts):
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def compute_centroid(points):
    """
    Compute the (x, y, z) centroid of a list of points.
    """
    arr = np.array(points)
    return tuple(arr.mean(axis=0))

def process_gaze_data(gaze_csv_path, timestamp, output_base="output"):
    """
    Reads raw gaze CSV, applies I-VT to detect fixations, and
    writes out fixation centroids (with timestamps & z) into
    output/fixation_centroids/fixation_centroids_<timestamp>.csv
    """
    # 1) Load gaze data
    df = pd.read_csv(gaze_csv_path)

    # 2) Compute velocity (normalized units/sec)
    df['dx'] = df['x'].diff()
    df['dy'] = df['y'].diff()
    df['dt'] = df['timestamp'].diff()
    df['velocity'] = np.sqrt(df['dx']**2 + df['dy']**2) / df['dt']
    df['velocity'].fillna(0, inplace=True)

    # 3) Label fixations by velocity threshold
    velocity_threshold = 0.15
    df['fixation'] = df['velocity'] < velocity_threshold

    # 4) Group consecutive fixations & compute centroids
    fixations = []
    buffer_pts = []
    start_ts = end_ts = None

    for _, row in df.iterrows():
        if row['fixation']:
            if start_ts is None:
                start_ts = row['timestamp']
            buffer_pts.append((row['x'], row['y'], row.get('z', np.nan)))
            end_ts = row['timestamp']
        else:
            if buffer_pts:
                cx, cy, cz = compute_centroid(buffer_pts)
                fixations.append({
                    'start_timestamp': start_ts,
                    'end_timestamp':   end_ts,
                    'start_time_readable': to_human(start_ts),
                    'end_time_readable':   to_human(end_ts),
                    'x': cx, 'y': cy, 'z': cz
                })
                buffer_pts = []
                start_ts = None

    # handle final group
    if buffer_pts:
        cx, cy, cz = compute_centroid(buffer_pts)
        fixations.append({
            'start_timestamp': start_ts,
            'end_timestamp':   end_ts,
            'start_time_readable': to_human(start_ts),
            'end_time_readable':   to_human(end_ts),
            'x': cx, 'y': cy, 'z': cz
        })

    # 5) Save to output/fixation_centroids/
    fc_dir = os.path.join(output_base, "fixation_centroids")
    os.makedirs(fc_dir, exist_ok=True)
    out_csv = os.path.join(fc_dir, f"fixation_centroids_{timestamp}.csv")
    pd.DataFrame(fixations).to_csv(out_csv, index=False)

    print("Fixation centroids saved to:", out_csv)
    return out_csv

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python ivt.py <gaze_csv_path> <timestamp>")
    else:
        process_gaze_data(sys.argv[1], sys.argv[2])
