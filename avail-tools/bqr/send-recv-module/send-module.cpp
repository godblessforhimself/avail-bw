/*
	preheat packet:
	预热包，preheatNumber个，loadSize的包，间隔preheatGap微秒
	preheat发送失败会重发


	stream:
	数量repeatNumber，间隔streamGap；每个stream包含最多retryNumber个train。train-train的间隔为trainGap。
	train发送失败会重发
	
	train:
	包含负载包和检查包。负载包数量loadNumber，大小loadSize，速率loadRate；检查包数量inspectNumber，大小inspectSize，与负载包间隔loadInspectGap，间隔inspectGap。

	严格按照参数进行发送，参数由接收端程序进行设置；
	需要设置的参数：负载包数量ln、检查包间隔G、可用带宽估计abw

*/
#include "send-module.h"
#include "util.h"
#include <algorithm>

int tcpFd = -1, udpFd = -1, destPort = 11106, globalPacketId = 0, noUpdate = 0;
int repeatNumber = 1, retryNumber = 5, loadNumber = 100, loadSize = 1472, inspectNumber = 0, inspectSize = 1472, preheatNumber = 0;
double loadRate = 0, streamGap = 10000, trainGap = 1000, preheatGap = 1000, inspectGap = 350, loadInspectGap = 40;
double abw = 50;
const double minimalAbw = 50;
const int n1Global = 60;
const double minGapGlobal = 40;
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
	repeatNumber, retryNumber, loadNumber, loadSize, inspectNumber, inspectSize
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
		preheatNumber,
		noUpdate
	};
	ctrlPacket.host2network();
	memset(udpBuffer, 0, sizeof(udpBuffer));
	memcpy(udpBuffer, &ctrlPacket, sizeof(controlParameter));
	ret = send(tcpFd, udpBuffer, CONTROL_MESSAGE_LENGTH_1, 0);
	if (ret != CONTROL_MESSAGE_LENGTH_1) {
		printf("send control message %zd\n", ret);
		exit(0);
	}
	printf("repeatNumber %d, retryNumber %d, loadNumber %d, loadSize %d, inspectNumber %d, inspectSize %d\n", repeatNumber, retryNumber, loadNumber, loadSize, inspectNumber, inspectSize);
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
void arrangeTime(double *inspectTime) {
	/*
		x = (LN+50) * p / A  ; p=1472*8
		设从t1开始以G发检查包，t1=max(begin+x-50G,end+g)
	*/
	double x = (loadNumber + 50) * 1472 * 8 / abw;
	double t1 = max(beginTimeDouble + (x - 50 * inspectGap) * 1e-6, endTimeDouble + loadInspectGap * 1e-6);
	for (int i = 0; i < inspectNumber; i++) {
		inspectTime[i] = t1 + i * inspectGap * 1e-6;
	}
}
void optimizeTime(double *inspectTime, double minGap, int n) {
	/*
		可优化区间为 end+g,inspectTime[n](第n+1个检查包)
		优化条件 区间长度>(n+1)minGap
		第1个时间：计算t1,t2对应的可用带宽A1,A2
		A=n*A1/(n+1)+A2/(n+1)
		计算t=P1/A
		如果t-t1<minGap, 则t=t1+minGap
		第2个时间：
		计算t1,t2对应A1,A2
		A=n*A1/(n+1)+A2/(n+1)
		t=P1/A
		如果t-t1<minGap,则t=t1+minGap
	*/
	double t1, t2;
	t1 = endTimeDouble + loadInspectGap * 1e-6;
	t2 = inspectTime[n];
	int loadBytes = loadSize * loadNumber;
	if (t2 - t1 > minGap * (n + 1) * 1e-6) {
		int i = 0, m;
		double f1, f2, A1, A2, A, t;
		while (i < n) {
			m = n - i;
			f1 = (double)m / (m + 1);
			f2 = (double)1 / (m + 1);
			A1 = (loadBytes + i * inspectSize) / (t1 - beginTimeDouble) * 1e-6;
			A2 = (loadBytes + n * inspectSize) / (t2 - beginTimeDouble) * 1e-6;
			A = f1 * A1 + f2 * A2;
			t = beginTimeDouble + (loadBytes + i * inspectSize) / A * 1e-6;
			if (t - t1 > minGap * 1e-6) {
				inspectTime[i] = t;
				A1 = A;
				for (int j = i + 1; j < n; j++) {
					f1 = (double)(m - j + i) / m;
					f2 = (double)(j - i) / m;
					A = f1 * A1 + f2 * A2; 
					t = beginTimeDouble + (loadBytes + j * inspectSize) / A * 1e-6;
					inspectTime[j] = t;
				}
				break;
			} else {
				t = t1 + minGap * 1e-6;
				inspectTime[i] = t;
				t1 = t;
				i++;
			}
		}
	}
}
void arrangeSpecial(double *inspectTime, double minGap, int n1, double abw) {
	/*
		第一段 [0,n1-1] 共n1个点，时间(end+loadInspectGap,inspectTime[n1])
		第二段 [n1,inspectNumber-1] 共inspectNumber-n1个点，时间以x为中心，间隔0.01x
		(endTime+loadInspectGap,maxTime) 计算带宽A[1],A[100]
		第i个带宽为A[i]=q*A[1]+(1-q)*A[100]
		第i个时间为t[i]=P[i]/A[i]
		如果t[i]-t[i-1]>minGap，
		如果t[i]-t[i-1]<minGap，则t[i]=t[i-1]+minGap，对(t[i],maxTime)重复以上划分
	*/
	inspectTime[0] = endTimeDouble + loadInspectGap * 1e-6;
	// x 对应的包下标
	int middle = n1, middleByte;
	int loadByte = loadSize * loadNumber;
	double x, tBeforeX;
	if ((inspectNumber - n1) % 2 == 0) {
		middle += (inspectNumber - n1) / 2;
	} else {
		middle += (inspectNumber - n1) / 2;
	}
	middleByte = loadByte + inspectSize * middle;
	x = middleByte * 8 / abw * 1e-6 + beginTimeDouble;
	tBeforeX = x - inspectGap * (middle - n1) * 1e-6;
	if (tBeforeX <= inspectTime[0] || tBeforeX - inspectTime[0] <= n1 * inspectGap * 1e-6) {
		/* 第一段长度不够 */
		printf("tBefore %.0f inspectTime[0] %.0f\n", (tBeforeX - beginTimeDouble) * 1e6, (inspectTime[0] - beginTimeDouble) * 1e6);
		for (int i = 1; i < inspectNumber; i++) {
			inspectTime[i] = inspectTime[i - 1] + inspectGap * 1e-6;
		}
	} else if (tBeforeX - inspectTime[0] > n1 * inspectGap * 1e-6){
		/* 设置第二段 */
		for (int i = n1; i < inspectNumber; i++) {
			inspectTime[i] = x + (i - middle) * inspectGap * 1e-6;
		}
		/* 
			第一段长度足够
			设置inspectTime[1]-inspectTime[n1-1]成A[0],A[n1]均匀分配的A
		*/
		double tleft, aleft, pleft, tright, aright, pright, qleft, qright, an, tn, pn;
		int n = 1;
		tright = inspectTime[n1];
		pright = loadByte + inspectSize * (n1 - 1);
		aright = pright * 8 / (tright - beginTimeDouble) * 1e-6;
		while (n < n1) {
			tleft = inspectTime[n - 1];
			pleft = loadByte + inspectSize * (n - 1);
			aleft = pleft * 8 / (tleft - beginTimeDouble) * 1e-6;
			qright = 1.0 / (n1 - n + 1);
			qleft = 1.0 - qright;
			an = qleft * aleft + qright * aright;
			pn = loadByte + inspectSize * n;
			tn = pn * 8 / an * 1e-6 + beginTimeDouble;
			if (tn - tleft >= minGap * 1e-6) {
				for (int i = n; i < n1; i++) {
					qright = (i - n + 1.0) / (n1 - n + 1);
					qleft = 1.0 - qright;
					an = qleft * aleft + qright * aright;
					pn = loadByte + inspectSize * i;
					tn = pn * 8 / an * 1e-6 + beginTimeDouble;
					inspectTime[i] = tn;
				}
				break;
			} else {
				inspectTime[n] = tleft + minGap * 1e-6;
				n++;
			}
		}
	}
}
void sendInspect(){
	/* 
		inspectNumber
		包间隔为inspectGap
		根据给定的A,G，计算开始发送检查包的时间 begin=(loadNumber+0.5*inspectNumber)/A-0.5*inspectNumber*G
		begin=max(begin,endtime)
		将(endTime+loadInspectGap,x)分成两段，第一段带宽均匀，第二段间隔均匀
	*/
	if (inspectNumber <= 0) {
		return;
	}
	tmpDouble = inspectGap * 1e-6;
	double inspectTime[inspectNumber];
	arrangeSpecial(inspectTime, minGapGlobal, n1Global, abw);
	int i = 0;
	while (1) {
		if (i >= inspectNumber) {
			break;
		}
		clock_gettime(clockToUse, &currentTime);
		currentTimeDouble = timespec2double(currentTime);
		if (currentTimeDouble >= inspectTime[i]) {
			setTimestampPacket(globalPacketId++, currentTimeDouble, 0);
			send(udpFd, udpBuffer, inspectSize, 0);
			i++;
		}
	}
	for (int i = 0; i < inspectNumber; i++) {
		printf("%d: %0f\n", i, (inspectTime[i] - beginTimeDouble) * 1e6);
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
			(inspectNumber,inspectSize) packet evenly spaced between (END,duration)
		
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
			printf("LN %d ABW %.0f G %.0f\n", sigPkt.loadNumber, sigPkt.abw, sigPkt.inspectGap);
			if (!noUpdate) {
				abw = sigPkt.abw;
				loadNumber = sigPkt.loadNumber;
				inspectGap = sigPkt.inspectGap;
			}
		} else if (signal == ctrlSignal::nextTrain) {
			printf("LN %d ABW %.0f G %.0f\n", sigPkt.loadNumber, sigPkt.abw, sigPkt.inspectGap);
			if (!noUpdate) {
				loadNumber = sigPkt.loadNumber;
				abw = sigPkt.abw;
				inspectGap = sigPkt.inspectGap;
			}
			smartSleep(trainGap);
		} else if (signal == ctrlSignal::nextStream) {
			printf("LN %d ABW %.0f G %.0f\n", sigPkt.loadNumber, sigPkt.abw, sigPkt.inspectGap);
			if (!noUpdate) {
				loadNumber = sigPkt.loadNumber;
				abw = sigPkt.abw;
				inspectGap = sigPkt.inspectGap;
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