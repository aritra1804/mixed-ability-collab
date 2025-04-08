import numpy as np

def normalized_to_pixels(normalized_point, width, height):
    """
    Convert a normalized coordinate (values between 0 and 1) to a pixel coordinate
    based on the given image width and height.

    Parameters:
        normalized_point (tuple): A tuple (x, y) in normalized coordinates.
        width (int): Width of the image in pixels.
        height (int): Height of the image in pixels.

    Returns:
        tuple: (x_pixel, y_pixel) corresponding to pixel coordinates.
    """
    x, y = normalized_point
    x_pixel = x * width
    y_pixel = y * height
    return (x_pixel, y_pixel)

def batch_normalized_to_pixels(normalized_points, width, height):
    """
    Convert a list of normalized coordinates to pixel coordinates.

    Parameters:
        normalized_points (list): List of tuples [(x, y), ...] with normalized values.
        width (int): Width of the image in pixels.
        height (int): Height of the image in pixels.

    Returns:
        list: List of tuples [(x_pixel, y_pixel), ...] with pixel coordinates.
    """
    return [normalized_to_pixels(point, width, height) for point in normalized_points]

def compute_centroid(points):
    """
    Compute the centroid (average position) of a list of (x, y) points.

    Parameters:
        points (list): List of tuples [(x, y), ...].

    Returns:
        tuple or None: The centroid as (x, y) or None if the list is empty.
    """
    if not points:
        return None
    points_array = np.array(points)
    centroid = points_array.mean(axis=0)
    return tuple(centroid)
