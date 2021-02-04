/*
*/
#include "send-module.h"
#include "util.h"
#include <algorithm>

int tcpFd = -1, udpFd = -1, destPort = 11106, globalPacketId = 0, noUpdate = 0;
int repeatNumber = 1, retryNumber = 5, loadNumber = 100, loadSize = 1472, inspectNumber = 0, inspectSize = 1472, inspectJumbo = 1, preheatNumber = 10;
double loadRate = 0, duration = 0, streamGap = 10000, trainGap = 1000, preheatGap = 1000, inspectGap;
char destIPString[20] = "192.168.5.1";
sockaddr_in srcAddress, destAddress;
socklen_t sockLen = sizeof(sockaddr_in);
signalPacket sigPkt;
timespec beginTime, currentTime, endTime, tempTime;
double beginTimeDouble, currentTimeDouble, endTimeDouble, timeDouble, actualRate, tmpDouble;
timestampPacket tpacketTemp;

int parseArgs(int argc, char *argv[]) {
	static struct option longOptions[] = {
		{"loadRate",   required_argument, 0,  0 },
		{"loadSize",    required_argument, 0,  0 },
		{"inspectSize",    required_argument, 0,  0 },
		{"loadNumber",  required_argument, 0,  0 },
		{"inspectNumber",    required_argument, 0,  0 },
		{"inspectJumbo",    required_argument, 0,  0 },
		{"repeatNumber",    required_argument, 0,  0 },
		{"retryNumber",    required_argument, 0,  0 },
		{"preheatNumber",    required_argument, 0,  0 },
		{"duration",    required_argument, 0,  0 },
		{"streamGap",    required_argument, 0,  0 },
		{"trainGap",    required_argument, 0,  0 },
		{"preheatGap",    required_argument, 0,  0 },
		{"port",    required_argument, 0,  0 },
		{"dest",    required_argument, 0,  0 },
		{"noUpdate",required_argument, 0,  0 },
		{0,         0,                 0,  0 }
	};
	#define ARG_EQUAL(x) (strncmp(longOptions[optionIndex].name, (x), maxOptLength) == 0)
	int optionIndex = 0, c, maxOptLength = 10;
    while ((c = getopt_long(argc, argv, "", longOptions, &optionIndex)) != -1) {
        switch (c) {
            case 0:
				if (ARG_EQUAL("loadRate")) {
					if (strncmp(optarg, "auto", 4) == 0) {
						loadRate = 0.0;
					} else {
						loadRate = atof(optarg);
					}
				} else if (ARG_EQUAL("loadSize")) {
					loadSize = atoi(optarg);
				} else if (ARG_EQUAL("inspectSize")) {
					inspectSize = atoi(optarg);
				} else if (ARG_EQUAL("loadNumber")) {
					loadNumber = atoi(optarg);
				} else if (ARG_EQUAL("inspectNumber")) {
					inspectNumber = atoi(optarg);
				} else if (ARG_EQUAL("inspectJumbo")) {
					inspectJumbo = atoi(optarg);
				} else if (ARG_EQUAL("repeatNumber")) {
					repeatNumber = atoi(optarg);
				} else if (ARG_EQUAL("retryNumber")) {
					retryNumber = atoi(optarg);
				} else if (ARG_EQUAL("preheatNumber")) {
					preheatNumber = atoi(optarg);
				} else if (ARG_EQUAL("duration")) {
					duration = atof(optarg);
				} else if (ARG_EQUAL("streamGap")) {
					streamGap = atof(optarg);
				} else if (ARG_EQUAL("trainGap")) {
					trainGap = atof(optarg);
				} else if (ARG_EQUAL("preheatGap")) {
					preheatGap = atof(optarg);
				} else if (ARG_EQUAL("dest")) {
					strncpy(destIPString, optarg, sizeof(destIPString));
				} else if (ARG_EQUAL("port")) {
					destPort = atoi(optarg);
				} else if (ARG_EQUAL("noUpdate")) {
					noUpdate = atoi(optarg);
				}
                break;
			default:
				printf("getopt returned character code 0%o\n", c);
        }
    }
	int minSize=(int)sizeof(timestampPacket);
	if (loadSize < minSize) {
		printf("load packet size %d < min %d\n", loadSize, minSize);
		loadSize = minSize;
	}
	if (inspectSize < minSize) {
		printf("inspect packet size %d < min %d\n", inspectSize, minSize);
		inspectSize = minSize;
	}
	printf("loadRate %.2f, size %d, number %d, recv ip %s, recv port %d\n", loadRate, loadSize, loadNumber, destIPString, destPort);
	printf("-------Parse Arg End---------\n");
    return 0;
}
void initialize() {
	setSockaddr(&destAddress, destIPString, destPort);
	setSockaddr(&srcAddress, destPort + 1);
	tcpFd = socket(AF_INET, SOCK_STREAM, 0);
	if (connect(tcpFd, (sockaddr*)&destAddress, sockLen)) {
		perror("sender tcp connect:");
	}
	udpFd = socket(AF_INET, SOCK_DGRAM, 0);
	bindAddress(udpFd, &srcAddress);
	if (connect(udpFd, (sockaddr*)&destAddress, sockLen)) {
		perror("sender udp connect:");
	}
	printf("--------Initialize End---------\n");
}
void exchangeParameter() {
	/* 
	repeatNumber, retryNumber, loadNumber, loadSize, inspectNumber, inspectSize, inspectJumbo
	loadRate, duration
	*/
	ssize_t ret;
	controlParameter ctrlPacket = {
		repeatNumber,
		retryNumber,
		loadNumber,
		loadSize,
		inspectNumber,
		inspectSize,
		inspectJumbo,
		preheatNumber
	};
	ctrlPacket.host2network();
	memset(udpBuffer, 0, sizeof(udpBuffer));
	memcpy(udpBuffer, &ctrlPacket, sizeof(controlParameter));
	ret = send(tcpFd, udpBuffer, CONTROL_MESSAGE_LENGTH_1, 0);
	if (ret != CONTROL_MESSAGE_LENGTH_1) {
		printf("send control message %zd\n", ret);
		exit(0);
	}
	printf("repeatNumber %d, retryNumber %d, loadNumber %d, loadSize %d, inspectNumber %d, inspectSize %d, inspectJumbo %d\n", repeatNumber, retryNumber, loadNumber, loadSize, inspectNumber, inspectSize, inspectJumbo);
	printf("-----------Parameter Exchange End------------\n");
}
void clean() {
	close(tcpFd);
	close(udpFd);
}
void sendPreheat(){
	/* (preheatNumber,inspectSize) packet with preheatGap us */
	if (preheatNumber <= 0) {
		return;
	}
	globalPacketId = 0;
	clock_gettime(clockToUse, &beginTime);
	beginTimeDouble = timespec2double(beginTime);
	setTimestampPacket(globalPacketId++, beginTimeDouble, 0);
	send(udpFd, udpBuffer, inspectSize, 0);
	timeDouble = beginTimeDouble + preheatGap * 1e-6;
	int i = 1;
	while (1) {
		if (i >= preheatNumber) {
			break;
		}
		clock_gettime(clockToUse, &currentTime);
		currentTimeDouble = timespec2double(currentTime);
		if (currentTimeDouble >= timeDouble) {
			setTimestampPacket(globalPacketId++, currentTimeDouble, 0);
			send(udpFd, udpBuffer, inspectSize, 0);
			timeDouble += preheatGap * 1e-6;
			i++;
		}
	}
}
void sendLoad(){
	/* (loadNumber,loadSize) packet at loadRate, end at time END */
	if (loadNumber <= 0) {
		return;
	}
	globalPacketId = 0;
	clock_gettime(clockToUse, &beginTime);
	beginTimeDouble = timespec2double(beginTime);
	setTimestampPacket(globalPacketId++, beginTimeDouble, 0);
	send(udpFd, udpBuffer, loadSize, 0);
	int i = 1;
	while (1) {
		if (i >= loadNumber) {
			break;
		}
		clock_gettime(clockToUse, &currentTime);
		currentTimeDouble = timespec2double(currentTime);
		actualRate = getRate(i * loadSize, currentTimeDouble - beginTimeDouble);
		if (actualRate <= loadRate) {
			setTimestampPacket(globalPacketId++, currentTimeDouble, 0);
			send(udpFd, udpBuffer, loadSize, 0);
			i++;
		}
	}
	endTimeDouble = currentTimeDouble;
}
void sendInspect(){
	/* (inspectNumber*inspectJumbo,inspectSize) packet evenly spaced between (END,duration+BEGIN) */
	/* while END>=BEGIN+duration, increase duration */
	if (inspectNumber <= 0) {
		return;
	}
	while (endTimeDouble >= duration * 1e-6 + beginTimeDouble) {
		duration = 2 * duration;
	}
	/* mean gap */
	tmpDouble = (duration * 1e-6 + beginTimeDouble - endTimeDouble) / inspectNumber;
	int i = 0, j = 0;
	timeDouble = endTimeDouble + tmpDouble;
	while (1) {
		if (i >= inspectNumber) {
			break;
		}
		clock_gettime(clockToUse, &currentTime);
		currentTimeDouble = timespec2double(currentTime);
		if (currentTimeDouble >= timeDouble) {
			for (j = 0; j < inspectJumbo; j++) {
				setTimestampPacket(globalPacketId++, currentTimeDouble, 0);
				send(udpFd, udpBuffer, inspectSize, 0);
			}
			timeDouble += tmpDouble;
			i++;
		}
	}
}
void smartSleep(double t) {
	/* sleep t us; if t is small, use loop; if t is large, use clock_nanosleep */
	clock_gettime(clockToUse, &beginTime);
	beginTimeDouble = timespec2double(beginTime);
	if (t <= 0) {
		return;
	} else if (t > 100) {
		tempTime = double2timespec(t * 1e-6);
		clock_nanosleep(clockToUse, 0, &tempTime, NULL);
	}
	while (1) {
		clock_gettime(clockToUse, &currentTime);
		currentTimeDouble = timespec2double(currentTime);
		if (currentTimeDouble >= beginTimeDouble + t * 1e-6){
			break;
		}
	}
	return;
}
void mainSend(){
	/*
		repeatNumber streams separated by streamGap
		<=retryNumber trains controlled by receiver signal

		one train:
			(loadNumber,loadSize) packet at loadRate, end at time END
			(inspectNumber*inspectJumbo,inspectSize) packet evenly spaced between (END,duration)
		
		signals by receiver:
			1. next stream
			2. next retry followed by new duration parameter
			3. retransmit train with same parameter
		
	*/
	int signal;
	while (1) {
		signal = waitSignal(tcpFd, &sigPkt);
		if (signal == ctrlSignal::preheat || signal == ctrlSignal::preheatTimeout) {
			sendPreheat();
			continue;
		} else if (signal == ctrlSignal::firstTrain) {
			;
		} else if (signal == ctrlSignal::nextTrain) {
			if (noUpdate == 0) {
				printf("update duration %.0f -> %.0f\n", duration, sigPkt.duration);
				duration = sigPkt.duration;
			}
			smartSleep(trainGap);
		} else if (signal == ctrlSignal::nextStream) {
			if (noUpdate == 0) {
				printf("update duration %.0f -> %.0f\n", duration, sigPkt.duration);
				duration = sigPkt.duration;
			}
			smartSleep(streamGap);
		} else if (signal == ctrlSignal::retransmit) {
			smartSleep(trainGap);
		} else if (signal == ctrlSignal::end) {
			break;
		} else {
			break;
		}
		sendLoad();
		sendInspect();
	}
}
void innerMain(int argc, char *argv[]){
	parseArgs(argc, argv);
	/* initialize tcp and udp socket */
	initialize();
	/* exchange parameters */
	exchangeParameter();
	/* begin to send main */
	mainSend();
	clean();
}