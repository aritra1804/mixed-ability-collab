"""
This code contains: data collection, filtering/processing, and visualization functions for the Tobii Pro Fusion eye tracker
It is able to calculate centroids live and write data to a csv file.

This code contains an implementation of the Tobii I-VT Fixation Filter, which is a fixation classification algorithm
This is *not* a saccade classification algorithm/ I-VT classification filter
Based on Olsen (2012) The Tobii I-VT Fixation Filter accessed from http://www.vinis.co.kr/ivt_filter.pdf
Tested with the Tobii Pro Fusion eye tracker

@author Juno Bartsch in collaboration with Andrew Begel and JiWoong (Joon) Jang at the Carnegie Mellon University VariAbility Lab
Portions of the code related to vector algebra modified from https://github.com/Yejining/I-VTFilter
Last modified July 2023

Modifications:
Instead of using left, right, average, or strict average eye selection, this code uses the participant's dominant eye
If this data is not available, it will look for the other eye and then for interpolated data (which is created only
in the absence of data from either eye).

This code uses a custom CentroidData class to hold centroid points. Some of the filter parameters may be
adjusted from the I-VT specification, but the default values are included in the comments.

There are also a plethora of plotting functions included in this code but not called in the main function.
These were used for testing purposes and can be used to visualize the data and the filter's performance.

Calibration code modified from the Tobii Pro SDK sample code at https://developer.tobiipro.com/python/python-sdk-reference-guide.html
This code generates calibration images using the pygame package.



"""

"""
some observations: 

conda env (eye) and python version 3.10 and (eyetracking) and python verison 3.6 work 

the code uses device time (eye tracker time which starts from 1970) but uses system time (computer time) in find_points_in_window and gaze_angle_velocity because only relative times matter
suspect device time is mainly used to avoid issues like latency, need further consideration when syncing different systems
it is noted that the time used by python is in UTC, which is four hours ahead of EST 
the device time and system time are in seconds * 1000_000 unix time, and the time-offset might change 

device time in centroids.csv

remember to close all the plots for the process to end 

the test image is 1920 * 1200, same for monitor width (1920) to monitor height 
"""

import tobii_research as tr # conda eyetracking created with python3.6 not able to install transformers, conda env eye created with python=3.10 and transformers installed
import time
from screeninfo import get_monitors
import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation as fa
import numpy as np
from scipy.spatial import ConvexHull
import math
from Point23D import Point3D
from Point23D import get_angular_distance
import sys
from getDom import DomObjectRetriever
import matplotlib.image as mpimg
from collections import deque
import pygame
from pygame.locals import *
import http.server
import json
import requests
from flask import Flask, render_template, jsonify
import threading
import asyncio
import websockets
import os
import base64
from image_to_text import caption_image
from PIL import Image,UnidentifiedImageError
from datetime import datetime
# Set the angle filter amount for the I-VT filter in the filter_centroids fn
# Check if command-line argument exists
if len(sys.argv) > 1:
    # Use the command-line argument
    angle_cap = float(sys.argv[1])
else:
    # default from I-VT specification is .5
    angle_cap = 0.5

#find the eye tracker
eyetrackers = tr.find_all_eyetrackers()
eyetracker = eyetrackers[0]
FREQUENCY = 250 #Hz

#get screen resolution
monitor = get_monitors()[0]
width = monitor.width
print("monitor width",width)
height = monitor.height
print("monitor height",height)

# I-VT filter parameters, ADJUST AS NEEDED paper
velocity_threshold = 30                     # maximum angle to be considered a fixation, default 30 degrees
maximum_interpolation_time_micro = 75000    # maximum allowed time for interpolation in microseconds
maximum_time_between_fixations = 75000      # maximumm allowed time between fixations in microseconds
maximum_angle_between_fixations = angle_cap # maximum angle between fixations in degrees, default from I-VT specification is .5
minimum_fixation_duration = 60000           # minimum fixation duration in microseconds
window_size_seconds = 0.01    # maximum time on either side of the spanning window for velocity calculations, default 10 ms --> 0.01 seconds

#global variable declaration- lists of coordinates for the left and right eyes as well as interpolated data
gaze_data_list, left_x, left_y, right_x, right_y, inter_x, inter_y, centroids_x, centroids_y = [], [], [], [], [], [], [], [], []
unfiltered_centroids_x, unfiltered_centroids_y = [], []
global_gaze_index, num_values_to_interpolate, prev_valid_point, prev_valid_time, prev_valid_idx, flag_interpolation = 0, 0, None, -1, -1, False
angle_velocity_deque, centroid_data, centroid_ids, prev_centroid = deque(), [], set(), None
av_deque_maxlen = math.floor(FREQUENCY * window_size_seconds * 2)
retriever = DomObjectRetriever()
data_to_send = {"x": height, "y": width}
new_system_time = []

#Switch based on the dominant eye of the participant
dominant_eye = 'left'
#dominantEye = 'right'
     
#set selected traits from the gaze data list based on the dominant eye
if dominant_eye == 'left':
    selected_poda = 'left_gaze_point_on_display_area'
    selected_gova = 'left_gaze_origin_validity'
    selected_gotcs = 'left_gaze_origin_in_trackbox_coordinate_system'
    selected_goucs = 'left_gaze_origin_in_user_coordinate_system'
