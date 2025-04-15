import os
import pandas as pd
import numpy as np
from datetime import datetime


def compute_centroid(points):
    """
    Computes the centroid (average point) of a list of (x, y) points.
    """
    if not points:
        return None
    points_array = np.array(points)
    return tuple(points_array.mean(axis=0))


def to_human(ts):
    """
    Convert timestamp to human-readable format.
    """
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')


def process_gaze_data(gaze_csv_path):
    """
    Reads raw gaze data CSV, computes velocities, detects fixations, computes centroids,
    and adds both raw & human-readable start/end timestamps for each fixation.
    """
    df = pd.read_csv(gaze_csv_path)

    # Calculate differences between consecutive points
    df['dx'] = df['x'].diff()
    df['dy'] = df['y'].diff()
    df['dt'] = df['timestamp'].diff()

    # Compute velocity
    df['velocity'] = np.sqrt(df['dx']**2 + df['dy']**2) / df['dt']
    df['velocity'].fillna(0, inplace=True)

    # Threshold for fixations
    velocity_threshold = 0.15
    df['fixation'] = df['velocity'] < velocity_threshold

    fixations = []
    fixation_points = []
    start_time = None
    end_time = None

    for _, row in df.iterrows():
        if row['fixation']:
            if start_time is None:
                start_time = row['timestamp']
            fixation_points.append((row['x'], row['y']))
            end_time = row['timestamp']
        else:
            if fixation_points:
                centroid = compute_centroid(fixation_points)
                fixations.append({
                    'start_timestamp': start_time,
                    'end_timestamp': end_time,
                    'start_time_readable': to_human(start_time),
                    'end_time_readable': to_human(end_time),
                    'x': centroid[0],
                    'y': centroid[1]
                })
                fixation_points = []
                start_time = None

    if fixation_points:
        centroid = compute_centroid(fixation_points)
        fixations.append({
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'start_time_readable': to_human(start_time),
            'end_time_readable': to_human(end_time),
            'x': centroid[0],
            'y': centroid[1]
        })

    # Save to output
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    fixation_csv_path = os.path.join(output_dir, "fixation_centroids.csv")
    fixation_df = pd.DataFrame(fixations)
    fixation_df.to_csv(fixation_csv_path, index=False)

    print("Fixation centroids saved to:", fixation_csv_path)
    return fixation_csv_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ivt.py <gaze_csv_path>")
    else:
        process_gaze_data(sys.argv[1])
