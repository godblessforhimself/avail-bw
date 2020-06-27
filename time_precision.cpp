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
using namespace std;
void printtime(timeval t) {
    double tdouble = 1e6 * t.tv_sec + t.tv_usec;
    printf("%f\n", tdouble);
}
double to_double(timeval a) {
    return a.tv_sec * 1e6 + a.tv_usec;
}
double to_double(timespec a) {
    return a.tv_sec * 1e6 + a.tv_nsec / 1000;
}
int main(int argc,char *argv[])
{
    int repeat_count = 10000;
    timeval sleep_time, begin, end;
    timespec sleep_time2,remain_time,begin2,end2;
    remain_time = {0,0};
    sleep_time2.tv_nsec = 20*1e3;
    sleep_time2.tv_sec = 0;
    double actual_time[repeat_count] = {0};
    for (int i = 0; i < repeat_count; i++) {
        sleep_time.tv_sec = 0;sleep_time.tv_usec = 20;
        //gettimeofday(&begin, NULL);
        clock_gettime(CLOCK_MONOTONIC, &begin2);
        int r = clock_nanosleep(CLOCK_MONOTONIC, 0, &sleep_time2, NULL);
        //int r = select(1,NULL,NULL,NULL,&sleep_time);
        if (r!=0)
            cout << strerror(r) << endl;
        //gettimeofday(&end, NULL);
        clock_gettime(CLOCK_MONOTONIC, &end2);
        //actual_time[i] = to_double(end) - to_double(begin);
        actual_time[i] = to_double(end2) - to_double(begin2);
    }
    sort(actual_time, actual_time+repeat_count);
    cout << actual_time[0] << endl;
    cout << actual_time[repeat_count/2] << endl;
    cout << actual_time[repeat_count-1] << endl;
}
