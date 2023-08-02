
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
from scipy.spatial import ConvexHull

plt.style.use('fivethirtyeight')

# Read the CSV file
data_df = pd.read_csv('handShape_data.csv')
# Add 265 to 'Intersection X' column (set lower left corner to be (o,o,-332))
data_df['Intersection X'] += 255
# Subtract 112 from 'Intersection Y' column
data_df['Intersection Y'] -= 247

# Set the figure size to match the monitor dimensions
fig, ax = plt.subplots(figsize=(16, 9))

# Initialize an empty scatter plot
scatter = ax.scatter([], [], color='blue')

# Set plot labels and title
ax.set_xlabel('Intersection X')
ax.set_ylabel('Intersection Y')
ax.set_title('Animated Scatter Plot')
# Set the aspect ratio to be equal
# ax.set_aspect('equal')

# Set the axis ranges
ax.set_xlim(0, 530)
ax.set_ylim(0, 295)

# Function to update the scatter plot at each animation frame
def update(frame):
    # Get the data points up to the current frame
    x = data_df['Intersection X'][:frame+1]
    y = data_df['Intersection Y'][:frame+1]
  
    # Update the scatter plot
    scatter.set_offsets(list(zip(x, y)))
  
    # Set the axis limits to accommodate all data points
    ax.set_xlim(data_df['Intersection X'].min(), data_df['Intersection X'].max())
    ax.set_ylim(data_df['Intersection Y'].min(), data_df['Intersection Y'].max())

# Create the animation using the update function (Uncomment to show animation)
#animation = FuncAnimation(fig, update, frames=len(data_df), interval=0, repeat=False)

# Calculate the average data point
avg_x = data_df['Intersection X'].mean()
avg_y = data_df['Intersection Y'].mean()

# Calculate the convex hull
# points = data_df[['Intersection X', 'Intersection Y']].values
# hull = ConvexHull(points)

# Plot the convex hull
# for simplex in hull.simplices:
#     plt.plot(points[simplex, 0], points[simplex, 1], 'r-', linewidth=2)

# Plot the scatter (comment to show animation)
scatter = ax.scatter(data_df['Intersection X'], data_df['Intersection Y'], color='blue')

# Plot the average data point in red
ax.scatter(avg_x, avg_y, color='red')
ax.text(avg_x, avg_y +5, f'Avg: ({avg_x:.2f}, {avg_y:.2f})', color='red', ha='center',va='bottom')

# Plot the center point
ax.scatter(265, 147.5, color='black')
ax.text(265, 135, 'center', color='black', ha='center', va='bottom')

# Display the plot
plt.show()