else:
    selected_poda = 'right_gaze_point_on_display_area'
    selected_gova = 'right_gaze_origin_validity'
    selected_gotcs = 'right_gaze_origin_in_trackbox_coordinate_system'
    selected_goucs = 'right_gaze_origin_in_user_coordinate_system'
inter_poda = 'inter_gaze_point_on_display_area'
inter_gova = 'inter_gaze_origin_validity'
inter_gotcs = 'inter_gaze_origin_in_trackbox_coordinate_system'
inter_goucs = 'inter_gaze_origin_in_user_coordinate_system'

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#This function completes basic linear interpolation for 2 and 3-variable arrays
def linear_interpolation(indices, criteria):
    global gaze_data_list, prev_valid_time
    #calculate the start and end points, time difference, and slope
    delta_t = gaze_data_list[indices[-1]]['device_time_stamp'] - prev_valid_time
    startx = gaze_data_list[indices[0]][criteria][0]
    starty = gaze_data_list[indices[0]][criteria][1]
    endx = gaze_data_list[indices[-1]][criteria][0]
    endy = gaze_data_list[indices[-1]][criteria][1]
    return_list = []
    x_slope = (endx  - startx) / delta_t
    y_slope = (endy - starty) / delta_t
    dt = 0
    # Fill in the missing data points as a line drawn between the valid points
    if(len(gaze_data_list[0][criteria])) == 2:
        for i in range(indices[0] + 1, indices[-1]):
            dt = gaze_data_list[i]['device_time_stamp']-prev_valid_time
            x_inter = x_slope * dt + startx
            y_inter = y_slope * dt + starty
            return_list.append([x_inter, y_inter])
    else:
        startz = gaze_data_list[indices[0]][criteria][2]
        endz = gaze_data_list[indices[-1]][criteria][2]
        z_slope = (endz - startz) / delta_t
        # Fill in the missing data points as a line drawn between the valid points
        for i in range(indices[0] + 1, indices[-1]):
            dt = gaze_data_list[i]['device_time_stamp']-prev_valid_time
            x_inter = x_slope * dt + startx
            y_inter = y_slope * dt + starty
            z_inter = z_slope * dt + startz
            return_list.append([x_inter, y_inter, z_inter])
    return return_list

# Function to perform linear interpolation on the gaze data
def interpolate_gaze_data(start, current):
    global gaze_data_list
    indices = range(start, current)
    #call the linear interpolation function for the desired variables (e.g. gaze on display area, location in trackbox/user coordinate systems)
    interpolated_data1, interpolated_data2, interpolated_data3 = linear_interpolation(indices, selected_poda), linear_interpolation(indices, 
        selected_gotcs), linear_interpolation(indices, selected_goucs)
    i = 0
    for x in indices:
        #this if statement excludes the valid points used for the interpolation
        if(math.isnan(gaze_data_list[x][selected_poda][0])):
            gaze_data_list[x]['selected_eye'] = 'inter'
            gaze_data_list[x][inter_gova] = 1
            gaze_data_list[x][inter_poda] = interpolated_data1[i]
            gaze_data_list[x][inter_gotcs] = interpolated_data2[i]
            gaze_data_list[x][inter_goucs] = interpolated_data3[i]
            i+=1
            #print('live interpolation at index ' + str(x), gaze_data_list[x][inter_poda])

#This function checks if interpolation needs to occur, identified by NaN in output.csv and below maximum threshold, if so it calls the interpolation function - linear_interpolation
def check_interpolation(gaze_data):
    global prev_valid_point, prev_valid_time, prev_valid_idx, flag_interpolation, gaze_data_list
    # Interpolation works as follows: maintain an index of the last valid data point.
    # If nans are encountered and another valid data point occurs within the time threshold, interpolate the data
    timestamp = gaze_data['device_time_stamp']
    time_check = (prev_valid_time != -1) and (timestamp - prev_valid_time) < maximum_interpolation_time_micro
    # Process interpolation if criteria are met- there must be valid data to interpolate and the time criteria must be met
    # The flag for interpolation is set based on the time criteria and availability of previous data
    if(not time_check):
        flag_interpolation = False
    if(not math.isnan(gaze_data[selected_poda][0])):
        if time_check and prev_valid_point is not None:
            flag_interpolation = True
            #indices are used to specify where the helper function should interpolate data
            idx = gaze_data['index']
            if (idx-prev_valid_idx>1):
                interpolate_gaze_data(prev_valid_idx, idx+1)
                flag_interpolation = False
        #set the previous valid point whenever a valid point is discovered
        prev_valid_point = gaze_data
        prev_valid_time = timestamp
        prev_valid_idx = gaze_data['index']
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#This callback function adds gaze data from the eye tracker to the global gaze_data_list and interpolates the data live
def gaze_data_callback(gaze_data):
    global centroid_data, retriever, data_to_send
    #append the gaze data to the list
    gaze_data_list.append(append_pixel_data(gaze_data))
    new_system_time.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    #check if interpolation needs to happen for this data point
    #print("gaze data:",gaze_data.get('left_gaze_point_on_display_area'),gaze_data.get('right_gaze_point_on_display_area'))
    check_interpolation(gaze_data)
    angle_velocity_deque.append(gaze_data)
    if(len(angle_velocity_deque) > av_deque_maxlen):
        angle_velocity_deque.popleft()
        points_data = find_points_in_window(angle_velocity_deque)
        gaze_angle_velocity(points_data)
    centroids_to_add = find_centroids(points_data)
    xta, yta = centroids_to_add[-1].coords()
    xta, yta = round(xta), round(yta)
    data_to_send = {"x": xta, "y": yta}
    for centroid in centroids_to_add:
        centroid_data.append(centroid)
            
