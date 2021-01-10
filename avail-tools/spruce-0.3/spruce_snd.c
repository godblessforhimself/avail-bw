/*
 * $Id: spruce_snd.c,v 1.10 2003/12/11 20:11:37 jastr Exp $
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
#include <sys/uio.h>
#include <unistd.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>
#include <math.h>
#include <limits.h>
#include <signal.h>
#include <sys/wait.h>
#include <sys/stat.h>

#include "spruce.h"

/*on linux hz is probably 100, but might not be*/
#ifdef __linux
#include <asm/param.h>
#endif

#ifndef HZ
/*meant for modified PDOS FreeBSD*/
#define HZ 1000
#endif

struct hostent *peer;
char peer_actual[16]; //how big is this really?

char *peername;

/*the tcp control socket*/
int tcp_control_socket=0;
struct sockaddr_in tcp_control_local;
struct sockaddr_in tcp_control_remote;

int starttime;

/*UDP header + IP Header should be 28 bytes*/
/*TCP header + IP header should be 40 bytes*/

int path_capacity = 100000000; /*default to 100 Mbit*/
int link_set = 0;

int inter_pair_gap = 100000;  /*100ms*/
int total_pairs = 10 * 10; /*10 seconds at the default*/
int packet_size = 1500 - 28;

int spruce_socket;
struct sockaddr_in spruce_local;
struct sockaddr_in spruce_remote;

extern char *environ[];

void
usage()
{
  fprintf(stderr,"usage:\n spruce_snd -h host -c capacity [-n # of pairs]\n");
  exit(1);
}

void
process_args(int argc, char * argv[])
{
  int ch;

  while((ch = getopt(argc, argv, "c:i:n:h:")) != -1){
    switch(ch) {
    case 'c':
      /*capacity of this path*/
      {
	int len = strlen(optarg);
	int mul = 1;
	switch(optarg[len-1]){
	case 'M':
	case 'm':
	  mul = 1000 * 1000;
	  break;
	case 'k':
	case 'K':
	  mul = 1000;
	  break;
	case 'G':
	case 'g':
	  mul = 1000 * 1000 * 1000;
	  break;
	}
	if(mul != 1){
	  optarg[len-1] = 0;
	}
	
	path_capacity=atoi(optarg);
	path_capacity*=mul;
	if(path_capacity <= 0 || path_capacity > 100000000 * 10){
	  fprintf(stderr, "illegal path capacity: %d\n", path_capacity);
	  exit(1);
	}

	link_set = 1;
      }
      break;
    case 'i':
      /*gap between pairs*/
      inter_pair_gap = atoi(optarg);
      if(inter_pair_gap <= 0 || inter_pair_gap > 100000000 * 10){
	fprintf(stderr, "illegal inter pair gap: %d\n", inter_pair_gap);
	exit(1);
      }
      break;
    case 'n':
      /*number of pairs to send*/
      total_pairs = atoi(optarg);
      if(total_pairs <= 0 || total_pairs > 100000000 * 10){
	fprintf(stderr, "illegal number of pairs: %d\n", total_pairs);
	exit(1);
      }
      break;
    case 'h':
      /*hostname*/
      peername=optarg;
      peer = gethostbyname(peername);
      if(peer == NULL){
	fprintf(stderr, "host not found: %s\n", peername);
	herror("");
	exit(1);
      }
      //copy away so future gethost* works
      memcpy(peer_actual, peer->h_addr, sizeof(spruce_remote.sin_addr.s_addr));
      break;
    case '?':
    default:
      usage();
    }
  }

  if(!link_set){
    fprintf(stderr, "must specify path capacity\n");
    usage();
  }

  if(peer==NULL){
    fprintf(stderr, "must specify a desitination host\n");
    usage();
  }

}

/*fill with random data*/
int
prepare_buffers(){
  struct timeval t;

  gettimeofday(&t,NULL);
  srandom(t.tv_usec);

  return 0;
}

long
timeval_diff(struct timeval *a, struct timeval *b){
  long r=0;

  r= (a->tv_sec - b->tv_sec)*1000000;
  r+= (a->tv_usec - b->tv_usec);
  return r;
}


