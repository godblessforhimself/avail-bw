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
int port = 11106, packet_size = 1472, packet_pair_number = 100;
int probing_rate = 0, link_capacity = 0;
FILE *timestamp_file = NULL;
char server_ip_str[16], client_ip_str[16];
unsigned int server_ip, client_ip;
int tcp_client=-1, udp_client=-1;
sockaddr_in server_addr, client_addr;
char msg_buf[4096];
int server_environment = -1;
timespec gap_in_pair, gap_between_pair;
void Usage() {
    printf("Avail-bw estimator client usage:\n");
	printf("\tavail-client [-o timestamp_file] [-p dst_port]\n");
	printf("\t           [-r probing_rate] dst_address\n");
	printf("\t-p      port number.\n");
    printf("\t-r      probing rate.\n");
    printf("\t-o      output timestamp filename.\n");
    printf("\t-h      print this message.\n");
    printf("\t-c      capacity.\n");
	printf("dst_address     can be either an IP address\n\n");
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
    const char *opt_string = "o:p:r:c:";
    int ret;
    while ((ret = getopt(argc, argv, opt_string)) != -1) {
        switch (ret) {
            case 'c':
                link_capacity = atoi(optarg);
                break;
            case 'r':
                probing_rate = atoi(optarg);
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
    return 0;
}
int start_tcp() {
    /*
        0正常，1异常
        connect
    */
    tcp_client = socket(AF_INET, SOCK_STREAM, 0);
    if (connect(tcp_client, (sockaddr*)&server_addr, sizeof(server_addr))) {
        return -1;
    }
    memset(msg_buf, 0, sizeof(msg_buf));
    ssize_t recv_size = recv(tcp_client, msg_buf, sizeof(int), 0);
    if (recv_size != sizeof(int)) {
        return -1;
    }
    server_environment = *(int*)msg_buf;
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
    gap_in_pair.tv_sec = 0; gap_in_pair.tv_nsec = packet_size * 8 * 1000 / link_capacity;
    gap_between_pair.tv_sec = 0; gap_between_pair.tv_nsec = 2 * 8 * 1000 * packet_size / probing_rate - gap_in_pair.tv_nsec;
    printf("Gaps are %ld %ld\n", gap_in_pair.tv_nsec, gap_between_pair.tv_nsec);
    printf("wait 3 seconds for sending UDP data\n");
    sleep(3);
    memset(msg_buf, 0, sizeof(msg_buf));
    timespec start_times[packet_pair_number], finish_times[packet_pair_number];
    ssize_t send_size = 0;
    int ret;
    time_control::init_wait(&gap_in_pair);
    for (int i = 0; i < packet_pair_number; i++) {
        *((int*)msg_buf) = i;
        send_size += sendto(udp_client, msg_buf, packet_size, 0, (sockaddr*)&server_addr, sizeof(server_addr));
        get_time(start_times+i);
        ret = clock_nanosleep(CLOCK_TAI, 0, &gap_in_pair, NULL);
        if (ret) {
            printf("Nanosleep 1 failed\n");
            return -2;
        }
        send_size += sendto(udp_client, msg_buf, packet_size, 0, (sockaddr*)&server_addr, sizeof(server_addr));
        get_time(finish_times+i);
        ret = clock_nanosleep(CLOCK_TAI, 0, &gap_between_pair, NULL);
        if (ret) {
            printf("Nanosleep 2 failed\n");
            return -3;
        }
    }
    printf("Total send %ld bytes, expected %d bytes\n", send_size, 2 * packet_pair_number * packet_size);
    if (timestamp_file != NULL) {
        char text_buffer[packet_pair_number * 2 * 21 + 1], *tmp = text_buffer; 
        memset(text_buffer, 0, sizeof(text_buffer));
        tmp = timespec2str(tmp, start_times, packet_pair_number);
        tmp = timespec2str(tmp, finish_times, packet_pair_number);
        fprintf(timestamp_file, "%s", text_buffer);
    }
    return 0;
}

struct server_report {
    timespec start, finish;
    int sequence_number;
    int set(timespec s, timespec f, int sn) {start = s; finish = f; sequence_number = sn; return 0;}
};
struct server_report_short {
    timespec_short start, finish;
    int sequence_number;
    int set(timespec_short s, timespec_short f, int sn) {start = s; finish = f; sequence_number = sn; return 0;}
};
int rcv_on_tcp() {
    /*
        0正常，1异常
        recv or read
    */
    printf("wait 3 seconds for tcp report\n");
    sleep(3);
    if (server_environment == 64) {
        server_report report_buffer[packet_pair_number]; 
        timespec start_times[packet_pair_number], finish_times[packet_pair_number];
        int sequence_number[packet_pair_number];
        memset(report_buffer, 0, sizeof(report_buffer));
        ssize_t recv_size = recv(tcp_client, report_buffer, sizeof(report_buffer), 0);
        if (recv_size != (ssize_t)sizeof(report_buffer)) {
            printf("Recv bytes < expected %lu bytes\n", sizeof(report_buffer));
        } else
            printf("Recv %ld bytes from server\n", recv_size);
        for (int i = 0; i < packet_pair_number; i++) {
            start_times[i] = report_buffer[i].start;
            finish_times[i] = report_buffer[i].finish;
            sequence_number[i] = report_buffer[i].sequence_number;
        }
        if (timestamp_file != NULL) {
            char text_buffer[packet_pair_number * 2 * (21 + 11) + 1], *tmp = text_buffer;
            memset(text_buffer, 0, sizeof(text_buffer));
            tmp = timespec2str(tmp, start_times, packet_pair_number);
            tmp = timespec2str(tmp, finish_times, packet_pair_number);
            tmp = int2str(tmp, sequence_number, packet_pair_number);
            
            fprintf(timestamp_file, "%s", text_buffer);
        }
    } else {
        server_report_short report_buffer[packet_pair_number]; 
        timespec_short start_times[packet_pair_number], finish_times[packet_pair_number];
        int sequence_number[packet_pair_number];
        memset(report_buffer, 0, sizeof(report_buffer));
        ssize_t recv_size = recv(tcp_client, report_buffer, sizeof(report_buffer), 0);
        if (recv_size != (ssize_t)sizeof(report_buffer)) {
            printf("Recv %ld bytes < expected %lu bytes\n", recv_size, sizeof(report_buffer));
        } else
            printf("Recv %ld bytes from server\n", recv_size);
        for (int i = 0; i < packet_pair_number; i++) {
            start_times[i] = report_buffer[i].start;
            finish_times[i] = report_buffer[i].finish;
            sequence_number[i] = report_buffer[i].sequence_number;
        }
        if (timestamp_file != NULL) {
            char text_buffer[packet_pair_number * 2 * (21 + 11) + 1], *tmp = text_buffer;
            memset(text_buffer, 0, sizeof(text_buffer));
            tmp = timespec2str(tmp, start_times, packet_pair_number);
            tmp = timespec2str(tmp, finish_times, packet_pair_number);
            tmp = int2str(tmp, sequence_number, packet_pair_number);
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
        return -1;
    } else {
        if (send_on_udp()) {
            return -2;
        } else {
            if (rcv_on_tcp()) {
                return -3;
            } else {
                close_all();
            }
        }
    }
}