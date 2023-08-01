<!-- ABOUT THIS FOLDER -->
## About This Folder

This folder contains code that helps you set up hand tracking using an Azure Kinect Camera and find where users are pointing at on a monitor screen.

<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.

### Prerequisites

This project is built and tested on an Microsoft Azure Kinect camera and a 24-inch Dell monitor.

### Installation

1. Download this folder to your local computer
2. Install the Tobii Pro SDK (tested with v 1.11) [https://developer.tobiipro.com/python/python-sdk-reference-guide.html](https://developer.tobiipro.com/python/python-sdk-reference-guide.html)
3. Install the necessary packages:
  ```
  pip install mediapipe
  pip install tensorflow
  pip install pykinect_azure
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage
![A monitor with a camera on the top and an eye tracker attached to the bottom of the monitor. The camera, eye tracker, and monitor are labeled with colored arrows.](images/setup.png) 

This image shows our setup, which includes a 24" monitor, an Azure Kinect camera above the monitor and a Tobii Pro Fusion eye tracker attached to the bottom bezel of the monitor.

![A user is pointing and looking at our monitor screen while the sensors estimate their position.](images/pointers.png) 

This image shows where the sensors are collecting data using dashed lines (pink coming from the eye tracker to the eye and cyan from the Azure Kinect to the pointing finger). There is a red line representing gaze to the estimated position on the screen and a yellow line representing pointing to the screen. The estimated area of interest is highlighted on the screen in a red box.

![Three graphs which show the raw eye tracking data, calculated centroids, and convex hulls displayed on the text "Work Experience"](images/eyetracking.png) 

The raw data displayed above has red and blue displaying the calculated positions for each eye and green for interpolated data from the user's dominant eye (the left in this example)/ From this data, centroids were calculated based on the time and position of the eye. The centroid points are averaged from all the points displayed in the convex hull graph.



<p align="right">(<a href="#readme-top">back to top</a>)</p>

