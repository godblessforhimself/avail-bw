CC = gcc
#CFLAGS = -g -Wall -O2
CFLAGS = -g -Wall -Werror -O2
LDFLAGS = -lm
INCLUDEDIRS = 

HEADERS = spruce.h
LIBOBJS = 
OBJS = $(LIBOBJS)

TARGETS = spruce_snd spruce_rcv

all: $(TARGETS)

spruce_snd: spruce_snd.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS) 

spruce_rcv: spruce_rcv.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS) 

%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) $(INCLUDEDIRS) -c $<

clean:
	rm -f *.o core
	rm -f $(TARGETS)

