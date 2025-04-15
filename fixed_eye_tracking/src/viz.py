import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd


def improved_capture_and_visualize(gaze_csv_path, fixation_csv_path, screenshot_name="screenshot.png", output_dir="output", delay=0):
    """
    Visualizes gaze & fixation data over a screenshot.
    Uses pre-captured screenshot from main.py.
    Saves everything with the same timestamp.
    """

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Derive timestamp from screenshot name (assumes format: 20250415_1450_screenshot.png)
    timestamp = screenshot_name.split("_screenshot")[0]

    # Full path to existing screenshot
    screenshot_path = os.path.join(output_dir, screenshot_name)

    if not os.path.exists(screenshot_path):
        raise FileNotFoundError(f"Screenshot not found at: {screenshot_path}")

    print(f"\n Using screenshot: {screenshot_path}")

    # Load gaze and fixation data
    gaze_df = pd.read_csv(gaze_csv_path)
    fixation_df = pd.read_csv(fixation_csv_path)

    # Save timestamped copies of input data
    gaze_out = os.path.join(output_dir, f"gaze_data_{timestamp}.csv")
    fixation_out = os.path.join(output_dir, f"fixation_centroids_{timestamp}.csv")
    gaze_df.to_csv(gaze_out, index=False)
    fixation_df.to_csv(fixation_out, index=False)

    # Load screenshot image
    img = mpimg.imread(screenshot_path)
    img_height, img_width = img.shape[:2]

    # Convert normalized coords to pixel coords
    gaze_df['x_pix'] = gaze_df['x'] * img_width
    gaze_df['y_pix'] = gaze_df['y'] * img_height
    fixation_df['x_pix'] = fixation_df['x'] * img_width
    fixation_df['y_pix'] = fixation_df['y'] * img_height

    # Plot
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

    print("Visualization saved to:", vis_path)

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
