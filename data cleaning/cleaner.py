import pandas as pd
import ast
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the raw gaze data CSV
file_path = "data cleaning/csv/output_amazon.csv"
df = pd.read_csv(file_path)

# Filter for valid gaze points
valid_gaze_data = df[df['left_gaze_point_validity'] == 1].copy()

# Function to extract coordinates from string format "(x, y)"
def extract_coordinates(coord_str):
    try:
        return ast.literal_eval(coord_str)
    except (ValueError, SyntaxError):
        return (None, None)

# Apply coordinate extraction
valid_gaze_data[['gaze_x', 'gaze_y']] = valid_gaze_data['left_gaze_point_on_display_area'].apply(
    lambda coord: pd.Series(extract_coordinates(coord))
)

# Remove rows with invalid or missing coordinates
valid_gaze_data = valid_gaze_data.dropna(subset=['gaze_x', 'gaze_y'])

# Define screen resolution (based on your screenshot)
screen_width = 1228
screen_height = 768

# Convert normalized gaze coordinates to pixel values
valid_gaze_data['gaze_x_px'] = valid_gaze_data['gaze_x'] * screen_width
valid_gaze_data['gaze_y_px'] = valid_gaze_data['gaze_y'] * screen_height

# Remove unwanted timestamp columns
cleaned_gaze_data = valid_gaze_data.drop(columns=['device_time_stamp', 'system_time_stamp'])

# Create the 'clean_csv' folder if it doesn't exist
output_folder = "data cleaning/clean_csv"
os.makedirs(output_folder, exist_ok=True)

# Save the cleaned data inside the 'clean_csv' folder
output_path = os.path.join(output_folder, "cleaned_amazon.csv")
cleaned_gaze_data.to_csv(output_path, index=False)

print("Cleaned gaze data saved as 'cleaned_amazon.csv'.")
