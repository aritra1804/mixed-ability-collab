import os
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
from datetime import datetime
import pyautogui


def improved_capture_and_visualize(gaze_csv_path, fixation_csv_path, screenshot_name="screenshot.png", output_dir="output", delay=5):
    """
    Visualizes gaze & fixation data over a screenshot.
    - Waits for `delay` seconds so user can switch to browser tab.
    - Captures screenshot.
    - Saves everything with timestamp.
    """

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Delay before screenshot
    print(f"\n Please switch to the screen you want to capture.")
    print(f" Taking screenshot in {delay} seconds...")
    time.sleep(delay)

    screenshot_path = os.path.join(output_dir, f"{timestamp}_{screenshot_name}")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    print(" Screenshot captured:", screenshot_path)

    # Load data
    gaze_df = pd.read_csv(gaze_csv_path)
    fixation_df = pd.read_csv(fixation_csv_path)

    # Save timestamped copies
    gaze_out = os.path.join(output_dir, f"gaze_data_{timestamp}.csv")
    fixation_out = os.path.join(output_dir, f"fixation_centroids_{timestamp}.csv")
    gaze_df.to_csv(gaze_out, index=False)
    fixation_df.to_csv(fixation_out, index=False)

    img = mpimg.imread(screenshot_path)
    img_height, img_width = img.shape[:2]

    # Convert normalized to pixel
    gaze_df['x_pix'] = gaze_df['x'] * img_width
    gaze_df['y_pix'] = gaze_df['y'] * img_height
    fixation_df['x_pix'] = fixation_df['x'] * img_width
    fixation_df['y_pix'] = fixation_df['y'] * img_height

    # Plot overlay
    plt.figure(figsize=(12, 8))
    plt.imshow(img)
    plt.scatter(gaze_df['x_pix'], gaze_df['y_pix'], c='red', s=10, alpha=0.4, label='Gaze Points')
    plt.scatter(fixation_df['x_pix'], fixation_df['y_pix'], c='blue', marker='x', s=80, label='Fixation Centroids', edgecolors='white')

    plt.legend()
    plt.axis('off')
    plt.title("Gaze and Fixation Overlay")

    vis_path = os.path.join(output_dir, f"visualization_{timestamp}.png")
    plt.savefig(vis_path, bbox_inches='tight')
    plt.close()

    print("📊 Visualization saved to:", vis_path)

    return {
        "screenshot_path": screenshot_path,
        "gaze_csv": gaze_out,
        "fixation_csv": fixation_out,
        "visualization_path": vis_path
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python viz.py <gaze_csv_path> <fixation_csv_path>")
    else:
        improved_capture_and_visualize(sys.argv[1], sys.argv[2])
