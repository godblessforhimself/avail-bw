/*
	
*/
#include "recv-module.h"
#include "util.h"
#include <iostream>
#include <fstream>
#include <iomanip>
/*
	listenFd: wait for sender
	connFd: fd for sender connection
	udpFd: fd for datagram
*/
int listenFd = -1, listenPort = 11106, connFd = -1, udpFd = -1;
int repeatNumber = 1, retryNumber = 5, loadNumber = 100, loadSize = 1472, inspectNumber = 0, inspectSize = 1472, inspectJumbo = 1, preheatNumber = 10, trainPacket;
socklen_t sockLen = 0;
sockaddr_in destAddress, srcAddress;
string timestampFilename("timestamp.txt"), resultFilename("result.txt"), logFilename("log.txt");
FILE *timeFile, *resultFile, *logFile;
int recvFlag = 0, busyPoll = 0, runOnce = 0;
signalPacket sigPkt;
double inspectGap, loadInspectGap;
double beginTimeDouble, currentTimeDouble, tmpDouble;
double *pool, *phin, *phout, *tin, *tout, *gin, *gout, *owd;
double owdMin, owdMax, owdEnd;
int poolPtr = 0;
void initPool(){
	trainPacket = loadNumber + inspectNumber * inspectJumbo;
	int sum = preheatNumber * 2 + trainPacket * 2 + (trainPacket - 1) * 2 + trainPacket;
	if (pool) {
		delete [] pool;
		pool = 0;
		poolPtr = 0;
	}
	pool = new double[sum];
	phin = poolAlloc(preheatNumber);
	phout = poolAlloc(preheatNumber);
	tin = poolAlloc(trainPacket);
	tout = poolAlloc(trainPacket);
	gin = poolAlloc(trainPacket - 1);
	gout = poolAlloc(trainPacket - 1);
	owd = poolAlloc(trainPacket);
}
double *poolAlloc(int number) {
	int ret = poolPtr;
	poolPtr += number;
	return pool + ret;
}
void innerMain(int argc, char *argv[]){
	signal(SIGINT, safeExit);
	parseParameter(argc, argv);
	initialize();
	while (1) {
		/* a new sender connects */
		waitConnection();
		openFile();
		/* when a connection comes, get the param, get prepared */
		exchangeParameter();
		/* loop M times */
		mainReceive();
		/* close some socket and files */
		clean();
		printf("End of connection\n");
		if (runOnce == 1) 
			break;
	}
	safeExit(0);
}
void safeExit(int signal) {
	if (pool) {
		delete [] pool;
		pool = 0;
		poolPtr = 0;
	}
	closeSocket();
	closeFile();
	printf("safe exit\n");
	exit(0);
}
void openFile() {
	logFile = fopen(logFilename.c_str(), "a");
	timeFile = fopen(timestampFilename.c_str(), "a");
	resultFile = fopen(resultFilename.c_str(), "a");
}
void qclose(FILE *&fp) {
	if (fp != 0) {
		fclose(fp);
		fp = 0;
	}
}
void closeFile(){
	qclose(timeFile);
	qclose(logFile);
	qclose(resultFile);
}
void closeSocket(){
	close(listenFd);
	close(connFd);
	close(udpFd);
}
static struct option longOptions[] = {
	{"port",      required_argument, 0,  1},
	{"timestamp", required_argument, 0,  2},
	{"result",    required_argument, 0,  3},
	{"log",       required_argument, 0,  4},
	{"polling",   required_argument, 0,  5},
	{"busy-poll", required_argument, 0,  6},
	{"once",            no_argument, 0,  7},
	{0,           0,                 0,  0}
};
void parseParameter(int argc, char *argv[]) {
	int optionIndex = 0, c;
    while ((c = getopt_long(argc, argv, "", longOptions, &optionIndex)) != -1) {
        switch (c) {
			case 1:
				listenPort = atoi(optarg);
				break;
			case 2:
				timestampFilename = string(optarg);
				break;
			case 3:
				resultFilename = string(optarg);
				break;
			case 4:
				logFilename = string(optarg);
				break;
			case 5:
				if (atoi(optarg) == 1) {
					recvFlag |= MSG_DONTWAIT;
				}
				break;
			case 6:
				busyPoll = atoi(optarg);
				break;
			case 7:
				runOnce = 1;
				break;
			default:
				printf("getopt returned character code 0%o\n", c);
				break;
        }
    }
	printf("-------Parse Arg End-----------\n");
}

