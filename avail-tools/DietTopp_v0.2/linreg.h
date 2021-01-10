/*  
 *  This file is part of DietTopp.
 *
 *  DietTopp is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  DietTopp is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with DietTopp; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 */





/*  linreg.h */
#ifndef linreg_h 
#define linreg_h

#include <stdlib.h>

// a class encapsulating a point in Cartesian coordinates
class Point2D
{
    public:
        Point2D(double X = 0.0, double Y = 0.0) : x(X), y(Y) 
        { }

        void setPoint(double X, double Y) { x = X; y = Y; }
        void setX(double X) { x = X; }
        void setY(double Y) { y = Y; }

        double getX() const { return x; }
        double getY() const { return y; }

    private:
        double x, y;
};

// a linear regression analysis class
class LinearRegression
{
  //   friend ostream& operator<<(ostream&, LinearRegression&);

    public:
        // Constructor using an array of Point2D objects
        // This is also the default constructor
        LinearRegression(Point2D *p = 0, long size = 0);

        LinearRegression(double *x, double *y, long size = 0);

virtual void addXY(const double& x, const double& y);
        void addPoint(const Point2D& p) 
        { addXY(p.getX(), p.getY()); }

        // Must have at least 3 points to calculate
        // standard error of estimate.  
        //Do we have enough data?
        int haveData() const { return (n > 2 ? 1 : 0); }
        long items() const { return n; }

virtual double getA() const { return a; }
virtual double getB() const { return b; }

        double getCoefDeterm() const  { return coefD; }
        double getCoefCorrel() const { return coefC; }
        double getStdErrorEst() const { return stdError; }
virtual double estimateY(double x) const 
        { return (a + b * x); }

    protected:
        long n;             // number of data points input
        double sumX, sumY;  // sums of x and y
        double sumXsquared, // sum of x squares
               sumYsquared; // sum y squares
        double sumXY;       // sum of x*y

        double a, b;        // coefficients of f(x) = a + b*x
        double coefD,       // coefficient of determination
               coefC,       // coefficient of correlation
               stdError;    // standard error of estimate

        void Calculate();   // calculate coefficients
};

#endif                      // end of linreg.h


