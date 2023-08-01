import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

# Points defining the plane
points = [
    (258.5, 348.23057220395225, 33.762693635452074),
    (-258.5, 348.23057220395225, 33.762693635452074),
    (258.5, 27, 0),
    (-258.5, 27, 0),
]

# Split the points into x, y, and z coordinates
x_coords, y_coords, z_coords = zip(*points)

# Read data from the CSV file and plot the points
csv_points = []
with open('intersection_points.csv', 'r') as csvfile: 
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        if all(value.strip() for value in row.values()):  # Check if all values in the row are non-empty
            x, y, z = map(float, row.values())
            csv_points.append((x, y, z))

# Create a 3D figure
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the points from the CSV file
x_csv, y_csv, z_csv = zip(*csv_points)
ax.scatter(x_csv, y_csv, z_csv, c='b', marker='o', label='CSV Points')

# Plot the points defining the plane (in blue color)
ax.scatter(x_coords, y_coords, z_coords, c='r', marker='o', label='Plane Points')

# Define the vertices of the rectangle representing the plane
vertices = [
    [points[0], points[1], points[3], points[2]],
]

# Define the faces of the rectangle representing the plane
faces = Poly3DCollection(vertices, linewidths=1, edgecolors='r', alpha=0.2, facecolors='g')

# Add the faces to the plot
ax.add_collection3d(faces)

# Calculate the max range for x, y, and z to set equal axis limits
max_range = np.array(list(x_csv) + list(y_csv) + list(z_csv) + list(x_coords) + list(y_coords) + list(z_coords)).max() - np.array(list(x_csv) + list(y_csv) + list(z_csv) + list(x_coords) + list(y_coords) + list(z_coords)).min()

# Set equal axis limits to create a cube-like view
x_mean = np.mean(list(x_coords) + list(x_csv))
y_mean = np.mean(list(y_coords) + list(y_csv))
z_mean = np.mean(list(z_coords) + list(z_csv))
ax.set_xlim([x_mean - max_range/2, x_mean + max_range/2])
ax.set_ylim([y_mean - max_range/2, y_mean + max_range/2])
ax.set_zlim([z_mean - max_range/2, z_mean + max_range/2])

# Set labels for the axes
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

# Set title for the plot
plt.title('Intersection Points and Plane in 3D Space')

# Show the legend
ax.legend()

# Show the plot
plt.show()

