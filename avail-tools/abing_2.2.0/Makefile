# Generated automatically from Makefile.in by configure.
CC = gcc
# CFLAGS = -g -O4 -Wall -I.
CFLAGS=-g -O2 

LIBS = -lnsl -lm 
# for sun
# LIBS = -lposix4 -lxnet -lm -lsocket -lnsl

CPU = i686

SRC=	Src
BIN=	Bin/$(CPU)

SRC=    Src
BIN=    Bin/$(CPU)

EOBJS=   $(SRC)/abw_rfl.c
FOBJS=   $(SRC)/abw.c $(SRC)/msdelay.c \
		$(SRC)/do_client.c $(SRC)/abw6.c

OBJS=    $(FOBJS) $(EOBJS)

TARGETS=$(BIN)/abw_rfl $(BIN)/abing 

all: $(TARGETS)

$(BIN)/abw_rfl: $(SRC)/abw_rfl.c $(SRC)/abw.h
	./mkinstalldirs $(BIN)
	$(CC) $(CFLAGS) $(EOBJS) -o $(BIN)/abw_rfl $(LIBS)

$(BIN)/abing: $(SRC)/abw.c $(SRC)/msdelay.c $(SRC)/abw.h \
	$(SRC)/do_client.c  $(SRC)/abw6.c
	./mkinstalldirs $(BIN)
	$(CC) $(CFLAGS) $(FOBJS) -o $(BIN)/abing $(LIBS)

clean: 
	rm -f ${TARGETS}
	rm -f config.cache config.log config.status

distclean: clean
	rm -f Makefile configure config.h

configure: configure.in
	autoconf

Makefile: Makefile.in configure
	./configure
