/*
	./recv-main --output output.txt --port 11106
*/
#include "recv-module.h"
#include "util.h"
#include <iostream>
#include <fstream>
#include <iomanip>
int listen_fd = -1, conn_fd = -1, udp_fd = -1, packet_number = -1, packet_size = 1472, listen_port = 11106, load_number = -1, inspect_number = -1, inspect_size = -1;
socklen_t sock_len = 0;
sockaddr_in dest_address, src_address;
char udpbuffer[10000];
timestamp_packet *receive_array;
string timestamp_filename("output.txt");
int recv_flag = 0, busy_poll = 0;

void parse_parameter(int argc, char *argv[]) {
    /* 
    */
	static struct option long_options[] = {
		{"port",    required_argument, 0,  0 },
		{"output",  required_argument, 0,  0 },
		{"polling", required_argument, 0,  0 },
		{"busy-poll",required_argument,0, 0 },
		{0,         0,                 0,  0 }
	};
	#define ARG_EQUAL(x) (strncmp(ptr, (x), max_opt_length) == 0)
	int option_index = 0, c, max_opt_length = 10;
	const char *ptr;
    while ((c = getopt_long(argc, argv, "", long_options, &option_index)) != -1) {
		ptr = long_options[option_index].name;
        switch (c) {
            case 0:
				if (ARG_EQUAL("port")) {
					listen_port = atoi(optarg);
				} else if (ARG_EQUAL("output")) {
					timestamp_filename = string(optarg);
				} else if (ARG_EQUAL("polling")) {
					if (atoi(optarg) == 1) {
						recv_flag |= MSG_DONTWAIT;
					}
				} else if (ARG_EQUAL("busy_poll")) {
					busy_poll = atoi(optarg);
				}
                break;    
			default:
				printf("?? getopt returned character code 0%o ??\n", c);
        }
    }
	if (true) {
		printf("listen port %d\n", listen_port);
	}
	printf("-------Parse Arg End-----------\n");
}

void initialize() {
	int ret;
	// listen socket
	listen_fd = socket(AF_INET, SOCK_STREAM, 0); 
	if (listen_fd == -1) {
		perror("receiver listen socket:");
	}
	ret = set_reuse_addr(listen_fd); 
	if (ret) {
		perror("receiver tcp reuse:");
	}
	set_sockaddr(&dest_address, listen_port);
	ret = bind_address(listen_fd, &dest_address); 
	if (ret) {
		perror("receiver bind:");
	}
	ret = listen(listen_fd, 5);
	if (ret) {
		perror("receiver listen:");
	}
	// udp receive socket
	udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (udp_fd == -1) {
		perror("receiver udp socket:");
	}
	ret = set_reuse_addr(udp_fd);
	if (ret) {
		perror("receiver udp reuse:");
	}
	if (busy_poll >= 0)
		set_busy_poll(udp_fd, busy_poll);
	bind_address(udp_fd, &dest_address);
	// connection socket
	conn_fd = accept(listen_fd, (sockaddr*)&src_address, &sock_len);
	if (conn_fd == -1) {
		perror("receiver accept:");
	}
	printf("-------Initialize End-----------\n");
}
void exchange_parameter() {
	/* 
		The parameters from sender:
		packet size
		load packet number
		inspect packet number

		Signal from receiver:
		ready for receiving
	*/
	ssize_t ret;
	memset(udpbuffer, 0, sizeof(udpbuffer));
	ret = recv(conn_fd, udpbuffer, CONTROL_MESSAGE_LENGTH_1, 0);
	if (ret != CONTROL_MESSAGE_LENGTH_1) {
		printf("recv sender parameter not enough %zd\n", ret);
		exit(0);
	}
	control_parameter control_instance(0, 0, 0, 0);
	memcpy(&control_instance, udpbuffer, sizeof(control_parameter));
	control_instance.network2host();
	packet_size = control_instance.packet_size;
	load_number = control_instance.load_number;
	inspect_number = control_instance.inspect_number;
	inspect_size = control_instance.inspect_size;

	if (true) {
		printf("receiver receives sender parameter: %d, %d, %d, %d\n", packet_size, load_number, inspect_number, inspect_size);
	}
	// send ready signal
	memset(udpbuffer, 0, sizeof(udpbuffer));
	*(uint32_t*)udpbuffer = htonl(READY_FOR_RECEIVE);
	ret = send(conn_fd, udpbuffer, CONTROL_MESSAGE_LENGTH_2, 0);
	if (ret != CONTROL_MESSAGE_LENGTH_2) {
		printf("receiver send ready signal failed %zd\n", ret);
		exit(0);
	}
	if (true) {
		printf("receiver sends ready signal %d\n", READY_FOR_RECEIVE);
	}
	printf("----------Exchange Parameter End----------\n");
}
void udp_receiving() {
	receive_array = new timestamp_packet[load_number + inspect_number];
	if (load_number > 0)
		udp_receive_packet(packet_size, load_number, receive_array);
	if (inspect_number > 0)
		udp_receive_packet(inspect_size, inspect_number, receive_array+load_number);
}
void udp_receive_packet(int packet_size, int packet_number, timestamp_packet *timestamp_array) {
	ssize_t ret;
	timespec receive_timestamp;
	clock_gettime(clock_to_use, &receive_timestamp);
	double begin_time = timespec2double(receive_timestamp), current_time;
	for (int i = 0; i < packet_number; ) {
		ret = recv(udp_fd, udpbuffer, packet_size, recv_flag);
		clock_gettime(clock_to_use, &receive_timestamp);
		current_time = timespec2double(receive_timestamp);
		if (ret == packet_size) {
			timestamp_array[i] = *(timestamp_packet*)udpbuffer;
			timestamp_array[i].network2host();
			timestamp_array[i].timestamp[1] = timespec2double(receive_timestamp);
			i++;
		} else if (current_time - begin_time > 10) {
			printf("Receive Timeout\n");
			break;
		}
	}
}
void save_timestamp() {
	write2file(receive_array, load_number + inspect_number, timestamp_filename);
}
void write2file(timestamp_packet *array, int number, string filename) {
	ofstream fout;
	fout.open(filename);
	fout << fixed << setprecision(6);
	double offset = long(array[0].timestamp[0]);
	for (int i = 0; i < number; i++) {
		fout << array[i].timestamp[0]-offset << " " << array[i].timestamp[1]-offset << endl;
	}
	fout.close();
}
void clean() {
	close(listen_fd);
	close(conn_fd);
	close(udp_fd);
}