int prep_sockets(){
  struct protoent *udp;
  int optval;
  int optsize;

  udp=getprotobyname("udp");

  /*now do the spruce socket UDP_SPRUCE_PORT*/

  bzero((void *)&spruce_local, sizeof(struct sockaddr_in));
  bzero((void *)&spruce_remote, sizeof(struct sockaddr_in));

  spruce_socket=socket(PF_INET,SOCK_DGRAM,udp->p_proto);
  if(spruce_socket < 0){
    perror("socket2x:");
    exit(1);
  }

  spruce_local.sin_family = AF_INET;
  spruce_local.sin_addr.s_addr = htonl(INADDR_ANY);
  spruce_local.sin_port = htons(0);
  
  spruce_remote.sin_family = AF_INET;
  memcpy((void*)&(spruce_remote.sin_addr.s_addr), peer_actual,
        sizeof(spruce_remote.sin_addr.s_addr));
  spruce_remote.sin_port = htons(SPRUCE_UDP_PORT);

  //12 bytes for payload... will this be combined or not?*/
  optval = packet_size;
  optsize = sizeof(optval);
  if(setsockopt(spruce_socket,SOL_SOCKET, SO_SNDBUF, &optval, optsize) < 0){
    perror("spruce: SNDBUF");
    exit(1);

  }

  if(bind(spruce_socket, (struct sockaddr*)&spruce_local,
         sizeof(spruce_local)) < 0){
    perror("udp pair bind");
    exit(1);
  }

  if(connect(spruce_socket, (struct sockaddr*)&spruce_remote,
            sizeof(spruce_remote)) < 0){
    perror("udp gap connect");
  }

  return 0;
}

double gen_pause_exp(int beta){
  int p = random();

  /*turn this into a random number between 0 and 1...*/
  double f = p / (double) INT_MAX;
  
  return -1 * beta * log(1-f);
}

//the uniform random version
double gen_pause_uniform(int min, int max){
  int p = random();

  /*turn this into a random number between 0 and 1...*/
  double f = p / (double) INT_MAX;
  
  return min + (max - min) * f;
}


void control_connect()
{
  struct protoent *tcp;
  int flags;
  char cmd;
  char ack;
  fd_set rset;
  fd_set wset;
  int sret;
  struct timeval timeout;
  int connect_failed=0;
  int n;
  int e;
  int rret;

  tcp=getprotobyname("tcp");
  assert(tcp != NULL);
  tcp_control_socket = socket(PF_INET,SOCK_STREAM,tcp->p_proto);
  if(tcp_control_socket < 0){
    perror("socket2:");
    exit(1);
  }

  bzero((void *)&tcp_control_local, sizeof(struct sockaddr_in));
  bzero((void *)&tcp_control_remote, sizeof(struct sockaddr_in));
  
  tcp_control_local.sin_family = AF_INET;
  tcp_control_local.sin_addr.s_addr = htonl(INADDR_ANY);
  tcp_control_local.sin_port = htons(0);
  
  tcp_control_remote.sin_family = AF_INET;
  memcpy((void*)&(tcp_control_remote.sin_addr.s_addr), peer_actual,
	 sizeof(tcp_control_remote.sin_addr.s_addr));
  tcp_control_remote.sin_port = htons(SPRUCE_TCP_CONTROL_PORT);

  if(bind(tcp_control_socket,
	  (struct sockaddr*)&tcp_control_local,
	  sizeof(tcp_control_local)) < 0){
    perror("tcp binddf");
    exit(1);
  }

  if((flags = fcntl(tcp_control_socket, F_GETFL,0)) < 0){
    perror("get flags");
  }
  if(fcntl(tcp_control_socket, F_SETFL, flags | O_NONBLOCK) < 0){
    perror("set flags:");
  }

  //printf("sockets created\n");

  //connect control socket
  if(connect(tcp_control_socket,
	     (struct sockaddr*)&tcp_control_remote,
	     sizeof(tcp_control_remote)) < 0){
    if(errno != EINPROGRESS){
      perror("connect failed -- is sink running?:");
      /*treat as throughput 0 or bug*/
      connect_failed=1;
    } else {
      FD_ZERO(&rset);
      FD_ZERO(&wset);
      FD_SET(tcp_control_socket, &rset);
      FD_SET(tcp_control_socket, &wset);
      timeout.tv_sec = 20;
      timeout.tv_usec = 0;
      n = select(tcp_control_socket+1, &rset, &wset, NULL, &timeout);
      if(n < 0){
	perror("bug select connect:");
	exit(1);
      }
      if(n == 0){
	/*treat as throughput 0*/
	connect_failed=1;
      }
      if(n > 0){
	int len=sizeof(e);
	if (getsockopt(tcp_control_socket,
		       SOL_SOCKET, SO_ERROR, &e, (socklen_t *)&len) < 0)  {
	  connect_failed=1;
    fprintf(stderr,"failed to connect control socket\n");
	}
      }
    }
  }

  if(connect_failed){
    fprintf(stderr,"failed to connect control socket\n");
    exit(1);
  }

  //send a NOOP to sink, wait for response.
  cmd = CONTROL_NOOP;
  write(tcp_control_socket,&cmd,sizeof(cmd));
  FD_ZERO(&rset);
  FD_SET(tcp_control_socket,&rset);
 
  bzero(&timeout,sizeof(timeout));
  timeout.tv_sec = 10;
  sret=select(tcp_control_socket+1,&rset,NULL,NULL,&timeout);

  if(sret > 0  && FD_ISSET(tcp_control_socket,&rset)){
    rret=read(tcp_control_socket,&ack,sizeof(ack));
    if(rret != sizeof(ack) || (ack & CONTROL_ACK) == 0){
      fprintf(stderr,"bad control response... is receiver running?\n");
      exit(1);
    }
  } else {
    fprintf(stderr,"no control response...\n");
    exit(1);
  }

}

