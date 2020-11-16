/*
	The functions and variables are declared in recv-module.h
	defined in recv-module.cpp
	organized and called in recv-main.cpp
*/
#ifndef RECV_MODULE_H
#define RECV_MODULE_H

#include "util.h"
#include <sys/socket.h>
#include <arpa/inet.h>
extern int listen_fd, conn_fd, udp_fd, packet_size, listen_port, load_number, inspect_number;
extern socklen_t sock_len;
extern sockaddr_in dest_address, src_address;
extern char udpbuffer[10000];


void parse_parameter(int argc, char *argv[]);
void initialize();
void exchange_parameter();
void udp_receiving();
void udp_receive_packet(int packet_size, int packet_number);
void save_timestamp();
void write2file(timestamp_packet *array, int number, string filename);
void clean();
#endif