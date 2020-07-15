/*
	util:

*/
#include <time.h> //timespec
#include <stdio.h> //fprintf
#include <unistd.h> //getopt
#include <sys/socket.h> //socket
#include <netinet/in.h> //sockaddr_in
#include <string.h> //memset
#include <string> //string s
#include <arpa/inet.h> //inet_ntoa
#include <linux/net_tstamp.h> //timestamping
#include <sys/epoll.h> //
//#include <linux/net_tstamp.h>
#include <linux/errqueue.h>  //scm_timestamping
#include <errno.h> //errno
#define CLIENT_MODE (0)
#define SERVER_MODE (1)
using namespace std;
double timespec2double(const timespec& t) {
	return t.tv_sec+double(t.tv_nsec)/1e9;
}
timespec double2timespec(double t){
	timespec ret;
	ret.tv_sec=(long)t;
	ret.tv_nsec=(t-(long)t)*1e9;
	return ret;
}
int set_reuse_addr(int fd) {
    int optval = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (const void*)&optval, sizeof(int)) == -1) {
        return -1;
    }
    return 0;
}
void set_local_port(sockaddr_in *addr, int port) {
    memset(addr, 0, sizeof(sockaddr_in));
    addr->sin_family = AF_INET;
    addr->sin_addr.s_addr = htonl(INADDR_ANY);
    addr->sin_port = htons(port);
}
int bind_local_port(int fd, sockaddr_in *addr) {
    if (bind(fd, (sockaddr*)addr, sizeof(sockaddr_in))) {
        return -1;
    }
    return 0;
}
void print_sockaddr(FILE *f, sockaddr_in *addr) {
    fprintf(f, "address %s, port %d\n", inet_ntoa(addr->sin_addr), addr->sin_port);
}
int set_timestamp_on(int fd, int mode) {
    int val = SOF_TIMESTAMPING_RAW_HARDWARE | SOF_TIMESTAMPING_SOFTWARE, err;
    if (mode == SERVER_MODE) {
        val |= SOF_TIMESTAMPING_RX_SOFTWARE;
        err = setsockopt(fd, SOL_SOCKET, SO_TIMESTAMPING, &val, sizeof(val));
        if (err) {
            return -1;
        }
        return 0;
    } else if (mode == CLIENT_MODE) {
        val |= SOF_TIMESTAMPING_OPT_TSONLY;
        err = setsockopt(fd, SOL_SOCKET, SO_TIMESTAMPING, &val, sizeof(val));
        if (err) {
            return -1;
        }
        return 0;
    }
    return -2;
}
int get_buffer_size(int fd) {
    int buffer_size;
    socklen_t slen = sizeof(int);
    if (getsockopt(fd, SOL_SOCKET, SO_RCVBUF, &buffer_size, &slen)) {
        return -1;
    }
    return buffer_size;
}
sockaddr_in generate_sockaddr(const char *ip, int port) {
	sockaddr_in ret;
	ret.sin_addr.s_addr = inet_addr(ip);
	ret.sin_family = AF_INET;
	ret.sin_port = htons(port);
	return ret;
}
timespec msg2timespec(msghdr *msg) {
	timespec ret;
    for (cmsghdr *cmsg = CMSG_FIRSTHDR(msg); cmsg; cmsg = CMSG_NXTHDR(msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_IP && cmsg->cmsg_type == IP_RECVERR) {
            continue;
        } else if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            scm_timestamping *ts = (scm_timestamping*)CMSG_DATA(cmsg);
            ret = ts->ts[0];
			return ret;
        }
    }
	throw "msghdr not include timestamp";
}
void set_timeout(int fd, int sec, int usec) {
    timeval timeout;
    timeout.tv_sec = sec;
    timeout.tv_usec = usec;
    if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, (char*)&timeout, sizeof(timeout)) < 0) {
        throw "set timeout error";
    }
}
int timespec2str(char *dst, timespec *src) {
    sprintf(dst, "%10lu.%09lu", src->tv_sec, src->tv_nsec);
    return 20;
}
int timespecs2str(char *buf, timespec *head, int n) {
    char *temp = buf;
    for (int i = 0; i < n; i++) {
        if (i != n - 1) {
            temp += timespec2str(temp, head + i);
            temp[0] = ','; temp+=1;
        } else {
            temp += timespec2str(temp, head + i);
            temp[0] = '\n'; temp+=1;
        }
    }
    return temp-buf;
}
int timespecs2len(int n) {
	return 21 * n + 1;
}