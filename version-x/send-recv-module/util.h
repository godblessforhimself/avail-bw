/*
	The functions and variables which are used by both sender and receiver should be declared in util.h
	The implements should be in util.cpp
*/
#ifndef UTIL_H
#define UTIL_H
#include <time.h>
#include <assert.h>
#include <netinet/tcp.h> // TCP_MAXSEG
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h> //close
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <algorithm> //sort
#include <iostream>
#include <getopt.h>
using namespace std;
#define CONTROL_MESSAGE_LENGTH_1 (100)
#define CONTROL_MESSAGE_LENGTH_2 (10)
#define READY_FOR_RECEIVE (77017)
struct control_parameter {
	int packet_size, load_number, inspect_number;
	control_parameter(int x, int y, int z);
	void network2host();
};
struct timestamp_packet {
	int packet_id;
	double timestamp[2];
	timestamp_packet();
	timestamp_packet(int x, double y);
	void update(int x, double y);
	void network2host();
};
extern clockid_t clock_to_use;
extern timespec program_begin, program_end;
int set_reuse_addr(int fd);
void set_sockaddr(sockaddr_in *addr, int port);
void set_sockaddr(sockaddr_in *addr, char *ip_str, int port);
void set_busy_poll(int fd, int busy_poll);
int bind_address(int fd, sockaddr_in *addr);
int get_mss(int conn_fd);
double timespec2double(timespec t);
timespec double2timespec(double t);
void print_timespec(timespec t);
void tick();
void tock();
#endif