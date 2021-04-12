#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <net/if.h>
#include <netinet/if_ether.h>
#include <net/ethernet.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <arpa/inet.h>
#include <pcap.h>
/* 将大小减去4字节 */
int main(int argc, char **argv) {
    pcap_t *fin;
    char errbuf[PCAP_ERRBUF_SIZE];
	struct pcap_pkthdr *p1, header;
	const u_char *p2;
	u_char data[2000];
	int res;
    if(argc < 2) {
        printf("usage: %s input output\n", argv[0]);
        return -1;
    }
    fin = pcap_open_offline(argv[1], errbuf);
    if (fin == NULL) {
	    fprintf(stderr, "\npcap_open_offline() failed: %s\n", errbuf);
	    return 0;
    }
	res = pcap_datalink(fin);
	pcap_dumper_t *fout;
	pcap_t *outputFormat = pcap_open_dead(res, 65536);
	if (argc == 3)
		fout = pcap_dump_open(outputFormat, argv[2]);
	fprintf(stdout, "data link type is %d\n", res);
	int i = 0;
	do {
		res = pcap_next_ex(fin, &p1, &p2);
		memcpy(&header, p1, sizeof(header));
		memcpy(data, p2, header.caplen);
		header.len -= 4;
		if (argc == 3)
			pcap_dump((u_char*)fout, &header, data);
	} while (res == 1);
	pcap_close(outputFormat);
	if (argc == 3)
		pcap_dump_close(fout);
	pcap_close(fin);
    return 0;
}