/*  
 *  This file is part of DietTopp.
 *
 *  DietTopp is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  DietTopp is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with DietTopp; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 */

/*
 * Copyright (c) 2004 Andreas Johnsson and Bob Melander
 *
 * Author: Andreas Johnsson
 *         Bob Melander
 *
 */





#include "udppacketsender.h"
#include "debugprint.h"
#include <linux/if_ether.h>

/*
** FUNCTION: UdpPacketSender
**
** USAGE: Constructor. Initializes member variables.
**
** ARGS: A initialized __ProbeInfo struct.
**
** RETURNS: -
*/

UdpPacketSender::UdpPacketSender(void *arg) {
  pI = (__ProbeInfo *) arg;

  try { sndPktBuf = new char[pI->maxPktSize]; }
  catch (...) { throw UdpPacketSenderEx(UPS_ERROR_MEMORY_ALLOCATION_FAILURE,
					"Could not allocate memory"); }

  sizeOfPktBuf = pI->maxPktSize;  
}

/* FUNCTION: ~UdpPacketSender
**
** USAGE: Destructor. Delete buffers.
**
** ARGS:  -
**
** RETURNS: -
*/

UdpPacketSender::~UdpPacketSender() {
  if (sndPktBuf)
    delete sndPktBuf;
}



/* FUNCTION: calculateFunctionLatency
**
** USAGE: calculates how much time it takes to call gettimeofday() 
**        and select() (Idea from Pathload)
**
** ARGS:  -
**
** RETURNS: stores values in internal class variables
*/
void UdpPacketSender::calculateFunctionLatency() {

  long 
    tm,
    latency[NOFUNCCALLS], 
    sortedLatency[NOFUNCCALLS];
    
  struct timeval 
    tv1, 
    tv2, 
    sleepTime, 
    time[NOFUNCCALLS];

  for(int i=0; i<NOFUNCCALLS; i++) {
    gettimeofday(&tv1, NULL);
    gettimeofday(&tv2, NULL);
    latency[i] = tv2.tv_sec*1000000 + tv2.tv_usec - tv1.tv_sec*1000000 - tv1.tv_usec;
  }

  order(latency, sortedLatency, NOFUNCCALLS);
  gettimeofdayLatency = sortedLatency[NOFUNCCALLS / 2];

  debugPrint("gettimeofdayLatency = %d\n", gettimeofdayLatency);

  for(int i=0; i<NOFUNCCALLS; i++) {
    sleepTime.tv_sec = 0;
    sleepTime.tv_usec = 1;
    gettimeofday(&time[i], NULL);
    select(0, NULL, NULL, NULL, &sleepTime);
  }

  for(int i=1; i<NOFUNCCALLS; i++) 
    latency[i-1] = (time[i].tv_sec-time[i-1].tv_sec)*1000000 + (time[i].tv_usec-time[i-1].tv_usec);

  order(sortedLatency, latency, NOFUNCCALLS-1);

  minSleepTime = (sortedLatency[NOFUNCCALLS/2] + sortedLatency[NOFUNCCALLS/2 + 1]) / 2;

  debugPrint("minSleepTime = %d\n", minSleepTime);

  gettimeofday(&time[0], NULL);
  tm = minSleepTime + minSleepTime/4;
  
  return;
}



/* 
** FUNCTION: probe
** 
** USAGE: Sends the UDP packets to a specified port on the 
**        destination host and records the send time of the 
**        sent packets. Results are stored in the 
**        __ProbeInfo struct.
**
** ARGS: -
**
** RETURNS: -
*/

