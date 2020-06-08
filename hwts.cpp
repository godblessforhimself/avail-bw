#include <assert.h>
#include <sys/epoll.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>
#include <linux/errqueue.h>
#include <linux/net_tstamp.h>
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MODE_SERVER (1)
#define MODE_CLIENT (2)
#define SERVER_RECV_LOSS (1)
#define CLIENT_WAITING_SIGNAL (2)
#define SERVER_ACKED (3)
#define SERVER_RECV_PAIR_SUCCESS (4)
#define CLIENT_SIGNAL_INVALID (5)
#define CLIENT_SIGNAL_VALID (6)
/*
    server
    sudo ./avail-server -p -20 -M S -C 1000 -L 100 -S 9000
    client
    sudo ./avail-client -p -20 -M C -C 1000 -L 100 -S 9000 -R 100 -B 1000 -O ../timestamps.txt 192.168.1.21
*/
int udp_packet_count = 100, udp_packet_size = 9674, udp_train_length = 50, udp_packet_rate = 10, link_speed = 1000, epoll_wait_ms = 72;
int server_tcp_fd = -1, conn_fd = -1, server_udp_fd = -1;
int client_tcp_fd = -1, client_udp_fd = -1;
char server_ip_str[16];
int mode = -1, priority = 0, savefile = 0;
int server_tcp_listen_port = 11106;
sockaddr_in local_addr, client_addr, server_addr;
char udp_data[10000], control_data[8192], tcp_data[256], *tcp_large_data = NULL;
int tcp_timespec_size = 0;
char filename[256];
FILE *server_timestamp = NULL, *client_file_descriptor = NULL;
timespec udp_packet_period;
int send_control_message(int fd, int mode = 0) {
    if (mode == 0)
        return write(fd, tcp_data, sizeof(tcp_data)) != sizeof(tcp_data);
    else
        return write(fd, tcp_large_data, tcp_timespec_size) != tcp_timespec_size;
}
int read_control_message(int fd, int mode = 0) {
    // 当接收的包超过MTU大小时需要接收多次
    ssize_t recv_size = 0, target, recv_sum = 0;
    if (mode == 0) {
        target = sizeof(tcp_data);
        recv_sum = read(fd, tcp_data, sizeof(tcp_data));
    } else {
        target = tcp_timespec_size;
        while (recv_sum < target) {
            recv_size = read(fd, tcp_large_data + recv_sum, tcp_timespec_size);
            recv_sum += recv_size;
        }
    }
    if (recv_sum != target) {
        printf("recv %zd, target %zd\n", recv_size, target);
    }
    return recv_sum != target;
}
double judge_valid(timespec *t) {
    int ns = t->tv_nsec;
    double us = ns / 1e3;
    double expected = 8 * udp_packet_count * (udp_packet_size + 68) / 1e4;
    return (double)(us) / expected;
}
int parse_args(int argc, char *argv[]) {
    const char *opt_string = "M:P:S:L:p:O:C:R:B:";
    int ret;
    while ((ret = getopt(argc, argv, opt_string)) != -1) {
        switch (ret)
        {
        case 'B':
            link_speed = atoi(optarg);
            break;
        case 'R':
            udp_packet_rate = atoi(optarg);
            break;
        case 'C':
            udp_packet_count = atoi(optarg);
            break;
        case 'O':
            savefile = 1;
            memset(filename, 0, sizeof(filename));
            strcpy(filename, optarg);
            break;
        case 'p':
            priority = atoi(optarg);
            break;
        case 'L':
            udp_train_length = atoi(optarg);
            break;
        case 'M':
            if (optarg[0] == 'C') {
                mode = MODE_CLIENT;
            } else if (optarg[0] == 'S') {
                mode = MODE_SERVER;
            } else {
                printf("Lack mode!\n");
                return -1;
            }
            break;
        case 'P':
            server_tcp_listen_port = atoi(optarg);
            break;
        case 'S':
            udp_packet_size = atoi(optarg);
            break;
        default:
            break;
        }
    }
    if (mode == MODE_CLIENT) {
        if (argc - optind != 1) {
            printf("Lack Server IP\n");
            return -2;
        }
        strcpy(server_ip_str, argv[optind]);
        server_addr.sin_addr.s_addr = inet_addr(server_ip_str);
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(server_tcp_listen_port);
        long ns_sum = (8 * long(1e3) * udp_packet_size * udp_packet_count / udp_packet_rate), ns_packet = ns_sum, sec_packet = 0;
        if (ns_sum >= long(1e9)) {
            ns_packet = ns_sum % (long)(1e9);
            sec_packet = ns_sum / (long)(1e9);
        }    
        udp_packet_period.tv_nsec = ns_packet;
        udp_packet_period.tv_sec = sec_packet;
        epoll_wait_ms = int(udp_packet_size * udp_packet_count / (125 * link_speed));
        if (epoll_wait_ms == 0)
            epoll_wait_ms = 1;
        printf("间隔时间 %ld.%09lds, 列车时间 %dms\n", sec_packet, ns_packet, epoll_wait_ms);
    }
    if (savefile) {
        if (mode == MODE_CLIENT) {
            client_file_descriptor = fopen(filename, "w");
        } else if (mode == MODE_SERVER) {
            server_timestamp = fopen(filename, "w");
        }
    }
    tcp_timespec_size = sizeof(timespec) * udp_packet_count;
    tcp_large_data = new char[tcp_timespec_size];
    return 0;
}
void print_sockaddr(sockaddr_in *addr) {
    printf("address %s, port %d\n", inet_ntoa(addr->sin_addr), addr->sin_port);
}
void set_control_message(timespec *t) {
    *(timespec*)tcp_data = *t;
}
void set_control_message(int message) {
    *(int*)tcp_data = message;
}
int get_control_message() {
    return *(int*)tcp_data;
}
int set_reuse_addr(int fd) {
    int optval = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (const void*)&optval, sizeof(int)) == -1) {
        printf("Set reuse error\n");
        return -1;
    }
    return 0;
}
int set_timestamp_on(int fd, int mode) {
    int val = SOF_TIMESTAMPING_RAW_HARDWARE | SOF_TIMESTAMPING_SOFTWARE, err;
    if (mode == MODE_SERVER) {
        val |= SOF_TIMESTAMPING_RX_SOFTWARE;
        err = setsockopt(fd, SOL_SOCKET, SO_TIMESTAMPING, &val, sizeof(val));
        if (err) {
            printf("set timestamp on failed on server, errno %d\n", errno);
            return -1;
        }
        return 0;
    } else if (mode == MODE_CLIENT) {
        val |= SOF_TIMESTAMPING_OPT_TSONLY;
        err = setsockopt(fd, SOL_SOCKET, SO_TIMESTAMPING, &val, sizeof(val));
        if (err) {
            printf("set timestamp on failed on client, errno %d\n", errno);
            return -1;
        }
        return 0;
    }
    return -2;
}
int set_timeout(int fd, int sec, int usec) {
    timeval timeout;
    timeout.tv_sec = sec;
    timeout.tv_usec = usec;
    if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, (char*)&timeout, sizeof(timeout)) < 0) {
        printf("Set Recv timeout error %d\n", errno);
        return -1;
    }
    return 0;
}
int get_buffer_size(int fd) {
    int buffer_size;
    socklen_t slen = sizeof(int);
    if (getsockopt(fd, SOL_SOCKET, SO_RCVBUF, &buffer_size, &slen)) {
        return -1;
    }
    return buffer_size;
}
int set_recv_buffer(int fd, int buffer_size) {
    if (setsockopt(fd, SOL_SOCKET, SO_RCVBUF, (const char*)&buffer_size, sizeof(int))) {
        printf("set recv buffer failed, error %s\n", strerror(errno));
        return -1;
    }
    return 0;
}
int bind_local_port(int fd, sockaddr_in *addr) {
    if (bind(fd, (sockaddr*)addr, sizeof(sockaddr_in))) {
        return -1;
    }
    return 0;
}
void set_local_port(sockaddr_in *addr, int port) {
    memset(addr, 0, sizeof(sockaddr_in));
    addr->sin_family = AF_INET;
    addr->sin_addr.s_addr = htonl(INADDR_ANY);
    addr->sin_port = htons(port);
}
void print_timespec(timespec *t, int mode) {
    if (mode == 0) {
        printf("%10ld.%06d.%03d\n", t->tv_sec, int(t->tv_nsec / 1000), int(t->tv_nsec % 1000));
    } else if (mode == 1) {
        long ns = t->tv_nsec;
        int high = ns / 1e6, middle = (ns % int(1e6)) / int(1e3), low = ns % int(1e3);
        printf("%10ld.%03d.%03d.%03d\n", t->tv_sec, high, middle, low);
    }
}
void print_scmtimestamp(scm_timestamping *ts) {
    timespec *temp = &ts->ts[0];
    print_timespec(temp, 0);
}
void handle_time(msghdr *msg) {
    for (cmsghdr *cmsg = CMSG_FIRSTHDR(msg); cmsg; cmsg = CMSG_NXTHDR(msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_IP && cmsg->cmsg_type == IP_RECVERR) {
            continue;
        } else if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            scm_timestamping *ts = (scm_timestamping*)CMSG_DATA(cmsg);
            print_scmtimestamp(ts);
        }
    }
}
void msg2timespec(msghdr *msg, timespec *t) {
    for (cmsghdr *cmsg = CMSG_FIRSTHDR(msg); cmsg; cmsg = CMSG_NXTHDR(msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_IP && cmsg->cmsg_type == IP_RECVERR) {
            continue;
        } else if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            scm_timestamping *ts = (scm_timestamping*)CMSG_DATA(cmsg);
            *t = ts->ts[0];
        }
    }
}
timespec diff_timespec(timespec *t2, timespec *t1) {
    bool carry = t2->tv_nsec < t1->tv_nsec;
    timespec ret;
    ret.tv_sec = carry ? t2->tv_sec - t1->tv_sec - 1 : t2->tv_sec - t1->tv_sec;
    ret.tv_nsec = carry ? t2->tv_nsec + 1e9 - t1->tv_nsec : t2->tv_nsec - t1->tv_nsec;
    return ret;
}
#define LENGTH_PER_TIMESPEC (21) //timespec输出时所占字符数
int timespec2str(char *dst, timespec *src) {
    sprintf(dst, "%10lu.%09lu", src->tv_sec, src->tv_nsec);
    return 20;
}
int timespecs2str(char *buf, timespec *head, int n) {
    char *temp = buf;
    for (int i = 0; i < n; i++) {
        if (i != n - 1) {
            temp += timespec2str(temp, head + i);
            temp[0] = ','; temp+=1;
        } else {
            temp += timespec2str(temp, head + i);
            temp[0] = '\n'; temp+=1;
        }
    }
    return temp-buf;
}
/*
    Server code
    listen
    accept
    udp init
    udp recv
*/
int server_tcp_init() {
    server_tcp_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_tcp_fd == -1) {
        return -1;
    }
    if (set_reuse_addr(server_tcp_fd)) {
        return -2;
    }
    set_local_port(&local_addr, server_tcp_listen_port);
    if (bind_local_port(server_tcp_fd, &local_addr)) {
        return -3;
    }
    if (listen(server_tcp_fd, 5)) {
        return -4;
    }
    return 0;
}
int wait_connection() {
    unsigned int client_len = sizeof(client_addr);
    conn_fd = accept(server_tcp_fd, (sockaddr*)&client_addr, &client_len);
    if (conn_fd == -1) {
        printf("Accept error %d\n", errno);
        return -1;
    } else {
        print_sockaddr(&client_addr);
        return 0;
    }
}
int server_udp_init() {
    server_udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (server_udp_fd == -1) {
        printf("init udp fd failed\n");
        return -1;
    }
    if (set_reuse_addr(server_udp_fd)) {
        return -2;
    }
    if (set_timestamp_on(server_udp_fd, MODE_SERVER)) {
        return -3;
    }
    int buffer_size = get_buffer_size(server_udp_fd);
    printf("server udp buffer size is %d\n", buffer_size);
    if (bind_local_port(server_udp_fd, &local_addr)) {
        return -5;
    }
    return 0;
}
int server_udp_recv() {
    iovec iov = {
        iov_base: udp_data,
        iov_len: size_t(udp_packet_size)
    };
    msghdr msg = {
        msg_name: (void*)&client_addr,
        msg_namelen: sizeof(sockaddr_in),  
        msg_iov: &iov,
        msg_iovlen: 1,
        msg_control: control_data,
        msg_controllen: sizeof(control_data),
        msg_flags: 0
    };
    timespec *timestamps = (timespec*)tcp_large_data;
    ssize_t recv_len;
    int index, control_msg, success_flag;
    for (int i = 0; i < udp_train_length; i++) {
        restart:
        success_flag = 0;
        /*
            设置udp包超时时间=2s，必须大于正常的包传输延时
        */
        if (set_timeout(server_udp_fd, 2, 0)) {
            printf("set timeout 1 failed\n");
        }
        for (int j = 0; j < udp_packet_count; j++) {
            recv_len = recvmsg(server_udp_fd, &msg, 0);
            index = *(int*)udp_data;
            if (recv_len == -1 || index != j) {
                if (recv_len == -1)
                    printf("server_udp_recv train %d, index %d, error %s\n", i, j, strerror(errno));
                else
                    printf("index mismatch train %d, index %d, %d\n", i, j, index);
                success_flag = 0;
                break;
            }
            msg2timespec(&msg, &timestamps[j]);
            if (j == udp_packet_count - 1) {
                success_flag = 1;
            }
        }
        /*
            设置udp包不阻塞，便于清空socket buffer
        */
        if (set_timeout(server_udp_fd, 0, 1)) {
            printf("set 2 failed\n");
        }
        if (read_control_message(conn_fd)) {
            printf("read cmsg failed 1\n");
            return -1;
        }
        control_msg = get_control_message();
        // 清空socket buffer
        while (recvmsg(server_udp_fd, &msg, 0) != -1) {;}
        if (control_msg == CLIENT_SIGNAL_INVALID) {
            printf("client invalid restart %d\n", i);
            set_control_message(SERVER_ACKED);
            if (send_control_message(conn_fd)) {
                return -1;
            }
            goto restart;
        } else if (control_msg == CLIENT_SIGNAL_VALID) {
            if (success_flag) {
                // 发送SERVER_RECV_PAIR_SUCCESS 发送timestamp
                set_control_message(SERVER_RECV_PAIR_SUCCESS);
                if (send_control_message(conn_fd)) {
                    printf("send fail 1\n");
                    return -1;
                }
                if (send_control_message(conn_fd, 1)) {
                    printf("send fail 2\n");
                    return -1;
                }
            } else {
                // 发送SERVER_RECV_LOSS
                set_control_message(SERVER_RECV_LOSS);
                if (send_control_message(conn_fd)) {
                    return -1;
                }
                goto restart;
            }
        }
    }
    return 0;
}
void server_close() {
    close(server_udp_fd);
    close(server_tcp_fd);
    close(conn_fd);
    if (server_timestamp != NULL)
        fclose(server_timestamp);
}
int server_main() {
    if (server_tcp_init()) {
        printf("server tcp init failed\n");
        return -1;
    }
    if (wait_connection()) {
        return -2;
    }
    if (server_udp_init()) {
        return -3;
    }
    if (server_udp_recv()) {
        return -4;
    }
    return 0;
}
/*
    Client Code
    tcp connect
    sleep 
    udp send
*/    
int client_tcp_connect() {
    client_tcp_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (client_tcp_fd == -1) {
        return -1;
    }
    if (connect(client_tcp_fd, (sockaddr*)&server_addr, sizeof(sockaddr_in))) {
        return -4;
    }
    return 0;
}
int client_udp_send() {
    client_udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (client_udp_fd == -1) {
        return -1;
    }
    if (set_timestamp_on(client_udp_fd, MODE_CLIENT)) {
        return -2;
    }
    iovec iov = {
        iov_base: udp_data,
        iov_len: (size_t)udp_packet_size
    };
    msghdr send_msg = {
        msg_name: (void*)&server_addr,
        msg_namelen: sizeof(sockaddr_in),
        msg_iov: &iov,
        msg_iovlen: 1,
        msg_control: NULL,
        msg_controllen: 0,
        msg_flags: 0
    };
    /*
        唯首尾包接收时间戳，设置首尾包选项
    */
    __u32 options = SOF_TIMESTAMPING_TX_SOFTWARE;
    union {
        char buf[CMSG_SPACE(sizeof(__u32))];
        cmsghdr align;
    } u;
    msghdr send_msg_sample_timestamp = {
        msg_name: (void*)&server_addr,
        msg_namelen: sizeof(sockaddr_in),
        msg_iov: &iov,
        msg_iovlen: 1,
        msg_control: u.buf,
        msg_controllen: sizeof(u.buf),
        msg_flags: 0
    };
    cmsghdr* cmsg = CMSG_FIRSTHDR(&send_msg_sample_timestamp);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SO_TIMESTAMPING;
    cmsg->cmsg_len = CMSG_LEN(sizeof(__u32));
    *((__u32 *) CMSG_DATA(cmsg)) = options;
    /*
        时间戳保存在control_data中
    */
    msghdr timestamp_msg = {
        msg_name: (void*)&server_addr,
        msg_namelen: sizeof(sockaddr_in),
        msg_iov: &iov,
        msg_iovlen: 1,
        msg_control: control_data,
        msg_controllen: sizeof(control_data),
        msg_flags: 0
    };
    ssize_t send_len, recv_len;
    int control_message, epoll_ret, train_valid;
    char text_buf[LENGTH_PER_TIMESPEC * (udp_packet_count + 1) + 1]; memset(text_buf, 0, sizeof(text_buf));
    long random_usec;
    timespec t[2], dt, remain_sleep = {0,0};
    int epoll_fd = epoll_create1(0), sleep_ret;
    epoll_event ev; ev.data.fd = client_udp_fd; ev.events = EPOLLERR;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_udp_fd, &ev);
    for (int i = 0; i < udp_train_length; i++) {
        client_restart:
        sleep_ret = clock_nanosleep(CLOCK_TAI, 0, &udp_packet_period, &remain_sleep);
        if (sleep_ret != 0) {
            printf("sleep ret %s, remain: ", strerror(sleep_ret));
            print_timespec(&remain_sleep, 1);
        }
        train_valid = 1;
        for (int j = 0; j < udp_packet_count; j++) {
            *(int*)udp_data = j;
            if (j == 0 || j == udp_packet_count - 1)
                send_len = sendmsg(client_udp_fd, &send_msg_sample_timestamp, 0);
            else
                send_len = sendmsg(client_udp_fd, &send_msg, 0);
            if (send_len != udp_packet_size) {
                train_valid = 0;
                printf("send train %d index %d, send ret %zd , error %s\n", i, j, send_len, strerror(errno));
                break;
            }
        }
        if (train_valid) {
            for (int j = 0; j < 2; j++) {
                /*
                    等待时间不小于列车时间
                */
                epoll_ret = epoll_wait(epoll_fd, &ev, 1, epoll_wait_ms); // ms
                if (epoll_ret != 1) {
                    train_valid = 0;
                    printf("epoll wait %d ret %d\n", j, epoll_ret);
                    break;
                }
                recv_len = recvmsg(client_udp_fd, &timestamp_msg, MSG_ERRQUEUE);
                if (recv_len == -1) {
                    train_valid = 0;
                    printf("send timestamp recv %zd, error %s\n", recv_len, strerror(errno));
                    break;
                }
                msg2timespec(&timestamp_msg, &t[j]);
            }
        }
        if (train_valid) {
            dt = diff_timespec(&t[1], &t[0]);
        }
        if (train_valid) {
            set_control_message(CLIENT_SIGNAL_VALID);
            if (send_control_message(client_tcp_fd)) {
                return -3;
            }
        } else {
            printf("train %d invalid \n", i);
            set_control_message(CLIENT_SIGNAL_INVALID);
            if (send_control_message(client_tcp_fd)) {
                return -4;
            }
        }
        if (read_control_message(client_tcp_fd)) {
            return -5;
        }
        control_message = get_control_message();
        if (control_message == SERVER_RECV_PAIR_SUCCESS) {
            if (read_control_message(client_tcp_fd, 1)) {
                return -6;
            }
            /*
                文件格式：
                t0,t1,...,t100\n
                t0为client发送第一个和最后一个包的时间差
                t1-t100是server收到第一个和最后一个包的时间
            */
            int offset = timespec2str(text_buf, &dt);
            text_buf[offset]=',';offset+=1;
            timespecs2str(text_buf+offset, (timespec*)tcp_large_data, udp_packet_count);
            fprintf(client_file_descriptor, "%s", text_buf);
        } else if (control_message == SERVER_RECV_LOSS) {
            printf("server %d SERVER_RECV_LOSS\n", i);
            goto client_restart;
        } else if (control_message == SERVER_ACKED) {
            printf("server %d SERVER_ACKED\n", i);
            goto client_restart;
        }
    }

    return 0;
}
int client_main() {
    int ret;
    if (client_tcp_connect()) {
        printf("client connect failed\n");
        return -1;
    }
    if ((ret = client_udp_send())) {
        printf("client udp send failed %d\n", ret);
        return -2;
    }
    return 0;
}
void client_close() {
    close(client_udp_fd);
    close(client_tcp_fd);
    if (client_file_descriptor) {
        printf("save %s\n", filename);
        fclose(client_file_descriptor);
    }
}
int main(int argc, char *argv[]) {
    timespec t1, t2, dt;
    clock_gettime(CLOCK_TAI, &t1);
    if (parse_args(argc, argv)) 
        return 0;
    if (setpriority(PRIO_PROCESS, 0, priority)) {
        printf("set priority %d failed\n", priority);
    }
    priority = getpriority(PRIO_PROCESS, 0);
    printf("priority %d\n", priority);
    if (mode == MODE_CLIENT) {
        client_main();
        client_close();
    } else if (mode == MODE_SERVER) {
        server_main();
        server_close();
    }
    clock_gettime(CLOCK_TAI, &t2);
    printf("program use:");
    dt = diff_timespec(&t2, &t1);
    print_timespec(&dt, 0);
    delete [] tcp_large_data;
}