/*
	version: exp2
	param: packet number
	example: ./jintao_server 3000
*/
#include "util.cpp"
int listen_fd = -1, conn_fd = -1, udp_fd = -1, packet_number = -1;
socklen_t sock_len = 0;
sockaddr_in server_address, client_address;
char udpbuffer[10000];
void init();
void get_basic_info_server();
long test_recv(int repeat, int packet_size);
void recv_udp_packets(int,int);
void recv_probe_packets(int packet_number);
int main(int argc, char *argv[]) {
	init();
	tick();
	if (argc != 2) {
		printf("lack packet number\n");
		return -1;
	}
	packet_number = atoi(argv[1]);
	printf("recving %d packet\n", packet_number);
	if (running_mode == 1) {
		get_basic_info_server();
	} else if (running_mode == 2) {
		recv_udp_packets(100, 10);
	} else if (running_mode == 3){
		recv_udp_packets(packet_number, 1472);
		tock();
		tick();
		recv_probe_packets(100);
	} else if (running_mode == 4) {
		recv_probe_packets(100);
	}
	tock();
}
void init(){
	int ret;
	listen_fd = socket(AF_INET, SOCK_STREAM, 0); 
	if (listen_fd == -1) perror("server init:");
	ret = set_reuse_addr(listen_fd); 
	if (ret) perror("server set tcp reuse:");
	set_sockaddr(&server_address, server_listen_port);
	ret = bind_address(listen_fd, &server_address); 
	if (ret) perror("server bind address:");
	ret = listen(listen_fd, 5);
	if (ret) perror("server listen:");
	udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (udp_fd == -1) perror("server udp socket:");
	ret = set_reuse_addr(udp_fd);
	if (ret) perror("server set udp reuse:");
	bind_address(udp_fd, &server_address);
	conn_fd = accept(listen_fd, (sockaddr*)&client_address, &sock_len);
	if (conn_fd == -1) perror("server accept:");
}
void get_basic_info_server(){
	/* mtu, clock_gettime, recv */
	int mss = get_mss(conn_fd);
	long gettimecost = test_clock_gettime(1e4);
	long recvcost = test_recv(send_repeat_count, 1472);
	printf("mss is %d, clock_gettime %luus, recv %luus, max speed %dMbps\n", mss, gettimecost, recvcost, mss * 8 / recvcost);
	test_clock_nanosleeps();
	test_selects();
}
long test_recv(int repeat, int packet_size) {
	timespec t1, t2, interval;
	interval.tv_sec = 0;
	interval.tv_nsec = 2e6;
	double *diff = new double[repeat];
	for (int i = 0; i < repeat; i++){
		recvfrom(udp_fd, udpbuffer, packet_size, 0, NULL, NULL);
		clock_gettime(clock_to_use, &t1);
		recvfrom(udp_fd, udpbuffer, packet_size, 0, NULL, NULL);
		clock_gettime(clock_to_use, &t2);
		diff[i] = timespec2double(t2) - timespec2double(t1);
		clock_nanosleep(clock_to_use, 0, &interval, NULL);
	}
	sort(diff, diff + repeat);
	double average = diff[repeat / 2];
	long us = 1e6 * (average - long(average));
	delete [] diff;
	return us;
}
void recv_udp_packets(int packet_number, int packet_size) {
	/* recv n udp packet */
	ssize_t recvsize, total = 0;
	for (int i = 0; i < packet_number; i++) {
		recvsize = recv(udp_fd, udpbuffer, packet_size, 0);
		if (recvsize > 0) total += recvsize;
		else perror("recv:");
	}
	printf("recv total %zd, average %zd\n", total, total / ssize_t(packet_number));
}
void recv_probe_packets(int packet_number) {
	/* recv n probe packets */
	ssize_t recvsize, total = 0;
	for (int i = 0; i < packet_number; i++) {
		recvsize = recv(udp_fd, udpbuffer, 4, 0);
		if (recvsize > 0) total += recvsize;
		else perror("recv:");
	}
	printf("recv total %zd, average %zd\n", total, total / ssize_t(packet_number));
}