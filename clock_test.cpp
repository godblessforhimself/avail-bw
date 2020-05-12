
#include <time.h>
#include <stdio.h>
#include <algorithm>
int main() {
    timespec t1,t2;
    int count=1024;
    long arr[count], diff, sum = 0;
    for (int i = 0; i < count; i++) {
        clock_gettime(CLOCK_TAI, &t1);
        clock_gettime(CLOCK_TAI, &t2);
        diff = t2.tv_nsec - t1.tv_nsec;
        arr[i] = diff;
        if (diff>0 && diff<1e9)
            sum += diff;
        else
            printf("unprocess diff %ld\n",diff);
    }
    std::sort(arr,arr+count);
    printf("nanoseconds mean %ld, median %ld, max %ld, min %ld\n", long(sum/count), arr[count/2], arr[count-1], arr[0]);
}