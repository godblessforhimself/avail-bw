#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <time.h>
#include "utils.h"
/*
    服务器监听TCP端口
    客户端发起TCP连接
    客户端发送UDP包，服务器接收UDP包
    服务器通过TCP发送结果
*/
int port = 11106, packet_size = 1472, packet_continous_count = 2, packet_pair_number = 1000, packet_total_count = 0;
double probing_rate = 1;
FILE *timestamp_file = NULL;
char server_ip_str[16], client_ip_str[16];
unsigned int server_ip, client_ip;
int tcp_client=-1, udp_client=-1;
sockaddr_in server_addr, client_addr;
char msg_buf[4096];
int server_environment = -1;
timespec gap_between_pair;
void Usage() {
    printf("Avail-bw estimator client usage:\n");
	printf("\tavail-client [-C] [-L] [-R]\n");
	printf("\t        [-o timestamp_file] [-p dst_port] dst_address\n");
	printf("\t-p      port number.\n");
    printf("\t-C      continous count.\n");
    printf("\t-L      pair count.\n");
    printf("\t-R      probing rate.(Mbps)\n");
    printf("\t-o      output timestamp filename.\n");
    printf("\t-h      print this message.\n");
	printf("dst_address     can be either an IP address\n");
    printf("example: ./avail-client -C 5 -L 100 -R 10.0 -o f.txt 10.10.114.21\n\n");
	exit(1);
}
int get_time(timespec *ts) {
    return clock_gettime(CLOCK_TAI, ts);
}
int parse_args(int argc, char *argv[]) {
    /* 
        0正常，1异常
        port
    */
    const char *opt_string = "o:p:R:C:L:h";
    int ret;
    while ((ret = getopt(argc, argv, opt_string)) != -1) {
        switch (ret) {
            case 'L':
                packet_pair_number = atoi(optarg);
                break;
            case 'C':
                packet_continous_count = atoi(optarg);
                break;
            case 'R':
                probing_rate = atof(optarg);
                break;
            case 'p':
                port = atoi(optarg);
                break;
            case 'o':
                if ((timestamp_file = fopen(optarg, "w")) == NULL) {
                    printf("open file %s fail.\n", optarg);
                }
                break;
            case '?':
                printf("Parse arg optopt: %c\n", optopt);
                printf("Parse arg opterr: %d\n", opterr);
                printf("optarg is %s\n", optarg);
                break;
            default:
                break;
        }
    }
    switch (argc - optind) {
        case 1:
            strcpy(server_ip_str, argv[optind]);
            server_ip = inet_addr(server_ip_str);
            server_addr.sin_addr.s_addr = server_ip;
            server_addr.sin_family = AF_INET;
            server_addr.sin_port = htons(port);
            break;
        default:
            printf("Lack of IP\n");
            Usage();
            return -1;
    }
    packet_total_count = packet_continous_count * packet_pair_number;
    return 0;
}
int start_tcp() {
    /*
        0正常，1异常
        connect
    */
    tcp_client = socket(AF_INET, SOCK_STREAM, 0);
    timeval timeout;      
    timeout.tv_sec = 3;
    timeout.tv_usec = 0;
    if (setsockopt(tcp_client, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout, sizeof(timeout)) < 0) {
        printf("Set Recv timeout error %d\n", errno);
        return -6;
    }
    if (connect(tcp_client, (sockaddr*)&server_addr, sizeof(server_addr))) {
        return -1;
    }
    // 服务器向客户端发送位数
    memset(msg_buf, 0, sizeof(msg_buf));
    ssize_t recv_size = recv(tcp_client, msg_buf, sizeof(int), 0);
    if (recv_size != sizeof(int)) {
        return -2;
    }
    server_environment = *(int*)msg_buf;
    // 客户端向服务器发送packet_continous_count, packet_pair_number
    memset(msg_buf, 0, sizeof(msg_buf));
    *(int*)msg_buf = packet_continous_count;
    *((int*)msg_buf + 1) = packet_pair_number;
    ssize_t send_size = send(tcp_client, msg_buf, 2*sizeof(int), 0);
    if (send_size != (ssize_t)2*sizeof(int)) {
        return -3;
    }
    return 0;
}
struct timespec_short
{
    unsigned int tv_sec;		/* Seconds.  */
    unsigned int tv_nsec;	/* Nanoseconds.  */
};
char *timespec2str(char *dst, timespec *ts) {
    /*
        [10].[9] 
    */
    sprintf(dst, "%10lu.%09lu", (long)ts->tv_sec, ts->tv_nsec);
    return dst+20;
}
char *timespec2str(char *dst, timespec *ts, int number) {
    /*
        [10].[9] 
    */
    for (int i = 0; i < number - 1; i++) {
        dst = timespec2str(dst, ts + i);
        *dst = ','; dst++;
    }
    dst = timespec2str(dst, ts + number-1);
    *dst = '\n';
    return ++dst;
}
char *timespec2str(char *dst, timespec_short *ts) {
    /*
        [10].[9] 
    */
    sprintf(dst, "%10u.%09u", ts->tv_sec, ts->tv_nsec);
    return dst+20;
}
char *timespec2str(char *dst, timespec_short *ts, int number) {
    /*
        [10].[9] 
    */
    for (int i = 0; i < number - 1; i++) {
        dst = timespec2str(dst, ts + i);
        *dst = ','; dst++;
    }
    dst = timespec2str(dst, ts + number-1);
    *dst = '\n';
    return ++dst;
}
char *int2str(char *dst, int *src) {
    sprintf(dst, "%5d", *src);
    return dst+5;
}
char *int2str(char *dst, int *src, int number) {
    for (int i = 0; i < number - 1; i++) {
        dst = int2str(dst, src + i);
        *dst = ','; dst++;
    }
    dst = int2str(dst, src + number - 1);
    *dst = '\n';
    return ++dst;
}
int send_on_udp() {
    /*
        0正常，1异常
        sendto
    */
    udp_client = socket(AF_INET, SOCK_DGRAM, 0);
    if (udp_client == -1) {
        return -1;
    }
    gap_between_pair.tv_sec = 0;
    gap_between_pair.tv_nsec = (long)((double)(packet_continous_count*8*1000*packet_size)/probing_rate);
    if (gap_between_pair.tv_nsec > 1e9) {
        printf("send_on_tcp->too large gap %ld\n", gap_between_pair.tv_nsec);
        return -2;
    }
    printf("Gap is %ld, probing time is %f\n", gap_between_pair.tv_nsec, (double)(gap_between_pair.tv_nsec * packet_pair_number)/(1e9));
    printf("Total count is %d\n", packet_total_count);
    printf("wait 1 seconds for sending UDP data\n");
    sleep(1);
    memset(msg_buf, 0, sizeof(msg_buf));
    timespec timestamps[packet_total_count];
    ssize_t send_size = 0;
    int ret, index = 0;
    for (int i = 0; i < packet_pair_number; i++) {
        for (int j = 0; j < packet_continous_count; j++) {
            *((int*)msg_buf) = index;
            send_size += sendto(udp_client, msg_buf, packet_size, 0, (sockaddr*)&server_addr, sizeof(server_addr));
            get_time(timestamps+index);
            index++;
        }
        ret = clock_nanosleep(CLOCK_TAI, 0, &gap_between_pair, NULL);
        if (ret) {
            printf("Nanosleep failed\n");
            return -3;
        }
    }
    printf("Total send %ld bytes, expected %d bytes\n", send_size, packet_total_count * packet_size);
    if (timestamp_file != NULL) {
        char text_buffer[21*packet_total_count + 1], *tmp = text_buffer; 
        memset(text_buffer, 0, sizeof(text_buffer));
        tmp = timespec2str(tmp, timestamps, packet_total_count);
        fprintf(timestamp_file, "%s", text_buffer);
    }
    return 0;
}

