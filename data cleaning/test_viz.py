import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
import ast

# ======= CONFIGURATION =======
cleaned_csv = "data cleaning/clean_csv/cleaned_amazon.csv"
screenshot_path = "data cleaning/screenshots/amazon.png"
# =============================

# Load the gaze data
gaze_data = pd.read_csv(cleaned_csv)

# Keep only valid left eye gaze points
gaze_data = gaze_data[gaze_data['left_gaze_point_validity'] == 1].copy()

# Extract (x, y) coordinates from left gaze point
def extract_coordinates(coord_str):
    try:
        return ast.literal_eval(coord_str)
    except (ValueError, SyntaxError):
        return (None, None)

gaze_data[['gaze_x', 'gaze_y']] = gaze_data['left_gaze_point_on_display_area'].apply(
    lambda coord: pd.Series(extract_coordinates(coord))
)

# Drop invalid gaze points
gaze_data = gaze_data.dropna(subset=['gaze_x', 'gaze_y'])

# Load the screenshot and get its size
background_img = mpimg.imread(screenshot_path)
img_height, img_width = background_img.shape[:2]
print(f"Image size: {img_width}x{img_height}")

# Scale normalized gaze coordinates to match the screenshot size
gaze_data['gaze_x_px'] = gaze_data['gaze_x'] * img_width
gaze_data['gaze_y_px'] = gaze_data['gaze_y'] * img_height

# Plot the screenshot as the background
fig, ax = plt.subplots(figsize=(12, 8))
ax.imshow(background_img, alpha=0.3)

# Plot heatmap
sns.kdeplot(
    x=gaze_data['gaze_x_px'],
    y=gaze_data['gaze_y_px'],
    cmap='Reds',
    fill=True,
    alpha=0.9,
    bw_adjust=0.2,
    thresh=0.01,
    levels=100
)

# Plot gaze points
plt.scatter(
    gaze_data['gaze_x_px'],
    gaze_data['gaze_y_px'],
    c='yellow',
    s=50,
    alpha=0.8,
    label='Gaze Points'
)

# Final plot settings
ax.set_xlim(0, img_width)
ax.set_ylim(img_height, 0)
ax.set_xlabel('X Coordinate (pixels)')
ax.set_ylabel('Y Coordinate (pixels)')
ax.set_title('Amazon Product Page Gaze Heatmap (Left Eye Only)')
plt.legend()
plt.show()
