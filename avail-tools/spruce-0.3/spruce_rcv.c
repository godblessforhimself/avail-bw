/*
 * $Id: spruce_rcv.c,v 1.7 2003/12/11 20:11:37 jastr Exp $
 *
 * This file is part of Spruce
 * Copyright (C) 2003 Jacob Strauss (jastr@lcs.mit.edu)
 * 
 * Spruce is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * Spruce is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with Spruce; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <stdio.h>
#include <string.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <assert.h>
#include <sys/types.h>
#include <sys/time.h>
#include <unistd.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/uio.h>
#include <signal.h>
#include <sys/wait.h>
#include <math.h>


#include "spruce.h"

static const int bufsize=2000;
char *buf;

/*the tcp control socket*/
int tcp_control_listener=0;
int tcp_control_socket=0;
struct sockaddr_in tcp_control_local;
struct sockaddr_in tcp_control_remote;

int spruce_socket;
struct sockaddr_in spruce_local;
struct sockaddr_in spruce_remote;

struct spruce_pkt {
  int size;
  long seqno;
  long bunch;
  long idealgap;
  long totalpairs;
  long sendgap;
  struct timeval t;
} ;

struct spruce_pkt *spruce_table;

int spruce_next_empty=0;
int spruce_total=-1;

long
timeval_diff(struct timeval *a, struct timeval *b){
  long r=0;

  r = (a->tv_sec - b->tv_sec)*1000000;
  r += (a->tv_usec - b->tv_usec);
  return r;
}

int
prep_sockets()
{
  struct protoent *udp;
  struct protoent *tcp;
  int opt;
  int one;


  udp=getprotobyname("udp");

  assert(udp != NULL);

  //need accurate timings on recieved packets here

  bzero((void *)&spruce_remote, sizeof(struct sockaddr_in));
  bzero((void *)&spruce_local, sizeof(struct sockaddr_in));
  
  spruce_socket=socket(PF_INET,SOCK_DGRAM,udp->p_proto);
  if(spruce_socket < 0){
    perror("socket3:");
    exit(1);
  }

  spruce_local.sin_family = AF_INET;
  spruce_local.sin_addr.s_addr = htonl(INADDR_ANY);
  spruce_local.sin_port = htons(SPRUCE_UDP_PORT);

  if(bind(spruce_socket, (struct sockaddr*)&spruce_local,
	  sizeof(spruce_local)) < 0){
    perror("udp bind 2");
    exit(1);
  }

  one=1;
  /*set SO_TIMESTAMP option*/
  if(setsockopt(spruce_socket, SOL_SOCKET, SO_TIMESTAMP,
                &one, sizeof(one)) < 0){
    perror("setsockopt(SO_TIMESTAMP) failed spruce_local:");
  }

  //now the tcp control listner
  tcp=getprotobyname("tcp");
  assert(tcp!= NULL);
  tcp_control_listener=socket(PF_INET,SOCK_STREAM,tcp->p_proto);
  if(tcp_control_listener < 0){
    perror("socket3:");
    exit(1);
  }

  opt=1;
  if (setsockopt(tcp_control_listener, SOL_SOCKET,
		 SO_REUSEADDR, (void*)&opt, sizeof(opt)) < 0)  {
    perror("setsockopt contol listner (SOL_SOCKET,SO_REUSEADDR):");
    exit(1);
  }

  bzero((void *)&tcp_control_local, sizeof(struct sockaddr_in));
  bzero((void *)&tcp_control_remote, sizeof(struct sockaddr_in));

  tcp_control_local.sin_family = AF_INET;
  tcp_control_local.sin_addr.s_addr    = htonl(INADDR_ANY);
  tcp_control_local.sin_port = htons(SPRUCE_TCP_CONTROL_PORT);

  if(bind(tcp_control_listener,
	  (struct sockaddr*)&tcp_control_local,
	  sizeof(tcp_control_local)) < 0){
    perror("tcp bind");
    exit(1);
  }
  
  if(listen(tcp_control_listener,-1) < 0){
    perror("tcp control listen");
    exit(1);
  }

  return 0;
}

