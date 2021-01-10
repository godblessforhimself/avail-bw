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



#include <math.h>
#include <float.h>
#include "linreg.h"

LinearRegression::LinearRegression(Point2D *p, long size)
{
    long i;
    a = b = sumX = sumY = sumXY = 0.0;
    sumXsquared = sumYsquared = 0.0;
    n = 0L;

    if (size > 0L && p != NULL)
        for (n = 0, i = 0L; i < size; i++)
            addPoint(p[i]);
}

LinearRegression::LinearRegression
    (double *x, double *y, long size)
{
    long i;
    a = b = sumX = sumY = sumXY = 0.0;
    sumXsquared = sumYsquared = 0.0;
    n = 0L;

    if (size > 0L && x != NULL && y != NULL)
        for (n = 0, i = 0L; i < size; i++)
            addXY(x[i], y[i]);
}

void LinearRegression::addXY(const double& x, const double& y)
{
    n++;
    sumX += x;
    sumY += y;
    sumXsquared += x * x;
    sumYsquared += y * y;
    sumXY += x * y;
    Calculate();
}

void LinearRegression::Calculate()
{
    if (haveData())
    {
        if (fabs( double(n) * sumXsquared - sumX * sumX) 
            > DBL_EPSILON)
        {
            b = ( double(n) * sumXY - sumY * sumX) /
                ( double(n) * sumXsquared - sumX * sumX);
            a = (sumY - b * sumX) / double(n);

            double sx = b * (sumXY - sumX * sumY / double(n));
            double sy2 = sumYsquared - sumY * sumY / double(n);
            double sy = sy2 - sx;

            coefD = sx / sy2;
            coefC = sqrt(coefD);
            stdError = sqrt(sy / double(n - 2));
        }
        else
        {
            a = b = coefD = coefC = stdError = 0.0;
        }
    }
}

