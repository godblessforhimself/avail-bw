/******************************************************************************/
/*
This file is part of "Abing" package.
Abing is Available bandwidth estimation tool based on Packet-Pair Dispersion 
Technique. 
Copyright (C) 2003 Jiri Navratil

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details (COPYING).

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software Foundation,
    Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

 ABing is result of the research in frame of the Project INCITE (Edge-based 
 Traffic Processing and Service Interface for High-Performance Network) 
 It is common project of RICE University, Los Alamos National Labs and 
 SLAC - Stanford Linear Accelerator (see http://incite.rice.edu) 
 supported from DoE in frame of SCIDAC program.
*/
/******************************************************************************/

#define RECVPORT	8175		/* port on which receiver waits */
#define	MIRRPORT	8176		/* port on which echo process waits */
#define MAXBUFF		32768		/* Maximum receive buffer */
#define LPP             1450            /* default packet size */
#define LCT             1500            /* default packet size */

#define NPKT            2               /* default number of packets */
#define	MAXMESG		8192		/* Maximum Message */
// #define	MAXMESG		16384		/* Maximum Message */
#define	MAXNAME		120		
#define MAXMBIN 	500
#define MAXPK 		200
#define MAXPP 		MAXPK/2
#define NMOD 		120
#define NMODMAX 	120	

#define	NO		0
#define	YES		1
// #define DELAYTIME       26           /* default 25 ms between PPairs */
#define DELAYTIME       50           /* 50 ms between PPairs ifor slow connections */
/**********************/
struct ABWrec {
	struct	timeval	snd;		/* sender's timestamp */
	struct	timeval	mirr;		/* reflector's timestamp */
	struct	timeval	rcv;		/* receiver's timestamp */
	int	num;			/* sender's pkt number */
	int	rnum;			/* return's pkt number */
	int     ppseq;                  /* packets in sequence(train) */
	unsigned short int rrcvport;	/* rel.rcvport send as info to rfl */ 
};
/**********************/
struct ABWreport {
	struct  timeval stmp;
	double	t_abw;
	double  t_xtr;
	double  t_dbc;
	double	f_abw;
	double  f_xtr;
	double  f_dbc;
	double  rtt;
	int 	rindex;
};
/**********************/
struct thread_args
	{
	int thread_id;
	char *hname;
	char *dirname;
	char *pkey;
	struct ABWreport *ptreport;
	unsigned short int rrcvport;
	unsigned short int mirrport;
};	
/**********************/
