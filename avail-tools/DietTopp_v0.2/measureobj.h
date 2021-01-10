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



#ifndef measureObj_h
#define measureObj_h

#include "common.h"

class MeasureObjEx {
public:
  MeasureObjEx(int errCode, char* errMsg) 
  { 
    errorCode = errCode;
    strcpy(errorMsg, errMsg);
  }

  inline int GetErrorCode() {return errorCode;}
  inline char* GetErrorMsg() {return errorMsg;}

#define MO_ERROR_UDP_SOCKET 1
#define MO_ERROR_SOCKOPT_SIZE 2
#define MO_ERROR_SOCKOPT_IPHDR 3
#define MO_ERROR_RAW_SOCKET 4
#define MO_ERROR_NO_DEST_HOST_SPEC 5
#define MO_ERROR_HOST_LOOKUP_FAILURE 6
#define MO_ERROR_SELECT_FAILURE 7
#define MO_ERROR_MEM_ALLOC_FAILURE 8
#define MO_ERROR_SOCKET_BIND_FAILURE 9
#define MO_ERROR_ROOT_PRIVILEDGES 10
#define MO_ERROR_TCP_SOCKET 11
#define MO_ERROR_SEND_FAILURE 12
#define MO_ERROR_RECEIVE_FAILURE 12

protected:
  int errorCode;
  char errorMsg[MAX_ERRMSG_LEN];
};

class MeasureObj {
 public:
  // Constructors
  MeasureObj(char *dstHost, char *probeDataFile, long minProbe, 
	     long maxProbe, long noSteps, 
	     int dstUdpPort = DEFAULT_SERVER_UDP_PORT,
	     int dstTcpPort = DEFAULT_SERVER_TCP_PORT);

  // Destructors
  ~MeasureObj();

  // Methods
  void tcpDispatcher();


 protected:
  inline int rootPriv();
  void setDstHost(char *newDstHost);
  void setProbeInfoStruct(void *arg);
  TcpControlMesg constructTcpControlMesg(short version, short mesg,
					 short value1, short value2);

  // Variables
  struct sockaddr_in destAddrTcp; // TCP 
  struct sockaddr_in destAddrUdp; // UDP
  struct in_addr dstAddr;         // Address where probe receiver is located
  int probeFd;                    // UDP socket to send probe packets on 
  int tcpFd;                      // TCP socket for control of probing
  struct PortNumStruct {    
    u_int16_t dstUdpPort;         // Port number where probe packets should go
    u_int16_t dstTcpPort;         // TCP port number for control of probing
  } portNums;

  long minProbeRate;
  long maxProbeRate;
  long noStepsBetweenMinMax;
  char *dataFileNameStruct;


};

#endif
