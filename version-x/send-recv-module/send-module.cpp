/*
	taskset -c 3 ./send-main --speed 1500 --load-size 1472 --inspect-size 24 --dest 192.168.5.1 --port 11106 --number 100 --inspect 800 1000 1200 1400 1600 1800 2000 2200 2400 2600
*/
#include "send-module.h"
#include "util.h"
#include <algorithm>

int tcp_fd = -1, udp_fd = -1, load_number = 100, packet_size = 1472, dest_port = 11106, inspection_number = 0, inspect_size = 1472;
double send_speed = 0, inspection_time[100];
char dest_ip_string[20] = "192.168.5.1", udpbuffer[10000];
sockaddr_in src_address, dest_address;
socklen_t sock_len = sizeof(sockaddr_in);
timespec start_time, current_time;
timestamp_packet tpacket_temp(0, 0);

int parse_args(int argc, char *argv[]) {
    /* 
    */
	static struct option long_options[] = {
		{"speed",   required_argument, 0,  0 },
		{"load-size",    required_argument, 0,  0 },
		{"inspect-size",    required_argument, 0,  0 },
		{"number",  required_argument, 0,  0 },
		{"dest",    required_argument, 0,  0 },
		{"port",    required_argument, 0,  0 },
		{"inspect", required_argument, 0,  0 },
		{0,         0,                 0,  0 }
	};
	#define ARG_EQUAL(x) (strncmp(long_options[option_index].name, (x), max_opt_length) == 0)
	int option_index = 0, c, max_opt_length = 10;
    while ((c = getopt_long(argc, argv, "", long_options, &option_index)) != -1) {
        switch (c) {
            case 0:
				if (ARG_EQUAL("speed")) {
					if (strncmp(optarg, "auto", 4) == 0) {
						send_speed = 0.0;
					} else {
						send_speed = atof(optarg);
					}
				} else if (ARG_EQUAL("load-size")) {
					packet_size = atoi(optarg);
				} else if (ARG_EQUAL("inspect-size")) {
					inspect_size = atoi(optarg);
				} else if (ARG_EQUAL("number")) {
					load_number = atoi(optarg);
				} else if (ARG_EQUAL("dest")) {
					strncpy(dest_ip_string, optarg, sizeof(dest_ip_string));
				} else if (ARG_EQUAL("port")) {
					dest_port = atoi(optarg);
				} else if (ARG_EQUAL("inspect")) {
					optind--;
					inspection_number = 0;
					for( ;optind < argc && *argv[optind] != '-'; optind++){
						inspection_time[inspection_number] = atof(argv[optind]);
						inspection_number++;
					}	
				}
                break;    
			default:
				printf("?? getopt returned character code 0%o ??\n", c);
        }
    }
	if (inspection_number > 0) {
		sort(inspection_time, inspection_time + inspection_number);
	}
	int min_packet_size=(int)sizeof(timestamp_packet);
	if (packet_size < min_packet_size) {
		printf("load packet size %d < min %d\n", packet_size, min_packet_size);
		packet_size = min_packet_size;
	}
	if (inspect_size < min_packet_size) {
		printf("inspect packet size %d < min %d\n", inspect_size, min_packet_size);
		inspect_size = min_packet_size;
	}
	if (true) {
		printf("speed %.2f, size %d, number %d, recv ip %s, recv port %d\n", send_speed, packet_size, load_number, dest_ip_string, dest_port);
		printf("inspection time list:");
		for (int i = 0; i < inspection_number; i++){
			printf(" %.2f", inspection_time[i]);
		}
		printf("\n");
	}
	printf("-------Parse Arg End---------\n");
    return 0;
}
void initialize() {
	set_sockaddr(&dest_address, dest_ip_string, dest_port);
	set_sockaddr(&src_address, dest_port + 1);
	tcp_fd = socket(AF_INET, SOCK_STREAM, 0);
	if (connect(tcp_fd, (sockaddr*)&dest_address, sock_len)) {
		perror("sender tcp connect:");
	}
	udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
	bind_address(udp_fd, &src_address);
	if (connect(udp_fd, (sockaddr*)&dest_address, sock_len)) {
		perror("sender udp connect:");
	}
	printf("--------Initialize End---------\n");
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
	control_parameter control_instance(packet_size, load_number, inspection_number, inspect_size);
	memset(udpbuffer, 0, sizeof(udpbuffer));
	memcpy(udpbuffer, &control_instance, sizeof(control_parameter));
	ret = send(tcp_fd, udpbuffer, CONTROL_MESSAGE_LENGTH_1, 0);
	if (ret != CONTROL_MESSAGE_LENGTH_1) {
		printf("send control message %zd\n", ret);
		exit(0);
	}
	if (true) {
		printf("sender sends parameter: %d, %d, %d\n", packet_size, load_number, inspection_number);
	}
	ret = recv(tcp_fd, udpbuffer, CONTROL_MESSAGE_LENGTH_2, 0);
	if (ret != CONTROL_MESSAGE_LENGTH_2) {
		printf("recv signal %zd\n", ret);
		exit(0);
	} 
	int signal = ntohl(*(uint32_t*)udpbuffer);
	if (true) {
		printf("sender receives receiver signal %d\n", signal);
	}
	if (signal != READY_FOR_RECEIVE) {
		printf("expect ready signal of %d, but got %d\n", READY_FOR_RECEIVE, signal);
		exit(0);
	}
	printf("-----------Parameter Exchange End------------\n");
}
void send_load() {
	/* 
		two conditions:
		1. send at maximum link speed
		The problem is we can not know the real sending time of the packet. We only know the user space time when the packet is sent to the skb_buffer which in most case sooner than it is sent by the physical network interface 

		2. sending at specific rate.
		The problem is whether the rate is achievable. If it is, then how much is the delay or difference between user space sending time and hardware sending time.

	*/
	if (send_speed == 0.0) {
		printf("Rate 0 is not supported\n");
		exit(0);
	} else if (send_speed > 0) {
		if (send_speed >= 2000.0) {
			printf("High precision on rate more than 2000Mbps is hard\n");
			exit(0);
		} else if (send_speed < 2000.0) {
			send_at_speed(send_speed, packet_size, load_number);
		}
	}
}
void send_inspect() {
	ssize_t ret;
	double current_time_us, current_time_double, start_time_us = timespec2double(start_time) * 1e6, elapse_time_us;
	clock_gettime(clock_to_use, &current_time);
	current_time_us = timespec2double(current_time) * 1e6;
	elapse_time_us = current_time_us - start_time_us;
	if (inspection_number > 0 && elapse_time_us > inspection_time[0]) {
		printf("current time %f > inspect[0] %f\n", elapse_time_us, inspection_time[0]);
	}
	memset(udpbuffer, 0, sizeof(udpbuffer));
	for (int i = 0; i < inspection_number; ) {
		clock_gettime(clock_to_use, &current_time);
		current_time_double = timespec2double(current_time);
		current_time_us = current_time_double * 1e6;
		elapse_time_us = current_time_us - start_time_us;
		if (inspection_time[i] <= elapse_time_us) {
			tpacket_temp.update(i, current_time_double);
			memcpy(udpbuffer, &tpacket_temp, sizeof(timestamp_packet));
			ret = send(udp_fd, udpbuffer, inspect_size, 0);
			if (ret != (ssize_t)packet_size) {
				perror("inspect packet:");
			}	
			i++;
		}
	}
}
void clean() {
	close(tcp_fd);
	close(udp_fd);
}
void send_at_speed(double speed, int packet_size, int packet_number) {
	ssize_t min_size = sizeof(timestamp_packet), ret;
	if ((ssize_t)packet_size < min_size) {
		printf("packet size should be larger than %zd\n", min_size);
		exit(0);
	}
	clock_gettime(clock_to_use, &start_time);
	memset(udpbuffer, 0, sizeof(udpbuffer));
	double current_speed, elapse_time_us, current_time_double, start_time_double = timespec2double(start_time);
	int packet_sent = 0;
	while (true) {
		clock_gettime(clock_to_use, &current_time);
		current_time_double = timespec2double(current_time);
		elapse_time_us = current_time_double - start_time_double;
		elapse_time_us *= 1e6;
		current_speed = double(packet_size * packet_sent * 8) / elapse_time_us;
		if (current_speed < speed) {
			tpacket_temp.update(packet_sent, current_time_double);
			memcpy(udpbuffer, &tpacket_temp, sizeof(timestamp_packet));
			ret = send(udp_fd, udpbuffer, packet_size, 0);
			if (ret != (ssize_t)packet_size) {
				perror("Sender udp send:");
			} 
			packet_sent += 1;
			if (packet_sent == packet_number) {
				break;
			}
		}
	}
	printf("------Send End------\n");
}