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
#define MAX_PACKET_NUMBER (1000)
int port = 11106, packet_size = 1472, packet_pair_number = 100;
int tcp_server = -1, tcp_client = -1, udp_server=-1, udp_client=-1; // socket fd
int conn_fd = -1; // the return fd of accept(tcp_server)
sockaddr_in client_addr, server_addr;
char msg_buf[4096], expected_buf[4096];
int sequence_number[MAX_PACKET_NUMBER], packet_valid[MAX_PACKET_NUMBER];
timespec start_times[MAX_PACKET_NUMBER], finish_times[MAX_PACKET_NUMBER];
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
    udp_server = socket(AF_INET, SOCK_DGRAM, 0);
    int optval = 1;
    if (setsockopt(udp_server, SOL_SOCKET, SO_REUSEADDR, (const void*)&optval, sizeof(int)) == -1) {
        printf("Set reuse error\n");
        return -2;
    }
    if (bind(udp_server, (sockaddr*)&server_addr, sizeof(server_addr))) {
        printf("Bind error %d\n", errno);
        return -2;
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
    memset(msg_buf, 0, sizeof(msg_buf)); memset(expected_buf, 0, sizeof(expected_buf)); memset(packet_valid, 0, sizeof(packet_valid));
    socklen_t cli_len = sizeof(client_addr);
    ssize_t recv_size = 0, recv_tmp;
    printf("Waiting UDP packets\n");
    for (int i = 0; i < packet_pair_number; i++) {
        recv_tmp = recvfrom(udp_server, msg_buf, packet_size, 0, (sockaddr*)&client_addr, &cli_len);
        get_time(start_times+i);
        if (recv_tmp == -1) {
            printf("Recv errno %d\n", errno);
        } else
            recv_size += recv_tmp;
        recv_tmp = recvfrom(udp_server, msg_buf, packet_size, 0, (sockaddr*)&client_addr, &cli_len);
        get_time(finish_times+i);
        if (recv_tmp == -1) {
            printf("Recv errno %d\n", errno);
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
    timespec start, finish;
    int sequence_number;
    int set(timespec s, timespec f, int sn) {start = s; finish = f; sequence_number = sn; return 0;}
};
int send_on_tcp() {
    /*
        0正常，1异常
        send 

    */
    server_report report_buffer[packet_pair_number];
    memset(report_buffer, 0, sizeof(report_buffer));
    for (int i = 0; i < packet_pair_number; i++) {
        report_buffer[i].set(start_times[i], finish_times[i], sequence_number[i]);
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
        while (wait_connection() == 0) {
            if (rcv_on_udp()) {
                return -2;
            } else {
                if (send_on_tcp()) {
                    return -3;
                } else {
                    close_all();
                }
            }
        }
    }

}