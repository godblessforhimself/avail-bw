/*
	The functions and variables used by send-main should be declared in send-module.h, and be defined in send-module.cpp.
*/
#ifndef SEND_MODULE_H
#define SEND_MODULE_H
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
extern int tcp_fd, udp_fd, load_number, packet_size, dest_port, inspection_number;
extern double send_speed, inspection_time[10000];
extern char dest_ip_string[20], udpbuffer[10000];
extern sockaddr_in dest_address, src_address;
extern socklen_t sock_len;


int parse_args(int argc, char *argv[]);
void exchange_parameter();
void initialize();
void send_load();
void send_inspect();
void clean();
void send_at_speed(double speed, int packet_size, int packet_number);
#endif