#This function implements a custom calibration sequence for the eye tracker
def calibrate_eyetracker():
    calibration = tr.ScreenBasedCalibration(eyetracker)

    # Enter calibration mode.
    calibration.enter_calibration_mode()
    print("Entered calibration mode for eye tracker with serial number {0}.".format(eyetracker.serial_number))

    # Define the points on screen we should calibrate at.
    # The coordinates are normalized, i.e. (0.0, 0.0) is the upper left corner and (1.0, 1.0) is the lower right corner.
    points_to_calibrate = [(0.5, 0.5), (0.1, 0.1), (0.1, 0.9), (0.9, 0.1), (0.9, 0.9)]

    #initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((width, height))

    for point in points_to_calibrate:
        # Clear the screen
        screen.fill((0, 0, 0))

        # Draw a circle at the calibration point
        circle_radius = 15
        circle_color = (255, 255, 255)  # Red
        circle_pos = (int(point[0] * width), int(point[1] * height))
        pygame.draw.circle(screen, circle_color, circle_pos, circle_radius)

        # Update the display
        pygame.display.flip()

        print("Show a point on screen at {0}.".format(point))

        # Wait a little for the user to focus.
        time.sleep(1.75)

        print("Collecting data at {0}.".format(point))
        if calibration.collect_data(point[0], point[1]) != tr.CALIBRATION_STATUS_SUCCESS:
            # Try again if it didn't go well the first time.
            # Not all eye tracker models will fail at this point but instead fail on ComputeAndApply.
            calibration.collect_data(point[0], point[1])

    print("Computing and applying calibration.")
    calibration_result = calibration.compute_and_apply()
    print("Compute and apply returned {0} and collected at {1} points.".format(calibration_result.status, len(calibration_result.calibration_points)))

    # Analyze the data and maybe remove points that weren't good.
    #recalibrate_point = (0.1, 0.1)
    #print("Removing calibration point at {0}.".format(recalibrate_point))
    #calibration.discard_data(recalibrate_point[0], recalibrate_point[1])

    # Redo collection at the discarded point.
    #print("Show a point on screen at {0}.".format(recalibrate_point))
    #calibration.collect_data(recalibrate_point[0], recalibrate_point[1])

    # Clean up the pygame resources
    pygame.quit()

    # Compute and apply again.
    print("Computing and applying calibration.")
    calibration_result = calibration.compute_and_apply()
    print("Compute and apply returned {0} and collected at {1} points.".format(calibration_result.status, len(calibration_result.calibration_points)))

    # The calibration is done. Leave calibration mode.
    calibration.leave_calibration_mode()
    print("Left calibration mode.")

#This function opens te eye tracker for the specified duration and then closes the connection
def run_eyetracker(duration):
    global data_to_send
    eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    time.sleep(duration)
    eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    #stop the website from sending get requests
    data_to_send = {"x": -1, "y": -1}

#This function modifies the gaze data to be in pixels rather than fractional values and adds the helper selected eye variable
def append_pixel_data(gaze_data):
    global global_gaze_index
    #the selected eye variable is set to the dominant eye if data is available, inter if interpolated, and none otherwise
    gaze_data['selected_eye'] = 'none'
    gaze_data['index'] = global_gaze_index
    global_gaze_index += 1
    #these variables are adjusted to pixel values based on the height and width of the screen
    lx, ly = gaze_data['left_gaze_point_on_display_area']
    rx, ry = gaze_data['right_gaze_point_on_display_area']
    if (not(math.isnan(rx))):
       rx, ry = rx * width, ry * height
       gaze_data['right_gaze_point_on_display_area'] = [rx, ry]
       if dominant_eye == 'right':
           gaze_data['selected_eye'] = dominant_eye
    if (not math.isnan(lx)):
        lx, ly = lx * width, ly * height
        gaze_data['left_gaze_point_on_display_area'] = [lx, ly]
        if dominant_eye == 'left':
            gaze_data['selected_eye'] = dominant_eye
    return gaze_data

#adds the index of the point within the window furthest before (window_1) and after (window_2) each gaze point
def find_points_in_window(gaze_points):
    # Loop over the gaze points
    for i, gaze_point in enumerate(gaze_points):
        current_time = gaze_point['system_time_stamp']  / 1000000
        
        # Find the point before the current point
        for j in range(i-1, -1, -1):
            time_diff = current_time - (gaze_points[j]['system_time_stamp'] / 1000000)
            if time_diff <= window_size_seconds:
                gaze_point['window_1'] = gaze_points[j]['index']
            else:
                break

        # Find the point after the current point
        for k in range(i+1, len(gaze_points)):
            time_diff = (gaze_points[k]['system_time_stamp'] / 1000000) - current_time
            if time_diff <= window_size_seconds:
                gaze_point['window_2'] = gaze_points[k]['index']
            else:
                break   
    return gaze_points

