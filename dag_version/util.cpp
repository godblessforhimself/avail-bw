#ifndef UTIL_C
#define UTIL_C
#include <time.h>
#include <assert.h>
#include <netinet/tcp.h> // TCP_MAXSEG
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h> //getopt
#include <string.h>
#include <stdio.h>
#include <algorithm> //sort
using namespace std;
clockid_t clock_to_use = CLOCK_TAI;
int server_listen_port = 11106, running_mode = 3, send_repeat_count = 1e3;
timespec program_begin, program_end;
int set_reuse_addr(int fd) {
    int optval = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (const void*)&optval, sizeof(int)) == -1) {
        return -1;
    }
    return 0;
}
void set_sockaddr(sockaddr_in *addr, int port) {
	/* set IP of addr to INADDR_ANY and port to param port */
    memset(addr, 0, sizeof(sockaddr_in));
    addr->sin_family = AF_INET;
    addr->sin_addr.s_addr = htonl(INADDR_ANY);
    addr->sin_port = htons(port);
}
int bind_address(int fd, sockaddr_in *addr) {
	/* bind listen socket to address */
    if (bind(fd, (sockaddr*)addr, sizeof(sockaddr_in))) {
        return -1;
    }
    return 0;
}
int get_mss(int conn_fd){
	int opt_len, mss;
	opt_len = sizeof(mss);
	if (getsockopt(conn_fd, IPPROTO_TCP, TCP_MAXSEG, (char*)&mss, (socklen_t*)&opt_len)){
		return -1;
	} else {
		return mss;
	}
}
void set_sockaddr(sockaddr_in *addr, char *ip_str, int port) {
	/* set address to (IP,port) */
	addr->sin_addr.s_addr = inet_addr(ip_str);
    addr->sin_family = AF_INET;
    addr->sin_port = htons(port);
}
double timespec2double(timespec t){
	return t.tv_sec + (double)t.tv_nsec / (1e9);
}
timespec double2timespec(double t){
	timespec ret;
	ret.tv_sec = (int)t;
	ret.tv_nsec = (t - ret.tv_sec) * 1e9;
	return ret;
}
void print_timespec(timespec t){
	printf("%10lu %09lu\n", t.tv_sec, t.tv_nsec);
}
long test_clock_gettime(int repeat){
	/* the minimum time one clock_gettime cost */
	timespec t1, t2;
	double *diff = new double[repeat];
	for (int i = 0; i < repeat; i++){
		clock_gettime(clock_to_use, &t1);
		clock_gettime(clock_to_use, &t2);
		diff[i] = timespec2double(t2) - timespec2double(t1);
	}
	sort(diff, diff + repeat);
	double middle = diff[repeat / 2], min_ = diff[0], max_ = diff[repeat - 1];
	long average = 1e6 * (middle - long(middle));
	delete [] diff;
	return average;
}
long test_clock_nanosleep(int repeat, long nano) {
	/* the minimum time one clock_nanosleep cost */
	timespec t1, t2, min_sleep_time;
	min_sleep_time.tv_sec = 0;
	min_sleep_time.tv_nsec = nano;
	double *diff = new double[repeat];
	for (int i = 0; i < repeat; i++){
		clock_gettime(clock_to_use, &t1);
		clock_nanosleep(clock_to_use, 0, &min_sleep_time, NULL);
		clock_gettime(clock_to_use, &t2);
		diff[i] = timespec2double(t2) - timespec2double(t1);
	}
	sort(diff, diff + repeat);
	double middle = diff[repeat / 2], min_ = diff[0], max_ = diff[repeat - 1];
	long average = 1e6 * (middle - long(middle));
	delete [] diff;
	return average;
}
void test_clock_nanosleeps() {
	long sleepcost_0 = test_clock_nanosleep(1e4, 0);
	long sleepcost_1k = test_clock_nanosleep(1e4, 1000);
	long sleepcost_10k = test_clock_nanosleep(1e4, 10000);
	printf("sleep cost %lu sleep cost %lu sleep cost %lu\n", sleepcost_0, sleepcost_1k, sleepcost_10k);
}
long test_select(int repeat, long us){
	timeval sleep_time = {
		.tv_sec = 0,
		.tv_usec = us
	}, sleep_temp;
	timespec t1, t2;
	double *diff = new double[repeat];
	for (int i = 0; i < repeat; i++){
		sleep_temp = sleep_time;
		clock_gettime(clock_to_use, &t1);
		select(1, NULL, NULL, NULL, &sleep_temp);
		clock_gettime(clock_to_use, &t2);
		diff[i] = timespec2double(t2) - timespec2double(t1);
	}
	sort(diff, diff + repeat);
	double middle = diff[repeat / 2], min_ = diff[0], max_ = diff[repeat - 1];
	long average = 1e6 * (middle - long(middle));
	delete [] diff;
	return average;
}
void test_selects() {
	int repeat = 1e4;
	long selectcost_0 = test_select(repeat, 0);
	long selectcost_1 = test_select(repeat, 1);
	long selectcost_10 = test_select(repeat, 10);
	long selectcost_100 = test_select(repeat, 100);
	printf("select cost %lu select cost %lu select cost %lu select cost %lu\n", selectcost_0, selectcost_1, selectcost_10, selectcost_100);
}
void tick() {
	clock_gettime(clock_to_use, &program_begin);
}
void tock() {
	clock_gettime(clock_to_use, &program_end);
	double dt = timespec2double(program_end) - timespec2double(program_begin);
	printf("program use %.2f s\n", dt);
}
#endif