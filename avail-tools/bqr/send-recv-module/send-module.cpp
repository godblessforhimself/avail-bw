/*
	preheat packet:
	预热包，preheatNumber个，loadSize的包，间隔preheatGap微秒
	preheat发送失败会重发


	stream:
	数量repeatNumber，间隔streamGap；每个stream包含最多retryNumber个train。train-train的间隔为trainGap。
	train发送失败会重发
	
	train:
	包含负载包和检查包。负载包数量loadNumber，大小loadSize，速率loadRate；检查包数量inspectNumber，大小inspectSize，与负载包间隔loadInspectGap，间隔inspectGap。

	负载包数量下限、上限
	检查包数量上限
	
*/
#include "send-module.h"
#include "util.h"
#include <algorithm>

int tcpFd = -1, udpFd = -1, destPort = 11106, globalPacketId = 0, noUpdate = 0;
int repeatNumber = 1, retryNumber = 5, loadNumber = 100, loadSize = 1472, inspectNumber = 0, inspectSize = 1472, inspectJumbo = 1, preheatNumber = 10;
double loadRate = 0, streamGap = 10000, trainGap = 1000, preheatGap = 1000, inspectGap = 200, loadInspectGap, jumboGap = 50;
char destIPString[20] = "192.168.5.1";
sockaddr_in srcAddress, destAddress;
socklen_t sockLen = sizeof(sockaddr_in);
signalPacket sigPkt;
timespec beginTime, currentTime, endTime, tempTime;
double beginTimeDouble, currentTimeDouble, endTimeDouble, timeDouble, actualRate, tmpDouble;
timestampPacket tpacketTemp;
static struct option longOptions[] = {
	{"loadRate",   required_argument, 0, 1},
	{"loadSize",    required_argument, 0,  2},
	{"inspectSize",    required_argument, 0,  3},
	{"loadNumber",  required_argument, 0,  4},
	{"inspectNumber",    required_argument, 0,  5},
	{"inspectJumbo",    required_argument, 0,  6},
	{"repeatNumber",    required_argument, 0,  7},
	{"retryNumber",    required_argument, 0,  8},
	{"preheatNumber",    required_argument, 0,  9},
	{"inspectGap",    required_argument, 0,  10},
	{"loadInspectGap",    required_argument, 0,  11},
	{"streamGap",    required_argument, 0,  12},
	{"trainGap",    required_argument, 0,  13},
	{"preheatGap",    required_argument, 0,  14},
	{"port",    required_argument, 0,  15},
	{"dest",    required_argument, 0,  16},
	{"noUpdate",required_argument, 0,  17},
	{"jumboGap",required_argument, 0,  18},
	{0,         0,                 0,  0}
};
int parseArgs(int argc, char *argv[]) {
	int optionIndex = 0, c;
    while ((c = getopt_long(argc, argv, "", longOptions, &optionIndex)) != -1) {
        switch (c) {
            case 1:
				loadRate = atof(optarg);
				break;
			case 2:
				loadSize = atoi(optarg);
				break;
			case 3:
				inspectSize = atoi(optarg);
				break;
			case 4:
				loadNumber = atoi(optarg);
				break;
			case 5:
				inspectNumber = atoi(optarg);
				break;
			case 6:
				inspectJumbo = atoi(optarg);
				break;
			case 7:
				repeatNumber = atoi(optarg);
				break;
			case 8:
				retryNumber = atoi(optarg);
				break;
			case 9:
				preheatNumber = atoi(optarg);
				break;
			case 10:
				inspectGap = atof(optarg);
				break;
			case 11:
				loadInspectGap = atof(optarg);
				break;
			case 12:
				streamGap = atof(optarg);
				break;
			case 13:
				trainGap = atof(optarg);
				break;
			case 14:
				preheatGap = atof(optarg);
				break;
			case 15:
				destPort = atoi(optarg);
				break;
			case 16:
				strncpy(destIPString, optarg, sizeof(destIPString));
				break;
			case 17:
				noUpdate = atoi(optarg);
				break;
			case 18:
				jumboGap = atoi(optarg);
				break;
			default:
				printf("getopt returned character code 0%o\n", c);
				break;
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
	/* 
		inspectNumber*inspectJumbo
		如果inspectJumbo=1，包间隔为inspectGap
		如果inspectJumbo>1，inspectGap需要大于jumboGap*inspectJumbo
	*/
	if (inspectNumber <= 0) {
		return;
	}
	tmpDouble = inspectGap * 1e-6 - (inspectJumbo - 1) * jumboGap * 1e-6;
	if (tmpDouble < 0) {
		printf("inspect gap %.0f us, jumboGap %.0f us, jumboNum %d\n", inspectGap, jumboGap, inspectJumbo);
		return;
	}
	int i = 0;
	timeDouble = endTimeDouble + (loadInspectGap - (inspectJumbo - 1) * jumboGap) * 1e-6;
	while (1) {
		if (i >= inspectNumber * inspectJumbo) {
			break;
		}
		clock_gettime(clockToUse, &currentTime);
		currentTimeDouble = timespec2double(currentTime);
		if (currentTimeDouble >= timeDouble) {
			setTimestampPacket(globalPacketId++, currentTimeDouble, 0);
			send(udpFd, udpBuffer, inspectSize, 0);
			i++;
			if (i % inspectJumbo == 0) {
				timeDouble += inspectGap * 1e-6;
			} else {
				timeDouble += tmpDouble;
			}
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
				printf("param %.0f\n", sigPkt.param);
			}
			smartSleep(trainGap);
		} else if (signal == ctrlSignal::nextStream) {
			if (noUpdate == 0) {
				printf("param %.0f\n", sigPkt.param);
			}
			smartSleep(streamGap);
		} else if (signal == ctrlSignal::retransmit) {
			smartSleep(trainGap);
		} else if (signal == ctrlSignal::end) {
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