void control_exit(){
  char cmd;
  char ack;
  fd_set rset;
  struct timeval timeout;
  int sret,rret;

  cmd = CONTROL_EXIT;

  write(tcp_control_socket,&cmd,sizeof(cmd));
  
  bzero(&timeout,sizeof(timeout));
  timeout.tv_sec = 20;
  FD_ZERO(&rset);
  FD_SET(tcp_control_socket,&rset);
  sret = select(tcp_control_socket+1,&rset,NULL,NULL,&timeout);
  if(sret > 0 && FD_ISSET(tcp_control_socket,&rset)){
    rret=read(tcp_control_socket,&ack,sizeof(ack));
    close(tcp_control_socket);
    
  }

}

long get_spruce_rate(){
  long rate=0;

  //tell sink to dump all data to file now and reset counters
  {
    char cmd;
    cmd = CONTROL_SPRUCE_OUTPUT;
    write(tcp_control_socket, &cmd, sizeof(cmd));
  }
  
  //read the ack from the sink
  {
    fd_set rset;
    struct timeval timeout;
    int sret, rret;
    char ack;
    long retrate;
    
    FD_ZERO(&rset);
    FD_SET(tcp_control_socket,&rset);      
    bzero(&timeout,sizeof(timeout));
    timeout.tv_sec = 10;
    sret=select(tcp_control_socket+1,&rset,NULL,NULL,&timeout);
      
    if(sret > 0  && FD_ISSET(tcp_control_socket,&rset)){
      rret=read(tcp_control_socket,&ack,sizeof(ack));
      if(rret != sizeof(ack) || (ack & CONTROL_ACK) == 0){
	fprintf(stderr,"got a bad response. sdf.. %d\n", rret);
	exit(1);
      }
      
      FD_ZERO(&rset);
      FD_SET(tcp_control_socket,&rset);      
      bzero(&timeout,sizeof(timeout));
      timeout.tv_sec = 10;
      sret=select(tcp_control_socket+1,&rset,NULL,NULL,&timeout);
      
      rret=read(tcp_control_socket,&retrate,sizeof(retrate));
      if(rret != sizeof(retrate)){
	fprintf(stderr,"got a bad response324985\n");
	exit(1);
      }
      rate = ntohl(retrate);

    } else {
      fprintf(stderr,"no response...\n");
      exit(1);
    }
  }

  return rate;
}

