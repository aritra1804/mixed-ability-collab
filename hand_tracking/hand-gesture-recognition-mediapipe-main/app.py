#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Thread
from sympy import Point3D, Line3D,Plane
import os
import csv
import math
import copy
import argparse
import itertools
from collections import Counter
from collections import deque

import cv2 as cv
import numpy as np
import mediapipe as mp
import pykinect_azure as pykinect

from utils import CvFpsCalc
from model import KeyPointClassifier
from model import PointHistoryClassifier

from queue import Queue

# hardware specifications
# DELL U2415 monitor:
# screen dimensions without bezel, width = 517 mm, height = 323 mm
# azure kinect dk camera (https://learn.microsoft.com/en-us/azure/kinect-dk/hardware-specification):
# from center of depth camera to bottom: 21.3 mm 
# from center of depth camera to top of monitor screen (exclusing bezel): 27 mm
top_left_coords = (258.5,27,0)
top_right_coords = (-258.5,27,0)
screen_width = 323 # in mm
screen_height = 517 # in mm
titled_angle = 6 # measured by Digital Angle Gauge in degrees
# initialize a queue both threads can read and write to
joint_queue = Queue(maxsize=1)  

def py_azure_kinect():
    """
    Initialize and configure the Azure Kinect sensor and body tracking for joint location tracking.

    This function initializes the necessary libraries for Azure Kinect and starts the device
    with specific camera configurations for joint location tracking. It continuously captures
    and processes data from the sensor to obtain joint positions of human bodies detected
    by the Azure Kinect body tracker.

    Note:
        This function requires the 'pykinect' library, which provides Python bindings
        for the Azure Kinect SDK.

    Returns:
        None: This function runs indefinitely and does not return a value. But joint_info
        is added to the joint_queue for the main thread to read in mediapipe().

    Usage:
        To use this function, ensure that the 'pykinect' library is installed and
        the required DLL files (k4a.dll and k4abt.dll) are provided as arguments
        to 'pykinect.initialize_libraries()' before calling this function.
    """
    # Initialize the library, if the library is not found, add the library path as argument
    pykinect.initialize_libraries(
        module_k4a_path="C:\\Users\\jbartsch\Desktop\mediapipe_azure_kinect_combined_hand_tracking-main\\Azure Kinect SDK v1.4.1\\sdk\\windows-desktop\\amd64\\release\\bin\\k4a.dll",
        module_k4abt_path="C:\\Users\\jbartsch\\Desktop\\mediapipe_azure_kinect_combined_hand_tracking-main\\kinect_bt_sdk v.1.1.2\\windows-desktop\\amd64\\release\\bin\\k4abt.dll",
        track_body=True,
    )

    # Modify camera configuration
    device_config = pykinect.default_configuration
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_OFF
    device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED
    # print(device_config)

    # Start device
    device = pykinect.start_device(config=device_config)
    # Start body tracker
    bodyTracker = pykinect.start_body_tracker()

    # cv.namedWindow('Depth image with skeleton',cv.WINDOW_NORMAL)

    while True:
        # following code is used for getting joint locations
        # Get capture
        capture = device.update()

        # Get body tracker frame
        body_frame = bodyTracker.update()

        # Access attributes of body_frame
        if body_frame is not None:
            num_bodies = body_frame.get_num_bodies()
            for i in range(num_bodies):
                body = body_frame.get_body(i)
                # Access joints of the body
                joint_info = [] # list of two tups, first one is wrist and second is index_tip right
                for joint in body.joints:
                    # joint.id starts from 0 and goes up
                    if joint.id in {14, 16}:  # 16 is tip of index finger
                        joint_info.append(
                            (
                                joint.id,
                                joint.position.x,
                                joint.position.y,
                                joint.position.z,
                            )
                        )
                        # print('joint_info:',joint_info)
                    elif joint.id > 16: # skip over the rest of joints
                        joint_queue.put(joint_info)
                        # print("new loc added to joint_queue!")
                        # print(type(joint))
                        # https://learn.microsoft.com/en-us/azure/kinect-dk/body-joints
                        # 14 is WRIST_RIGHT, 15 is HAND_RIGHT, 16 is HANDTIP_RIGHT
                        # Print joint information

