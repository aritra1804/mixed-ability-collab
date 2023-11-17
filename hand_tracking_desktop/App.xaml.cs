using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using Mediapipe.Net.Framework.Protobuf;
using Microsoft.Azure.Kinect.BodyTracking;
using Microsoft.Azure.Kinect.Sensor;

namespace hand_tracking_desktop
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {

        private Device device;
        private Joint wrist;
        private Joint hand;
        private Joint tip;

        private void start_kinect()
        { 
            device = Device.Open();

            device.StartCameras(new DeviceConfiguration()
            {
                CameraFPS = FPS.FPS30,
                ColorResolution = ColorResolution.Off,
                DepthMode = DepthMode.NFOV_Unbinned,
                WiredSyncMode = WiredSyncMode.Standalone,
            }) ;
        }

        private void get_kinect_data()
        {

            var calibration = device.GetCalibration();
            using (Tracker tracker = Tracker.Create(calibration, new TrackerConfiguration( { ProcessingMode = TrackerProcessingMode.Gpu, SensorOrientation = SensorOrientation.Default }))
            {
                using (Capture sensorCapture = device.GetCapture())
                {
                    tracker.EnqueueCapture(sensorCapture);
                }

                using (Frame frame = tracker.PopResult(TimeSpan.Zero, throwOnTimeout: false))
                {
                    if (frame != null)
                    {
                        uint num_bodies = frame.NumberOfBodies;

                        for (uint i = 0; i < num_bodies; i++)
                        {
                            Body body = frame.GetBody(i);
                            wrist = body.Skeleton.GetJoint(JointId.WristRight);
                            hand = body.Skeleton.GetJoint(JointId.HandRight);
                            tip = body.Skeleton.GetJoint(JointId.HandTipRight);
                        }

                    }

                }

            }
    }
}