void initialize() {
	int ret;
	/* listen socket */
	listenFd = socket(AF_INET, SOCK_STREAM, 0); 
	if (listenFd == -1) {
		perror("receiver listen socket:");
	}
	ret = setReuseAddr(listenFd);
	if (ret) {
		perror("receiver tcp reuse:");
	}
	setSockaddr(&destAddress, listenPort);
	ret = bindAddress(listenFd, &destAddress); 
	if (ret) {
		perror("receiver bind:");
	}
	ret = listen(listenFd, 5);
	if (ret) {
		perror("receiver listen:");
	}
	/* udp receive socket */
	udpFd = socket(AF_INET, SOCK_DGRAM, 0);
	if (udpFd == -1) {
		perror("receiver udp socket:");
	}
	ret = setReuseAddr(udpFd);
	if (ret) {
		perror("receiver udp reuse:");
	}
	if (busyPoll >= 0)
		setBusyPoll(udpFd, busyPoll);
	bindAddress(udpFd, &destAddress);
	printf("-------Initialize End-----------\n");
}
void waitConnection(){
	/* connection socket */
	connFd = accept(listenFd, (sockaddr*)&srcAddress, &sockLen);
	if (connFd == -1) {
		perror("receiver accept:");
	}
}
void updateParam(const controlParameter& pkt) {
	repeatNumber = pkt.param[0];
	retryNumber = pkt.param[1];
	loadNumber = pkt.param[2];
	loadSize = pkt.param[3];
	inspectNumber = pkt.param[4];
	inspectSize = pkt.param[5];
	inspectJumbo = pkt.param[6];
	preheatNumber = pkt.param[7];
}
void exchangeParameter() {
	/* receive sender ctrlPacket */
	ssize_t ret;
	memset(udpBuffer, 0, sizeof(udpBuffer));
	ret = recv(connFd, udpBuffer, CONTROL_MESSAGE_LENGTH_1, 0);
	if (ret != CONTROL_MESSAGE_LENGTH_1) {
		printf("send control message %zd\n", ret);
		exit(0);
	}
	controlParameter ctrlPacket;
	memcpy(&ctrlPacket, udpBuffer, sizeof(controlParameter));
	ctrlPacket.network2host();
	/* update global parameters */
	updateParam(ctrlPacket);
	initPool();
	fprintf(logFile, "repeatNumber %d, retryNumber %d, loadNumber %d, loadSize %d, inspectNumber %d, inspectSize %d, inspectJumbo %d, preheatNumber %d\n", repeatNumber, retryNumber, loadNumber, loadSize, inspectNumber, inspectSize, inspectJumbo, preheatNumber);
	fprintf(logFile, "-----------Parameter Exchange End------------\n");
}
int recvPreheat(){
	return recvWithTimeout(0, inspectSize, preheatNumber, 1.0, phin, phout);
}
int recvWithTimeout(int offset, int ps, int pn, double timeout, double *a, double *b) {
	/* if packet gap exceeds timeout, discard the train */
	ssize_t ret;
	int i = 0;
	beginTimeDouble = getTimeDouble();
	while (i < pn) {
		ret = recv(udpFd, udpBuffer, ps, recvFlag);
		currentTimeDouble = getTimeDouble();
		tpBuffer->network2host();
		if (ret == ps) {
			if (tpBuffer->packetId == i + offset) {
				a[i] = tpBuffer->timestamp[0];
				b[i] = currentTimeDouble;
				i++;
				beginTimeDouble = currentTimeDouble;
			} else {
				return 1;
			}
		} else {/* timeout */
			if (timeout > 0 && currentTimeDouble >= beginTimeDouble + timeout) {
				return 1;
			}
		}
	}
	return 0;
}
int recvTrain(){
	/* load, inspect */
	if (recvWithTimeout(0, loadSize, loadNumber, 1.0, tin, tout)) return 1;
	if (recvWithTimeout(loadNumber, inspectSize, inspectNumber * inspectJumbo, 1.0, tin + loadNumber, tout + loadNumber)) return 1;
	return 0;
}
void denoising(){

}
void updateOwd(){
	for (int i = 0; i < trainPacket; i++) {
		owd[i] = tout[i] - tin[i];
	}
	owdMax = owd[loadNumber - 1];
	owdEnd = owd[trainPacket - 1];
	owdMin = min(owd[0],owdEnd);
}
int getRecoverInfo(double &recoverDegree, int &recoverPos) {
	/* 
		define bound * (owdMax - owdMin) + owdMin as recovered
		recoverPos - 1 not recovered
		recoverPos recovered
		recoverPos [loadNumber, loadNumber + inspectNumber)
	*/
	int recovered = 0;
	if (owdMax <= owdMin) {
		recoverDegree = 0;
		return 0;
	}
	recoverDegree = (owdMax - owdEnd) / (owdMax - owdMin);
	double owdBound = 0.05 * (owdMax - owdMin) + owdMin;
	recoverPos = loadNumber;
	while (recoverPos < trainPacket) {
		if (owd[recoverPos] < owdBound) {
			recovered = 1;
			break;
		} else {
			recoverPos++;
		}
	}
	return recovered;
}
double min(double a, double b) {
	return a>b ? b : a;
}
double getX(double x1, double x2, double y1, double y2, double y) {
	double ret;
	if (y1 == y2) {
		return DoubleMax;
	} else {
		ret = x2 + (x1 - x2) * (y - y2) / (y1 - y2);
	}
	return ret;
}
double vaMin(double a, double b, double c, double d) {
	return min(min(a,b),min(c,d));
}
double vaMax(double a, double b, double c) {
	return (max(a,b),c);
}
int getSuggestion() {
	/*
		one way delay & remove noise
		find recover idx & recover degree
		if recovered adjust making it centered
		if not recovered if see obvious recover degree, then estimate 
		if vague recover trend, double duration
		if centered, return satisfied = 1; else return 0;
	*/
	return 1;
}
void getPrediction(){
	fprintf(logFile, "=============Predict Begins===========\n");
	double ub1 = DoubleMax, sendRate, receiveRate, rateChange, lb1 = DoubleMin;
	sendRate = getRate((loadNumber - 1) * loadSize, tin[loadNumber - 1] - tin[0]);
	receiveRate = getRate((loadNumber - 1) * loadSize, tout[loadNumber - 1] - tout[0]);
	rateChange = (receiveRate - sendRate) / sendRate;
	/* if load owd is increasing, vin>vout>A, ub1=vout
	   if load owd does not change, vin<A, lb1=vin */
	if (owd[loadNumber - 1] > owd[0] && rateChange < -0.05){
		ub1 = receiveRate;
		fprintf(logFile, "load owd increasing, %.0f->%.0f, ub1 %.2f, rateChange %.2f\n", sendRate, receiveRate, ub1, rateChange);
	} else {
		lb1 = sendRate;
		fprintf(logFile, "load owd isn't increasing, lb1=sendRate=%.2f\n", lb1);
	}
	/* 
		if inspect owd is increasing, vinspect>A, ub2=vinspect
		if inspect owd is decreasing and not recovered, lb3=vinspect, ub3=(A for recovered at the end)
		if inspect owd is decreasing to recovered, lb4=(A for longer recovered time), ub4=(A for shorter recovered time).
	*/
	double ub2, ub3, ub4, lb3, lb4, inspectRate, recoverDegree;
	int recoverPos, recoverFlag;
	ub2 = ub3 = ub4 = DoubleMax;
	lb3 = lb4 = DoubleMin;
	inspectRate = getRate(inspectNumber * inspectSize * inspectJumbo, tin[trainPacket - 1] - tin[loadNumber - 1]);
	recoverFlag = getRecoverInfo(recoverDegree, recoverPos);
	fprintf(logFile,"inspect rate %.2f\n", inspectRate);
	if (recoverDegree < 0.10) {
		ub2 = inspectRate;
		fprintf(logFile, "inspect owd increasing, ub2 %.2f\n", ub2);
	} else if (!recoverFlag) {
		lb3 = inspectRate;
		ub3 = getRate((loadNumber - 1) * loadSize + inspectNumber * inspectSize * inspectJumbo, tin[trainPacket - 1] - tin[0]);
		fprintf(logFile, "inspect owd decreasing not recovered, lb3, ub3 %.2f-%.2f\n", lb3, ub3);
	} else if (recoverFlag) {
		int bytesL, bytesU;
		double tL, tU;
		bytesL = (loadNumber - 1) * loadSize + (recoverPos - loadNumber + 1) * inspectSize * inspectJumbo;
		tL = tin[recoverPos] - tin[0];
		lb4 = getRate(bytesL, tL);
		bytesU = (loadNumber - 1) * loadSize + max(recoverPos - 1 - loadNumber, 0) * inspectSize * inspectJumbo;
		tU = tin[recoverPos - 1] - tin[0];
		ub4 = getRate(bytesU, tU);
		fprintf(logFile, "%d, %.6f\n%d, %.6f\n", bytesL, tL, bytesU, tU);
		fprintf(logFile,"inspect owd decreasing to recovered & rp=%d, lb4 %.2f ub4 %.2f\n", recoverPos, lb4, ub4);
	}
	/* estimate using linear regression */
	double abw = -1, x;
	int properEstimation = 0;
	if (recoverFlag) {
		if (recoverPos >= loadNumber + 2) {
			for (int posLeft = recoverPos - 1; posLeft >= loadNumber; posLeft--) {
				for (int posRight = recoverPos; posRight > posLeft; posRight--) {
					x = getX(tin[posLeft], tin[posRight], owd[posLeft], owd[posRight], owdMin);
					if (x >= tin[recoverPos - 1] && x <= tin[recoverPos]) {
						properEstimation = 1;
						break;
					}
				}
				if (properEstimation) {
					break;
				}
			}
			if (properEstimation) {
				abw = getRate((loadNumber - 1) * loadSize + (recoverPos - 1) * inspectSize * inspectJumbo, x - tin[0]);
			}
		}
	} else if (recoverDegree > 0.25) {
		for (int posLeft = trainPacket - 2; posLeft >= loadNumber; posLeft--) {
			for (int posRight = trainPacket - 1; posRight > posLeft; posRight--) {
				x = getX(tin[posLeft], tin[posRight], owd[posLeft], owd[posRight], owdMin);
				if (x > tin[trainPacket - 1]) {
					properEstimation = 1;
					break;
				}
			}
			if (properEstimation) {
				break;
			}
		}
		if (properEstimation) {
			abw = getRate((loadNumber - 1) * loadSize + inspectNumber * inspectSize * inspectJumbo, x - tin[0]);
		}
	}
	fprintf(logFile, "recoverFlag %d, recoverDegree %.2f, properEstimation %d\n", recoverFlag, recoverDegree, properEstimation);
	double ub, lb;
	ub = vaMin(ub1, ub2, ub3, ub4);
	lb = vaMax(lb1, lb3, lb4);
	fprintf(logFile, "lower bound %.2f %.2f %.2f\n", lb1, lb3, lb4);
	fprintf(logFile, "upper bound %.2f %.2f %.2f %.2f\n", ub1, ub2, ub3, ub4);
	fprintf(logFile, "abw, lb, ub %.2f,%.2f,%.2f\n", abw, lb, ub);
	fprintf(logFile, "=============END==========\n");
	fprintf(resultFile, "%.2f,%.2f,%.2f\n", abw, lb, ub);
}
void writeTrain(int stream, int train, FILE *fp){
	//fprintf(fp, "stream %d, train %d, loadNumber %d, inspectNumber %d, inspectJumbo %d\n", stream, train, loadNumber, inspectNumber, inspectJumbo);
	for (int i = 0; i < trainPacket; i++) {
		fprintf(fp, "%.6f,%.6f\n", tin[i], tout[i]);
	}
	fprintf(fp, "\n");
}
void mainReceive(){
	int preheatRepeat = 0;
	if (preheatNumber > 0) {
		int preheatLost = 0;
		sigPkt = {ctrlSignal::preheat, 0};
		do {
			if (preheatLost)
				sigPkt = {ctrlSignal::preheatTimeout, 0};
			sendSignal(connFd, &sigPkt);
			preheatLost = recvPreheat();
			preheatRepeat++;
		} while (preheatLost);
		fprintf(logFile, "========== preheat %d tries\n", preheatRepeat);
		for (int i = 0; i < preheatNumber; i++) {
			fprintf(logFile, "%.6f,%.6f\n", phin[i], phout[i]);
		}
		fprintf(logFile, "=========  preheat End=======\n");
	}
	int streamNumber = 0, trainNumber = 0, satisfied = 0, trainLost = 0, exitFlag = 0;
	sigPkt = {ctrlSignal::firstTrain, 0};
	while (1) {
		sendSignal(connFd, &sigPkt);
		if (exitFlag == 1)
			break;
		trainLost = recvTrain();
		if (trainLost == 1) {
			sigPkt = {ctrlSignal::retransmit, 0};
			fprintf(logFile, "train lost detected\n");
		} else if (trainLost == 0) {
			fprintf(logFile, "=====send %d, %d=======\n", streamNumber, trainNumber);
			writeTrain(streamNumber, trainNumber, timeFile);
			satisfied = getSuggestion();
			trainNumber++;
			if (!satisfied && trainNumber < retryNumber) {
				sigPkt = {ctrlSignal::nextTrain, 0};
			} else {
				getPrediction();
				streamNumber++;
				if (streamNumber < repeatNumber) {
					trainNumber = 0;
					sigPkt = {ctrlSignal::nextStream, 0};
				} else {
					sigPkt = {ctrlSignal::end, 0};
					exitFlag = 1;
				}
			}
		}
	};
	fprintf(resultFile, "\n");
}

void clean() {
	close(connFd);
	closeFile();
}