/*
	calling functions from recv-module.h and util.h
*/
#include "recv-module.h"
#include "util.h"

int main(int argc, char *argv[]) {
	tick();
	parse_parameter(argc, argv);
	// initialize tcp listen socket and wait
	initialize();
	// when a connection comes, get the param, get udp prepared. Then echo 'ready' back
	exchange_parameter();
	// udp receiving
	udp_receiving();
	// save to file
	save_timestamp();
	clean();
	tock();
}