void
spruce_sink(){
  struct msghdr msg;
  struct iovec iov;
  struct sockaddr_in from;
  char ctrl[CMSG_SPACE(sizeof(struct timeval))];
  struct cmsghdr *cmsg = (struct cmsghdr *)&ctrl;
  struct timeval t;

  int rsize;
  
  bzero(&msg, sizeof(msg));
  bzero(&t, sizeof(t));
  bzero(ctrl, CMSG_SPACE(sizeof(struct timeval)));
  msg.msg_iov = &iov;
  msg.msg_iovlen = 1;
  iov.iov_base = buf;
  iov.iov_len = bufsize;
  msg.msg_namelen = sizeof(from); //need this?
  msg.msg_name = (caddr_t) &from; //need this?
  msg.msg_control = (caddr_t) ctrl;
  msg.msg_controllen = sizeof(ctrl);

  if((rsize=recvmsg(spruce_socket,&msg, 0)) < 0){
    perror("spruce recmsg:");
    exit(1);
  }
  
  if (cmsg->cmsg_level == SOL_SOCKET &&
      cmsg->cmsg_type == SCM_TIMESTAMP &&
      cmsg->cmsg_len == CMSG_LEN(sizeof(struct timeval))) {
    memcpy(&t,CMSG_DATA(cmsg),sizeof(t));
  } else {
    gettimeofday(&t, NULL);
    fprintf (stderr, "didn't get timestamp data!\n");
  }

  {
    long seqno;
    long bunch;
    long idealgap;
    long totalpairs;
    long sendgap;

    seqno = ntohl(*(((long*)buf)+0));
    bunch = ntohl(*(((long*)buf)+1));
    idealgap = ntohl(*(((long*)buf)+2));
    totalpairs = ntohl(*(((long*)buf)+3));
    sendgap = ntohl(*(((long*)buf)+4));
    
    if((bunch == 1 || bunch == 2) &&
       (seqno >= 0 && seqno < 30000)){
      //printf("bunch %d seq %d received\n",(int)bunch,(int) seqno);
      
      int n = spruce_next_empty;

      if(n >= 0 && n < spruce_total){
	spruce_table[n].size = rsize;
	spruce_table[n].seqno = seqno;
	spruce_table[n].idealgap = idealgap;
	spruce_table[n].bunch = bunch;
	spruce_table[n].totalpairs = totalpairs;
	spruce_table[n].sendgap = sendgap;
	
	memcpy(&(spruce_table[n].t), &t, sizeof(struct timeval));

	spruce_next_empty++;
      }
     
    }
    
  }

}

long
spruce_dump(char * filename){
  int i;
  FILE *out;
  double avg=0;
  double capacity=0;

  //fprintf(stderr,"dumping spruce estimates: %s\n", filename);

  out = fopen(filename, "w");

  fprintf(out, "spruce dump:\n");
  for(i=0 ; i < spruce_next_empty && i < spruce_total ; i++ ){
    fprintf(out, "%d %d %d %d %d %d %d.%d\n",
	   (int) spruce_table[i].seqno,
	   (int) spruce_table[i].bunch,
	   (int) spruce_table[i].idealgap,
	   (int) spruce_table[i].size,
	   (int) spruce_table[i].totalpairs,
	   (int) spruce_table[i].sendgap,
	   (int) spruce_table[i].t.tv_sec,
	   (int) spruce_table[i].t.tv_usec);
  }
  fprintf(out, "spruce dump end\n");
  
  fprintf(out, "spruce estimates begin\n");
  {
    long expected=-1;
    long storedgap=-1;
    long storedsize=-1;
    long storedtotpairs=-1;
    struct timeval storedtime;
    long storedsendgap=-1;
    double sum = 0;
    int howmany = 0;
    
    for(i=0 ; i < spruce_next_empty && i < spruce_total; i++){
      if(spruce_table[i].bunch == 1){
	
	//store all the values
	expected = spruce_table[i].seqno;
	storedgap = spruce_table[i].idealgap;
	storedsize = spruce_table[i].size + 28;
	storedtotpairs = spruce_table[i].totalpairs;
	storedtime.tv_sec = spruce_table[i].t.tv_sec;
	storedtime.tv_usec = spruce_table[i].t.tv_usec;
	storedsendgap = spruce_table[i].sendgap; 
	
      } else if(spruce_table[i].bunch == 2){
	if(spruce_table[i].seqno == expected){
	  double dr;
	  double abw;
	  long rgap = timeval_diff(&(spruce_table[i].t), &storedtime);
	  
	  capacity = (storedsize * 8 * (long long) (1000000))
	    / storedgap;
	  
	  dr = rgap - ((spruce_table[i].size + 28) * 8) / (capacity / 1e6);
	  dr = dr < 0 ? 0 : dr;
	  abw = 1 - dr / spruce_table[i].sendgap;
	  
	  //ignore preemptions
	  abw = abw < -0.8 ? -0.8 : abw;
	
	  //average value
	  sum += abw;
	  howmany++;
	  avg = sum / howmany;

	  avg = max(avg, 0);

	  fprintf(out, "%d.%d %f %f\n", (int)storedtime.tv_sec,
		 (int)storedtime.tv_usec, abw, avg);
	}
	//unset all
	expected = -1;
	storedgap = -1;
	storedsize = -1;
	storedtotpairs = -1;
	storedtime.tv_sec = -1;
	storedtime.tv_usec = -1;
	storedsendgap = -1;
      } else { //unknown packet type...
	expected = -1;
	storedgap = -1;
	storedsize = -1;
	storedtotpairs = -1;
	storedtime.tv_sec = -1;
	storedtime.tv_usec = -1;
	storedsendgap = -1;
      }
    }
    
  }
  fprintf(out, "spruce estimates end\n");

  spruce_next_empty = 0;
  fclose(out);
  {
    long ret = (avg * capacity) / 1000;
    fprintf(stderr, "Available Bandwidth: %ld Kbps (\%ld Mbps)\n", ret, ret/1000);
    return ret;
  }

}

