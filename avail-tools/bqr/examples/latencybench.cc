/*
    select

*/
#include <iostream>
#include <algorithm>
#include <sys/select.h>
#include <sys/time.h>
#include <time.h>
#include <errno.h>
#include <string.h>
#include <boost/format.hpp>
using namespace std;
clockid_t clock_value=CLOCK_REALTIME;
string time2string(double t){
    boost::format f;
    if (t<1e-9) {
        return string("0");
    } else if (t<1e-6) {
        f = boost::format("%dns") % int(t*1e9);
    } else if (t<1e-3) {
        f = boost::format("%.3fus") % (t*1e6);
    } else if (t<1) {
        f = boost::format("%.3fms") % (t*1e3);
    } else {
        f = boost::format("%.3fs") % (t);
    }
    return f.str();
}
double to_double(timespec a) {
    return (double)a.tv_sec + (double)a.tv_nsec * 1e-9;
}
timespec diff(struct timespec tic, struct timespec toc)
{
    struct timespec temp;
    if ((toc.tv_nsec-tic.tv_nsec)<0)
    {
        temp.tv_sec = toc.tv_sec-tic.tv_sec-1;
        temp.tv_nsec = 1000000000+toc.tv_nsec-tic.tv_nsec;
    }
    else
    {
        temp.tv_sec = toc.tv_sec-tic.tv_sec;
        temp.tv_nsec = toc.tv_nsec-tic.tv_nsec;
    }
    return temp;
}
int main(int argc,char *argv[])
{
    int repeat_count = 10000;
    if (argc>1)
        repeat_count = atoi(argv[1]);
    timespec begin, end, temp;
    double actual_time[repeat_count] = {0}, sum = 0;
    for (int i = 0; i < repeat_count; i++) {
        clock_gettime(clock_value, &begin);
        clock_gettime(clock_value, &end);
        temp = diff(begin, end);
        actual_time[i] = to_double(temp);
        sum+= actual_time[i];
    }
    sort(actual_time, actual_time+repeat_count);
    cout << "Min " << time2string(actual_time[0]) << endl;
    cout << "Median " << time2string(actual_time[repeat_count/2]) << endl;
    cout << "Max " << time2string(actual_time[repeat_count-1]) << endl;
    cout << "Mean time " << time2string(sum/repeat_count) << endl;
    cout << "Total time " << time2string(sum) << endl;
}
