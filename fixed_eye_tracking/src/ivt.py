import os
import pandas as pd
import numpy as np

def compute_centroid(points):
    """
    Computes the centroid (average point) of a list of (x, y) points.
    """
    if not points:
        return None
    points_array = np.array(points)
    return tuple(points_array.mean(axis=0))

def process_gaze_data(gaze_csv_path):
    """
    Reads the raw gaze data CSV, computes velocities between consecutive points,
    applies a velocity threshold to label fixations, groups consecutive fixation points,
    computes the centroid for each group, and saves them into a CSV.
    Returns the path to the fixation centroids CSV file.
    """
    df = pd.read_csv(gaze_csv_path)

    # Calculate differences between consecutive points
    df['dx'] = df['x'].diff()
    df['dy'] = df['y'].diff()
    df['dt'] = df['timestamp'].diff()

    # Compute velocity: Euclidean distance divided by the time difference
    df['velocity'] = np.sqrt(df['dx']**2 + df['dy']**2) / df['dt']
    df['velocity'].fillna(0, inplace=True)

    # Apply a velocity threshold to identify fixations (tune as necessary)
    velocity_threshold = 0.15
    df['fixation'] = df['velocity'] < velocity_threshold

    fixations = []
    fixation_points = []
    for _, row in df.iterrows():
        if row['fixation']:
            fixation_points.append((row['x'], row['y']))
        else:
            if fixation_points:
                centroid = compute_centroid(fixation_points)
                fixations.append(centroid)
                fixation_points = []
    # Check if the last points form a fixation group
    if fixation_points:
        centroid = compute_centroid(fixation_points)
        fixations.append(centroid)

    # Save the computed fixation centroids to CSV
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    fixation_csv_path = os.path.join(output_dir, "fixation_centroids.csv")
    fixation_df = pd.DataFrame(fixations, columns=["x", "y"])
    fixation_df.to_csv(fixation_csv_path, index=False)
    print("Fixation centroids saved to", fixation_csv_path)
    return fixation_csv_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ivt.py <gaze_csv_path>")
    else:
        process_gaze_data(sys.argv[1])