def find_third_point_on_tilted_screen(point1,width,angle):
    """
    Given the top left point on a tilted screen, find the bottom left point on the screen
    based on the titled angle of the screen and width of the screen.
    """
    angle_in_radians = math.radians(angle)
    # print(math.sqrt(math.pow(500,2)-math.pow(250,2))+20)
    return (point1[0],point1[1]+width*math.cos(angle_in_radians),point1[2]+width*math.sin(angle_in_radians))

def get_all_plane_points(point1,point2,width,angle):
    """
    Given the top left and top right points on a tilted screen, find the bottom left and
    bottom right points on the screen based on the width and the titled angle of the screen.
    """
    point3 = find_third_point_on_tilted_screen(point1,width,angle)
    point4 = find_third_point_on_tilted_screen(point2,width,angle)
    return [point1,point2,point3,point4]

def intersect_line_plane(plane_points, line_point1, line_point2):
    """
    Compute the intersection point between a line and a plane in 3D space.

    Parameters:
        plane_points (list or array-like): Three points defining the plane in 3D space.
        line_point1 (list or array-like): The first point on the line in 3D space.
        line_point2 (list or array-like): The second point on the line in 3D space.

    Returns:
        numpy.ndarray or None: If the line intersects the plane, returns the intersection point as a NumPy array.
        If the line is parallel to the plane, returns None.
    """
    
    # Convert the points to NumPy arrays for vector operations
    plane_points = np.array(plane_points)
    line_point1 = np.array(line_point1)
    line_point2 = np.array(line_point2)

    # Calculate the normal vector of the plane using the cross product of two vectors in the plane
    plane_normal = np.cross(plane_points[1] - plane_points[0], plane_points[2] - plane_points[0])

    # Calculate the direction vector of the line
    line_direction = line_point2 - line_point1

    # Check if the line is parallel to the plane (dot product of the line direction and plane normal is zero)
    if np.dot(line_direction, plane_normal) == 0:
        return None  # The line is parallel to the plane, no intersection

    # Calculate the distance from line_point1 to the plane
    t = np.dot(plane_points[0] - line_point1, plane_normal) / np.dot(line_direction, plane_normal)

    # Calculate the intersection point
    intersection_point = line_point1 + t * line_direction

    return intersection_point 


