from collect_data import collect_gaze_data
from ivt import process_gaze_data
from viz import improved_capture_and_visualize
import pyautogui
import os
from datetime import datetime
import time


def main():
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # STEP 1 — Take Screenshot FIRST
    screenshot_path = os.path.join(output_dir, f"{timestamp}_screenshot.png")
    print(f"\n⚠️  Please open the screen to capture...")
    print("📸 Taking screenshot in 5 seconds...")
    time.sleep(5)
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    print("✅ Screenshot saved at:", screenshot_path)

    # STEP 2 — Start Gaze Data Collection
    gaze_csv_path = collect_gaze_data(timestamp)

    # STEP 3 — Run IVT
    fixation_csv_path = process_gaze_data(gaze_csv_path)

    # STEP 4 — Visualization
    improved_capture_and_visualize(
        gaze_csv_path=gaze_csv_path,
        fixation_csv_path=fixation_csv_path,
        screenshot_name=f"{timestamp}_screenshot.png",
        output_dir=output_dir,
        delay=0  # No delay now — screenshot already taken
    )


if __name__ == "__main__":
    main()
