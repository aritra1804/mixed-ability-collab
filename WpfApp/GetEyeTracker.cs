using System;
using System.Diagnostics;
using System.Linq.Expressions;
using Tobii.Research;

namespace WpfApp
{
    public static class GetEyeTracker
    {

        public static IEyeTracker Get()
        {
            EyeTrackerCollection eyeTrackers = EyeTrackingOperations.FindAllEyeTrackers();
            foreach (IEyeTracker eyeTracker in eyeTrackers)
            {
                Trace.WriteLine("Device name: " + eyeTracker.DeviceName);
                Trace.WriteLine("Firmware version: " + eyeTracker.FirmwareVersion);
                Trace.WriteLine("Runtime version: " + eyeTracker.RuntimeVersion);
            }
            if (eyeTrackers.Count == 0)
            {
                throw new NullReferenceException("Eye tracker not found");
            }
            return eyeTrackers[0];
        }

    }
}