#this function finds the gaze angle for the points within the window
def gaze_angle_velocity(points_data):
    for gaze_data in points_data:
        #initialize variables for the gaze angle and velocity
        prev_point_screen, next_point_screen, window_1, window_2 = None, None, None, None
        user_pos = gaze_data[selected_goucs]
        try:
            window_1 = gaze_data['window_1']
            window_2 = gaze_data['window_2']
        except KeyError:
            continue
        if((not math.isnan(window_1)) & (not math.isnan(window_2)) & (user_pos is not None)):
            prev_point_screen = gaze_data_list[window_1][selected_poda]
            next_point_screen = gaze_data_list[window_2][selected_poda]
            if((prev_point_screen is not None) and (next_point_screen is not None)):
                #if there is data to calculate an angle, generate Point3D objects for the user's position 
                #in the user coordinate system, the previous point, and the next point
                user_origin = Point3D(user_pos[0], user_pos[1], user_pos[2])
                prev_point = Point3D(prev_point_screen[0]*width, prev_point_screen[1]*height, user_pos[2])
                next_point = Point3D(next_point_screen[0]*width, next_point_screen[1]*height, user_pos[2])
                #Uses Yejining's function for angular distance in degrees
                ang_dist = get_angular_distance(user_origin, prev_point, next_point)
                gaze_data['angular_distance'] = ang_dist
                prev_gaze = gaze_data_list[window_1]
                next_gaze = gaze_data_list[window_2]
                time_diff = (next_gaze['system_time_stamp'] / 1000000) - (prev_gaze['system_time_stamp'] / 1000000)
                #if the time condition is met, calculate velocity as well
                if time_diff != 0:
                    velocity = gaze_data['angular_distance'] / time_diff
                    gaze_data['velocity'] = velocity

#this function uses the angle and velocity data to find centroids and calls the function to merge adjacent fixations (filter centroids)
def find_centroids(angle_velocity_data):
    unfiltered_centroids = []
    for gaze_data in angle_velocity_data:
        try:
            vel = gaze_data['velocity']
            if (vel != 0) & (vel <= velocity_threshold):
                gaze_data_x = gaze_data['left_gaze_point_on_display_area'][0] if dominant_eye == 'left' else gaze_data['inter_gaze_point_on_display_area'][0]
                gaze_data_y = gaze_data['left_gaze_point_on_display_area'][1] if dominant_eye == 'left' else gaze_data['inter_gaze_point_on_display_area'][1]
                gaze_id = gaze_data['index']
                if((not math.isnan(gaze_data_x)) & (not math.isnan(gaze_data_y)) & (gaze_id not in centroid_ids)):
                    unfiltered_centroids.append(gaze_data)
                    unfiltered_centroids_x.append(gaze_data_x)
                    unfiltered_centroids_y.append(gaze_data_y)
                    centroid_ids.add(gaze_id)
        except KeyError:
            continue
    if(len(unfiltered_centroids) > 0):
        return filter_centroids(unfiltered_centroids)
    else:
        return []

#This class holds centroid data and contains functions to access time/coordinate data
class CentroidData:
    def __init__(self, id, start, end, x, y, z):
        self.id = id
        self.start = start
        self.end = end
        self.x = x
        self.y = y
        self.origin = z
        self.tdo = None
        self.aoi = None
    #returns the difference in start and end time of the centroid
    def time(self):
        return self.end - self.start
    #returns the sum of the x coordinates of the centroid
    def sum_x(self):
        sum_x = 0
        for item in self.x:
            sum_x += item
        return sum_x
    #returns the sum of the y coordinates of the centroid
    def sum_y(self):
        sum_y = 0
        for item in self.y:
            sum_y += item
        return sum_y
    #returns the average [x,y] coordinates of the centroid in pixels
    def coords(self):
        return [self.sum_x()/len(self.x), self.sum_y()/len(self.y)]

#This function converts a gaze data point to a CentroidData object
def gaze_tuple_to_centroid_data(gaze_tuple):
    x, y = gaze_tuple[selected_poda] 
    z = gaze_tuple[selected_goucs]
    return CentroidData([gaze_tuple['index']], gaze_tuple['device_time_stamp'], gaze_tuple['device_time_stamp'], [x], [y], z)    

