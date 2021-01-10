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
#include "receiverobj.h"
#include "debugprint.h"



/*
** FUNCTION: ReceiverObj
**
** USAGE: Constructor. Allocate memory for tmp storage of incomming 
**        packets. Creates TCP and UDP server sockets.
**
** ARGS: Server UDP port and TCP port numbers.
**
** RETURNS: -
*/

ReceiverObj::ReceiverObj(int srvUdpPort, int srvTcpPort) {
  int maxPktSize = max (MAX_PACKET_SIZE_FOR_ETHERNET, 
			(int) sizeof(ProbeData));

  pktBuf = NULL;

  try { pktBuf = new char[maxPktSize]; }
  catch (...) { throw ReceiverObjEx(ROE_ERROR_MEM_ALLOC_FAILURE,
				    "Could not allocate memory"); }
  
  sizeOfPktBuf = maxPktSize;
  
  lstUdpPort = srvUdpPort;  // UDP port at destination  
  lstTcpPort = srvTcpPort;  // TCP port at destination  

  clientLen = sizeof(clientAddr);

  //
  // Setup socket to receive the UDP probe packets on.
  debugPrint("setup udpFd\n");
  if ((udpFd = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    throw ReceiverObjEx(ROE_ERROR_UDP_SOCKET, "Could not create udp socket");

  bzero(&listenAddr, sizeof(listenAddr));
  listenAddr.sin_family = AF_INET;
  listenAddr.sin_addr.s_addr = htonl(INADDR_ANY);
  listenAddr.sin_port = htons(lstUdpPort);

  if (bind(udpFd, (struct sockaddr*) &listenAddr, sizeof(listenAddr)) < 0)
    throw ReceiverObjEx(ROE_ERROR_SOCKET_BIND_FAILURE, "Could not bind socket");

  //
  // Setup TCP socket for communication with the probe generator.
  debugPrint("setup tcpFd\n");
  if ((tcpFd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    throw ReceiverObjEx(ROE_ERROR_TCP_SOCKET, "Could not create tcp socket");
  
  bzero((char *) &replyAddr, sizeof(replyAddr));
  replyAddr.sin_family = AF_INET;
  replyAddr.sin_addr.s_addr = htonl(INADDR_ANY);
  replyAddr.sin_port = htons(lstTcpPort); // htons

  debugPrint("Server TCP port = %d\n", lstTcpPort);

  if (bind(tcpFd, (struct sockaddr *) &replyAddr, sizeof(replyAddr)) < 0)
    throw ReceiverObjEx(ROE_ERROR_SOCKET_BIND_FAILURE, "Could not bind socket");
}


/*
** FUNCTION: ~ReceiverObj
**
** USAGE: Destructor. Close sockets, etc.
**
** ARGS: -.
**
** RETURNS: -
*/

ReceiverObj::~ReceiverObj() {
  close(tcpFd);
  close(udpFd);
}


/* 
** FUNCTION: startReceiver
** 
** USAGE: Handles the basic TCP socket acception phase. When
**        there is a TCP channel available control is given to
**        handleProbeSession().
**
** ARGS: -
**
** RETURNS: -
*/

void ReceiverObj::startReceiver() {
  int clientSocket; 

  if (listen(tcpFd, 5) < 0)
    throw ReceiverObjEx(ROE_ERROR_SOCKET_BIND_FAILURE, "Could not listen");

  // Connection loop
  for ( ; ; ) {
    if ((clientSocket = accept(tcpFd, 
			       (struct sockaddr *) &clientAddr, &clientLen)) < 0)
      throw ReceiverObjEx(ROE_ERROR_SOCKET_ACCEPT_FAILURE, "Could not accept");
    
    // We have a connection, handle it

    handleProbeSession(clientSocket);

    close(clientSocket);
  }

  return;
}


/* 
** FUNCTION: handleProbeSession
** 
** USAGE: The main loop for handling incomming probe packets. Make
**        decisions what to do depending on what TcpControlMesg the 
**        probe sender sends.
**
** ARGS: The TCP socket for communication with the probe sender. 
**
** RETURNS: -
*/

void ReceiverObj::handleProbeSession(int clientSocket) {
  bool probeDone = false;     
  TcpControlMesg rep;
  TcpControlMesg tcm;
  
  debugPrint("connection accepted\n");

  while (!probeDone) {
    if (recv(clientSocket, (char *)&tcm, sizeof(TcpControlMesg), 0) == -1)
      throw ReceiverObjEx(ROE_ERROR_RECEIVE_FAILURE, 
			  "Can't receive packet from TCP socket\n");
    
    debugPrint("Received TCM from client: %d\n", ntohs(tcm.mesg));

    if (ntohs(tcm.mesg) == START_RAMP) {
      numPktsToReceive = ntohs(tcm.value1);
      debugPrint("numPktsToReceive: %d\n", numPktsToReceive);

      srand(time(NULL));	
      sessionID = rand() % 1000; // Should be a random value.

      cleanUdpInQueue();
	
      // Okej to start probe
      rep = constructTcpControlMesg(0, ACK, sessionID, 0);

      if (send(clientSocket, (char *)&rep, sizeof(TcpControlMesg), 0) < 0)
	throw ReceiverObjEx(ROE_ERROR_SEND_FAILURE, 
			    "Can't send packet to TCP client\n");

      // Now receive UDP probe packets from peer
      //      if(!timeArray)
      //	delete timeArray;
      debugPrint("start probeReceiver\n");
      probeReceiver(clientSocket);    

    } else if (ntohs(tcm.mesg) == GET_RESULT) {
      // Send back the results
      // Call send back results method

      sendBackResults(clientSocket);

    } else if (ntohs(tcm.mesg) == SHUTDOWN) {
      // The probe generator are finished. 
      probeDone = true;
    }

  }
  return;
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

TcpControlMesg ReceiverObj::constructTcpControlMesg(short version, short mesg, 
						   short value1, short value2) {
  TcpControlMesg tcm;
  
  tcm.version = htons(version);
  tcm.mesg    = htons(mesg);
  tcm.value1  = htons(value1);
  tcm.value2  = htons(value2);

  return tcm;
}


/*
** FUNCTION: cleanUdpInQueue
**
** USAGE: Removes all old UDP packets that might be in the queue.
**
** ARGS: -
**
** RETURNS: -
*/

void ReceiverObj::cleanUdpInQueue() {
  bool done = false;
  struct timeval timeout;
  fd_set fdSet;
  int tmp, n;
  socklen_t addrLen = sizeof(struct sockaddr_in);  // length of the address

  debugPrint("Clean UDP in-queue\n");

  timeout.tv_sec = PKT_TIMEOUT;
  timeout.tv_usec = 0;

  while(!done) {
    FD_ZERO(&fdSet);
    FD_SET(udpFd, &fdSet);

    // Only check for tcp messages if we have had a timeout

    tmp = select(udpFd+1, &fdSet, NULL, NULL, &timeout);

    if (FD_ISSET(udpFd, &fdSet)) 
      n = recvfrom(udpFd, pktBuf, sizeOfPktBuf, 0, 
		   (struct sockaddr*) &clientAddr, &addrLen);

    if (n < 0)
      throw ReceiverObjEx(ROE_ERROR_RECEIVE_FAILURE, "Clean in queue failed");

    if (tmp < 0)
      throw ReceiverObjEx(ROE_ERROR_SELECT_FAILURE, "Select failed");

    if (tmp == 0) // timeout
      done = true;      
  }
}



/*
** FUNCTION: probeReceiver
**
** USAGE: Receives UDP probe packets and timestamp them. End when all
**        UDP probe packets has arrived OR when the sender uses the
**        TCP channel to send a message (to handle lost packets etc).
**
** ARGS: The TCP socket for communication with the probe sender.
**
** RETURNS: -
*/

void ReceiverObj::probeReceiver(int clientSocket) {
  bool endProbeSession = false, lookForTcpControlMesg = false;
  int numIterations = 0, n, tmp;
  fd_set fdSet;
  struct timeval recvTime;  // the time when we receive a packet
  struct timeval timeout;   // after how long time should be timeout in select

  timeArray = new struct timeval[numPktsToReceive];

  for(int i=0; i<numPktsToReceive; i++) {
    timeArray[i].tv_sec = 0;
    timeArray[i].tv_usec = 0;
  }

  timeout.tv_sec = PKT_TIMEOUT;
  timeout.tv_usec = 0;

  debugPrint("Start receiving data from client\n");
  
  while(!endProbeSession) {
    FD_ZERO(&fdSet);
    FD_SET(udpFd, &fdSet);

    // Only check for tcp messages if we have had a timeout
    if(lookForTcpControlMesg) 
      FD_SET(clientSocket, &fdSet);
    
    tmp = select(max(udpFd, clientSocket)+1, &fdSet, NULL, NULL, &timeout);
    //    gettimeofday(&recvTime, NULL);

    if (FD_ISSET(udpFd, &fdSet)) {
      // a UDP packet, hopefully a Probe packet.
      socklen_t addrLen = sizeof(struct sockaddr_in);  // length of the address
      
      //      gettimeofday(&recvTime, NULL);
      n = recvfrom(udpFd, pktBuf, sizeOfPktBuf, 0, 
		   (struct sockaddr*) &clientAddr, &addrLen);

      gettimeofday(&recvTime, NULL);      

      if (n < 0)
	throw ReceiverObjEx(ROE_ERROR_RECEIVE_FAILURE, 
			      "Internal error: Failed to receive packet\n");
      
      //      numIterations++;
      
      if (n >= sizeof(ProbeData)) { // Could be a probe packet

	//#ifdef PROBE_DEBUG
	//	PrintPktBuf(pktBuf, n, __UDP_PKT, __DEC_DUMP);
	//#endif
	
	//	debugPrint("received probe packet");
	
	ProbeData* probeData = (ProbeData*) pktBuf; // Get data from UDP packet
	
	//	debugPrint("%d == %d?\n", ntohs(probeData->sessionID), sessionID);

	if (ntohs(probeData->sessionID) == sessionID) {  
	  // A packet from the same batch we are working with

	  numIterations++;

	  //	  debugPrint("We received packet: %d\n", ntohs(probeData->pktIndex));
	  timeArray[ntohs(probeData->pktIndex)].tv_sec = recvTime.tv_sec;
	  timeArray[ntohs(probeData->pktIndex)].tv_usec = recvTime.tv_usec;

	} else {
	  // Just Discart the packet. Do nothing.
	  debugPrint("Not a probe packet within this session\n");
	}
      } else {
	// Just Discard the packet. Do nothing.	
	debugPrint("Not a probe packet at all\n");
      }
    }
    else if (tmp < 0)
      throw ReceiverObjEx(ROE_ERROR_SELECT_FAILURE, "Select failed");
    else if (tmp == 0)
      lookForTcpControlMesg = true;
      // we had a timeout, check if the client is still alive with a control message
      // Packets might be lost, we might have gotten the last one. If so, end loop.
      // Not implemented yet
    

    else if (FD_ISSET(clientSocket, &fdSet))
      // we had a controll message, return!
      // We assume that if we get a control msg all probe pkts has been
      // sent. End probe session!
      endProbeSession = true;      
    
    // Check if we have got all packets.
    if (numIterations == numPktsToReceive)
      endProbeSession = true;
  }
}


/* 
** FUNCTION: sendBackResults
** 
** USAGE: Send back the timestamps to the probe sender. Before
**        sending the results, send a TcpControlMesg giving info
**        about whats happening.
**
** ARGS: The TCP socket for communication with the probe sender. 
**
** RETURNS: -
*/

void ReceiverObj::sendBackResults(int clientSocket) {
  TcpControlMesg tcm;

  debugPrint("Values to send back = %d\n", numPktsToReceive);
  tcm = constructTcpControlMesg(0, ACK, numPktsToReceive, 0);

  if (send(clientSocket, (char *)&tcm, sizeof(TcpControlMesg), 0) < 0)
    throw ReceiverObjEx(ROE_ERROR_SEND_FAILURE, 
			"Can't send packet to TCP client\n");
  
  for(int j=0; j<numPktsToReceive; j++) {
    timeArray[j].tv_sec = htonl(timeArray[j].tv_sec);
    timeArray[j].tv_usec = htonl(timeArray[j].tv_usec);

    debugPrint("Packet %d was received at: %d:%d\n", j, ntohl(timeArray[j].tv_sec), ntohl(timeArray[j].tv_usec))
      ;
    if (send(clientSocket, (char *) &(timeArray[j]), sizeof(struct timeval), 0) < 0)
      throw ReceiverObjEx(ROE_ERROR_SEND_FAILURE, 
			  "Can't send packet to TCP client\n");
  }

  
}



/*
 *
 * Main.
 *
 *
 *
 *
 */

int main() {
  ReceiverObj ro(DEFAULT_SERVER_UDP_PORT, DEFAULT_SERVER_TCP_PORT);

  debugPrint("start receiver\n");


  try {
    ro.startReceiver();  
         
  } catch (ReceiverObjEx rOE) {
    fprintf(stderr, "An error occured: %s.", rOE.GetErrorMsg());
  }
  

}


