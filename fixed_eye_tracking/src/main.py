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
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    # 0) Ask user for dominant eye
    dominant_eye = ""
    while dominant_eye not in ('left', 'right', 'both'):
        dominant_eye = input("Choose your dominant eye ('left', 'right'): ").strip().lower()

    # 1) Take Screenshot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shot_name = f"{timestamp}_screenshot.png"
    print("\n Please switch to the screen to capture...")
    print(" Taking screenshot in 5 seconds...")
    time.sleep(5)
    shot = pyautogui.screenshot()
    shot.save(os.path.join(output_dir, shot_name))
    print("Screenshot saved at:", os.path.join(output_dir, shot_name))

    # 2) Collect Gaze Data (using chosen eye)
    gaze_csv = collect_gaze_data(dominant_eye, timestamp)

    # 3) IVT & Fixations
    fixation_csv = process_gaze_data(gaze_csv, timestamp)

    # 4) Visualization (no extra delay)
    improved_capture_and_visualize(
        gaze_csv_path=gaze_csv,
        fixation_csv_path=fixation_csv,
        screenshot_name=shot_name,
        output_dir=output_dir,
        delay=0
    )

if __name__ == "__main__":
    main()