void spruce_test(){
  
  /*note these calculations will fail for anything faster than 2 Gbps*/
  /*that's okay since we can't pause for less than one usec anyway*/
  
  long long din = (packet_size * 8 * (long long) (1000000))
    / path_capacity;

  double shortest_allowed = (packet_size+28)*2.*8.*1e6 / path_capacity / 0.05;

  //need to compute the average pause here
  int avg_pause = (shortest_allowed > inter_pair_gap) ?
    shortest_allowed : inter_pair_gap;

  int elapsed=0;
  int pause;
  struct timeval *times;
  int packetcnt = 0;
  int overflow;
  void *buf;
  int dropcnt=0;
  int current_gap;

  times = malloc(sizeof(struct timeval) * total_pairs);
  assert (times != NULL);
  buf = malloc(packet_size);
  assert (buf != NULL);

  srandom(time(NULL));

  gettimeofday(&(times[0]), NULL);
  times[0].tv_sec+=1; /*don't start right now*/
  
  for(packetcnt = 1 ;packetcnt < total_pairs ; packetcnt++){
    pause = rint(gen_pause_exp(avg_pause));
    elapsed += pause;

    times[packetcnt].tv_sec = times[packetcnt-1].tv_sec;
    times[packetcnt].tv_usec = times[packetcnt-1].tv_usec + pause;
    overflow = times[packetcnt].tv_usec / 1000000;
    times[packetcnt].tv_sec += overflow;
    times[packetcnt].tv_usec -= overflow * 1000000;
    
  }

  for(packetcnt = 0; packetcnt < total_pairs ;
      /*increment done if successful later*/){
    struct timeval sleep_time;
    struct timeval now;
    int sret;
    int busy_wait = 0;
    long long diff;
    long gap;

    gettimeofday(&now,NULL);
    sleep_time.tv_sec = times[packetcnt].tv_sec - now.tv_sec;
    sleep_time.tv_usec = times[packetcnt].tv_usec - now.tv_usec;
    if(sleep_time.tv_usec < 0){
      sleep_time.tv_usec += 1000000;
      sleep_time.tv_sec--;
    }

    diff = (times[packetcnt].tv_sec - now.tv_sec) * 1000000 +
      (times[packetcnt].tv_usec - now.tv_usec);
    
    if(diff < -500){ /*more than 500us late*/
      /*too late, skip this*/
      packetcnt++;
      dropcnt++;
      continue;
    }

    if(diff < 2 * (1000000 / HZ)){
      /*we're now almost committed to sending this*/
      busy_wait = 1;
    }

    assert(sleep_time.tv_usec >= 0);
    assert(sleep_time.tv_usec < 1000000);
    
    if(busy_wait){
      do{
	if(diff < (-1 * (1000000 / HZ)/2)){
	  /*oh well, got interrupted*/
	  dropcnt++;
	  packetcnt++;
	  continue;
	}
	diff = (times[packetcnt].tv_sec - now.tv_sec) * 1000000 +
	  (times[packetcnt].tv_usec - now.tv_usec);
	gettimeofday(&now,NULL);
	gap = (now.tv_sec - times[packetcnt].tv_sec) * 1000000 +
	  (now.tv_usec - times[packetcnt].tv_usec);
	*(((long*)buf)+4) = htonl(gap);
      } while(diff > 0);
            
    } else {
      /*yield for the minimum possible time*/
      sleep_time.tv_sec=0;
      sleep_time.tv_usec=1;

      sret = select(0, NULL, NULL, NULL, &sleep_time);

      if (sret<0){
	perror("select");
	fprintf(stderr,"%ld %ld\n",sleep_time.tv_sec,sleep_time.tv_usec);
	exit(1);
      }
      continue;
    }

    /*now... what to send...what to send*/
    {
      struct timeval first;
      struct timeval target;
      struct timeval current_time;
      register long diff;
      register long gap;
      int send_size = packet_size;


      *(((long*)buf)+0) = htonl(packetcnt);
      *(((long*)buf)+1) = htonl(1);
      *(((long*)buf)+3) = htonl(total_pairs);

      current_gap = din;
      
      *(((long*)buf)+2) = htonl(current_gap);      
      gettimeofday(&first,NULL);
      if(send(spruce_socket, buf, send_size, 0) < 0){
	if(errno == ENOBUFS){
	  packetcnt++;
	  dropcnt++;
	  continue;
	}
	  
	perror("send pair1");
	exit(1);
      }

      *(((long*)buf)+1) = htonl(2);

    
      /*spin for a little while, then send second packet*/
      target.tv_sec = first.tv_sec;
      target.tv_usec = first.tv_usec + current_gap;
      if(target.tv_usec >= 1000000){
	target.tv_sec++;
	target.tv_usec -= 1000000;
      }
      
      do{
	gettimeofday(&current_time,NULL);
	diff = (target.tv_sec - current_time.tv_sec) * 1000000 +
	  (target.tv_usec - current_time.tv_usec);
	gap = (current_time.tv_sec - first.tv_sec) * 1000000 +
	  (current_time.tv_usec - first.tv_usec);
	*(((long*)buf)+4) = htonl(gap);
      } while(diff > 0);

      if(send(spruce_socket, buf, send_size, 0) < 0){
	if(errno == ENOBUFS){
	  packetcnt++;
	  dropcnt++;
	  continue;
	}
	perror("send pair2");
	exit(1);
      }

      packetcnt++;

    }
      
  }

}


int
main(int argc, char *argv[])
{
  long abw=0;

  printf("sender starting up\n");

  starttime = time(NULL);

  prepare_buffers();
  process_args(argc, argv);
  control_connect();
  prep_sockets();

  spruce_test();

  abw = get_spruce_rate();
  fprintf(stderr, "availalble bandwidth estimate: %ld Kbps\n", abw);
  
  control_exit();
  
  printf("sender finished\n");
  
  exit(0);
}
