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





#include "common.h"
#include "analyzeobj.h"
#include "linreg.h"
#include "debugprint.h"



/*
** FUNCTION: AnalyzeObj
**
** USAGE: Constructor. Initializes member variables.
**
** ARGS: -
**
** RETURNS: -
*/

AnalyzeObj::AnalyzeObj() {
  m = 1;   //NO_TRAINS, inits later on.
  loadBuffer = CONST_LOAD_BUFFER_PER_LEVEL; // not used

  defPktSize = 8 * MAX_PACKET_SIZE_FOR_ETHERNET; // should be in bits
  pp = NULL;
  spacing = NULL;
  sizeArray = NULL;
}

/*
** FUNCTION: ~AnalyzeObj
**
** USAGE: Destructor.
**
** ARGS: -
**
** RETURNS: -
*/

AnalyzeObj::~AnalyzeObj() {
  if(pp != NULL)
    delete [] pp;
  if(spacing != NULL)
    delete [] spacing;
  if(sizeArray != NULL)
    delete [] sizeArray;
}


/*
** FUNCTION: generatePropShareList
**
** USAGE: generate a send list when probing for the prop share value
**
** ARGS: arg. Contains probe packet time interval list
**
** RETURNS: arg.
*/

void AnalyzeObj::generatePropShareList(void *arg) {
  this->generateSendList(arg, BACK2BACK, BACK2BACK, 48, 10, 1);
}


/*
** FUNCTION: analyzePair
**
** USAGE: this function implements the analysis part of DietTopp
**        gives a value of available bandwidth and link capacity on screen
**
** ARGS: A __ProbeInfo struct and the propShare value
**
** RETURNS: - 
*/

