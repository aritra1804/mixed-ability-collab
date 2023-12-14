using System;
using System.Collections.Generic;
using System.Collections.Concurrent;
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
using System.Collections;

namespace WpfApp
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        IEyeTracker eyeTracker = null;
        static Ellipse ellipse = null;
        static Ellipse ellipseCentroid = null;
        ConcurrentQueue<Point> queue = new ConcurrentQueue<Point>();

        List<Point> buffer = new List<Point>();
        Point centroid;
        Point bufferCentroid;

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
            title.Visibility = Visibility.Collapsed;
            textReminder.Visibility = Visibility.Collapsed;
        }

        private void Start_Click(object sender, RoutedEventArgs e)
        {
            // Initializes the ellipse
            if (ellipse == null)
            {
                ellipse = new Ellipse();
                ellipse.Width = 10;
                ellipse.Height = 10;
                ellipse.Fill = Brushes.Blue;
                canvas.Children.Add(ellipse);
            }

            if (ellipseCentroid == null)
            {
                ellipseCentroid = new Ellipse();
                ellipseCentroid.Width = 70;
                ellipseCentroid.Height = 70;
                ellipseCentroid.Fill = Brushes.Green;
                canvas.Children.Add(ellipseCentroid);
            }
            this.UpdateLayout();
            Thread.Sleep(1000);

            // Start listening to gaze data.
            eyeTracker.GazeDataReceived += EyeTracker_GazeDataReceived;
            // Wait for some data to be received.

            _ = Task.Run(() =>
            {
                if (ellipse == null)
                {
                    ellipse = new Ellipse();
                    ellipse.Width = 10;
                    ellipse.Height = 10;
                    ellipse.Fill = Brushes.Blue;
                    canvas.Children.Add(ellipse);
                }

                if (ellipseCentroid == null)
                {
                    ellipseCentroid = new Ellipse();
                    ellipseCentroid.Width = 70;
                    ellipseCentroid.Height = 70;
                    ellipseCentroid.Fill = Brushes.Green;
                    canvas.Children.Add(ellipseCentroid);
                }
                while (true)
                {
                    if (!queue.IsEmpty)
                    {
                        bool removed = queue.TryDequeue(out Point p);
                        if (removed)
                        {
                            this.Dispatcher.Invoke(() =>
                            {
                                Canvas.SetLeft(ellipse, p.getX() * 1920);
                                Canvas.SetTop(ellipse, p.getY() * 1200);
                            });

                            if (centroid == null || !isNear(p, centroid))
                            {
                                if (bufferCentroid != null && !isNear(bufferCentroid, p))
                                {
                                    buffer.Clear();
                                    bufferCentroid = null;
                                }

                                if (bufferCentroid == null)
                                {
                                    bufferCentroid = p;
                                }
                                else
                                {
                                    double bufferCentroidX = (bufferCentroid.getX() * buffer.Count + p.getX()) / (buffer.Count + 1);
                                    double bufferCentroidY = (bufferCentroid.getY() * buffer.Count + p.getY()) / (buffer.Count + 1);
                                    bufferCentroid = new Point(bufferCentroidX, bufferCentroidY);
                                }
                                buffer.Add(p);

                                if (buffer.Count >= 10)
                                {
                                    centroid = bufferCentroid;

                                    this.Dispatcher.Invoke(() =>
                                    {
                                        Canvas.SetLeft(ellipseCentroid, centroid.getX() * 1920);
                                        Canvas.SetTop(ellipseCentroid, centroid.getY() * 1200);
                                    });

                                    buffer.Clear();
                                    bufferCentroid = null;
                                }

                                else
                                {
                                    //ellipseCentroid.Height += 1;
                                    //ellipseCentroid.Width += 1;
                                }
                            }

                        }
                    }
                }
            });
        }

        private void Stop_Click(object sender, RoutedEventArgs e)
        {
            // Stop listening to gaze data.
            eyeTracker.GazeDataReceived -= EyeTracker_GazeDataReceived;
            Trace.WriteLine("Stopped!");
        }

        private void EyeTracker_GazeDataReceived(object sender, GazeDataEventArgs e)
        {

            if (e.LeftEye.GazePoint.Validity == Validity.Valid)
            {
                Trace.Write("L: (" + e.LeftEye.GazePoint.PositionOnDisplayArea.X + ", " + e.LeftEye.GazePoint.PositionOnDisplayArea.Y + ")");

                double x = e.LeftEye.GazePoint.PositionOnDisplayArea.X;
                double y = e.LeftEye.GazePoint.PositionOnDisplayArea.Y;
                Point p = new Point(x, y);

                queue.Enqueue(p);
            }

            if (e.RightEye.GazePoint.Validity == Validity.Valid)
            {
                Trace.WriteLine("R: (" + e.RightEye.GazePoint.PositionOnDisplayArea.X + ", " + e.RightEye.GazePoint.PositionOnDisplayArea.Y + ")");
            }
        }

        private bool isNear(Point a, Point b)
        {
            return Math.Sqrt((a.getX() - b.getX()) * (a.getX() - b.getX()) + (a.getY() - b.getY()) * (a.getY() - b.getY())) < 0.05;
        }
    }
}
