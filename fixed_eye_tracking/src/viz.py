import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd

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
    screenshot_path = os.path.join(os.getcwd(), "output", "screenshot.png")
    if not os.path.exists(screenshot_path):
        import pyautogui
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
