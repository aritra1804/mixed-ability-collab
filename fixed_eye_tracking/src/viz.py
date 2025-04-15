import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import pyautogui


def normalized_to_pixels(normalized_point, width, height):
    """
    Converts a normalized point (values between 0 and 1) to pixel coordinates based on width and height.
    """
    x, y = normalized_point
    return (x * width, y * height)

def batch_normalized_to_pixels(normalized_points, width, height):
    return [normalized_to_pixels(point, width, height) for point in normalized_points]

def capture_and_visualize(gaze_csv_path, fixation_csv_path):
    """
    Loads raw gaze data and fixation centroids, loads a screenshot image, converts normalized coordinates to pixel coordinates,
    overlays gaze data and fixation centroids on the image, and saves the visualization as an image file.
    """
    # Load raw gaze data
    gaze_df = pd.read_csv(gaze_csv_path)
    gaze_points = list(zip(gaze_df['x'], gaze_df['y']))

    # Load fixation centroids
    fixation_df = pd.read_csv(fixation_csv_path)
    fixation_points = list(zip(fixation_df['x'], fixation_df['y']))

    # Attempt to load an existing screenshot from output folder; otherwise, capture one using pyautogui.
    screenshot_path = os.path.join(os.getcwd(), "output", "screenshot2.png")
    if not os.path.exists(screenshot_path):
        os.makedirs(os.path.join(os.getcwd(), "output"), exist_ok=True)
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
    
    # Load screenshot image
    img = mpimg.imread(screenshot_path)
    img_height, img_width = img.shape[0], img.shape[1]

    # Convert normalized points to pixel coordinates
    gaze_pixels = batch_normalized_to_pixels(gaze_points, img_width, img_height)
    fixation_pixels = batch_normalized_to_pixels(fixation_points, img_width, img_height)

    # Plot the screenshot with overlays
    plt.figure(figsize=(12, 8))
    plt.imshow(img)
    if gaze_pixels:
        x_gaze, y_gaze = zip(*gaze_pixels)
        plt.scatter(x_gaze, y_gaze, s=10, c='red', alpha=0.5, label="Gaze Points")
    if fixation_pixels:
        x_fix, y_fix = zip(*fixation_pixels)
        plt.scatter(x_fix, y_fix, s=100, marker='x', c='blue', label="Fixation Centroids")
    plt.title("Gaze Data and Fixation Centroids Overlay")
    plt.legend()
    plt.axis("off")
    
    # Save the visualization as an image file
    visualization_path = os.path.join(os.getcwd(), "output", "visualization.png")
    plt.savefig(visualization_path, bbox_inches="tight")
    plt.close()
    print("Visualization saved to", visualization_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python viz.py <gaze_csv_path> <fixation_csv_path>")
    else:
        capture_and_visualize(sys.argv[1], sys.argv[2])


def improved_capture_and_visualize(gaze_csv_path, fixation_csv_path, screenshot_name="screenshot.png", output_dir="output"):
    """
    Improved visualization function:
    1. Captures live screenshot using pyautogui
    2. Saves screenshot, gaze CSV, fixation CSV with timestamp
    3. Plots gaze points & fixation centroids over screenshot
    """

    # Create output directory if doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Take live screenshot
    screenshot_path = os.path.join(output_dir, f"{timestamp}_{screenshot_name}")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)

    # Load gaze and fixation data
    gaze_df = pd.read_csv(gaze_csv_path)
    fixation_df = pd.read_csv(fixation_csv_path)

    # Save copies with timestamp for both CSVs
    gaze_out_path = os.path.join(output_dir, f"gaze_data_{timestamp}.csv")
    fixation_out_path = os.path.join(output_dir, f"fixation_centroids_{timestamp}.csv")
    gaze_df.to_csv(gaze_out_path, index=False)
    fixation_df.to_csv(fixation_out_path, index=False)

    # Load Screenshot Image
    img = mpimg.imread(screenshot_path)
    img_height, img_width = img.shape[:2]

    # Convert normalized (0-1) coordinates to pixel coordinates
    gaze_df['x_pix'] = gaze_df['x'] * img_width
    gaze_df['y_pix'] = gaze_df['y'] * img_height
    fixation_df['x_pix'] = fixation_df['x'] * img_width
    fixation_df['y_pix'] = fixation_df['y'] * img_height

    # Plot Overlay
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

    print("Visualization Saved at:", vis_path)

    return {
        "screenshot_path": screenshot_path,
        "gaze_csv": gaze_out_path,
        "fixation_csv": fixation_out_path,
        "visualization_path": vis_path
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python viz.py <gaze_csv_path> <fixation_csv_path>")
    else:
        improved_capture_and_visualize(sys.argv[1], sys.argv[2])