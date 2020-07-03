/*
	利用单向延迟回复推测可用带宽
	单向延迟测量
	队列长度选择
	测量间隔选择
	client
		./recover-client -M C 192.168.1.21
	server
		./recover-server -M S
*/
#include "util.cpp"
FILE *log_filename = stdout, *data_fd = NULL;
int running_mode = -1;
int cli_tcp_fd = -1, cli_udp_fd = -1;
char cli_server_ipstr[16];
int epoll_fd = epoll_create1(0);
epoll_event ev;
int serv_listen_fd = -1, serv_tcp_listen_port = 11106, serv_conn_fd = -1, serv_udp_fd = -1;
sockaddr_in local_addr, client_addr, server_addr;
char tcp_buffer[1024], udp_buffer[1024], control_buffer[8192];
void help() {
	fprintf(log_filename, "help information\n");
}
void wrap_help(char const *caller_name){
	fprintf(log_filename, "function: %s\n", caller_name);
	help();
}
#define help() wrap_help(__func__)
iovec iov = {
	iov_base: udp_buffer,
	iov_len: 0
};
union {
	char buf[CMSG_SPACE(sizeof(__u32))];
	cmsghdr align;
} u;
msghdr message_header = {
	msg_name: (void*)&server_addr,
	msg_namelen: sizeof(sockaddr_in),
	msg_iov: &iov,
	msg_iovlen: 1,
	msg_control: NULL,
	msg_controllen: 0,
	msg_flags: 0
};
int parse_args(int argc, char *argv[]) {
    const char *opt_string = "M:P:S:L:p:O:C:R:B:";
    int ret;
	char temp;
    while ((ret = getopt(argc, argv, opt_string)) != -1) {
        switch (ret)
        {
			case 'M':
				temp = optarg[0];
				if (temp == 'C') {
					running_mode = CLIENT_MODE;
				} else if (temp == 'S') {
					running_mode = SERVER_MODE;
				} else {
					return -1;
				}
				break;
			case 'O':
				data_fd = fopen(optarg, "w");
				break;
			default:
				break;
        }
    }
	if (running_mode == CLIENT_MODE) {
		int remain_arg = argc - optind;
		if (remain_arg != 1) {
			return -1;
		}
		strcpy(cli_server_ipstr, argv[optind]);
		server_addr = generate_sockaddr(cli_server_ipstr, serv_tcp_listen_port);

		message_header.msg_control = u.buf;
		message_header.msg_controllen = sizeof(u.buf);
		cmsghdr* cmsg = CMSG_FIRSTHDR(&message_header);
		cmsg->cmsg_level = SOL_SOCKET;
		cmsg->cmsg_type = SO_TIMESTAMPING;
		cmsg->cmsg_len = CMSG_LEN(sizeof(__u32));
		__u32 options = SOF_TIMESTAMPING_TX_SOFTWARE;
		*((__u32 *) CMSG_DATA(cmsg)) = options;
	}
    return 0;
}
void cli_init_conn() {
	cli_tcp_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (cli_tcp_fd == -1) {
        throw "cli init socket fail";
    }
    if (connect(cli_tcp_fd, (sockaddr*)&server_addr, sizeof(sockaddr_in))) {
        throw "cli init connect fail";
    }
	cli_udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (cli_udp_fd == -1) {
        throw "cli udp init sock fail";
    }
    if (set_timestamp_on(cli_udp_fd, CLIENT_MODE)) {
        throw "cli set udp timestamp fail";
    }
}
#define OWD_MEAS_BEGIN (0)
#define OWD_MEAS_BEGIN_ACK (1)
void cli_send_command(int command) {
	*(int*)tcp_buffer = htonl(command);
	ssize_t ret = send(cli_tcp_fd, tcp_buffer, sizeof(int), 0);
	if (ret == sizeof(int)) {
		return;
	} else {
		char temp[100];
		memset(temp, 0, sizeof(temp));
		sprintf(temp, "cli_send_command %zd", ret);
		throw temp;
	}
}
int cli_recv_command() {
	ssize_t ret = recv(cli_tcp_fd, tcp_buffer, sizeof(int), 0);
	if (ret == sizeof(int)) {
		int command = ntohl(*(int*)tcp_buffer);
		return command;
	} else {
		char temp[100];
		memset(temp, 0, sizeof(temp));
		sprintf(temp, "cli_recv_command %zd", ret);
		throw temp;
	}
}

