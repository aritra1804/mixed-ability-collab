import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from screeninfo import get_monitors
# File path
csv_file = "intersection_points.csv"

# Read data from the CSV file using pandas
pointing_data = pd.read_csv(csv_file)
#get screen resolution
monitor = get_monitors()[0]
width = monitor.width
height = monitor.height
max_y = 348.23057220395225 # max y value in mm

# the following functions are from Tobii.py file, and these two files can be combined 
# to plot both the eye tracking data and the pointing data on the same graph
def flip_y(cen_y):
    """
    This function flips the directionality of a set of coordinates in the y direction.
    """
    newList = []
    for y in cen_y:
        newList.append(height - y)
    return newList

def graph(x, y, title, image_path):
    """
    Basic graphing function for the pointing data.
    """
    # Load the image
    img = mpimg.imread(image_path)
    # Plotting with the image as the background
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0, width, 0, height])
    plt.scatter(x, y, facecolor = 'none', edgecolor = 'blue', label=title)
    # Set the x and y limits
    plt.xlim(0, width)
    plt.ylim(0, height)
    # set pic to "work experience"
    # plt.xlim(740, 1040)
    # plt.ylim(1010, 1055)
    # Add labels and legend
    plt.xlabel('X (pixels)')
    plt.ylabel('Y (pixels)')
    #plt.legend()
    plt.title(title)
    #plot the function
    plt.show()

def convert_3d_to_2d(val,axis):
    """
    Converts a given value 'val' from the 3D coordinate system to the 2D coordinate system.

    The function performs scaling and translation to map the value to the 2D screen coordinates.
    The 3D coordinate system is based on the physical space, while the 2D coordinate system 
    represents the screen space.

    The screen dimensions are defined as follows:
    - Bottom-left corner: (0, 0) in pixels.
    - Top-right corner: (1920, 1200) in pixels.

    Logic of the conversion:
    1. add 258.5 to the X values so that all X values are positive
    2. flip y values so that the y axis increases as you go up (the y axis of the azure kinect increases as you go down)
    3. scale the X values to the range [0, 1920] and the Y values to the range [0, 1200]

    Note that if you are using this function to display eye gaze and hand data on a website, 
    you need to flip the y-coordinate by calling the 'flip_y()' function in this file. 
    Websites often use a different coordinate system for plotting data on the screen.

    Parameters:
        val (int or float): The value to be converted from 3D to 2D.
        axis (str): The axis along which the value is being converted. 
                    Possible values are 'x' and 'y'.

    Returns:
        int or float: The converted value in the 2D coordinate system.

    3D locations of the four corners of the screen:
    Azure Kinect Coordinate System: https://learn.microsoft.com/en-us/azure/kinect-dk/coordinate-systems
        (258.5, 348.23057220395225, 33.762693635452074),
        (-258.5, 348.23057220395225, 33.762693635452074),
        (258.5, 27, 0),
        (-258.5, 27, 0)
    """
    if axis == 'x':
        # Add 258.5 to the X values because the range of X values is [-258.5, 258.5]
        return 1920 - ((val + 258.5) * 1920 / 517)
    elif axis == 'y':
        # flip y values because azure kinect's y axis increases as you go down
        return (max_y-val) * 1200 / max_y
    else:
        raise ValueError("Invalid axis. Possible values are 'x' and 'y'.")

def run_plots_csv():
    global pointing_data

    # Extract X, Y, and Z columns from pointing_data
    x_values = convert_3d_to_2d(pointing_data["intersection_x"],'x').tolist() 
    y_values = convert_3d_to_2d(pointing_data["intersection_y"],'y').tolist()

    # Call the graph function to plot the 3D points on the 2D plane with the image background
    graph(x_values, y_values, 'Pointing Intersections', 'images/test.png')

if __name__ == "__main__":
    run_plots_csv()
