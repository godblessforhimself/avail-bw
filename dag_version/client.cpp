#include "util.cpp"
int tcp_fd = -1, udp_fd = -1;
char server_ip_str[] = "192.168.5.1";
char udpbuffer[10000];
sockaddr_in server_address, client_addr;
socklen_t sock_len = sizeof(sockaddr_in);
void init();
void get_basic_info_client();
void send_udp_packets(int packet_number, int packet_size, int microsecond);
void send_at_speed(double speed, int packet_size, int packet_number);
long test_send(int repeat, int packet_size);
int main(int argc, char *argv[]) {
	tick();
	init();
	if (running_mode == 1) {
		get_basic_info_client();
	} else if (running_mode == 2) {
		send_udp_packets(100, 10, 100);
	} else if (running_mode == 3){
		send_at_speed(1000, 1472, 10000);
	}
	tock();
}
void init(){
	set_sockaddr(&server_address, server_ip_str, server_listen_port);
	set_sockaddr(&client_addr, 0);
	tcp_fd = socket(AF_INET, SOCK_STREAM, 0);
	if (connect(tcp_fd, (sockaddr*)&server_address, sock_len)) {
		printf("connect fail\n");
	}
	udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
	bind_address(udp_fd, &client_addr);
	if (connect(udp_fd, (sockaddr*)&server_address, sock_len)) perror("udp connect:");
}
void get_basic_info_client(){
	/* mtu, clock_gettime, send */
	int mss = get_mss(tcp_fd);
	long gettimecost = test_clock_gettime(1e4);
	long sendcost = test_send(send_repeat_count, 1472);
	printf("mss is %d, clock_gettime %luus, send %luus, max speed %dMbps\n", mss, gettimecost, sendcost, mss * 8 / sendcost);
	test_clock_nanosleeps();
	test_selects();
}
void send_udp_packets(int packet_number, int packet_size, int microsecond){
	/* send udp packet with us interval */
	timespec sleep_time;
	sleep_time.tv_sec = 0;
	sleep_time.tv_nsec = 1e3 * microsecond;
	ssize_t send_temp, send_total = 0;
	for (int i = 0; i < packet_number; i++) {
		send_temp = send(udp_fd, udpbuffer, packet_size, 0);
		if (send_temp != -1) {
			send_total += send_temp;
		}
		if (i != packet_number - 1) {
			clock_nanosleep(clock_to_use, 0, &sleep_time, NULL);
		}
	}
	printf("send total %zd\n", send_total);
}
void send_at_speed(double speed, int packet_size, int packet_number){
	/* send udp with controlled speed, stop when server loses packet */
	timespec start_time, current_time;
	double current_speed, elapse_time_us, packet_sent = 0;
	clock_gettime(clock_to_use, &start_time);
	while (true) {
		clock_gettime(clock_to_use, &current_time);
		elapse_time_us = timespec2double(current_time) - timespec2double(start_time);
		elapse_time_us *= 1e6;
		current_speed = double(packet_size * 8) * packet_sent / elapse_time_us;
		if (current_speed < speed) {
			send(udp_fd, udpbuffer, packet_size, 0);
			packet_sent += 1;
			if (packet_sent == packet_number) {
				break;
			}
		}
	}
}
long test_send(int repeat, int packet_size){
	/* test send time for repeat times */
	timespec t1, t2, interval;
	interval.tv_sec = 0;
	interval.tv_nsec = 1e6;
	double *diff = new double[repeat];
	for (int i = 0; i < repeat; i++){
		send(udp_fd, udpbuffer, packet_size, 0);
		clock_gettime(clock_to_use, &t1);
		send(udp_fd, udpbuffer, packet_size, 0);
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