#this function merges adjacent fixations using the maximum time and angle between fixations
def filter_centroids(unfiltered_centroids):
    global prev_centroid
    #convert unfiltered data to CentroidData objects
    intermediary_centroids = []
    for centroid in unfiltered_centroids:
        intermediary_centroids.append(gaze_tuple_to_centroid_data(centroid))
    if prev_centroid is None:
        prev_centroid = intermediary_centroids[0]
    filtered_centroids = []
    i = 0
    while i < len(intermediary_centroids):
        # check if the current point is within the maximum time and angle between fixations
        centroid = intermediary_centroids[i]
        prev_centroid_time = prev_centroid.end
        centroid_time = centroid.start
        if abs(centroid_time - prev_centroid_time) < maximum_time_between_fixations:
            # calculate angle between the last sample in the first fixation and the first sample in the second fixation
            origin = Point3D(prev_centroid.origin[0], prev_centroid.origin[1], prev_centroid.origin[2])
            p1x, p1y = prev_centroid.coords()
            point1 = Point3D(p1x, p1y, prev_centroid.origin[2])
            p2x, p2y = centroid.coords()
            point2 = Point3D(p2x, p2y, centroid.origin[2])
            angle = get_angular_distance(origin, point1, point2)
            if angle < angle_cap : 
                # merge to centroid to add
                prev_centroid.id += centroid.id
                prev_centroid.end = centroid.end
                prev_centroid.x += centroid.x
                prev_centroid.y += centroid.y
            else:
                filtered_centroids.append(prev_centroid)
                prev_centroid = centroid
        else:
            filtered_centroids.append(prev_centroid)
            prev_centroid = centroid
        i += 1
    return list(filtered_centroids)

#This function writes data to a csv file. Additional data column header values should be added to headers/headers2.extend as necessary
def write_to_csv(data_to_write, centroid_data):
    #main data csv
    headers = ['new_timestamps'] +  list(data_to_write[0].keys())
    headers.extend(['angular_distance', 'velocity', 'window_1', 'window_2', 'inter_gaze_point_on_display_area', 'inter_gaze_origin_validity', 'inter_gaze_origin_in_trackbox_coordinate_system', 'inter_gaze_origin_in_user_coordinate_system'])
    with open('csv/output/output.csv', 'w', newline = '') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for row, timestamp in zip(data_to_write,new_system_time):
            row = {"new_timestamps":timestamp,**row}
            writer.writerow(row)
    
    #centroid csv
    headers2 = ['id', 'start', 'end', 'x_avg', 'y_avg', 'x_list', 'y_list', 'origin']
    with open('csv/centroid/centroids.csv', 'w', newline='') as file2:
        writer = csv.DictWriter(file2, fieldnames=headers2)
        writer.writeheader()
        for centroid in centroid_data:
            x, y = centroid.coords()
            x_list = [item for item in centroid.x]
            y_list = [item for item in centroid.y]
            writer.writerow({
                'id': centroid.id,
                'start': centroid.start,
                'end': centroid.end,
                'x_avg': x,
                'y_avg': y,
                'x_list': x_list,
                'y_list': y_list,
                'origin': centroid.origin
            })

#This function draws the unfiltered and interpolated data 
def draw_unfiltered(title, image_path):
    # Load the image
    img = mpimg.imread(image_path)
    # Plotting convex hulls with the image as the background
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0, width, 0, height])
    
    # Plot the new scatter plot with the updated data, left eye in blue, righ eye in red, and interpolated in green
    plt.scatter(left_x, left_y, facecolor = 'none', edgecolor = 'blue', label = 'Left Eye')
    plt.scatter(right_x, right_y, facecolor = 'none', edgecolor = 'red', label = 'Right Eye')
    plt.scatter(inter_x, inter_y, facecolor = 'none', edgecolor = 'green', label = "Interpolated")

    # Set the x and y limits
    plt.xlim(0, width)
    plt.ylim(0, height)

    # Add labels and legend
    plt.xlabel('X (pixels)')
    plt.ylabel('Y (pixels)')
    plt.legend()
    plt.title(title)

    plt.show()

#This function draws the data as an animation
def draw_pixels(data, title):
    fig = plt.figure()
    fa(fig, update, frames=len(data), interval=0)
    plt.title(title)
    plt.show()

#This is the update function for the animated plots
def update(filtered_data, frame):
    # Clear the previous plot
    plt.cla()

    # Get the x and y coordinates for the current frame from the filtered data
    frame_data = filtered_data[-frame:]
    frame_left_x = [data['left_gaze_point_on_display_area'][0] for data in frame_data]
    frame_left_y = [data['left_gaze_point_on_display_area'][1] for data in frame_data]
    frame_right_x = [data['right_gaze_point_on_display_area'][0] for data in frame_data]
    frame_right_y = [data['right_gaze_point_on_display_area'][1] for data in frame_data]

    # Plot the new scatter plot with the updated data
    plt.scatter(frame_left_x, frame_left_y, color='blue', label='Left Eye')
    plt.scatter(frame_right_x, frame_right_y, color='red', label='Right Eye')

    # Set the x and y limits
    plt.xlim(0, width)
    plt.ylim(0, height)

    # Add labels and legend
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.title('Animated')

    plt.show()

#This is a basic graphing function using the x and y data and a title
def graph(x, y, title, image_path):
    # Load the image
    img = mpimg.imread(image_path)
    # Plotting with the image as the background
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0, width, 0, height])
    plt.scatter(x, y, facecolor = 'none', edgecolor = 'blue', label=title)
    # Set the x and y limits
    plt.xlim(0, width)
    plt.ylim(0, height)
    # Add labels and legend
    plt.xlabel('X (pixels)')
    plt.ylabel('Y (pixels)')
    #plt.legend()
    plt.title(title)
    #plot the function
    plt.show()

