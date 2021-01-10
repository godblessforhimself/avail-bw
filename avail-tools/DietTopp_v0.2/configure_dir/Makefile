# $Id: Makefile.in,v 1.9 2000/09/26 21:08:45 melander Exp $

SHELL = /bin/sh
srcdir = .


CC = gcc
CXX = g++
CFLAGS = -g -O2 -DPACKAGE_NAME=\"DietTopp\" -DPACKAGE_TARNAME=\"DietTopp.tar\" -DPACKAGE_VERSION=\"0.1\" -DPACKAGE_STRING=\"DietTopp\ 0.1\" -DPACKAGE_BUGREPORT=\"\" -DHAVE_LIBNSL=1 -DHAVE_LIBM=1 -D__LINUX_COMPILE=1 
CXXFLAGS = -g -O2 -DPACKAGE_NAME=\"DietTopp\" -DPACKAGE_TARNAME=\"DietTopp.tar\" -DPACKAGE_VERSION=\"0.1\" -DPACKAGE_STRING=\"DietTopp\ 0.1\" -DPACKAGE_BUGREPORT=\"\" -DHAVE_LIBNSL=1 -DHAVE_LIBM=1 -D__LINUX_COMPILE=1  
LIBS =  -lm -lnsl  

DIETTOPP_SRCS = common.h debugprint.h debugprint.c udppacketsender.h udppacketsender.cc measureobj.h measureobj.cc analyzeobj.h analyzeobj.cc receiverobj.h receiverobj.cc linreg.h linreg.cc

MEASURE_OBJS = analyzeobj.o udppacketsender.o measureobj.o debugprint.o linreg.o
SERVER_OBJS = receiverobj.o debugprint.o 


all:	server measure

server: $(SERVER_OBJS)
	$(CXX) -o server $(SERVER_OBJS) $(LIBS) 

measure: $(MEASURE_OBJS)
	$(CXX) -o measure $(MEASURE_OBJS) $(LIBS) 

clean:
	rm -f *.o printout.ps

clean_all: clean
	rm -f measure server 

print:
	a2ps -o printout.ps configure_dir/configure.in configure_dir/Makefile.in $(DIETTOPP_SRCS)

tar:
	tar -cvf DietTopp.tar *

.PHONY: all clean_all
