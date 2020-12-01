#include "util.h"
clockid_t clock_to_use = CLOCK_REALTIME;
timespec program_begin, program_end;
control_parameter::control_parameter(int x, int y, int z, int w) {
	packet_size = htonl(x);
	load_number = htonl(y);
	inspect_number = htonl(z);
	inspect_size = htonl(w);
}
void control_parameter::network2host() {
	packet_size = ntohl(packet_size);
	load_number = ntohl(load_number);
	inspect_number = ntohl(inspect_number);
	inspect_size = ntohl(inspect_size);
}
timestamp_packet::timestamp_packet() {
	packet_id = 0;
	timestamp[0] = 0;
	timestamp[1] = 0;
}
timestamp_packet::timestamp_packet(int x, double y) {
	update(x, y);
}
void timestamp_packet::update(int x, double y) {
	// This will bring problem when the sender and receiver use different endians!
	// use google protocol buffers for compatibility
	packet_id = htonl(x);
	timestamp[0] = y;
	timestamp[1] = 0;
}
void timestamp_packet::network2host() {
	// bring problem when endians of sender and receiver not match
	// use google protocol buffers
	packet_id = ntohl(packet_id);
	timestamp[0] = timestamp[0];
	timestamp[1] = timestamp[1];
}

int set_reuse_addr(int fd) {
    int optval = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (const void*)&optval, sizeof(int)) == -1) {
        return -1;
    }
    return 0;
}
void set_busy_poll(int fd, int busy_poll) {
	int r = setsockopt(fd, SOL_SOCKET, SO_BUSY_POLL, (char *)&busy_poll, sizeof(busy_poll));
	if (r < 0) {
		perror("setsockopt(SO_BUSY_POLL)");
	}
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
void tick() {
	clock_gettime(clock_to_use, &program_begin);
}
void tock() {
	clock_gettime(clock_to_use, &program_end);
	double dt = timespec2double(program_end) - timespec2double(program_begin);
	printf("program use %.2f s\n", dt);
}