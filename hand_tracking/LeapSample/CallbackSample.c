/**************************************************************************************
 * Leap Motion Hand Tracking Data to Screen Intersection - Example Code
 * Author: Yanzi (Veronica) Lin
 * Last Modified: July 2023
 *
 * This C code demonstrates how to use the Leap Motion SDK to track hand movements
 * and calculate the intersection of a pointing finger with a monitor screen.
 * The code reads hand tracking data from the Leap Motion device, identifies hand shapes,
 * and calculates the 3D position of the fingertip. If the hand is in the "Index-Point"
 * shape, the code calculates the intersection of the pointing finger with the 
 * monitor screen based on the known monitor position.
 *
 * Note: The code assumes that it is run with the Leap Tracking Software v.5.12 and that
 * the Leap Motion SDK is located in the Program Files/Ultraleap directory.
 *
 * Copyright (C) 2012-2017 Ultraleap Limited. All rights reserved.
 * Use of this code is subject to the terms of the Ultraleap SDK agreement available at
 * https://central.leapmotion.com/agreements/SdkAgreement unless Ultraleap has signed a
 * separate license agreement with you or your organization.
 *
 * This code is provided as an example and may require modifications or integration
 * into a larger project for practical use. For more information on using the Leap Motion
 * SDK, refer to the official documentation and SDK agreement available on the Ultraleap
 * website.
**************************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include "LeapC.h"
#include "ExampleConnection.h"
#include <errno.h>
#include <string.h>
#include <Windows.h> //Windows-specific functions for screen coordinate conversion

static LEAP_CONNECTION* connectionHandle;
static FILE* csvFile;
static errno_t err;

/** Callback for when the connection opens. */
static void OnConnect(void) {
    printf("Connected.\n");
}

/** Callback for when a device is found. */
static void OnDevice(const LEAP_DEVICE_INFO* props) {
    printf("Found device %s.\n", props->serial);
}

// Function to convert 3D position to screen coordinates
// 1. draw a vector between the direction point and the finger tip position
// 2. extend that vector in the 3D space
// 3. because we know where the monitor is, we find that piercing point


// Global variables for intersection coordinates
float intersectionX = 0.0f;
float intersectionY = 0.0f;
float intersectionZ = 0.0f;