void tcp_control_accept()
{
  socklen_t addrlen=sizeof(struct sockaddr_in);
  int farg;
  
  assert(tcp_control_socket==0);
  if((tcp_control_socket=accept(tcp_control_listener,
				(struct sockaddr *)&tcp_control_remote,
				&addrlen)) < 0){
    perror("control_accpet");
    tcp_control_socket=0;
    return;
  }
  
  if((farg=fcntl(tcp_control_socket,F_GETFL,0)) < 0){
    perror("getfl failed");
    exit(1);
  }
  farg |= O_NONBLOCK;
  if((farg=fcntl(tcp_control_socket,F_SETFL,farg)) < 0){
    perror("setfl failed");
    exit(1);
  }
  
  return;
}

void tcp_control_read(){
  int s;
  unsigned char cmd;
  unsigned char ack;

  s=read(tcp_control_socket,&cmd,sizeof(cmd));
  
  if(s<0){
    if(errno != EAGAIN){
      perror("tcp control read:");
      exit(1);
    }
    return;
  }

  if(s==0){
    printf("connection closed...\n");
    fflush(stdout);
    exit(0);
  }

  switch(cmd){
  case CONTROL_NOOP:
    ack = cmd | CONTROL_ACK;
    write(tcp_control_socket,&ack,sizeof ack);
    break;
  case CONTROL_EXIT:
    ack = cmd | CONTROL_ACK;
    write(tcp_control_socket,&ack,sizeof ack);
    close(tcp_control_socket);
    //printf("normal exit\n");
    exit(0);
    break;
  case CONTROL_SPRUCE_OUTPUT:
    ack = cmd | CONTROL_ACK;
    {
      long rate;
      rate = spruce_dump("spruce.log");
      rate = htonl(rate);
      write(tcp_control_socket, &ack, sizeof ack);
      write(tcp_control_socket, &rate, sizeof(long));
    }
    
    break;
  default:
    fprintf(stderr,"unknown control command received: %d %c\n",(int) cmd, cmd);
  }
    
}

void
select_loop(){
  fd_set rset, wset;
  struct timeval timeout;
  int sret;
  int beencontacted=0;
  int maxsocknum;

  while(1){
    FD_ZERO(&rset);
    FD_ZERO(&wset);
    maxsocknum = 0;

    FD_SET(spruce_socket,&rset);
    maxsocknum = max(spruce_socket, maxsocknum);

    //only does this if already contacted
    bzero(&timeout,sizeof(timeout));
    timeout.tv_sec=200;

    if(tcp_control_socket > 0){
      FD_SET(tcp_control_socket, &rset);
      maxsocknum = max(tcp_control_socket, maxsocknum);
    } else {
      FD_SET(tcp_control_listener, &rset);
      maxsocknum = max(tcp_control_listener, maxsocknum);
    }
 
    if((sret=select(maxsocknum + 1,
		    &rset,&wset,NULL,beencontacted ? &timeout : NULL))< 0){
      perror("select");
      exit(1);
    }
    
    if(sret==0){
      //timeout
      fprintf(stderr,"timeout with sender... quitting\n");
      exit(1);
    }
    
    beencontacted=1;

    if(FD_ISSET(spruce_socket,&rset)){
      spruce_sink();
    }

    if(FD_ISSET(tcp_control_listener, &rset)){
      tcp_control_accept();
    }
       
    if(FD_ISSET(tcp_control_socket, &rset)){
      tcp_control_read();
    }

  }
}

int
main(int argc, char *argv[]){

  buf=malloc(bufsize);
  assert(buf!=NULL);
  
  spruce_total = 10000;
  spruce_table = malloc(sizeof(struct spruce_pkt) * spruce_total);
  assert(spruce_table != NULL);
  spruce_next_empty = 0;
  bzero(spruce_table, sizeof(struct spruce_pkt) * spruce_total);

  prep_sockets();

  select_loop();

  exit(0);
}