struct server_report {
    timespec timestamp;
    int sequence_number;
    int set(timespec ts, int sn) {timestamp = ts; sequence_number = sn; return 0;}
};
struct server_report_short {
    timespec_short timestamp;
    int sequence_number;
    int set(timespec_short s, int sn) {timestamp = s; sequence_number = sn; return 0;}
};
int rcv_on_tcp() {
    /*
        0正常，1异常
        recv or read
    */
    printf("wait for tcp report\n");
    if (server_environment == 64) {
        server_report report_buffer[packet_total_count]; 
        timespec timestamps[packet_total_count];
        int sequence_number[packet_total_count];
        memset(report_buffer, 0, sizeof(report_buffer));
        ssize_t recv_size;
        int offset = 0;
        while (offset<sizeof(report_buffer)) {
            recv_size = recv(tcp_client, (void*)report_buffer+offset, sizeof(report_buffer), 0);
            if (recv_size <= 0) {
                printf("Client.rcv_on_tcp.timeout error %d, rs %ld\n", errno, recv_size);
                return -1;
            }
            else
                offset += recv_size;
        }
        if (offset != sizeof(report_buffer)) {
            printf("Recv %d bytes < expected %lu bytes\n", offset, sizeof(report_buffer));
        } else
            printf("Recv %d bytes from server\n", offset);
        for (int i = 0; i < packet_total_count; i++) {
            timestamps[i] = report_buffer[i].timestamp;
            sequence_number[i] = report_buffer[i].sequence_number;
        }
        if (timestamp_file != NULL) {
            char text_buffer[packet_total_count*(21+6) + 1], *tmp = text_buffer;
            memset(text_buffer, 0, sizeof(text_buffer));
            tmp = timespec2str(tmp, timestamps, packet_total_count);
            tmp = int2str(tmp, sequence_number, packet_total_count);
            fprintf(timestamp_file, "%s", text_buffer);
        }
    } else {
        server_report_short report_buffer[packet_total_count]; 
        timespec_short timestamps[packet_total_count];
        int sequence_number[packet_total_count];
        memset(report_buffer, 0, sizeof(report_buffer));
        ssize_t recv_size = recv(tcp_client, report_buffer, sizeof(report_buffer), 0);
        if (recv_size != (ssize_t)sizeof(report_buffer)) {
            printf("Recv %ld bytes < expected %lu bytes\n", recv_size, sizeof(report_buffer));
        } else
            printf("Recv %ld bytes from server\n", recv_size);
        for (int i = 0; i < packet_total_count; i++) {
            timestamps[i] = report_buffer[i].timestamp;
            sequence_number[i] = report_buffer[i].sequence_number;
        }
        if (timestamp_file != NULL) {
            char text_buffer[packet_total_count*(21+6) + 1], *tmp = text_buffer;
            memset(text_buffer, 0, sizeof(text_buffer));
            tmp = timespec2str(tmp, timestamps, packet_total_count);
            tmp = int2str(tmp, sequence_number, packet_total_count);
            fprintf(timestamp_file, "%s", text_buffer);
        }
    }
    return 0;
}
int close_all() {
    /*
        0正常，1异常
        close
    */
    close(tcp_client);
    close(udp_client);
    if (timestamp_file != NULL)
        fclose(timestamp_file);
    return 0;
}
int main(int argc, char *argv[]) {
    if (parse_args(argc, argv)) return 0;
    if (start_tcp()) {
        printf("Start tcp failed\n");
        close_all();
        return -1;
    } else {
        if (send_on_udp()) {
            printf("Send on udp failed\n");
            close_all();
            return -2;
        } else {
            if (rcv_on_tcp()) {
                printf("Rcv on tcp failed\n");
                close_all();
                return -3;
            } else {
                close_all();
            }
        }
    }
}