/** Callback for when a frame of tracking data is available. */
static void OnFrame(const LEAP_TRACKING_EVENT* frame) {
    if (frame->info.frame_id % 60 == 0)
        printf("Frame %lli with %i hands.\n", (long long int)frame->info.frame_id, frame->nHands);

    for (uint32_t h = 0; h < frame->nHands; h++) {
        LEAP_HAND* hand = &frame->pHands[h];
        printf("    Hand id %i is a %s hand with position (%f, %f, %f).\n",
            hand->id,
            (hand->type == eLeapHandType_Left ? "left" : "right"),
            hand->palm.position.x,
            hand->palm.position.y,
            hand->palm.position.z);

        // digits are members of the LEAP_HAND struct
        LEAP_DIGIT thumb = hand->digits[0];
        LEAP_DIGIT index = hand->digits[1];
        LEAP_DIGIT middle = hand->digits[2];
        LEAP_DIGIT ring = hand->digits[3];
        LEAP_DIGIT pinky = hand->digits[4];


        // Determine hand shape based on grab strength and whether fingers are extended
        const char* handShape = "Unknown";
        
        if (index.is_extended && !thumb.is_extended && !middle.is_extended
            && !ring.is_extended && !hand->pinky.is_extended)
            handShape = "Index-Point";
        //&& !thumb.is_extended 
        //else if (hand->grab_strength > 0.8)
            //handShape = "Closed Fist";
        else if (index.is_extended && thumb.is_extended && middle.is_extended
            && ring.is_extended && hand->pinky.is_extended)
            // pointing w/ pinkie is open
            handShape = "Open";
        printf("    Hand shape: %s\n", handShape);

        // get finger tip position and the direction the finger points toward if index finger is pointing

        // Declare tipPosition, screenX, and screenY to write to file later
        LEAP_VECTOR tipPosition = { 0.0, 0.0, 0.0 };
        LEAP_VECTOR fingerDirection = { 0.0, 0.0, 0.0 };

        if (strcmp(handShape, "Index-Point") == 0) { // checking whether handShape is "Index-Point"
            //(handShape == "Index-Point")
            tipPosition = index.bones[3].next_joint;

            printf("    Pointing Finger Tip Position: (%f, %f, %f)\n",
                tipPosition.x,
                tipPosition.y,
                tipPosition.z);

            // Get the direction vector of the finger
            // Calculate the direction vector of the finger based on bone positions
            //LEAP_VECTOR proximalPosition = index.bones[1].prev_joint;
            // using intermediatePosition for now, need to test whether proximal gives more accurate direction
            LEAP_VECTOR intermediatePosition = index.bones[2].prev_joint;

            // prev joint of intermediate joint --> fingertip: direction vector
            //fingerDirection.x = tipPosition.x - intermediatePosition.x;
           // fingerDirection.y = tipPosition.y - intermediatePosition.y;
            //fingerDirection.z = tipPosition.z - intermediatePosition.z;

            // Calculate the direction vector of the finger based on bone positions
            LEAP_VECTOR proximalPosition = index.bones[1].prev_joint;

            // proximal joint --> fingertip: direction vector
            fingerDirection.x = tipPosition.x - proximalPosition.x;
            fingerDirection.y = tipPosition.y - proximalPosition.y;
            fingerDirection.z = tipPosition.z - proximalPosition.z;


            // start point: intermediatePosition
            // end point: tipPosition
            // parametrization of the line
            // x = tipPosition.x + t * fingerDirection.x
            // y = tipPosition.y + t * fingerDirection.y
            // z = tipPosition.z + t * fingerDirection.z

            // plane equation is z + 332 = 0 and plug in parametric form of the line, we get:
            float t = -(tipPosition.z + 332) / fingerDirection.z;

            float intersectionX = tipPosition.x + t * fingerDirection.x;
            float intersectionY = tipPosition.y + t * fingerDirection.y;
            float intersectionZ = tipPosition.z + t * fingerDirection.z;


            printf("    Pointing Finger Direction: (%f, %f, %f)\n",
                fingerDirection.x,
                fingerDirection.y,
                fingerDirection.z);

            /* Dell 24 inch E2423H monitor (without bezel) :
            * viewable size: 23.8 in
            * monitor width: 20.8 in/53 cm
            * monitor height: 11.6 in/29.5cm
            * distance between monitor and the red dot: 33.2 cm
            * distance between the desk and bottom of the screen: 11.2 cm
            * lower left: A = (-265, 112, -332)
            * lower right: B = (265, 112, -332)
            * upper left: C = (-265, 398, -332)
            * upper right: D = (265, 398, -332)
            * top y: 384
            * bottom y:
            */

            // calculate equation of the plane
            // correct equation of the plane: z + 332 = 0

            /*
            // given the direction vector of index finger + plane, find intersection
            float extensionFactor = -300.0; // Distance from the controller to the monitor screen
            // Calculate the extended finger vector
            LEAP_VECTOR extendedFingerVector = {
                fingerDirection.x * extensionFactor,
                fingerDirection.y * extensionFactor,
                fingerDirection.z * extensionFactor
            };

            // Normalize the finger direction vector
            float fingerLength = sqrt(fingerDirection.x * fingerDirection.x + fingerDirection.y * fingerDirection.y + fingerDirection.z * fingerDirection.z);

            // Calculate the intersection point
            float monitorZ = -300.0; // Z-coordinate of the monitor plane
            float t = (monitorZ - tipPosition.z) / extendedFingerVector.z;
            intersectionX = tipPosition.x + extendedFingerVector.x * t;
            intersectionY = tipPosition.y + extendedFingerVector.y * t;
            intersectionZ = monitorZ;

            // Adjust intersection point based on fingertip position
            intersectionX += tipPosition.x;
            intersectionY += tipPosition.y;
            intersectionZ += tipPosition.z;
            */
            // Calculate the intersection point
            //float monitorZ = -300.0; // Z-coordinate of the monitor plane
            //float t = (monitorZ - tipPosition.z) / extendedFingerVector.z;
            //intersectionX = tipPosition.x + extendedFingerVector.x * t;
            //intersectionY = tipPosition.y + extendedFingerVector.y * t;
            //intersectionZ = monitorZ;

            printf("    Intersection Point: (%f, %f, %f)\n",
                intersectionX,
                intersectionY,
                intersectionZ);
            

            // Write hand data to the CSV file
            fprintf(csvFile, "%lli,%i,%s,%f,%f,%f,%s,%f,%f,%f,%f,%f,%f,%f,%f,%f\n",
                (long long int)frame->info.frame_id,
                hand->id,
                (hand->type == eLeapHandType_Left ? "left" : "right"),
                hand->palm.position.x,
                hand->palm.position.y,
                hand->palm.position.z,
                handShape,
                tipPosition.x,
                tipPosition.y,
                tipPosition.z,
                fingerDirection.x,
                fingerDirection.y,
                fingerDirection.z,
                intersectionX,
                intersectionY,
                intersectionZ);
        }
        //else if (hand->pinch_strength > 0.7)
        // Note: pointing w/ middle/ring finger would also be considered pinch
        //handShape = "Pinch";

    }
}