void AnalyzeObj::analyzePair(void *arg, long long propShare) {

  LinearRegression *lr = NULL, *lr1 = NULL, *lr2 = NULL;
  __ProbeInfo *pI = (__ProbeInfo *) arg;
  long noValues = 0, receivedTimeDiff = 0;
  double y[noLevels+1], x[noLevels+1], z[noLevels+1];
  float totalReceivedTimeDiff = 0;

  long sentTimeDiff = 0;
  float totalSentTimeDiff = 0;

  long noLost = 0, noReceivedLevels = 0;

  o = saved_omin;

  // Calculat time diffs between packets in each sent/received train 
  for (int i = 0; i < noLevels; i++) {  
    for (int j = 0; j < m; j++) {
      for (int k = 0; k < (n-1); k++) {

	if( (pI->pInfo[(i*n*m)+(j*n)+(k+1)].rRecvTime.tv_sec  == 0) &&
	    (pI->pInfo[(i*n*m)+(j*n)+(k+1)].rRecvTime.tv_usec == 0) 
	    ||
	    (pI->pInfo[(i*n*m)+(j*n)+(k)].rRecvTime.tv_sec  == 0) &&
	    (pI->pInfo[(i*n*m)+(j*n)+(k)].rRecvTime.tv_usec == 0) ) {
	  
	  // Do nothing if we have a packet loss, i.e. pI->pInfo... == 0

	  noLost++;

       } else {
       
	  receivedTimeDiff = 1000000 *
	    (pI->pInfo[(i*n*m)+(j*n)+(k+1)].rRecvTime.tv_sec - 
	     pI->pInfo[(i*n*m)+(j*n)+(k)].rRecvTime.tv_sec) +
	    (pI->pInfo[(i*n*m)+(j*n)+(k+1)].rRecvTime.tv_usec - 
	     pI->pInfo[(i*n*m)+(j*n)+(k)].rRecvTime.tv_usec);

	  totalReceivedTimeDiff += receivedTimeDiff/1000000.0;
	  noValues += 1;
	  
	  sentTimeDiff = 1000000 *
	    (pI->pInfo[(i*n*m)+(j*n)+(k+1)].sendTime.tv_sec - 
	     pI->pInfo[(i*n*m)+(j*n)+(k)].sendTime.tv_sec) +
	    (pI->pInfo[(i*n*m)+(j*n)+(k+1)].sendTime.tv_usec - 
	     pI->pInfo[(i*n*m)+(j*n)+(k)].sendTime.tv_usec);
	  
	  totalSentTimeDiff += sentTimeDiff/1000000.0;
       }
      }
    }

    if(noValues == 0) {
      // We do not want to divide by 0. Do not use these results in 
      // our calculation. I.e. all packets in this train got lost.
    } else {

      x[noReceivedLevels] = ((defPktSize) / (1.0 * totalSentTimeDiff / noValues)) / 1048576.0;

      y[noReceivedLevels] = x[noReceivedLevels] / (((defPktSize*1.0) / (1.0*totalReceivedTimeDiff / noValues)) / 1048576.0);

      noReceivedLevels++;

    }

    noValues = 0;
    totalReceivedTimeDiff = 0;
    totalSentTimeDiff = 0;
    
    o += (saved_omax - saved_omin) / noLevels; 
  }



  // When we do our linear regression we also want to use the values from
  // measuring the prop share

  x[noReceivedLevels] = ((defPktSize*1.0) / (1.0 * propShareSentTimeDiff)) / 1048576.0;
  y[noReceivedLevels] = x[noReceivedLevels] / ((1.0*propShare) / 1048576.0);


  /************************************************************

  double tmp_x1[noReceivedLevels], tmp_x2[noReceivedLevels], tmp_y1[noReceivedLevels],
  tmp_y2[noReceivedLevels], tx[noReceivedLevels], ty[noReceivedLevels];
  
  iterateNow = 0;
  
  for(int i=0; i<(noReceivedLevels/2); i++) {
  tmp_x1[i] = x[i];
  tmp_y1[i] = y[i];
  }
  
  for(int i=(noReceivedLevels/2); i<noReceivedLevels+2; i++) {
  tmp_x2[i-noReceivedLevels/2]=x[i];
  tmp_y2[i-noReceivedLevels/2]=y[i];
  }
  
  int a = 0;
  for(int i = 0; i<noReceivedLevels/2; i++) {
  if(y[i] > 1.05 && x[i] < propShare) {
  tx[a]=x[i];
  ty[a]=y[i];
  a++;
  }
  
  }

  lr1 = new LinearRegression(tx, ty, a);
  double abt = (1.0-lr1->getA())/(lr1->getB());
  printf("AB = %fn", abt);

  delete lr1;
  

  lr1 = new LinearRegression(tmp_x1, tmp_y1, noReceivedLevels/2);
  lr2 = new LinearRegression(tmp_x2, tmp_y2, noReceivedLevels/2+1);
  
  double ab1 = (1.0-lr1->getA())/(lr1->getB());
  double ab2 = (1.0-lr2->getA())/(lr2->getB());
  
  if((lr1->getB() < lr2->getB()*1.05) && (lr1->getB() > lr2->getB()*0.95)) {
  printf("Available bandwidth (equal slope) = [%f, %f]\n", 
  min(ab1,ab2), max(ab1, ab2));
  } else if (lr1->getB() < 0.1) {
  printf("Available bandwidth (slope1 = 0) = [%f, %f]\n", 
  ab2-2.5*lr2->getStdErrorEst(), ab2+2.5*lr2->getStdErrorEst());
  } else if(ab1 < ab2 && ab1 > 0) {
  printf("Available bandwidth = [%f, %f]\n", ab1, ab2);
  } else if(ab1 > 0 && ab1 < ab2)
  printf("Available bandwidth <= %f\n", ab1);
  else
  printf("Available bandwidth can not be estimated\nTry again\n");
  
  ****************************************************/
  
  // Do the linear regression
  
  lr = new LinearRegression(x, y, noReceivedLevels+1);
  
  s.stdErr = lr->getStdErrorEst();
  s.coefDeterm = lr->getCoefDeterm();
  s.coefCorrel = lr->getCoefCorrel();
  s.pktLoss = noLost / 2;
    
  // for(int i=0;i<noLevels+1;i++)
  //  printf("%f %f\n", x[i], y[i]);
  // printf("\n\n ");
    
  // printf("Packet loss = %d packets\n", noLost / 2);
  
  printf("The line is y = %f*x + (%f)\n\n", lr->getB(), lr->getA());
  
  printf("Determ = %f\n", lr->getCoefDeterm());
  printf("Correl = %f\n", lr->getCoefCorrel());
  printf("StdErr = %f\n", lr->getStdErrorEst());
  
  printf("Available bandwidth = %f\n", (1.0-lr->getA())/(lr->getB()));
  printf("Link capacity = %f\n", 1/lr->getB());
  
  delete lr;
  
  return;
}


// Not yet implemented
bool AnalyzeObj::iterate() {
  //  fprintf(stderr, "iterateNow = %d\n", iterateNow);

  if (iterateNow == 1)
    return true;
  else
    return false;


}


/*
** FUNCTION: calculatePropShare
**
** USAGE: Calculate the propShare given send and received time values
**
** ARGS: A __ProbeInfo struct and the propShare value
**
** RETURNS: the propShare
*/