void UdpPacketSender::probe() {
  struct sockaddr_in destAddr;

  struct timeval tmp1, tmp2, sleepTime;
  long long missedTime = 0, tmp = 0, tm_remaining = 0, sleepTimeUsec = 0, diff = 0;
  double t1 = 0, t2 = 0;

  setFixedUdpData(V_PD, pI->sessionID);
  
  memset(&destAddr, 0, sizeof(destAddr));
  destAddr.sin_family = AF_INET;
  destAddr.sin_addr = pI->dstAddr;
  destAddr.sin_port = htons(pI->dstUdpPort);

  calculateFunctionLatency();

  for (int i = 0; i < pI->numPktsToSend; i++) {
    debugPrint("Packet %d: %d\n", i, pI->pktSize[i]);
    debugPrint("Packet %d: spacing = %d\n", i, pI->timeInterval[i]);
  }

  gettimeofday(&tmp1, NULL);
  t1 = (double) tmp1.tv_sec * 1000000.0 + (double) tmp1.tv_usec;

  // Now send the prob packets.
  for (int i = 0; i < pI->numPktsToSend; i++) {
    int result;

    // Make sure that dataSize is not too small. The +25 bytes is due to
    // the fact that ethernet cards add a space corresponding to 25 bytes
    // between all back-to-back packets.

    short pktSize = (pI->pktSizeIsArray ? (pI->pktSize)[i] : *pI->pktSize);
    short dataSize = max (pktSize - (sizeof(struct ip)+sizeof(struct udphdr)+sizeof(struct ethhdr)+25),sizeof(ProbeData));

    long timeInterval = pI->timeIntervalIsArray ? 
      (pI->timeInterval)[i] : *pI->timeInterval;

    // Divide timeInterval by 1000, timeInterval is in nanoseconds. But
    // we want it in microseconds.    
    timeInterval = (long) timeInterval / 1000;

    // Set the packet index and size    
    setDynamicUdpData(i, dataSize);  

    if ((result = sendto(pI->probeFd, 
			 (void*) &(((ProbePkt*) (sndPktBuf))->probeData), 
		       	 dataSize, 0, (struct sockaddr*) &destAddr, 
			 sizeof(struct sockaddr_in))) < dataSize)
      throw UdpPacketSenderEx(UPS_ERROR_SEND_FAILURE,
			      "Internal error: sendto failed");

    gettimeofday(&pI->pInfo[i].sendTime, NULL);
    pI->pInfo[i].pktSize = pktSize;

    // Time intervall between two probe packets
    if(timeInterval > 0) {
      tmp2 = pI->pInfo[i].sendTime;
      t2 = (double) tmp2.tv_sec * 1000000.0 + (double) tmp2.tv_usec;

      tmp = (long) (t2 - t1);	

      tm_remaining = timeInterval - tmp;      

      diff = gettimeofdayLatency>0?gettimeofdayLatency-1:0;

      if(tm_remaining > minSleepTime)
	while((t2 - t1) < ((timeInterval) - diff)) {
	  gettimeofday(&tmp2, NULL);
	  t2 = (double) tmp2.tv_sec * 1000000.0 + (double) tmp2.tv_usec;
	}

      tmp1 = tmp2;
      t1 = t2;
    }
  }
}


/* FUNCTION: nanoSleep
**
** USAGE: NOT USED ANYMORE. 
**        This method is used to add a specific amount of time 
**        between packets to be sent. 
**
** ARGS:  sleepNanoSec - the time (in nano seconds) to sleep.
**
** RETURNS: -
*/

inline void UdpPacketSender::nanoSleep(unsigned long sleepNanoSec) {
  // It the specified sleep time is less than one microsecond
  // we might as well return immediately since busy sleep using
  // 'gettimeofday' only give us microsecond resolution.
  if (sleepNanoSec < 1000)
    return;
  // For sleep times up to 170 milliseconds we use busy wait.
  if (sleepNanoSec < 170000000) {
    struct timeval startTime;
    struct timeval now;
    
    gettimeofday(&startTime, NULL);
    while (!gettimeofday(&now, NULL) &&
	   ((now.tv_sec - startTime.tv_sec)*1000000000 + 
	    (now.tv_usec - startTime.tv_usec)*1000) < sleepNanoSec)
      ;

    return;

  } else {
    // For all other sleep times we use the real nanosleep.

    int noSecs = (int) floor(sleepNanoSec / 1000000000);
    long nanoSecs = (long) (sleepNanoSec - noSecs*1000000000);
    struct timespec sleepTime = {noSecs, 
				 nanoSecs};
    
    while (nanosleep(&sleepTime, &sleepTime) == -1 && errno == EINTR)
      ;
  } 
}


/* FUNCTION: setFixedUdpData
**
** USAGE: Set values in the ProbeData struct that are the same for
**        all packets sent to the receiver.
**
** ARGS:  The version number of the ProbeData struct, the session ID
**        for the current probe session.
**
** RETURNS: -
*/

inline void UdpPacketSender::setFixedUdpData(byte version, short sessionID) {
  ProbePkt *probePkt = (ProbePkt *) sndPktBuf;

  probePkt->probeData.version = version;
  probePkt->probeData.sessionID = htons(sessionID);
}


/* FUNCTION: setDynamicUdpData
**
** USAGE: Set values in the ProbeData struct that change for every packet.
**
** ARGS:  Packet index and the packet size.
**
** RETURNS: -
*/

inline void UdpPacketSender::setDynamicUdpData(short index, int dataSize) {
  ProbePkt* probePkt = (ProbePkt*) sndPktBuf;

  probePkt->probeData.dataSize = htonl(dataSize);
  probePkt->probeData.pktIndex = htons(index);
}

	 



