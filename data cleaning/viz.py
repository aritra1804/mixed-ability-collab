import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
from sklearn.preprocessing import MinMaxScaler

# ======= CONFIGURATION =======
cleaned_csv = "data cleaning/clean_csv/cleaned_amazon.csv"  # Path to cleaned CSV
screenshot_path = "data cleaning/screenshots/amazon.png"        # Path to screenshot
# =============================

# Load the cleaned gaze data
gaze_data = pd.read_csv(cleaned_csv)

# Load the screenshot
background_img = mpimg.imread(screenshot_path)
img_height, img_width = background_img.shape[:2]
print(f"Image size: {img_width}x{img_height}")

# Rescale gaze_x_px and gaze_y_px to match the image size
scaler_x = MinMaxScaler(feature_range=(0, img_width))
scaler_y = MinMaxScaler(feature_range=(0, img_height))

gaze_data['gaze_x_scaled'] = scaler_x.fit_transform(gaze_data[['gaze_x_px']])
gaze_data['gaze_y_scaled'] = scaler_y.fit_transform(gaze_data[['gaze_y_px']])

# Plot the screenshot as the background with reduced opacity
fig, ax = plt.subplots(figsize=(12, 8))
ax.imshow(background_img, alpha=0.3)

# Overlay the heatmap
sns.kdeplot(
    x=gaze_data['gaze_x_scaled'],
    y=gaze_data['gaze_y_scaled'],
    cmap='Reds',
    fill=True,
    alpha=0.9,       # Strong visibility
    bw_adjust=0.2,   # Tighter clusters
    thresh=0.01,
    levels=100
)

# Overlay the actual gaze points as blue dots
plt.scatter(
    gaze_data['gaze_x_scaled'],
    gaze_data['gaze_y_scaled'],
    c='blue',
    s=20,
    alpha=0.8,
    label='Gaze Points'
)

# Set the plot limits and labels
ax.set_xlim(0, img_width)
ax.set_ylim(img_height, 0)  # Invert Y-axis to match image coordinates
ax.set_xlabel('X Coordinate (pixels)')
ax.set_ylabel('Y Coordinate (pixels)')
ax.set_title('Amazon Product Page Gaze Heatmap with Rescaled Gaze Points')
plt.legend()

# Show the heatmap overlay
plt.show()