void cli_udp_send(ssize_t size, bool enable_timestamping){
	iov.iov_len = size;
	if (enable_timestamping) {
		message_header.msg_control = u.buf;
		message_header.msg_controllen = sizeof(u.buf);
	} else {
		message_header.msg_control = NULL;
		message_header.msg_controllen = 0;
	}
    ssize_t ret = sendmsg(cli_udp_fd, &message_header, 0);
	if (ret != size) {
		char temp[100];
		memset(temp, 0, sizeof(temp));
		sprintf(temp, "cli_udp_send %zd", ret);
		throw temp;
	}
	fprintf(log_filename, "sent %zd\n", ret);
}
void cli_udp_gettimestamp(timespec *dst, int num, int epoll_wait_ms) {
	int epoll_ret;
	ssize_t ret;
	message_header.msg_control = control_buffer;
	message_header.msg_controllen = sizeof(control_buffer);
	for (int i = 0; i < num; i++) {
		epoll_ret = epoll_wait(epoll_fd, &ev, 1, epoll_wait_ms); // ms
		if (epoll_ret != 1) {
			fprintf(log_filename, "epoll ret %d\n", epoll_ret);
			throw "epoll ret != 1";
		}
		ret = recvmsg(cli_udp_fd, &message_header, 0);
		dst[i] = msg2timespec(&message_header);
	}
}
#define SERV_TIMESTAMP_REPLY (0)
#define SERV_TIMESTAMP_LOSS (1)
struct control_msg
{
	int msg_type;
	union msg_data
	{
		struct serv_timestamp_reply
		{
			int packet_index;
			timespec t;
		} reply;
		struct serv_timestamp_loss
		{
			int packet_index;
		} loss;
	} data;
};
int cli_recv_timestamp(timespec *dst, int i) {
	ssize_t ret = recv(cli_tcp_fd, tcp_buffer, sizeof(control_msg), 0);
	if (ret == sizeof(control_msg)) {
		control_msg cmsg_temp = *(control_msg*)tcp_buffer;
		if (cmsg_temp.msg_type == SERV_TIMESTAMP_REPLY) {
			*dst = cmsg_temp.data.reply.t;
		} else if (cmsg_temp.msg_type == SERV_TIMESTAMP_LOSS) {
			return cmsg_temp.data.loss.packet_index;
		}
		return -1;
	} else {
		return -2;
	}
}
timespec generate_timespec(long s, long ms, long us, long ns) {
	timespec ret;
	long ns_sum = s * 1e9 + ms * 1e6 + us * 1e3 + ns;
	long s_sum = ns_sum / 1e9;
	ns_sum = ns_sum % long(1e9);
	ret.tv_sec = s_sum;
	ret.tv_nsec = ns_sum;
	return ret;
}
void force_sleep(long n, const char *precision) {
	timespec req, remain;
	int ret;
	if (strcmp(precision, "s") == 0) {
		req = generate_timespec(n, 0, 0, 0);
	} else if (strcmp(precision, "ms") == 0) {
		req = generate_timespec(0, n, 0, 0);
	} else if (strcmp(precision, "us") == 0) {
		req = generate_timespec(0, 0, n, 0);
	} else if (strcmp(precision, "ns") == 0) {
		req = generate_timespec(0, 0, 0, n);
	}
	ret = clock_nanosleep(CLOCK_TAI, 0, &req, &remain);
	if (ret != 0) {
		fprintf(log_filename, "force_sleep %d\n", ret);
		throw "sleep not supported";
	}
}
#define OWD_MEAS_PARAM_NUM (100)
#define OWD_MEAS_PARAM_PACKET_SIZE (500)
void cli_owd_meas() {
	timespec sendtime[OWD_MEAS_PARAM_NUM], recvtime[OWD_MEAS_PARAM_NUM];
	ev.data.fd = cli_udp_fd; 
	ev.events = EPOLLERR;
	epoll_ctl(epoll_fd, EPOLL_CTL_ADD, cli_udp_fd, &ev);
	try {
		set_timeout(cli_tcp_fd, 1, 0);
		cli_send_command(OWD_MEAS_BEGIN);
		int reply = cli_recv_command(), ret;
		if (reply == OWD_MEAS_BEGIN_ACK) {
			for (int i = 0; i < OWD_MEAS_PARAM_NUM; i++) {
				*(int*)udp_buffer = htonl(i);
				cli_udp_send(OWD_MEAS_PARAM_PACKET_SIZE, true);
				cli_udp_gettimestamp(sendtime+i, 1, 10);
				if ((ret = cli_recv_timestamp(recvtime+i, i)) >= 0) {
					i = ret;
					fprintf(log_filename, "%s cli_recv_timestamp fail at %d\n", __func__, ret);
				} else if (ret == -2) {
					fprintf(log_filename, "%s cli_recv_timestamp fail\n", __func__);
				}
				if (i != OWD_MEAS_PARAM_NUM - 1) {
					force_sleep(1, "ms");
				}
			}
		}
		int buffer_len = timespecs2len(OWD_MEAS_PARAM_NUM);
		char buffer_temp[buffer_len] = {0};
		timespecs2str(buffer_temp, sendtime, OWD_MEAS_PARAM_NUM);
		fprintf(data_fd, "%s", buffer_temp);
		timespecs2str(buffer_temp, recvtime, OWD_MEAS_PARAM_NUM);
		fprintf(data_fd, "%s", buffer_temp);
	} catch (const char *msg) {
		fprintf(log_filename, "%s: %s\n", __func__, msg);
	}
}
void cli_train_length_meas() {

}
void cli_measure_gap_meas() {

}
void serv_init_conn() {
	serv_listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (serv_listen_fd == -1) {
        throw "server socket init fail";
    }
    if (set_reuse_addr(serv_listen_fd)) {
        throw "server set reuse address fail";
    }
    set_local_port(&local_addr, serv_tcp_listen_port);
    if (bind_local_port(serv_listen_fd, &local_addr)) {
        throw "server bind port fail";
    }
    if (listen(serv_listen_fd, 5)) {
        throw "server listen fail";
    }
	unsigned int client_len = sizeof(client_addr);
    serv_conn_fd = accept(serv_listen_fd, (sockaddr*)&client_addr, &client_len);
    if (serv_conn_fd == -1) {
        throw "server init accept fail";
    } else {
        print_sockaddr(log_filename, &client_addr);
    }
	serv_udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (serv_udp_fd == -1) {
        throw "server udp socket init fail";
    }
    if (set_reuse_addr(serv_udp_fd)) {
        throw "server set udp reuse address fail";
    }
    if (set_timestamp_on(serv_udp_fd, SERVER_MODE)) {
        throw "server timestamp on fail";
    }
    int buffer_size = get_buffer_size(serv_udp_fd);
    //fprintf(log_filename, "server udp buffer size is %d\n", buffer_size);
    if (bind_local_port(serv_udp_fd, &local_addr)) {
        throw "server bind udp port fail";
    }
}
int serv_recv_command() {
	ssize_t ret = recv(serv_conn_fd, tcp_buffer, sizeof(int), 0);
	if (ret == sizeof(int)) {
		int command = ntohl(*(int*)tcp_buffer);
		return command;
	} else {
		throw "serv_recv_command fail";
	}
}
void serv_send_command(int command) {
	*(int*)tcp_buffer = htonl(command);
	ssize_t ret = send(serv_conn_fd, tcp_buffer, sizeof(int), 0);
	if (ret != sizeof(int)) {
		throw "serv_send_command fail";
	}
}
void serv_udp_recv(ssize_t size) {
	iov.iov_len = size;
	ssize_t recv_size = recvmsg(serv_udp_fd, &message_header, 0);
	if (recv_size != size) {
		throw "serv_udp_recv fail";
	}
}
void serv_owd_meas() {
	message_header.msg_name = (void*)&client_addr;
	message_header.msg_control = control_buffer;
	message_header.msg_controllen = sizeof(control_buffer);
	int reply = serv_recv_command();
	if (reply == OWD_MEAS_BEGIN) {
		serv_send_command(OWD_MEAS_BEGIN_ACK);
		for (int i = 0; i < OWD_MEAS_PARAM_NUM; i++) {
			serv_udp_recv(OWD_MEAS_PARAM_PACKET_SIZE);
			int packet_index = ntohl(*(int*)udp_buffer);
			if (packet_index != i) {
				control_msg *cmsg_temp = (control_msg*)tcp_buffer;
				cmsg_temp->msg_type = SERV_TIMESTAMP_LOSS;
				cmsg_temp->data.loss.packet_index = i;
				send(serv_conn_fd, tcp_buffer, sizeof(control_msg), 0);
				i--;
				continue;
			} else {
				timespec temp = msg2timespec(&message_header);
				control_msg *cmsg_temp = (control_msg*)tcp_buffer;
				cmsg_temp->msg_type = SERV_TIMESTAMP_REPLY;
				cmsg_temp->data.reply.packet_index = i;
				cmsg_temp->data.reply.t = temp;
				send(serv_conn_fd, tcp_buffer, sizeof(control_msg), 0);
			}
		}
	}
	fprintf(log_filename, "serv_owd_meas success!");
}
void serv_train_length_meas() {

}
void serv_measure_gap_meas() {

}
void client_main() {
	try
	{
		cli_init_conn();
		fprintf(log_filename, "cli init\n");
		cli_owd_meas();
		fprintf(log_filename, "cli owd\n");
		cli_train_length_meas();
		cli_measure_gap_meas();
	}
	catch(const char *msg)
	{
		fprintf(log_filename, "Error in %s: %s\n", __func__, msg);
	}
}
void server_main() {
	try
	{
		serv_init_conn();
		fprintf(log_filename, "serv init\n");
		serv_owd_meas();
		fprintf(log_filename, "serv owd\n");
		serv_train_length_meas();
		serv_measure_gap_meas();
	}
	catch(const char *msg)
	{
		fprintf(log_filename, "Error in %s: %s\n", __func__, msg);
	}
}
void client_close() {
	if (data_fd != NULL) {
		fclose(data_fd);
	}
	close(cli_tcp_fd);
	close(cli_udp_fd);
}
void server_close() {
	close(serv_listen_fd);
	close(serv_conn_fd);
	close(serv_udp_fd);
}
int main(int argc, char *argv[]) {
	timespec begin_time, end_time;
	double time_cost, begin_t, end_t;
	clock_gettime(CLOCK_TAI, &begin_time);
	begin_t = timespec2double(begin_time);
	/* start of program */
	if (parse_args(argc, argv)) {
		help();
		return -1;
	}
	if (running_mode==CLIENT_MODE) {
		client_main();
		client_close();
	} else if (running_mode==SERVER_MODE) {
		server_main();
		server_close();
	}
	/*   end of program */
	clock_gettime(CLOCK_TAI, &end_time);
	end_t = timespec2double(end_time);
	time_cost = end_t - begin_t;
	fprintf(log_filename, "program use %.2f s.\n", time_cost);
	if (log_filename != NULL) {
		fclose(log_filename);
	}
}