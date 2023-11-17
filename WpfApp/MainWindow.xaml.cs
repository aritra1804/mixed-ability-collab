using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using Tobii.Research;

namespace WpfApp
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        IEyeTracker eyeTracker = null;
        static Ellipse ellipse = null;
        static double X = 0.5;
        static double Y = 0.5;

        public MainWindow()
        {
            InitializeComponent();
        }

        private void Connect_Click(object sender, RoutedEventArgs e)
        {
            eyeTracker = GetEyeTracker.Get();
            if (eyeTracker == null)
            {
                throw new NullReferenceException("No eyetracker found!");
            }
            title.Visibility= Visibility.Collapsed;
            textReminder.Visibility = Visibility.Collapsed;
        }

        private void Calibrate_Click(object sender, RoutedEventArgs e)
        {

        }

        private void Start_Click(object sender, RoutedEventArgs e)
        {
            if (ellipse == null)
            {
                ellipse = new Ellipse();
                ellipse.Width = 10;
                ellipse.Height = 10;
                ellipse.Fill = Brushes.Orange;
                canvas.Children.Add(ellipse);
            }
            Canvas.SetLeft(ellipse, 960);
            Canvas.SetTop(ellipse, 600);
            Thread.Sleep(1000);
            double oldX = X;
            double oldY = Y;
            // Start listening to gaze data.
            eyeTracker.GazeDataReceived += EyeTracker_GazeDataReceived;
            
            // Wait for some data to be received.
            _ = Task.Run(() =>
            {
                while (true)
                {
                    if (oldX != X || oldY != Y)
                    {
                        oldX = X;
                        oldY = Y;
                        this.Dispatcher.Invoke(() =>
                        {
                            Canvas.SetLeft(ellipse, X * 1920);
                            Canvas.SetTop(ellipse, Y * 1200);
                        });
                    }

                }
            });
        }

        private void Stop_Click(object sender, RoutedEventArgs e)
        {
            // Stop listening to gaze data.
            eyeTracker.GazeDataReceived -= EyeTracker_GazeDataReceived;
            Trace.WriteLine("Stopped!");
            Close();
        }

        private static void EyeTracker_GazeDataReceived(object sender, GazeDataEventArgs e)
        {

            if (e.LeftEye.GazePoint.Validity == Validity.Valid)
            {
                Trace.Write("L: (" + e.LeftEye.GazePoint.PositionOnDisplayArea.X + ", " + e.LeftEye.GazePoint.PositionOnDisplayArea.Y + ")");
                X = e.LeftEye.GazePoint.PositionOnDisplayArea.X;
                Y = e.LeftEye.GazePoint.PositionOnDisplayArea.Y;
            }

            if (e.RightEye.GazePoint.Validity == Validity.Valid)
            {
                Trace.WriteLine("R: (" + e.RightEye.GazePoint.PositionOnDisplayArea.X + ", " + e.RightEye.GazePoint.PositionOnDisplayArea.Y + ")");
            }
        }
    }
}
