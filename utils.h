#include <time.h>
#include <stdio.h>
struct time_control{
    static long tmp_for_wait, wait_loop;
    static void init_wait(timespec *period);
    static inline void wait(int k);
};
