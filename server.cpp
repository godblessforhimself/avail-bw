#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <time.h>
#include <errno.h>
#if __GNUC__
#if __x86_64__ || __ppc64__
#define ENVIRONMENT64
#else
#define ENVIRONMENT32
#endif
#endif
/*
    服务器监听TCP端口
    客户端发起TCP连接
    客户端发送UDP包，服务器接收UDP包
    服务器通过TCP发送结果
*/
#define MAX_PACKET_NUMBER (100000)
int port = 11106, packet_size = 1472, packet_continous_count = 2, packet_pair_number = 1000, packet_total_count = 0;
int tcp_server = -1, tcp_client = -1, udp_server=-1, udp_client=-1; // socket fd
int conn_fd = -1; // the return fd of accept(tcp_server)
sockaddr_in client_addr, server_addr;
char msg_buf[4096];
int sequence_number[MAX_PACKET_NUMBER];
timespec timestamps[MAX_PACKET_NUMBER];
int parse_args(int argc, char *argv[]) {
    /* 
        0正常，1异常
        port
    */
    const char *opt_string = "p:";
    int ret;
    while ((ret = getopt(argc, argv, opt_string)) != -1) {
        switch (ret) {
            case 'p':
                port = atoi(optarg);
                break;
            case '?':
                printf("Parse arg optopt: %c\n", optopt);
                printf("Parse arg opterr: %d\n", opterr);
                break;
            default:
                break;
        }
    }
    return 0;
}
int init_sock() {
    /* 
        0正常，1异常
        初始化TCP监听端口
        sock, bind, listen
    */
    tcp_server = socket(AF_INET, SOCK_STREAM, 0);
    int optval = 1;
    if (setsockopt(tcp_server, SOL_SOCKET, SO_REUSEADDR, (const void*)&optval, sizeof(int)) == -1) {
        printf("Set reuse error\n");
        return -1;
    }
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(port);
    if (bind(tcp_server, (sockaddr*)&server_addr, sizeof(server_addr))) {
        return -1;
    }
    if (listen(tcp_server, 5)) {
        return -2;
    }
    return 0;
}
int wait_connection() {
    /* 
        0正常，1异常
        阻塞，等待新的连接，设置连接信息
        accept
    */
    printf("Server listening at %d\n", port);
    unsigned int client_len = sizeof(client_addr);
    conn_fd = accept(tcp_server, (sockaddr*)&client_addr, &client_len);
    printf("New TCP connection from client\n");
    if (conn_fd == -1) {
        printf("Accept error %d\n", errno);
        return -1;
    }
    memset(msg_buf, 0, sizeof(msg_buf));
    #ifdef ENVIRONMENT64
    *(int*)msg_buf = 64;
    #else
    *(int*)msg_buf = 32;
    #endif
    ssize_t send_size = send(conn_fd, msg_buf, sizeof(int), 0);
    if (send_size != (ssize_t)sizeof(int)) {
        return -1;
    }
    // 等待客户端发送packet_continous_count, packet_pair_number
    memset(msg_buf, 0, sizeof(msg_buf));
    ssize_t recv_size = recv(conn_fd, msg_buf, 2*sizeof(int), 0);
    if (recv_size != 2*sizeof(int)) {
        return -2;
    }
    packet_continous_count = *(int*)msg_buf;
    packet_pair_number = *((int*)msg_buf + 1);
    packet_total_count = packet_continous_count * packet_pair_number;
    printf("Client continous_count %d, pair count %d\n", packet_continous_count, packet_pair_number);
    if (packet_pair_number <= 0 || packet_continous_count <= 0) {
        return -3;
    }
    udp_server = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    int optval = 1;
    if (setsockopt(udp_server, SOL_SOCKET, SO_REUSEADDR, (const void*)&optval, sizeof(int)) == -1) {
        printf("Set reuse error\n");
        return -4;
    }
    timeval timeout;
    timeout.tv_sec = 1;
    timeout.tv_usec = 0;
    if (setsockopt(udp_server, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout, sizeof(timeout)) < 0) {
        printf("Set Recv timeout error %d\n", errno);
        return -6;
    }
    if (bind(udp_server, (sockaddr*)&server_addr, sizeof(server_addr))) {
        printf("Bind error %d\n", errno);
        return -5;
    }
    return 0;
}
int get_time(timespec *ts) {
    return clock_gettime(CLOCK_TAI, ts);
}
int rcv_on_udp() {
    /*
        0正常，1异常
        recvfrom 客户数据中的序号、验证
        start_times
        finish_times
        sequence_number
        packet_valid
    */
    memset(msg_buf, 0, sizeof(msg_buf));
    socklen_t cli_len = sizeof(client_addr);
    ssize_t recv_size = 0, recv_tmp;
    printf("Waiting %d UDP packets\n", packet_total_count);
    for (int i = 0; i < packet_total_count; i++) {
        recv_tmp = recvfrom(udp_server, msg_buf, packet_size, 0, (sockaddr*)&client_addr, &cli_len);
        get_time(timestamps+i);
        if (recv_tmp <= 0) {
            printf("Recv errno %d, rs %ld\n", errno, recv_tmp);
            printf("Only recv %ld bytes, current i %d\n", recv_size, i);
            return -1;
        } else
            recv_size += recv_tmp;
        sequence_number[i] = *(int*)msg_buf;
    }
    #ifdef ENVIRONMENT64
    printf("Recv %ld bytes from client\n", recv_size);
    #else
    printf("Recv %d bytes from client\n", recv_size);
    #endif
    return 0;
}
struct server_report {
    timespec timestamp;
    int sequence_number;
    int set(timespec ts, int sn) {timestamp = ts; sequence_number = sn; return 0;}
};
int send_on_tcp() {
    /*
        0正常，1异常
        send 

    */
    server_report report_buffer[packet_total_count];
    memset(report_buffer, 0, sizeof(report_buffer));
    for (int i = 0; i < packet_total_count; i++) {
        report_buffer[i].set(timestamps[i], sequence_number[i]);
    }
    ssize_t send_size = send(conn_fd, report_buffer, sizeof(report_buffer), 0);
    #ifdef ENVIRONMENT64
    printf("Send %lu bytes to client\n", send_size);
    #else
    printf("Send %u bytes to client\n", send_size);
    #endif
    return 0;
}
int close_all() {
    /*
        0正常，1异常
        close
    */
    close(conn_fd);
    close(udp_server);
    return 0;
}
int main(int argc, char *argv[]) {
    if (parse_args(argc, argv)) return 0;
    if (init_sock()) {
        return -1;
    } else {
        if (wait_connection() == 0) {
        //while (wait_connection() == 0) {
            if (rcv_on_udp()) {
                printf("Rcv on udp failed\n");
                close_all();
                return -2;
            } else {
                if (send_on_tcp()) {
                    printf("Send on tcp failed\n");
                    close_all();
                    return -3;
                } else {
                    close_all();
                }
            }
        }
    }

}