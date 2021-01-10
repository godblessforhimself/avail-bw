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




#ifndef receiverObj_h
#define receiverObj_h

#include "common.h"



// An error class for the ProbeReceiver class.

class ReceiverObjEx
{
public:
  ReceiverObjEx(int errCode, char* errMsg) 
  { 
    errorCode = errCode;
    strcpy(errorMsg, errMsg);
  }

  inline int GetErrorCode() {return errorCode;}
  inline char* GetErrorMsg() {return errorMsg;}

#define ROE_ERROR_UDP_SOCKET 1
#define ROE_ERROR_SOCKOPT_SIZE 2
#define ROE_ERROR_SOCKOPT_IPHDR 3
#define ROE_ERROR_RAW_SOCKET 4
#define ROE_ERROR_NO_DEST_HOST_SPEC 5
#define ROE_ERROR_HOST_LOOKUP_FAILURE 6
#define ROE_ERROR_SELECT_FAILURE 7
#define ROE_ERROR_MEM_ALLOC_FAILURE 8
#define ROE_ERROR_SOCKET_BIND_FAILURE 9
#define ROE_ERROR_TCP_SOCKET 10
#define ROE_ERROR_RECEIVE_FAILURE 11
#define ROE_ERROR_SEND_FAILURE 12
#define ROE_ERROR_SOCKET_ACCEPT_FAILURE 13

protected:
  int errorCode;
  char errorMsg[MAX_ERRMSG_LEN];
};


class ReceiverObj {
 public:
  // Constructors
  ReceiverObj(int srvUdpPort = DEFAULT_SERVER_UDP_PORT,
	      int srvTcpPort = DEFAULT_SERVER_TCP_PORT);

  // Destructors
  ~ReceiverObj();

  // Methods
  void startReceiver();
  
 protected:
  void handleProbeSession(int clientSocket);
  TcpControlMesg constructTcpControlMesg(short version, short mesg, 
					 short value1, short value2);
  void probeReceiver(int clientSocket);
  void sendBackResults(int clientSocket);
  void cleanUdpInQueue();

  // Variables
  struct sockaddr_in clientAddr; 
  struct sockaddr_in listenAddr;
  struct sockaddr_in replyAddr;
  socklen_t clientLen;

  struct timeval *timeArray;
  short numPktsToReceive;
  short sessionID;
  struct in_addr thisHost;   // Address of this host (the server)
  char* pktBuf;              // Buffer for packets to receive
  int sizeOfPktBuf;          // Amount of memory allocated for the buffer
  int udpFd;                 // "Socket" that will receive udp packets
  int tcpFd;                 // "Socket" that will reply data to probeG
  u_int16_t lstUdpPort;      // UDP port to listen on for probe packets
  u_int16_t lstTcpPort;      // TCP port to listen on for out of probe traffic 
  

};


#endif



