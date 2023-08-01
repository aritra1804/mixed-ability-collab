import csv
import matplotlib.pyplot as plt
import numpy as np

# Points defining the plane
points = [
    (258.5, 348.23057220395225, 33.762693635452074),
    (-258.5, 348.23057220395225, 33.762693635452074),
    (258.5, 27, 0),
    (-258.5, 27, 0),
]

# Read data from the CSV file and filter the points that fall on the plane
csv_points_on_plane = []
with open('intersection_points.csv', 'r') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        if all(value.strip() for value in row.values()):  # Check if all values in the row are non-empty
            x, y, z = map(float, row.values())
            if abs(z - 33.762693635452074) < 0.0001:  # Adjust the tolerance value as needed
                csv_points_on_plane.append((x, y, z))

# Split the points defining the plane into x, y, and z coordinates
x_coords, y_coords, z_coords = zip(*points)

# Split the points from the CSV file that fall on the plane into x, y, and z coordinates
if csv_points_on_plane:
    x_csv_on_plane, y_csv_on_plane, _ = zip(*csv_points_on_plane)

# Create a 2D figure for the plane plot
fig = plt.figure()
ax = fig.add_subplot(111)

# Plot the points from the CSV file that fall on the plane
if csv_points_on_plane:
    ax.plot(x_csv_on_plane, y_csv_on_plane, 'bo', label='CSV Points on Plane')

# Plot the points defining the plane (in red color)
ax.plot(x_coords, y_coords, 'ro', label='Plane Points')

# Set labels for the axes
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')

# Set title for the plot
plt.title('Points on the Plane in 2D')

# Show the legend
ax.legend()

# Show the plot
plt.show()