float AnalyzeObj::calculatePropShare(void *arg) {
  __ProbeInfo *pI = (__ProbeInfo *) arg; 
  long receivedTimeDiff = 0;
  float totalReceivedTimeDiff = 0.0;
  long noValues = 0, sentTimeDiff = 0;
  double totalSentTimeDiff = 0;
  int loss = 0;

  for (int i = 0; i < noLevels; i++) {  
    for (int j = 0; j < m; j++) {
      for (int k = 0; k < (n-1); k++) {

	if( (pI->pInfo[(i*n*m)+(j*n)+(k+1)].rRecvTime.tv_sec  == 0) &&
	    (pI->pInfo[(i*n*m)+(j*n)+(k+1)].rRecvTime.tv_usec == 0) 
	    ||
	    (pI->pInfo[(i*n*m)+(j*n)+(k)].rRecvTime.tv_sec  == 0) &&
	    (pI->pInfo[(i*n*m)+(j*n)+(k)].rRecvTime.tv_usec == 0) )
	  
	  // Do nothing if we have a packet loss, i.e. pI->pInfo... == 0
	  //	  fprintf(stderr,"Lost packet!\n");
	  loss++;
	else {

	  receivedTimeDiff = 1000000 *
	    (pI->pInfo[(i*n*m)+(j*n)+(k+1)].rRecvTime.tv_sec - 
	     pI->pInfo[(i*n*m)+(j*n)+(k)].rRecvTime.tv_sec) +
	    (pI->pInfo[(i*n*m)+(j*n)+(k+1)].rRecvTime.tv_usec - 
	     pI->pInfo[(i*n*m)+(j*n)+(k)].rRecvTime.tv_usec);

	  totalReceivedTimeDiff += receivedTimeDiff/1000000.0;
	  noValues += 1;


	  sentTimeDiff = 1000000 *
	    (pI->pInfo[(i*n*m)+(j*n)+(k+1)].sendTime.tv_sec - 
	     pI->pInfo[(i*n*m)+(j*n)+(k)].sendTime.tv_sec) +
	    (pI->pInfo[(i*n*m)+(j*n)+(k+1)].sendTime.tv_usec - 
	     pI->pInfo[(i*n*m)+(j*n)+(k)].sendTime.tv_usec);
	  
	  totalSentTimeDiff += sentTimeDiff/1000000.0;
	}    
      }
    }
  }

  debugPrint("Number of lost pkts in propShare phase: %d %d\n", loss, noValues);

  noValues = noValues; // + m;

  propShareSentTimeDiff = totalSentTimeDiff / noValues;

  return (totalReceivedTimeDiff / noValues);
}


/*
** FUNCTION: generateSendList
**
** USAGE: generate a list of time intervals
**
** ARGS: A __ProbeInfo struct and the propShare value, at what probe rate we
** want to start, at what probe rate we want to stop, number of packets in 
** each train, number of trains and the number of levels
**
** RETURNS: The __ProbeInfo struct containing the time interval list
*/

void AnalyzeObj::generateSendList(void *arg, long omin, long omax, int noPkts, int noTrains, int nolevels) {
  __ProbeInfo *pI = (__ProbeInfo *) arg;

  saved_omin = omin;
  saved_omax = omax;
  noLevels = nolevels;
  n = noPkts;
  m = noTrains;
  
  o = omin;  // Start probe at minimum offered rate

  if(pp != NULL)
    delete [] pp;
  if(spacing != NULL)
    delete [] spacing;
  if(sizeArray != NULL)
    delete [] sizeArray;

  pp = new ProbeInfo[n*m*noLevels];
  spacing = new long[n*m*noLevels];
  sizeArray = new short[n*m*noLevels];

  // Construct the spacing array
  for(int i = 0; i<noLevels; i++) {
    
    for(int j = 0; j<m; j++) {

      dt = (int) floor(1000000000*(1.0*defPktSize) / (1.0*o)); // nanoseconds

      T = (long) 
	max ((1.0/0.1) * (dt * (n-1) + dt) - (n-1) * dt,
	     1000000000*
	     ((1.0*defPktSize/o*1.0 - 1.0*defPktSize/omax*1.0)));

      for(int k = 0; k<(n-1); k++) {
	spacing[i*n*m+j*n+k] = dt;
	sizeArray[i*n*m+j*n+k] = MAX_PACKET_SIZE_FOR_ETHERNET;      
      }
      
      if (T < 0) 
	T = MAXLONG-1;
      spacing[i*n*m+j*n + n-1] = T;
      sizeArray[i*n*m+j*n + n-1] = MAX_PACKET_SIZE_FOR_ETHERNET;      
        
    }
    
    o += (omax - omin) / noLevels; //(omax) / noLevels;

  }

  pI->numPktsToSend = n * m * noLevels;
  pI->pktSize = sizeArray;
  pI->pktSizeIsArray = true;
  pI->maxPktSize = MAX_PACKET_SIZE_FOR_ETHERNET;
  pI->timeInterval = spacing;
  pI->timeIntervalIsArray = true;
  pI->pInfo = pp;
  
  return;
}


