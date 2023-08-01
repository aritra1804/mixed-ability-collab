import cv2
import pykinect_azure as pykinect

# # Add path to the k4a.dll module to sys.path
# k4a_path = r"C:\Users\verol\OneDrive\Desktop\Azure Kinect SDK v1.4.1\sdk\windows-desktop\amd64\release\bin\k4a.dll"
# # path: "C:\Users\verol\OneDrive\Desktop\Azure Kinect SDK v1.4.1\sdk\windows-desktop\amd64\release\bin\k4a.dll"
# sys.path.append(k4a_path)

if __name__ == "__main__":
	
	# Initialize the library, if the library is not found, add the library path as argument
	# added path to k4d.dll to overwrite default path
	pykinect.initialize_libraries(
	module_k4a_path="C:\\Users\\verol\\OneDrive\\Desktop\\Azure Kinect SDK v1.4.1\\sdk\\windows-desktop\\amd64\\release\\bin\\k4a.dll")
	module_k4a_path="C:\\Users\\verol\\OneDrive\\Desktop\\Azure Kinect SDK v1.4.1\\sdk\\windows-desktop\\amd64\\release\\bin\\k4a.dll"

	# Modify camera configuration
	device_config = pykinect.default_configuration
	device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_OFF
	device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED

	# Start device
	device = pykinect.start_device(config=device_config)

	cv2.namedWindow('Depth Image',cv2.WINDOW_NORMAL)
	while True:

		# Get capture
		capture = device.update()

		# Get the color depth image from the capture
		ret, depth_image = capture.get_depth_image()

		if not ret:
			continue
			
		# Plot the image
		cv2.imshow('Depth Image',depth_image)
		
		# Press q key to stop
		if cv2.waitKey(1) == ord('q'):  
			break
	
	
	# while True:

	# 	# Get capture
	# 	capture = device.update()

	# 	# Get the color depth image from the capture
	# 	ret, depth_image = capture.get_colored_depth_image()

	# 	if ret:
	# 		# continue

	# 		# Get the body frame
	# 		# body_frame = capture.get_body_frame()
	# 		depth_image = capture.get_depth_image()
	# 		# Get the first tracked body
	# 		# bodies = body_frame.bodies
	# 		bodies = capture.
	# 		if len(bodies) > 0:
	# 			body = bodies[0]

	# 			# Get the wrist joint
	# 			wrist_joint = body.skeleton.joints[pykinect.K4ABT_JOINT_WRIST_LEFT]

	# 			# Get the wrist position in 3D space
	# 			wrist_position = wrist_joint.position

	# 			print("Wrist Position (x, y, z):", wrist_position.x, wrist_position.y, wrist_position.z)


			
	# 	# Plot the image
	# 	cv2.imshow('Depth Image',depth_image)
		
		# Press q key to stop
		if cv2.waitKey(1) == ord('q'):  
			break