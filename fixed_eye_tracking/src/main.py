# from collect_data import collect_gaze_data
# from ivt import process_gaze_data
# from viz import improved_capture_and_visualize
# import pyautogui
# import os
# from datetime import datetime
# import time


# def main():
#     output_dir = os.path.join(os.getcwd(), "output")
#     os.makedirs(output_dir, exist_ok=True)

#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

#     # Take Screenshot First
#     screenshot_path = os.path.join(output_dir, f"{timestamp}_screenshot.png")
#     print(f"\n Please open the screen to capture...")
#     print(f" Taking screenshot in 5 seconds...")
#     time.sleep(5)
#     screenshot = pyautogui.screenshot()
#     screenshot.save(screenshot_path)
#     print(" Screenshot saved at:", screenshot_path)

#     # Collect Gaze Data
#     gaze_csv_path = collect_gaze_data(timestamp)

#     # Run IVT
#     fixation_csv_path = process_gaze_data(gaze_csv_path, timestamp)

#     # Visualization
#     improved_capture_and_visualize(
#         gaze_csv_path=gaze_csv_path,
#         fixation_csv_path=fixation_csv_path,
#         screenshot_name=f"{timestamp}_screenshot.png",
#         output_dir=output_dir,
#         delay=0  
#     )


# if __name__ == "__main__":
#     main()


import os
import time
import pyautogui
from datetime import datetime
from collect_data import collect_gaze_data
from ivt import process_gaze_data
from viz import improved_capture_and_visualize

def main():
    # Base output folder
    base_out = os.path.join(os.getcwd(), "output")
    # Sub‐folders
    screenshots_dir     = os.path.join(base_out, "screenshots")
    fixations_dir       = os.path.join(base_out, "fixation_centroids")
    visualization_dir   = os.path.join(base_out, "visualization")
    # Ensure they exist
    for d in (screenshots_dir, fixations_dir, visualization_dir):
        os.makedirs(d, exist_ok=True)

    # 0) Ask user for dominant eye
    dominant_eye = ""
    while dominant_eye not in ("left", "right", "both"):
        dominant_eye = input("Choose your dominant eye ('left', 'right', or 'both'): ").strip().lower()

    # 1) Take screenshot into screenshots/
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shot_name = f"{timestamp}_screenshot.png"
    shot_path = os.path.join(screenshots_dir, shot_name)
    print("\n  Please switch to the screen to capture...")
    print("Taking screenshot in 5 seconds...")
    time.sleep(5)
    pyautogui.screenshot().save(shot_path)
    print("Screenshot saved at:", shot_path)

    # 2) Collect gaze data → saves to data/gaze_data_<timestamp>.csv
    gaze_csv = collect_gaze_data(dominant_eye, timestamp)

    # 3) Process IVT → saves to output/fixation_centroids/fixation_centroids_<timestamp>.csv
    fixation_csv = process_gaze_data(gaze_csv, timestamp)

    # 4) Visualization → reads screenshot from screenshots/, writes to visualization/
    improved_capture_and_visualize(
        gaze_csv_path=gaze_csv,
        fixation_csv_path=fixation_csv,
        screenshot_path=shot_path,
        output_base=base_out
    )

if __name__ == "__main__":
    main()
