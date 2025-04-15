import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation, FFMpegWriter
import os

def create_gaze_video(gaze_csv_path, screenshot_path, output_video_path):
    df = pd.read_csv(gaze_csv_path)

    img = mpimg.imread(screenshot_path)
    img_height, img_width = img.shape[:2]

    # Convert normalized gaze to pixel
    df['x_pix'] = df['x'] * img_width
    df['y_pix'] = df['y'] * img_height

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(img)
    scatter = ax.scatter([], [], c='red', s=50, alpha=0.6)

    def update(frame):
        data = df.iloc[:frame+1]  # Show till current frame
        scatter.set_offsets(data[['x_pix', 'y_pix']])
        ax.set_title(f"Gaze Replay - Timestamp: {data.iloc[-1]['time_readable']}")
        return scatter,

    anim = FuncAnimation(fig, update, frames=len(df), interval=100, blit=True)

    writer = FFMpegWriter(fps=10)
    anim.save(output_video_path, writer=writer)
    plt.close()

    print("Video saved at:", output_video_path)


create_gaze_video(
    gaze_csv_path="output/gaze_data_20250415_123855.csv",
    screenshot_path="output/20250415_123855_screenshot.png",
    output_video_path="output/gaze_animation_20250415_1503.mp4"
)
