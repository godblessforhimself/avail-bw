/*
	The main of sender
	using the variables and functions declared in send-module.h
*/
#include "send-module.h"
#include "util.h"
int main(int argc, char *argv[]) {
	parse_args(argc, argv);
	// initialize tcp and udp socket
	initialize();
	// exchange parameters
	exchange_parameter();
	// begin to send load packets
	timespec sleep_time = {1, 0};
	clock_nanosleep(clock_to_use, 0, &sleep_time, NULL);
	send_load();
	// begin to send inspect packets
	send_inspect();
	clean();
}