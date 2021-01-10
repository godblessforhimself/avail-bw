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




#ifndef analyzeObj_h
#define analyzeObj_h

/* Many structs and variables are not used anymore */

/* These defines are not used anymore */
#define HIST_NO_INTERVAL 10000
#define NUMBER_OF_BOXES 50

#define MAX_NUMBER_OF_ELEMENTS 1000

#define CONST_LOAD_BUFFER_PER_LEVEL 1920000//180000//1920000 //960000 //1966080 //3840000 // to get 64 packets per train, when using 5 trains per offered rate, each packet having a size of 1500*8 bits
 //1966080 //983040 // 122880*8 bits = 8*120 * 2^10 = 120kB
	
#define NO_TRAINS 50

#define O_MAX 10485760   // 10485760 bps = 10 * 2^20 = 10Mbps
#define O_MIN 1048576    // 524288 bps = 0.5 * 2^20 = 0.5Mbps

#define NO_LEVELS 10      // 10? number of levels between O_MAX and O_MIN


/* An exception class for AnalyzeObj */
class AnalyzeObjEx {
public:
  AnalyzeObjEx(int errCode, char* errMsg) 
  { 
    errorCode = errCode;
    strcpy(errorMsg, errMsg);
  }

  inline int GetErrorCode() {return errorCode;}
  inline char* GetErrorMsg() {return errorMsg;}

#define AO_UNDEF_ERROR 1

protected:
  int errorCode;
  char errorMsg[MAX_ERRMSG_LEN];
};


class AnalyzeObj {
 public:
  // Constructors
  AnalyzeObj();

  // Destructors
  ~AnalyzeObj();

  float calculatePropShare(void *arg);
  void generatePropShareList(void *arg);
  void generateSendList(void *arg, long omin, long omax, int noPkts, int noTrains, int nolevels);
  void analyzePair(void *arg, long long propShare);
  bool iterate();

 protected:

  // A histogram structure... 
  /*
    typedef struct __histogram {
    int histogram[HIST_NO_INTERVAL];
    int noIntervals;
    long dt;
    long median;
    long minValueX;
    long maxValueX;
    long numberOfTimeDiffs;
    } histogram;
  */

  /* A struct to store linear regression info */
  typedef struct __stat {
    float stdErr;
    float coefDeterm;
    float coefCorrel;
    int pktLoss;
  } stat;
  
  stat s;

  short *sizeArray;
  long *spacing;
  ProbeInfo *pp;

  int dt;           // time between two packets
  long T;            // time between two trains in the same level
  long o;           // offered rate
  int m;            // number of trains on one level
  int n;            // number of packets in one train
  int noLevels;     // number of levels between offered(min) and offered(max)
  int loadBuffer;   // send a const amount of bits/level
  short defPktSize; // default pkt size, in BITS
  long saved_omin;
  long saved_omax;
  double propShareSentTimeDiff;
  int iterateNow;

};








#endif
