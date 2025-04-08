from collect_data import collect_gaze_data
from ivt import process_gaze_data
from viz import capture_and_visualize

def main():
    # Stage 1: Collect gaze data until Ctrl+C is pressed
    gaze_csv_path = collect_gaze_data()

    # Stage 2: Process the raw gaze data to compute fixation centroids using IVT
    fixation_csv_path = process_gaze_data(gaze_csv_path)

    # Stage 3: Capture a screenshot and visualize the gaze data with fixation centroids
    capture_and_visualize(gaze_csv_path, fixation_csv_path)

if __name__ == "__main__":
    main()