#This is a basic graphing function using two sets of x/y points and titles
def graph2(x1, y1, x2, y2, title1, title2, image_path):
    # Load the image
    img = mpimg.imread(image_path)
    # Plotting with the image as the background
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0, width, 0, height])
    plt.scatter(x1, y1, color='blue', label=title1)
    plt.scatter(x2, y2, color='red', label=title2)
    # Set the x and y limits
    plt.xlim(0, width)
    plt.ylim(0, height)
    # Add labels and legend
    plt.xlabel('X (pixels)')
    plt.ylabel('Y (pixels)')
    plt.legend()
    plt.title(title1 + " and " + title2)
    # Plot the scatter points
    plt.show()

#Plots the 3D trackbox coordinate data 
def plot_trackbox_data(interpolated_data, title, origin, origin2):
    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    mx, my, mz, intx, inty, intz = [], [], [], [], [], []
    for gaze_data in interpolated_data:
        tempx2, tempy2, tempz2 = gaze_data[origin]
        if not np.isnan(tempx2) and not np.isnan(tempy2) and not np.isnan(tempz2):
            mx.append(tempx2)
            my.append(tempy2)
            mz.append(tempz2)
        try:
            tempx, tempy, tempz = gaze_data[origin2]
            if not np.isnan(tempx) and not np.isnan(tempy) and not np.isnan(tempz):
                intx.append(tempx)
                inty.append(tempy)
                intz.append(tempz)
        except KeyError:
            continue
    
    # Plot the coordinates
    ax.scatter(intx, inty, intz, color='red', label = 'Interpolated')
    ax.scatter(mx, my, mz, color = 'gray', label = 'Dominant Eye')

    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)

    # Combine both sets of points
    x = np.concatenate([intx, mx])
    y = np.concatenate([inty, my])
    z = np.concatenate([intz, mz])

    # Set the same scaling for all axes
    max_range = np.max([x.max() - x.min(), y.max() - y.min(), z.max() - z.min()])
    mid_x = (x.max() + x.min()) * 0.5
    mid_y = (y.max() + y.min()) * 0.5
    mid_z = (z.max() + z.min()) * 0.5
    ax.set_xlim(mid_x - max_range * 0.5, mid_x + max_range * 0.5)
    ax.set_ylim(mid_y - max_range * 0.5, mid_y + max_range * 0.5)
    ax.set_zlim(mid_z - max_range * 0.5, mid_z + max_range * 0.5)

    # Show the plot
    ax.legend()
    plt.show()

#flips the directionality of a set of coordinates, this is done to match screen coordinates, whose y increases as you move down the screen and the matplotlib, whose y decreases as you move down 
def flip_y(cen_y):
    newList = []
    for y in cen_y:
        newList.append(height - y)
    return newList

def convex_hull_plot(centroid_data, title, image_path):
    convex_list = []
    plot_number = 1  # Counter for plot numbers

    # Load the image
    img = mpimg.imread(image_path)

    for centroid in centroid_data:
        x_adj = [value for value in centroid.x]
        y = [value for value in centroid.y]
        y_adj = flip_y(y)
        points = list(zip(x_adj, y_adj))
        if len(points) > 3:
            convex_list.append(ConvexHull(points))

    # Plotting convex hulls with the image as the background
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0, width, 0, height])

    for hull in convex_list:
        ax.plot(hull.points[:, 0], hull.points[:, 1], 'o')
        for simplex in hull.simplices:
            ax.plot(hull.points[simplex, 0], hull.points[simplex, 1], 'k-')

        # Add plot number as text annotation
        centroid = hull.points.mean(axis=0)
        ax.text(centroid[0], centroid[1], str(plot_number), ha='center', va='center')
        plot_number += 1

    plt.title(title)
    # Set the x and y limits
    plt.xlim(0, width)
    plt.ylim(0, height)
    plt.xlabel('X (pixels)')
    plt.ylabel('Y (pixels)')
    plt.show()

    return convex_list

def is_within_boundary(x, y, boundary):
    x_min, y_min, x_max, y_max = boundary
    return x_min <= x <= x_max and y_min <= y <= y_max

def check_in_bounds(x, y):
    areas_of_interest = [
        [0, 0, 1200, 50], #taskbar
        [0, 50, 1200, 140], #footer bar
        [265, 180, 715, 1080], #left column
        [730, 233, 1635, 477], #bottom right box
        [730, 493, 1635, 1080], #top right box
    ]
    area_names = [
        "Taskbar",
        "Footer Bar",
        "Left Column",
        "Bottom Right Box",
        "Top Right Box"
    ]
    for aoi, name in zip(areas_of_interest, area_names):
        if is_within_boundary(x, y, aoi):
            #print(x, y)
            print(name)
            return name, aoi
        

#  returns the AOI coordinates based on a series of x and y data, two std long for each axis 
def calculate_aoi(x_data, y_data, std_dev=2):

    mean_x, mean_y = np.mean(x_data), np.mean(y_data)
    std_x, std_y = np.std(x_data), np.std(y_data)

    aoi_x_min = mean_x - std_dev * std_x
    aoi_x_max = mean_x + std_dev * std_x
    aoi_y_min = mean_y - std_dev * std_y
    aoi_y_max = mean_y + std_dev * std_y
    
    return {
        "x_min": aoi_x_min,
        "x_max": aoi_x_max,
        "y_min": aoi_y_min,
        "y_max": aoi_y_max
        }

        
