import cv2
import pykinect_azure as pykinect

# depth camera coordinate system (depth in millimeters)
# https://learn.microsoft.com/en-us/azure/kinect-dk/coordinate-systems

if __name__ == "__main__":

	# Initialize the library, if the library is not found, add the library path as argument
	pykinect.initialize_libraries(
		module_k4a_path="C:\\Users\\verol\\OneDrive\\Desktop\\Azure Kinect SDK v1.4.1\\sdk\\windows-desktop\\amd64\\release\\bin\\k4a.dll", 
		module_k4abt_path = "C:\\Program Files\\sdk\\windows-desktop\\amd64\\release\\bin\\k4abt.dll",
		track_body=True)

	# Modify camera configuration
	device_config = pykinect.default_configuration
	device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_OFF
	device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED
	#print(device_config)

	# Start device
	device = pykinect.start_device(config=device_config)

	# Start body tracker
	bodyTracker = pykinect.start_body_tracker()

	cv2.namedWindow('Depth image with skeleton',cv2.WINDOW_NORMAL)
	while True:
		# following code is used for getting joint locations
		# Get capture
		capture = device.update()

		# Get body tracker frame
		body_frame = bodyTracker.update(capture)

		# Access attributes of body_frame
		if body_frame is not None:
			num_bodies = body_frame.get_num_bodies()
			for i in range(num_bodies):
				body = body_frame.get_body(i)

				# Access joints of the body
				for joint in body.joints:
					if joint.id in {14,15,16}:
						# https://learn.microsoft.com/en-us/azure/kinect-dk/body-joints 
						# 14 is WRIST_RIGHT, 15 is HAND_RIGHT, 16 is HANDTIP_RIGHT
						# Print joint information
						print(type(joint))
	
		# Uncomment following code to get depth image with skeleton
		# # Get capture
		# capture = device.update()

		# # Get body tracker frame
		# body_frame = bodyTracker.update()

		# # Get the color depth image from the capture
		# ret_depth, depth_color_image = capture.get_colored_depth_image()

		# # Get the colored body segmentation
		# ret_color, body_image_color = body_frame.get_segmentation_image()

		# if not ret_depth or not ret_color:
		# 	continue
			
		# # Combine both images
		# combined_image = cv2.addWeighted(depth_color_image, 0.6, body_image_color, 0.4, 0)

		# # Draw the skeletons
		# combined_image = body_frame.draw_bodies(combined_image)

				# # Overlay body segmentation on depth image
		# cv2.imshow('Depth image with skeleton',combined_image)

		# # Press q key to stop
		# if cv2.waitKey(1) == ord('q'):  
		# 	break



