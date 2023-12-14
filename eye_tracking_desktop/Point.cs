using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WpfApp
{
    internal class Point
    {
        double x, y;

        public Point()
        {
            this.x = 0.5; this.y = 0.5;
        }

        public Point(double x, double y) {
            this.x = x; this.y = y;
        }

        public double getX()
        {
            return x;
        }

        public double getY()
        {
            return y;
        }
    }
}