def extend_and_crop_image(image_path, aoi_coordinates):
   

    img = mpimg.imread(image_path)
    
    img_height, img_width, _ = img.shape
    
    # #Create a new figure for the full screen size and plot the image using 'extent'
    # fig, ax = plt.subplots(figsize=(screen_width / 100, screen_height / 100))  # Adjust size for screen resolution
    # ax.imshow(img, extent=[0, screen_width, 0, screen_height])
    
    # # Save the extended image from the figure into a NumPy array
    # ax.axis('off') 
    # fig.canvas.draw() 
    # extended_image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    # extended_image = extended_image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    # plt.close(fig)  
    
    x_min, y_min, x_max, y_max = [int(val) for val in aoi_coordinates]

    # Crop the extended image: extended_image[y_min:y_max, x_min:x_max]
    cropped_img = img[y_min:y_max, x_min:x_max]

    return cropped_img



def serv():
    '''# Set up the server
    HOST = 'localhost'
    PORT = 80 
    # Create a socket object, bind it, and listen for connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print('Server is listening on {}:{}'.format(HOST, PORT))

    # Accept a client connection
    client_socket, client_address = server_socket.accept()
    print('Connected to client:', client_address)'''

    # Send eye tracking data to the client
    centroids = [(1, 2), (3, 4), (5, 6)]  # Replace with your actual centroid data
    data = json.dumps(centroids)
    #for centroid in centroids:
        # Convert the centroid data to a string
        #data = '{} {}'.format(centroid[0], centroid[1])
        #print('Sending data:', data)
        #data_list.append(data)

        # Send the data to the client
        #client_socket.sendall(data.encode())

    # Create an HTTP connection to the web server
    conn = http.client.HTTPConnection("127.0.0.1", 8000)

    # Define the HTTP headers and send the data as a POST request
    headers = {'Content-type': 'application/json'}
    conn.request("POST", "/eye-tracking-data", data, headers)
    response = conn.getresponse()

    # Check if the data was successfully sent
    if response.status == 200:
        print('Data sent successfully to the web server')
    else:
        print('Failed to send data to the web server')

    # Close the HTTP connection and the client connection
    conn.close()
    #client_socket.close()
    #server_socket.close()
    print('Connection closed')

def serv2():
    # Set up the server
    '''HOST = 'localhost'
    PORT = 8000

    # Create a socket object, bind it, and listen for connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print('Server is listening on {}:{}'.format(HOST, PORT))

    # Accept a client connection
    client_socket, client_address = server_socket.accept()
    print('Connected to client:', client_address)

    # Send eye tracking data to the client
    centroids = 'centroid data here'#[(1, 2), (3, 4), (5, 6)]  # Replace with your actual centroid data
    data = json.dumps(centroids)  # Convert centroids to JSON

    # Close the connection to the client
    client_socket.close()
    server_socket.close()
    print('Connection closed')'''

    url = 'http://localhost:8080'
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data='test', headers=headers)

    if response.status_code == 200:
        print('Data sent successfully to the web server')
    else:
        print('Failed to send data to the web server')

def serv3():
    url = 'http://localhost:8000/'
    query = {'data': 'test'}
    res = requests.post(url, data=query)
    print('res', res.text)

def serv4():
    
    data_to_send = {"x": 500, "y": 500}
   
    app = Flask(__name__)

    # Route to serve the webpage
    @app.route('/')
    def serve_webpage():
       return render_template('web.html', data = data_to_send)

    # Route to handle the data received from the webpage
    @app.route('/data', methods=['GET'])
    def get_data():
        return jsonify(data_to_send)

    if __name__ == '__main__':
        app.run(debug=True, threaded=True)

received_container_data = []

# WebSocket server function that sends real-time eye-tracking data to web.html and receive "w3-container" id, not generalizable to other html structures
async def websocket_server(websocket, path):
    global data_to_send 
    while True:
        try:
            #send 
            await websocket.send(f"{data_to_send}")   

            #receive
            message = await websocket.recv()  
            data = json.loads(message)
           
            container_id = data.get('container_id')
            if container_id:
                received_container_data.append(container_id)
                print(f"WebSocket Server: Received container ID: {container_id}")
                
            await asyncio.sleep(1)  # Send updates every 1 second
        except websockets.ConnectionClosed:
            print("Client disconnected")
            break


SAVE_DIR = 'screenshots'
os.makedirs(SAVE_DIR, exist_ok=True)

# save html screenshot
def save_screenshot(image_data, filename):

    image_data = image_data.split(",")[1]
    image_bytes = base64.b64decode(image_data)
    with open(os.path.join(SAVE_DIR, filename), "wb") as f:
        f.write(image_bytes)


