import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
from sklearn.preprocessing import MinMaxScaler
import os

# ======= CONFIGURATION =======
cleaned_csv = "data cleaning/clean_csv/cleaned_nbc.csv"
centroids_csv = "data cleaning/centroid/centroids_nbcshopping.csv"
screenshot_path = "data cleaning/screenshots/nbc.png"
output_folder = "data cleaning/heatmaps"
output_filename = "side_by_side_heatmap_nbc.png"
# =============================

# Create the heatmaps folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load gaze data
gaze_data = pd.read_csv(cleaned_csv)
centroids_data = pd.read_csv(centroids_csv)

# Load screenshot
background_img = mpimg.imread(screenshot_path)
img_height, img_width = background_img.shape[:2]
print(f"Image size: {img_width}x{img_height}")

# Rescale cleaned gaze data
scaler_x = MinMaxScaler(feature_range=(0, img_width))
scaler_y = MinMaxScaler(feature_range=(0, img_height))

gaze_data['gaze_x_scaled'] = scaler_x.fit_transform(gaze_data[['gaze_x_px']])
gaze_data['gaze_y_scaled'] = scaler_y.fit_transform(gaze_data[['gaze_y_px']])

# Rescale centroids data
scaler_cx = MinMaxScaler(feature_range=(0, img_width))
scaler_cy = MinMaxScaler(feature_range=(0, img_height))

centroids_data['x_avg_scaled'] = scaler_cx.fit_transform(centroids_data[['x_avg']])
centroids_data['y_avg_scaled'] = scaler_cy.fit_transform(centroids_data[['y_avg']])

# ========= PLOT SIDE-BY-SIDE =========
fig, axes = plt.subplots(1, 2, figsize=(24, 12))

# --- Cleaned gaze data heatmap ---
axes[0].imshow(background_img, alpha=0.3)
sns.kdeplot(
    x=gaze_data['gaze_x_scaled'],
    y=gaze_data['gaze_y_scaled'],
    cmap='Reds',
    fill=True,
    alpha=0.9,
    bw_adjust=0.2,
    thresh=0.01,
    levels=100,
    ax=axes[0]
)
axes[0].scatter(
    gaze_data['gaze_x_scaled'],
    gaze_data['gaze_y_scaled'],
    c='blue',
    s=20,
    alpha=0.8,
    label='Gaze Points'
)
axes[0].set_xlim(0, img_width)
axes[0].set_ylim(img_height, 0)
axes[0].set_title('Heatmap Overlay: Cleaned CSV (Raw Gaze Data)')
axes[0].set_xlabel('X Coordinate (pixels)')
axes[0].set_ylabel('Y Coordinate (pixels)')
axes[0].legend()

# --- Centroids fixation heatmap ---
axes[1].imshow(background_img, alpha=0.3)
sns.kdeplot(
    x=centroids_data['x_avg_scaled'],
    y=centroids_data['y_avg_scaled'],
    cmap='Reds',
    fill=True,
    alpha=0.9,
    bw_adjust=0.2,
    thresh=0.01,
    levels=100,
    ax=axes[1]
)
axes[1].scatter(
    centroids_data['x_avg_scaled'],
    centroids_data['y_avg_scaled'],
    c='blue',
    s=20,
    alpha=0.8,
    label='Fixation Centroids'
)
axes[1].set_xlim(0, img_width)
axes[1].set_ylim(img_height, 0)
axes[1].set_title('Heatmap Overlay: Centroids CSV (Fixation Clusters)')
axes[1].set_xlabel('X Coordinate (pixels)')
axes[1].set_ylabel('Y Coordinate (pixels)')
axes[1].legend()

plt.tight_layout()
plt.savefig(f"{output_folder}/{output_filename}", dpi=300)
print(f"Side-by-side heatmaps saved as '{output_folder}/{output_filename}'")
plt.show()