static void OnImage(const LEAP_IMAGE_EVENT* image) {
    printf("Image %lli  => Left: %d x %d (bpp=%d), Right: %d x %d (bpp=%d)\n",
        (long long int)image->info.frame_id,
        image->image[0].properties.width, image->image[0].properties.height, image->image[0].properties.bpp * 8,
        image->image[1].properties.width, image->image[1].properties.height, image->image[1].properties.bpp * 8);
}

static void OnLogMessage(const eLeapLogSeverity severity, const int64_t timestamp,
    const char* message) {
    const char* severity_str;
    switch (severity) {
    case eLeapLogSeverity_Critical:
        severity_str = "Critical";
        break;
    case eLeapLogSeverity_Warning:
        severity_str = "Warning";
        break;
    case eLeapLogSeverity_Information:
        severity_str = "Info";
        break;
    default:
        severity_str = "";
        break;
    }
    printf("[%s][%lli] %s\n", severity_str, (long long int)timestamp, message);
}

static void* allocate(uint32_t size, eLeapAllocatorType typeHint, void* state) {
    void* ptr = malloc(size);
    return ptr;
}

static void deallocate(void* ptr, void* state) {
    if (!ptr)
        return;
    free(ptr);
}

void OnPointMappingChange(const LEAP_POINT_MAPPING_CHANGE_EVENT* change) {
    if (!connectionHandle)
        return;

    uint64_t size = 0;
    if (LeapGetPointMappingSize(*connectionHandle, &size) != eLeapRS_Success || !size)
        return;

    LEAP_POINT_MAPPING* pointMapping = (LEAP_POINT_MAPPING*)malloc((size_t)size);
    if (!pointMapping)
        return;

    if (LeapGetPointMapping(*connectionHandle, pointMapping, &size) == eLeapRS_Success &&
        pointMapping->nPoints > 0) {
        printf("Managing %u points as of frame %lld at %lld\n", pointMapping->nPoints, (long long int)pointMapping->frame_id, (long long int)pointMapping->timestamp);
    }
    free(pointMapping);
}

void OnHeadPose(const LEAP_HEAD_POSE_EVENT* event) {
    printf("Head pose:\n");
    printf("    Head position (%f, %f, %f).\n",
        event->head_position.x,
        event->head_position.y,
        event->head_position.z);
    printf("    Head orientation (%f, %f, %f, %f).\n",
        event->head_orientation.w,
        event->head_orientation.x,
        event->head_orientation.y,
        event->head_orientation.z);
    printf("    Head linear velocity (%f, %f, %f).\n",
        event->head_linear_velocity.x,
        event->head_linear_velocity.y,
        event->head_linear_velocity.z);
    printf("    Head angular velocity (%f, %f, %f).\n",
        event->head_angular_velocity.x,
        event->head_angular_velocity.y,
        event->head_angular_velocity.z);
}

int main(int argc, char** argv) {

    if ((err = fopen_s(&csvFile, "handShape_data.csv", "w")) != 0) {
        // File could not be opened. filepoint was set to NULL
        // error code is returned in err.
        // error message can be retrieved with strerror(err);
        char buf[256];
        strerror_s(buf, sizeof(buf), err);
        fprintf_s(stderr, "cannot open file '%s': %s\n", "handShape_data.csv", buf);
    }
    else {
        // File was opened, filepoint can be used to read the stream.

        // Write column names to the CSV file
        fprintf(csvFile, "Frame ID,Hand ID,Hand Type,Palm Position X,Palm Position Y,Palm Position Z,Hand Shape,TipPosition X,TipPosition Y,TipPosition Z,PointDirection X,PointDirection Y,PointDirection Z,Intersection X,Intersection Y,Intersection Z\n");

        //Set callback function pointers
        ConnectionCallbacks.on_connection = &OnConnect;
        ConnectionCallbacks.on_device_found = &OnDevice;
        ConnectionCallbacks.on_frame = &OnFrame;
        ConnectionCallbacks.on_image = &OnImage;
        ConnectionCallbacks.on_point_mapping_change = &OnPointMappingChange;
        ConnectionCallbacks.on_log_message = &OnLogMessage;
        ConnectionCallbacks.on_head_pose = &OnHeadPose;

        connectionHandle = OpenConnection();
        {
            LEAP_ALLOCATOR allocator = { allocate, deallocate, NULL };
            LeapSetAllocator(*connectionHandle, &allocator);
        }
        LeapSetPolicyFlags(*connectionHandle, eLeapPolicyFlag_Images | eLeapPolicyFlag_MapPoints, 0);

        printf("Press Enter to exit program.\n");
        getchar();


        // Close the CSV file if it was successfully opened
        if (csvFile != NULL) {
            fclose(csvFile);
        }
    }

    CloseConnection();
    DestroyConnection();
    // Wait for the plot thread to finish (optional)
    // WaitForSingleObject(plotThread, INFINITE);

    return 0;
}
