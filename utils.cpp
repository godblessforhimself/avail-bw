#include "utils.h"
long time_control::wait_loop = 1;
long time_control::tmp_for_wait = 1;
int compare_timespec(timespec *t1, timespec *t2) {
    if (t1->tv_sec == t2->tv_sec) {
        if (t1->tv_nsec < t2->tv_nsec)
            return -1;
        else if (t1->tv_nsec == t2->tv_nsec) 
            return 0;
        else
            return 1;
    } else if (t1->tv_sec < t2->tv_sec)
        return -1;
    return 1;
}
int expand_timespec(timespec *dst, timespec *src, int k) {
    long temp;
    if (src->tv_sec == 0) {
        temp = src->tv_nsec * k;
        dst->tv_sec = temp / (long)(1e9);
        dst->tv_nsec = temp % (long)(1e9);
        return 0;
    }
    return -1;
}
void time_control::init_wait(timespec *period){
    timespec t1, t2, t3;
    long m = -1, M = -1, k = 10;
    timespec multiplied_spec;
    expand_timespec(&multiplied_spec, period, k);
    while (true) {
        clock_gettime(CLOCK_TAI, &t1);
        time_control::wait(k);
        clock_gettime(CLOCK_TAI, &t2);
        t3.tv_nsec = (t2.tv_nsec >= t1.tv_nsec) ? t2.tv_nsec - t1.tv_nsec : t2.tv_nsec - t1.tv_nsec + 1e9;
        t3.tv_sec = (t2.tv_nsec >= t1.tv_nsec) ? t2.tv_sec - t1.tv_sec : t2.tv_sec - t1.tv_sec - 1;
        int comp = compare_timespec(&t3, &multiplied_spec);
        if (comp>0) {
            if (m==-1) {
                m=wait_loop/2;
                M=wait_loop;
            } else {
                M=(m+M)/2;
            }
        } else if (comp<0) {
            if (m==-1)
                wait_loop *= 2;
            else
                m=(m+M)/2;
        } else if (comp == 0) {
            break;
        }
        if (m+1==M) {
            wait_loop=m;
            break;
        } else if (m>0) {
            wait_loop = (m+M)/2;
        }
    }
    printf("time control init success: %ld takes %ld.%09ld for %ld times\n", wait_loop, t3.tv_sec, t3.tv_nsec, k);
}

inline void time_control::wait(int k) {
    for (long i = 0; i < wait_loop * k; i++){
        tmp_for_wait += 3;
        tmp_for_wait -= 3;
    }
}