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
#include "measureobj.h"
#include "udppacketsender.h"
#include "analyzeobj.h"
#include "debugprint.h"

/*
** FUNCTION: MeasureObj
**
** USAGE: Constructor. Setup TCP socket and connects to probe receiver.
**        Setup UDP socket to send probe packets on. If running on a
**        Linux system, modify the kernel scheduler algorithm and 
**        priority (if root).
**
** ARGS: TO BE MODIFIED
**
** RETURNS: -
*/

MeasureObj::MeasureObj(char *dstHost, char *probeDataFile, long minProbe, 
		       long maxProbe, long noSteps, int dstUdpPort,
		       int dstTcpPort) {
  

  setDstHost(dstHost);
  portNums.dstUdpPort = dstUdpPort;
  portNums.dstTcpPort = dstTcpPort;

  dataFileNameStruct = strdup(probeDataFile);
  minProbeRate = minProbe;
  maxProbeRate = maxProbe;
  noStepsBetweenMinMax = noSteps;

  // Perhaps this work under Solaris to? I guess so actually.. 
#ifdef __LINUX_COMPILE
  // If we are running under Linux, as root, we want to have high 
  // priority within the kernel scheduler
  struct sched_param sp;
  sp.sched_priority = sched_get_priority_max(SCHED_FIFO);
  if(rootPriv()) 
    sched_setscheduler(0, SCHED_FIFO, &sp);
#endif

  // Setup the UDP probing socket 
  if ((probeFd = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    throw MeasureObjEx(MO_ERROR_UDP_SOCKET, 
		       "Could not create udp client socket");
  
  memset(&destAddrUdp, 0, sizeof(destAddrUdp));
  destAddrUdp.sin_family = AF_INET;
  destAddrUdp.sin_addr.s_addr = inet_addr(dstHost);
  destAddrUdp.sin_port = htons(dstUdpPort);

  // Setup the TCP communication channel 
  if ((tcpFd = socket(AF_INET, SOCK_STREAM, 0)) < 0) 
    throw MeasureObjEx(MO_ERROR_TCP_SOCKET, 
		       "Could not create tcp client socket");
  
  memset(&destAddrTcp, 0, sizeof(destAddrTcp));
  destAddrTcp.sin_family = AF_INET;
  destAddrTcp.sin_addr.s_addr = inet_addr(inet_ntoa(dstAddr));
  destAddrTcp.sin_port = htons(dstTcpPort);

  // Now connect to probe receiver
  if (connect(tcpFd, (struct sockaddr *) &destAddrTcp, sizeof(destAddrTcp)) < 0)
    throw MeasureObjEx(MO_ERROR_TCP_SOCKET, 
		       "Could not connect to tcp server");
  
  debugPrint("Connected to %s:%d\n", dstHost, dstTcpPort);
}



/*
** FUNCTION: ~MeasureObj
**
** USAGE: Destructor. Close the TCP socket.
**
** ARGS: -
**
** RETURNS: -
*/

MeasureObj::~MeasureObj() {
  
  close(tcpFd);     // Close down the TCP connection
}


/* 
** FUNCTION: tcpDispatcher
** 
** USAGE: The actual probe engine. Talks with the probe receiver via TCP,
**        constructs UdpPacketSender objects to probe, constructs AnalyzeObj
**        to analyze the results send back from the probe receiver.
**
** ARGS: -
**
** RETURNS: -
*/

void MeasureObj::tcpDispatcher() {
  bool endProbeSession = false;
  bool calculatePropShare = true;
  __ProbeInfo probeInfo;
  TcpControlMesg tcm;
  TcpControlMesg rep;
  UdpPacketSender *ups = NULL;
  AnalyzeObj *ao = NULL;
  long propShare = 0;
  int iteration = 1;

  ao = new AnalyzeObj();

  

  debugPrint("Set values in the __ProbeInfo struct\n");
  setProbeInfoStruct(&probeInfo);  




  while(!endProbeSession) {
    debugPrint("Set the spacing and pktsize values in __ProbeInfo struct\n");


    // Generate list of packet spacings. Fist calculate propShare. Then 
    // generate a list of ab and lc measurement probes. 
    // The number of pakets per train depends on the proportional share

    if(calculatePropShare == true)
      ao->generatePropShareList(&probeInfo);
    else {
      if((propShare/1048576) < 11)
	ao->generateSendList(&probeInfo, (long) trunc(propShare*1), (long) trunc(propShare*1.5), 16, 5, noStepsBetweenMinMax);
      else if((propShare/1048576) < 50)
	ao->generateSendList(&probeInfo, (long) trunc(propShare*1), (long) trunc(propShare*1.5), 32, 5, noStepsBetweenMinMax);
      else
	ao->generateSendList(&probeInfo, (long) trunc(propShare*1), (long) trunc(propShare*1.5), 64, 5, noStepsBetweenMinMax);
    }




    // Send START_RAMP to receiver
    do {
      tcm = constructTcpControlMesg(0, START_RAMP, probeInfo.numPktsToSend, 0);
      debugPrint("tcm.mesg = %d, numPktsToSend = %d\n", ntohs(tcm.mesg), ntohs(tcm.value1));
     
      if (send(tcpFd, (char *) &tcm, sizeof(TcpControlMesg), 0) < 0)
	throw MeasureObjEx(MO_ERROR_SEND_FAILURE, 
			   "Can't send packet on TCP connection\n");

      // RECEIVE ANSWER
      if (recv(tcpFd, (char *) &rep, sizeof(TcpControlMesg), 0) == -1)
	throw MeasureObjEx(MO_ERROR_RECEIVE_FAILURE, 
			   "Can't receive packet from TCP socket\n");

    } while(ntohs(rep.mesg)!=ACK);





    // Store the sessionID in the probeInfo struct
    probeInfo.sessionID = ntohs(rep.value1);

    // Construct a UdpIpPacketSender objekt
    ups = new UdpPacketSender(&probeInfo);

    // Send all probe data
    ups->probe();

    // delete ups;  
    delete ups;







    debugPrint("GET RESULT\n");

    // Send GET_RESULT to the receiver
    do {
      tcm = constructTcpControlMesg(0, GET_RESULT, 0, 0);
      
      if (send(tcpFd, (char *) &tcm, sizeof(TcpControlMesg), 0) < 0)
	throw MeasureObjEx(MO_ERROR_SEND_FAILURE, 
			   "Can't send packet on TCP connection\n");
      
      // RECEIVE ANSWER, rep.value1 contains the number of timevals to
      // receive
      if (recv(tcpFd, (char *) &rep, sizeof(TcpControlMesg), 0) == -1)
	throw MeasureObjEx(MO_ERROR_RECEIVE_FAILURE, 
			   "Can't receive packet from TCP socket\n"); 

      debugPrint("rep.mesg = %d\n", ntohs(rep.mesg));

    } while(ntohs(rep.mesg)!=ACK);






    // Receive results from receiver
    struct timeval timeVar;

    debugPrint("receive results\n");
    debugPrint("rep.value1 = %d\n", ntohs(rep.value1));

    for(int j=0; j<ntohs(rep.value1); j++) {
      
      if (recv(tcpFd, (char *) &timeVar, sizeof(struct timeval), 0) == -1)
	throw MeasureObjEx(MO_ERROR_RECEIVE_FAILURE, 
			   "Can't receive packet from TCP socket\n");
      
      probeInfo.pInfo[j].rRecvTime.tv_sec = ntohl(timeVar.tv_sec);     
      probeInfo.pInfo[j].rRecvTime.tv_usec = ntohl(timeVar.tv_usec);     

      debugPrint("Packet %d was received at %d:%d\n", j, ntohl(timeVar.tv_sec), ntohl(timeVar.tv_usec));
      debugPrint("Packet %d was received at %d:%d\n", j, probeInfo.pInfo[j].rRecvTime.tv_sec, probeInfo.pInfo[j].rRecvTime.tv_usec);
    }



    /* Should we calculate the propShare? If yes, do that. If not, we 
     * should analyze the packets using DietTopp
     */

    if(calculatePropShare == true) {
      propShare = (long) trunc((MAX_PACKET_SIZE_FOR_ETHERNET*8.0 / ao->calculatePropShare(&probeInfo)));
      debugPrint("Prop. share = %d Mbps\n\n", propShare);
      calculatePropShare = false;
    } else {

      ao->analyzePair(&probeInfo, propShare);

      //      endProbeSession = true;
      //     debugPrint("endProbeSession\n");

      
      if(ao->iterate() && iteration < 3) {
	propShare = (long) trunc(propShare * 0.75);
	//	calculatePropShare = true;
	iteration++;
	printf("ITERATE\n\n");
      } else {
	endProbeSession = true;
	debugPrint("endProbeSession\n");
      }
      

    }

  }





  // Tell receiver that we are done.
  tcm = constructTcpControlMesg(0, SHUTDOWN, 0, 0);


  if (send(tcpFd, (char *) &tcm, sizeof(TcpControlMesg), 0) < 0)
    throw MeasureObjEx(MO_ERROR_SEND_FAILURE, 
		       "Can't send packet on TCP connection\n");  

}


/* FUNCTION: rootPriv
**
** USAGE: Used to determine if program is begin run
**         as root.
**
** ARGS: -
**
** RETURNS: 1 if root, 0 otherwise.
*/

inline int MeasureObj::rootPriv()
{
  return (geteuid() == 0); 
}


/* 
** FUNCTION: setDstHost
** 
** USAGE: Gets the address of the host that will be 
**        the destination host when probing.
**
** ARGS: newDstHost - Name of the destination host.
**
** RETURNS: -
*/

void MeasureObj::setDstHost(char* newDstHost) {
  struct hostent* he;
  
  if (newDstHost == NULL)
    throw MeasureObjEx(MO_ERROR_NO_DEST_HOST_SPEC, 
		       "No destination host specified");
  
  if ((he = gethostbyname(newDstHost)) == NULL)
    throw MeasureObjEx(MO_ERROR_HOST_LOOKUP_FAILURE, 
		       "Could not lookup host");
  
  memcpy(&dstAddr, he->h_addr_list[0], sizeof(dstAddr));
}


/* 
** FUNCTION: setProbeInfoStruct
** 
** USAGE: Sets the values known to the MeasureObj
**
** ARGS:  __ProbeInfo 
**
** RETURNS: -
*/

void MeasureObj::setProbeInfoStruct(void *arg) {
  __ProbeInfo *pI = (__ProbeInfo *) arg;

  pI->dstAddr = dstAddr;
  pI->dstUdpPort = portNums.dstUdpPort;
  pI->probeFd = probeFd;
  pI->maxPktSize = MAX_PACKET_SIZE_FOR_ETHERNET;
}


/* 
** FUNCTION: constructTcpControlMesg
** 
** USAGE: Constructs a control message to send to the other peer
**
** ARGS: version number, message number and two values
**
** RETURNS: a TcpControlMesg struct
*/

TcpControlMesg MeasureObj::constructTcpControlMesg(short version, short mesg, 
						   short value1, short value2) {
  TcpControlMesg tcm;
  
  tcm.version = htons(version);
  tcm.mesg    = htons(mesg);
  tcm.value1  = htons(value1);
  tcm.value2  = htons(value2);

  return tcm;
}


/*
** SHOULD NOT BE HERE... IMPLEMENT A GREAT GUI OR SOMETHING!
**
** argv[1] = dns name or ip address of probe receiver
** argv[2] = probe data storage name
** argv[3] = minimum probe rate
** argv[4] = maximum probe rate
** argv[5] = number of steps 
**
**
**
*/

int main(int argc, char **argv) {

  try {
    
    // Of course these arguments has to be checked before 
    // initialization of the MeasureObj.

    if(argc == 2) {
      MeasureObj mo(strdup(argv[1]), strdup(argv[1]), 0, 0, 10, 
		    DEFAULT_SERVER_UDP_PORT, DEFAULT_SERVER_TCP_PORT);
      mo.tcpDispatcher();

    } else if(argc == 3) {
      MeasureObj mo(strdup(argv[1]), "", 0, 0, atol(argv[2]), 
		    DEFAULT_SERVER_UDP_PORT, DEFAULT_SERVER_TCP_PORT);
      mo.tcpDispatcher();

    } else if(argc == 6) {
      
      MeasureObj mo(strdup(argv[1]), strdup(argv[2]), atol(argv[3]), 
		    atol(argv[4]), atol(argv[5]), 
		    DEFAULT_SERVER_UDP_PORT, DEFAULT_SERVER_TCP_PORT);
      
      // Start the actual probe activity
      mo.tcpDispatcher();
      
    } else {
      fprintf(stderr, "Usage: ./measure <host address> <accuracy: 5-50>\n");

      //fprintf(stderr, "Usage: ./measure <host address> <logfile identifier> <min rate>\n");
      //fprintf(stderr, "                 <max rate> <number of probe rate levels>\n");
      
    }

  } catch (MeasureObjEx mOE) {
    fprintf(stderr, "An error occured: %s.\n", mOE.GetErrorMsg());
  }

  return 1;
}