# receive web.html screenshot
async def receive_messages(websocket):
    i = 1
    while True:
        try:       
            message = await websocket.recv()
            data = json.loads(message)

            if 'screenshot' in data:
                print("Screenshot received")
                save_screenshot(data['screenshot'], f"screenshot_{i}.png")
                print(f"Screenshot saved as screenshot_{i}.png")
                #caption_image(image_path= f"screenshots/screenshot_{i}.png")
                 # Add a delay to make sure the image is fully written 
                time.sleep(0.5)  

                # Check if the image is valid 
                try:
                    with Image.open(os.path.join(SAVE_DIR, f"screenshot_{i}.png")) as img:
                        img.verify() 

                    caption_image(image_path=os.path.join(SAVE_DIR, f"screenshot_{i}.png"))
                except (UnidentifiedImageError, FileNotFoundError) as e:
                    print(f"Error opening image screenshot_{i}.png: {e}")

                
                i = i + 1

        except websockets.ConnectionClosed:
            print("Client disconnected")
            break

# collect data for 10 seconds and send AOI to web.html
async def websocket_server_aoi(websocket):
    global data_to_send
    collected_gaze_data = []

    start_time = time.time()
    while True:
        try:
            current_time = time.time()

            if current_time - start_time < 10: # change if want to collect data for a different range of time
                collected_gaze_data.append((data_to_send["x"], data_to_send["y"]))
                print(f"Collected: {data_to_send}")
                # seems not working here so created receive_messages
                # message = await websocket.recv()
                # data = json.loads(message)

                # if 'screenshot' in data:
                #     # Save the screenshot received from the client
                #     print("Screenshot received")
                #     save_screenshot(data['screenshot'], "screenshot.png")
                #     print("Screenshot saved as screenshot.png")
                await asyncio.sleep(1)  # Sleep for 1 second (same rate as updates)
            else:
                x_data = [point[0] for point in collected_gaze_data]
                y_data = [point[1] for point in collected_gaze_data]

                aoi_result = calculate_aoi(x_data, y_data)

                await websocket.send(json.dumps(aoi_result))
                print("Sent AOI result to client:", aoi_result)

                # reset timer every 10 seconds
                start_time = time.time()
                collected_gaze_data = []
            
        except websockets.ConnectionClosed:
            print("Client disconnected")
            break


# runs both send and receive aoi
async def websocket_handler(websocket, path):
    await asyncio.gather(
        websocket_server_aoi(websocket),
        receive_messages(websocket)
    )

# start the WebSocket server on localhost 9000, check if socket is listening on 9000 by netstat -aon |findstr 9000 check if there are things on  a port

def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(websocket_handler, "localhost", 9000)
    print("server started")
    loop.run_until_complete(start_server)
    loop.run_forever()


def run_plots_csv():
    global centroid_data, left_x, left_y, right_x, right_y, inter_x, inter_y
    left_x = [gaze_data['left_gaze_point_on_display_area'][0] for gaze_data in gaze_data_list]
    left_y = [gaze_data['left_gaze_point_on_display_area'][1] for gaze_data in gaze_data_list]
    right_x = [gaze_data['right_gaze_point_on_display_area'][0] for gaze_data in gaze_data_list]
    right_y = [gaze_data['right_gaze_point_on_display_area'][1] for gaze_data in gaze_data_list]
    inter_x = [gaze_data['inter_gaze_point_on_display_area'][0] for gaze_data in gaze_data_list if 'inter_gaze_point_on_display_area' in gaze_data]
    inter_y = [gaze_data['inter_gaze_point_on_display_area'][1] for gaze_data in gaze_data_list if 'inter_gaze_point_on_display_area' in gaze_data]
    left_y, right_y, inter_y = flip_y(left_y), flip_y(right_y), flip_y(inter_y)
    draw_unfiltered('Unfiltered', 'images/test.png')
    # C:\Users\erynm\Downloads\mixed-ability-collab\eye_tracking\Tobii\images\test.png
    for value in centroid_data:
        coords_x, coords_y = value.coords()
        centroids_x.append(coords_x)
        centroids_y.append(coords_y)
    newY = flip_y(centroids_y)
    graph(centroids_x, newY, 'Centroids', 'images/test.png')
    convex_hull_plot(centroid_data, 'Convex Hull', 'images/test.png')
    write_to_csv(gaze_data_list, centroid_data)
    #interpolatedData, centroidData = apply_ivt_filter(dominantEye)
    #left_y, right_y, inter_y = flip_y(left_y), flip_y(right_y), flip_y(inter_y)
    #draw_unfiltered('Unfiltered', 'images/test.png')

# run_eyetracker(5)
# thread1 = threading.Thread(target=serv4)
#start_websocket_server()

#thread2 = threading.Thread(target=run_eyetracker(50))

# # Start the threads
# thread1 = threading.Thread(target=start_websocket_server) #comment out these two lines only
# thread1.start()
#thread2.start()
print("gonna start eye tracker")
print("start time",int(time.time()))
run_eyetracker(180)
print("end time",int(time.time()))

# # Wait for both threads to finish
# thread1.join()
# thread2.join()

print("Both functions have completed.")
run_plots_csv()
#Instructions for running in a local server:
#1. Open a terminal and start a local server using the command "python -m http.server"
#2. Open a second terminal and run this file
#3. Refresh the webpage and the server should run as expected