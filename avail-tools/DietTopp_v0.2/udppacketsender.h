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






#ifndef udpPacketSender_h
#define udpPacketSender_h

#include "common.h"

// An error class for the UdpPacketSender class
//
class UdpPacketSenderEx {
 public:
  UdpPacketSenderEx(int errCode, char* errMsg) 
    { 
      errorCode = errCode;
      strcpy(errorMsg, errMsg);
  }
  
  inline int GetErrorCode() {return errorCode;}
  inline char* GetErrorMsg() {return errorMsg;}
  
#define UPS_ERROR_SEND_FAILURE 1
#define UPS_ERROR_MEMORY_ALLOCATION_FAILURE 2
  
 protected:
  int errorCode;
  char errorMsg[MAX_ERRMSG_LEN];
};


// The purpose of this class is to send probe packets to a 
// probe receiver. All information needed to probe is contained
// in a __ProbeInfo struct given as argument to the constructor.
//
class UdpPacketSender {
 public:
  // Constructors
  UdpPacketSender(void *arg);

  // Destructors
  ~UdpPacketSender();

  // Methods
  void probe();

 protected:
  inline void nanoSleep(unsigned long timeInterval);
  inline void setFixedUdpData(byte version, short sessionID);
  inline void setDynamicUdpData(short index, int dataSize);

  void calculateFunctionLatency();

  // Variables
  __ProbeInfo *pI;            // All info needed for probing
  char* sndPktBuf;            // Buffer for packets to send
  int sizeOfPktBuf;           // Size of sndPktBuf
  
  long gettimeofdayLatency;   // latency when calling gettimeofday()
  long minSleepTime;          // min sleep time when using select()
  long minTimerIntr;          // something else...

};

#endif