def mediapipe():

    def get_args():
        parser = argparse.ArgumentParser()

        parser.add_argument("--device", type=int, default=0)
        parser.add_argument("--width", help='cap width', type=int, default=960)
        parser.add_argument("--height", help='cap height', type=int, default=540)

        parser.add_argument('--use_static_image_mode', action='store_true')
        parser.add_argument("--min_detection_confidence",
                            help='min_detection_confidence',
                            type=float,
                            default=0.7)
        parser.add_argument("--min_tracking_confidence",
                            help='min_tracking_confidence',
                            type=int,
                            default=0.5)

        args = parser.parse_args()

        return args


    def main():

        # Argument parsing #################################################################
        args = get_args()
        # print('arg',args)
        cap_device = args.device
        cap_width = args.width # same as image.width and image.height
        cap_height = args.height

        use_static_image_mode = args.use_static_image_mode
        min_detection_confidence = args.min_detection_confidence
        min_tracking_confidence = args.min_tracking_confidence

        use_brect = True

        # Camera preparation ###############################################################
        cap = cv.VideoCapture(cap_device)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

        # Model load #############################################################
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=use_static_image_mode,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        keypoint_classifier = KeyPointClassifier()

        point_history_classifier = PointHistoryClassifier()

        # Read labels ###########################################################
        with open('model/keypoint_classifier/keypoint_classifier_label.csv',
                encoding='utf-8-sig') as f:
            keypoint_classifier_labels = csv.reader(f)
            keypoint_classifier_labels = [
                row[0] for row in keypoint_classifier_labels
            ]
        with open(
                'model/point_history_classifier/point_history_classifier_label.csv',
                encoding='utf-8-sig') as f:
            point_history_classifier_labels = csv.reader(f)
            point_history_classifier_labels = [
                row[0] for row in point_history_classifier_labels
            ]

        # FPS Measurement ########################################################
        cvFpsCalc = CvFpsCalc(buffer_len=10)

        # Coordinate history #################################################################
        history_length = 16
        point_history = deque(maxlen=history_length)

        # Finger gesture history ################################################
        finger_gesture_history = deque(maxlen=history_length)

        #  ########################################################################
        mode = 0

        csv_file_path = "intersection_points.csv"  # Replace with your desired CSV file path
        fieldnames = ['intersection_x', 'intersection_y', 'intersection_z'] 
        # create a csv file with the fieldnames. this will overwrite any existing data in the csv file
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

        while True:

            fps = cvFpsCalc.get()

            # Process Key (ESC: end) #################################################
            key = cv.waitKey(10)
            if key == 27:  # ESC
                break
            number, mode = select_mode(key, mode)

            # Camera capture #####################################################
            ret, image = cap.read()
            if not ret:
                break
            image = cv.flip(image, 1)  # Mirror display
            debug_image = copy.deepcopy(image)

            # Detection implementation #############################################################
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True

            #  ####################################################################
            if results.multi_hand_landmarks is not None:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                    results.multi_handedness):
                    # Bounding box calculation
                    brect = calc_bounding_rect(debug_image, hand_landmarks)
                    # Landmark calculation
                    landmark_list = calc_landmark_list(debug_image, hand_landmarks)

                    # Conversion to relative coordinates / normalized coordinates
                    pre_processed_landmark_list = pre_process_landmark(
                        landmark_list)
                    pre_processed_point_history_list = pre_process_point_history(
                        debug_image, point_history)
                    # Write to the dataset file
                    logging_csv(number, mode, pre_processed_landmark_list,
                                pre_processed_point_history_list)

                    # Hand sign classification
                    hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                    if hand_sign_id == 2:  # Point gesture
                        point_history.append(landmark_list[8])

                        # Output Location of joints of index finger only when pointing

                        # Assuming 'image' is the NumPy array representing the image
                        # image_height, image_width, _ = image.shape # 3rd value is # of color channels, rgb -> 3

                        # print("Image Width (Pixels):", image_width) # 1290 for azure kinect rgb camera
                        # print("Image Height (Pixels):", image_height) # 720 for azure kinect rgb camera

                        ## CALCULATIONS FOR METACARPOPHALANGEAL JOINT ##
                        # Top left corner is where (x,y) is (0,0) ************
                        # Get the x, y, and z coordinates of the landmarks with indices 0, 5, and 8
                        # 0 WRIST
                        # 5 INDEX_FINGER_MCP
                        # 8 INDEX_FINGER_TIP
                        x_0, y_0, z_0 = landmark_list[0][0], landmark_list[0][1], hand_landmarks.landmark[0].z
                        x_5, y_5, z_5 = landmark_list[5][0], landmark_list[5][1], hand_landmarks.landmark[5].z
                        x_8, y_8, z_8 = landmark_list[8][0], landmark_list[8][1], hand_landmarks.landmark[8].z
                        
                        # Notice that in this code, x and y coordinates represent pixe locations in the image,
                        # and z coordinate represents the landmark depth, with the depth at the wrist being the origin
                        # print(f"Landmark 0: x={x_0}, y={y_0}, z={z_0}")
                        # print(f"Landmark 5: x={x_5}, y={y_5}, z={z_5}")
                        # print(f"Landmark 8: x={x_8}, y={y_8}, z={z_8}")

                        # Print the coordinates
                        # check https://developers.google.com/mediapipe/solutions/vision/gesture_recognizer#hand_landmark_model_bundle
                        # for which joints this is outputting

                        # print("REACHED HERE!")
                        # add a timer here 
                        # latency (loop time) 2 to 3 frames per second + time to the first number (delay?)
                        if not joint_queue.empty():
                            joint_info = joint_queue.get() # see detail of joint_info in py_azure_kinect
                            # print('Retrieved Joint Info!!!')
                            # print('Retrieved Joint Info:',joint_info)

                            _, wrist_x, wrist_y, wrist_z = joint_info[0]
                            _, tip_x, tip_y, tip_z = joint_info[1]

                            # print('real wrist location:',joint_info[0])
                            # # print('calculated tip','x:',wrist_x/x_0*x_8,'y:',wrist_y/y_0*y_8)
                            # print('real tip location:',joint_info[1])
                            # print('                        tip to wrist distance in mm:',math.sqrt(pow(wrist_x-tip_x,2)+pow(wrist_y-tip_y,2)+pow(wrist_z-tip_z,2)))
                            # print(f"normalized wrist loc: x={x_0}, y={y_0}, z={z_0}")
                            # print(f"normalized tip loc: x={x_8}, y={y_8}, z={z_8}")

                            # formula to calculate depth of the matecarpophalangeal joint: *important
                            # (tip_z - wrist_z)/(z_8-z_0) = (mcp_z-wrist_z)/(z_5-z_0)
                            # therefore, mcp_z = (tip_z - wrist_z)/(z_8-z_0)*(z_5-z_0) + wrist_z
                            mcp_x, mcp_y, mcp_z = (tip_x/x_8)*x_5, (tip_y/y_8)*y_5, (tip_z-wrist_z)/(z_8-z_0)*(z_5-z_0)+wrist_z

                            # print('calculated mcp loc:',mcp_x,mcp_y,mcp_z)
                            # print('           distance btw mcp and wrist',math.sqrt(pow(wrist_x-mcp_x,2)+pow(wrist_y-mcp_y,2)+pow(wrist_z-mcp_z,2)))
                            # mcp_x, mcp_y, mcp_z = (tip_x/x_8)*x_5, (tip_y/y_8)*y_5, (tip_z/z_8)*z_5
                            # finger_direction = [tip_x - mcp_x, tip_y - mcp_y, tip_z - mcp_z]
                            # print('Tip:',tip_x,tip_y,tip_z)
                            # print('mcp:',mcp_x,mcp_y,mcp_z)
                            # print('finger direction:',finger_direction)
                            # intersection_point = isect_line_plane_v3([tip_x,tip_y,tip_z],[mcp_x,mcp_y,mcp_z],point4,normal_vector)

                            # Define the points that form the plane
                            plane_points = get_all_plane_points(top_left_coords,top_right_coords,screen_width,titled_angle)
                            print('plane points:',plane_points)
                            # plane_points = [
                            #     (258.5, 348.23057220395225, 33.762693635452074),
                            #     (-258.5, 348.23057220395225, 33.762693635452074),
                            #     (258.5, 27, 0),
                            #     (-258.5, 27, 0)
                            # ]

                            # Define the two points that form the line
                            index_tip_coords = (tip_x, tip_y, tip_z)  # Replace with the actual values of a, b, and c
                            mcp_coords = (mcp_x, mcp_y, mcp_z)  # Replace with the actual values of x, y, and z

                            # Calculate the intersection point
                            intersection_point = intersect_line_plane(plane_points, index_tip_coords, mcp_coords)
                            # print('mcp:',mcp_coords)
                            # print('index_tip:',index_tip_coords)
                            print('intersection point:',intersection_point)
                            # Append the intersection_point to the CSV file
                            with open(csv_file_path, mode='a', newline='') as csv_file:
                                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                                # if intersection_point is not None and -258.5 <= intersection_point[0] <= 258.5 and 27 <= intersection_point[1] <= 348.23057220395225 and 0 <= intersection_point[2] <= 33.762693635452074:  # Check if the point is within the plane
                                writer.writerow({'intersection_x': intersection_point[0], 'intersection_y': intersection_point[1], 'intersection_z': intersection_point[2]})
                            # indicate processing is complete for this item
                            joint_queue.task_done()


                    else:
                        point_history.append([0, 0])

                    # Finger gesture classification
                    finger_gesture_id = 0
                    point_history_len = len(pre_processed_point_history_list)
                    if point_history_len == (history_length * 2):
                        finger_gesture_id = point_history_classifier(
                            pre_processed_point_history_list)

                    # Calculates the gesture IDs in the latest detection
                    finger_gesture_history.append(finger_gesture_id)
                    most_common_fg_id = Counter(
                        finger_gesture_history).most_common()

                    # Drawing part
                    debug_image = draw_bounding_rect(use_brect, debug_image, brect)
                    debug_image = draw_landmarks(debug_image, landmark_list)
                    debug_image = draw_info_text(
                        debug_image,
                        brect,
                        handedness,
                        keypoint_classifier_labels[hand_sign_id],
                        point_history_classifier_labels[most_common_fg_id[0][0]],
                    )
                    

            else:
                point_history.append([0, 0])

            debug_image = draw_point_history(debug_image, point_history)
            debug_image = draw_info(debug_image, fps, mode, number)

            # Screen reflection #############################################################
            # imageSize = cv.resize(image, (1920, 1200))  
            # cv.imshow('Hand Gesture Recognition', imageSize)
            cv.imshow('Hand Gesture Recognition', debug_image)


    def select_mode(key, mode):
        number = -1
        if 48 <= key <= 57:  # 0 ~ 9
            number = key - 48
        if key == 110:  # n
            mode = 0
        if key == 107:  # k
            mode = 1
        if key == 104:  # h
            mode = 2
        return number, mode


    def calc_bounding_rect(image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        landmark_array = np.empty((0, 2), int)

        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)

            landmark_point = [np.array((landmark_x, landmark_y))]

            landmark_array = np.append(landmark_array, landmark_point, axis=0)

        x, y, w, h = cv.boundingRect(landmark_array)

        return [x, y, x + w, y + h]


    def calc_landmark_list(image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        landmark_point = []

        # Keypoint
        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            landmark_z = landmark.z

            landmark_point.append([landmark_x, landmark_y])

        return landmark_point


    def pre_process_landmark(landmark_list):
        temp_landmark_list = copy.deepcopy(landmark_list)

        # Convert to relative coordinates
        base_x, base_y = 0, 0
        for index, landmark_point in enumerate(temp_landmark_list):
            if index == 0:
                base_x, base_y = landmark_point[0], landmark_point[1]

            temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
            temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

        # Convert to a one-dimensional list
        temp_landmark_list = list(
            itertools.chain.from_iterable(temp_landmark_list))

        # Normalization
        max_value = max(list(map(abs, temp_landmark_list)))

        def normalize_(n):
            return n / max_value

        temp_landmark_list = list(map(normalize_, temp_landmark_list))

        return temp_landmark_list


    def pre_process_point_history(image, point_history):
        image_width, image_height = image.shape[1], image.shape[0]

        temp_point_history = copy.deepcopy(point_history)

        # Convert to relative coordinates
        base_x, base_y = 0, 0
        for index, point in enumerate(temp_point_history):
            if index == 0:
                base_x, base_y = point[0], point[1]

            temp_point_history[index][0] = (temp_point_history[index][0] -
                                            base_x) / image_width
            temp_point_history[index][1] = (temp_point_history[index][1] -
                                            base_y) / image_height

        # Convert to a one-dimensional list
        temp_point_history = list(
            itertools.chain.from_iterable(temp_point_history))

        return temp_point_history


    def logging_csv(number, mode, landmark_list, point_history_list):
        if mode == 0:
            pass
        if mode == 1 and (0 <= number <= 9):
            csv_path = 'model/keypoint_classifier/keypoint.csv'
            with open(csv_path, 'a', newline="") as f:
                writer = csv.writer(f)
                writer.writerow([number, *landmark_list])
        if mode == 2 and (0 <= number <= 9):
            csv_path = 'model/point_history_classifier/point_history.csv'
            with open(csv_path, 'a', newline="") as f:
                writer = csv.writer(f)
                writer.writerow([number, *point_history_list])
        return


    def draw_landmarks(image, landmark_point):
        if len(landmark_point) > 0:
            # Thumb
            cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[3]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[3]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[3]), tuple(landmark_point[4]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[3]), tuple(landmark_point[4]),
                    (255, 255, 255), 2)

            # Index finger
            cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[6]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[6]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[6]), tuple(landmark_point[7]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[6]), tuple(landmark_point[7]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[7]), tuple(landmark_point[8]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[7]), tuple(landmark_point[8]),
                    (255, 255, 255), 2)

            # Middle finger
            cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[10]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[10]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[10]), tuple(landmark_point[11]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[10]), tuple(landmark_point[11]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[11]), tuple(landmark_point[12]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[11]), tuple(landmark_point[12]),
                    (255, 255, 255), 2)

            # Ring finger
            cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[14]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[14]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[14]), tuple(landmark_point[15]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[14]), tuple(landmark_point[15]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[15]), tuple(landmark_point[16]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[15]), tuple(landmark_point[16]),
                    (255, 255, 255), 2)

            # Little finger
            cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[18]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[18]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[18]), tuple(landmark_point[19]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[18]), tuple(landmark_point[19]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[19]), tuple(landmark_point[20]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[19]), tuple(landmark_point[20]),
                    (255, 255, 255), 2)

            # Palm
            cv.line(image, tuple(landmark_point[0]), tuple(landmark_point[1]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[0]), tuple(landmark_point[1]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[1]), tuple(landmark_point[2]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[1]), tuple(landmark_point[2]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[5]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[5]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[9]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[9]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[13]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[13]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[17]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[17]),
                    (255, 255, 255), 2)
            cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[0]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[0]),
                    (255, 255, 255), 2)

        # Key Points
        for index, landmark in enumerate(landmark_point):
            if index == 0:  # 手首1 Same as WRIST_RIGHT in Azure Kinect
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 1:  # 手首2
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 2:  # 親指：付け根
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 3:  # 親指：第1関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 4:  # 親指：指先
                cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
            if index == 5:  # 人差指：付け根
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 6:  # 人差指：第2関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 7:  # 人差指：第1関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 8:  # 人差指：指先
                cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
            if index == 9:  # 中指：付け根
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 10:  # 中指：第2関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 11:  # 中指：第1関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 12:  # 中指：指先
                cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
            if index == 13:  # 薬指：付け根
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 14:  # 薬指：第2関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 15:  # 薬指：第1関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 16:  # 薬指：指先
                cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
            if index == 17:  # 小指：付け根
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 18:  # 小指：第2関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 19:  # 小指：第1関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 20:  # 小指：指先
                cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                        -1)
                cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)

        return image


    def draw_bounding_rect(use_brect, image, brect):
        if use_brect:
            # Outer rectangle
            cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]),
                        (0, 0, 0), 1)

        return image


    def draw_info_text(image, brect, handedness, hand_sign_text,
                    finger_gesture_text):
        cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22),
                    (0, 0, 0), -1)

        info_text = handedness.classification[0].label[0:]
        if hand_sign_text != "":
            info_text = info_text + ':' + hand_sign_text
        cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
                cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)

        if finger_gesture_text != "":
            cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                    cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv.LINE_AA)
            cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                    cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2,
                    cv.LINE_AA)

        return image


    def draw_point_history(image, point_history):
        for index, point in enumerate(point_history):
            if point[0] != 0 and point[1] != 0:
                cv.circle(image, (point[0], point[1]), 1 + int(index / 2),
                        (152, 251, 152), 2)

        return image


    def draw_info(image, fps, mode, number):
        cv.putText(image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX,
                1.0, (0, 0, 0), 4, cv.LINE_AA)
        cv.putText(image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX,
                1.0, (255, 255, 255), 2, cv.LINE_AA)

        mode_string = ['Logging Key Point', 'Logging Point History']
        if 1 <= mode <= 2:
            cv.putText(image, "MODE:" + mode_string[mode - 1], (10, 90),
                    cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                    cv.LINE_AA)
            if 0 <= number <= 9:
                cv.putText(image, "NUM:" + str(number), (10, 110),
                        cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                        cv.LINE_AA)
        return image
    main()

# multi-threading to run two cameras concurrently
Thread(target = mediapipe).start()
Thread(target = py_azure_kinect).start() 


# if __name__ == '__main__':
#         point1 = (258.5,27,0)
#         # top right: 
#         point2 = (-258.5,27,0)
#         # find bottom left:
#         point3 = find_third_point_on_tilted_screen(point1,323,6)
#         # find bottom right:
#         point4 = find_third_point_on_tilted_screen(point2,323,6)
#         print(point3)
#         print(point4)
#     # main()
#     print(find_third_point_on_tilted_screen((-60,20,0),500,30))