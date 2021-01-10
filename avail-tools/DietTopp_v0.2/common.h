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




#ifndef common_h
#define common_h

#ifdef __LINUX_COMPILE
#include <sched.h>
#include <time.h>
#include <bits/time.h>   // for timeval under linux!
#endif

#include <strings.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in_systm.h>
#include <netinet/in.h>
#include <sys/time.h>
#include <values.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <math.h>  // needs floor()
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <netinet/udp.h>

#define START_RAMP       0
#define GET_RESULT       1
#define SEND_BACK_RESULT 2
#define SHUTDOWN         3
#define ACK              4
#define NACK             5

#define DEFAULT_SERVER_UDP_PORT 13232
	#define DEFAULT_SERVER_TCP_PORT 15002

#define V_PD 0         // Version 0 of struct ProbeData 

#define MAX_PACKET_SIZE_FOR_ETHERNET 1500  // Should fit into one ethernet frame

#define PKT_TIMEOUT 2    // 2 seconds should be enough to wait for UDP pkts

#define BACK2BACK 10485760000LL // back2back rate is 100 Mbps... :)

#define PROPSHARE_INTERVALL 0.5

#define NOFUNCCALLS 30

#define MAX_ERRMSG_LEN 255

// Datatype definitions.
#ifdef __NO_U_INT16_T
typedef unsigned short u_int16_t;
#endif
#ifdef __NO_SOCKLEN_T
typedef int socklen_t;
#endif
typedef unsigned char byte;

// These are the values that are measured during the probing.
struct ProbeInfo {
  struct timeval sendTime;             // Send time of packet
  struct timeval rRecvTime;            // Remote receive time of packet
  short pktSize;                       // Size of packet
};

// Information about HOW to probe, and storage of measured times
typedef struct __ProbeInfoStruct {
  struct in_addr dstAddr;      // Destination address
  u_int16_t dstUdpPort;        // Destination UDP port
  int probeFd;                 // UDP socket to send probe packets on
  short sessionID;             // Session ID in all packets
  int numPktsToSend;           // Number of packets that will be sent
  short* pktSize;              // Size of the packets to send
  bool pktSizeIsArray;         // TRUE if pktSize points to an array
  int maxPktSize;              // How big can a UDP packet be, maximum
  long* timeInterval;          // inter packet time
  bool timeIntervalIsArray;    // TRUE if timeInterval points to an array
  ProbeInfo* pInfo;            // The array where we store the measurements
} __ProbeInfo;

// Definition of Control messages between the sender and receiver 
typedef struct __TcpControlMesg {
  short version;
  short mesg;
  short value1;
  short value2;
} TcpControlMesg;

// All probe packets at least contains this in it's data field
struct ProbeData
{
  byte version;                        // Struct version
  int dataSize;                        // Size of the data in probe packet
  //  struct timeval sendTime;             // Send time of the packet
  //  struct timeval rRecvTime;            // Remote receive time of the packet
  //  short numPktsSent;                   // Total number of packets in batch
  short pktIndex;                      // Packet index in a batch, first = 0
  //  u_int16_t replyPort;                 // Port to send reply to
  //  int replyPktSize;                    // Requested size of reply packet
  short sessionID;                     // Each probe session has a unique ID
};  

// This is layout of the probe packets that are sent when probing.
struct ProbePkt
{
  struct ip ipHdr;                     // IP header
  union protoHdrUnion
  {
    struct udphdr udpHdr;              // UDP header
    struct icmp icmpHdr;               // ICMP header
  } protoHdr;
  ProbeData probeData;                 // UDP (or ICMP) data
};


/*
**       Some handy functions...
*/

/* 
** FUNCTION: max
** 
** USAGE: Returns the larger of two numbers.
**
** ARGS: n1 - the first number.
**       n2 - the second number.
**
** RETURNS: The largest of n1 and n2.
*/

template<class T> inline T max(T n1, T n2) {
  if (n1 > n2)
    return n1;
  else
    return n2;
}

/* 
** FUNCTION: min
** 
** USAGE: Returns the smaller of two numbers.
**
** ARGS: n1 - the first number.
**       n2 - the second number.
**
** RETURNS: The smallest of n1 and n2.
*/

template<class T> inline T min(T n1, T n2) {
  if (n1 < n2)
    return n1;
  else
    return n2;
}


/* 
** FUNCTION: order
** 
** USAGE: Bubble sort
**
** ARGS: unsorted array, sorted array, number of elements in array
**
** RETURNS: A sorted array
*/

template<class T> inline T order(T unsorted[], T sorted[], int numElems)
{
  int i, j;
  T temp;
  for(i=0;i<numElems;i++) 
    sorted[i]=unsorted[i];
  for(i=1; i<numElems; i++) {
    for (j=i-1; j>=0; j--) {
      if (sorted[j+1] < sorted[j]) {
	temp=sorted[j]; 
	sorted[j]=sorted[j+1]; 
	sorted[j+1]=temp;
      }
      else break;
    }
  }
}

#endif


