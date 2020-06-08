#!/bin/bash
# author: tony
# exp4：验证数据。每组3*100包，文件名为exp4testonload{}.txt
IP_DST="192.168.1.21"
IP_SRC="192.168.0.19"
IP_TRAFFIC="192.168.0.20"
IP_ROUTER="192.168.0.22"
USERNAME_DST="liqing"
USERNAME_SRC="liqing"
USERNAME_TRAFFIC="liqing"
USERNAME_ROUTER="liqing"
PATH_DST="/home/liqing/avail-bw"
PATH_SRC="/home/liqing/avail-bw"
IPERF3_DURATION=300
IPERF3_SERVER_LOG="~/iperfserver.log"
IPERF3_CLIENT_LOG="~/iperfclient.log"
AVAIL_SERVER_LOG="${PATH_DST}/build/server.log"
set_src_link(){
    sudo tc qdisc del dev enp61s0f1 root; sudo tc qdisc add dev enp61s0f1 root tbf rate 100mbit burst 10kb limit 10000kb
}
set_router_link(){
    ssh -l ${USERNAME_ROUTER} -o StrictHostKeyChecking=no ${IP_ROUTER} \
    "sudo tc qdisc del dev vlan1 root; sudo tc qdisc add dev vlan1 root tbf rate 100mbit burst 10kb limit 10000kb"
}
reset_link(){
    sudo tc qdisc del dev enp61s0f1 root
    ssh -l ${USERNAME_ROUTER} -o StrictHostKeyChecking=no ${IP_ROUTER} \
    "sudo tc qdisc del dev vlan1 root"
}
set_cross_traffic(){
    TRAFFIC=$1
    printf "Setting up cross traffic ${TRAFFIC}..."
    COMP=$(echo "${TRAFFIC}==0"|bc)
    if [ ${COMP} -eq 1 ]; then
        printf "... finished.\n"
        return 0
    fi
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} \
    "pkill iperf3; nohup iperf3 -s 1>>${IPERF3_SERVER_LOG} 2>&1 &"
    ssh -l ${USERNAME_TRAFFIC} -o StrictHostKeyChecking=no ${IP_TRAFFIC} \
    "pkill iperf3; nohup iperf3 -c ${IP_DST} -ub ${TRAFFIC}M -l 9000 -t ${IPERF3_DURATION} --pacing-timer 100 1>>${IPERF3_CLIENT_LOG} 2>&1 &"
    printf "... finished.\n"
}
start_probing(){
    printf "Start probing ..."
    CONTINOUS_COUNT=$1
    PAIR_COUNT=$2
    TS_FILENAME=$3
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} \
    "nohup sudo ${PATH_DST}/build/avail-server -p -20 -M S -C 100 -L 100 -S 9000 1>${AVAIL_SERVER_LOG} 2>&1 &"
    mkdir -p ${PATH_SRC}/data
    sudo ${PATH_SRC}/build/avail-client -p -20 -M C -C ${CONTINOUS_COUNT} -L ${PAIR_COUNT} -S 9000 -O ${TS_FILENAME} ${IP_DST}
    printf "... finished.\n"
}
clear_all(){
    printf "Start clearing ..."
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} "pkill iperf3; sudo pkill avail-server"
    ssh -l ${USERNAME_TRAFFIC} -o StrictHostKeyChecking=no ${IP_TRAFFIC} "pkill iperf3"
    sudo pkill avail-client
    printf "... finished.\n"
}
run_epoch(){
    #run_epoch CROSS_TRAFFIC CONTINUOUS_COUNT PAIR_COUNT 
    CROSS_TRAFFIC_=$1
    TS_FILENAME="/home/liqing/avail-bw/data/exp4testonload${CROSS_TRAFFIC_}.txt"
    printf "Load is %2.1f\n" $1
    clear_all
    set_cross_traffic $1
    start_probing $2 $3 ${TS_FILENAME}
    clear_all
}

CONTINUOUS_COUNT_=100
PAIR_COUNT_=3
main(){
    set_src_link
    set_router_link
    CROSS_TRAFFIC_RANGE=$(seq 0 0.1 90)
    for CROSS_TRAFFIC_ in ${CROSS_TRAFFIC_RANGE}; do
        run_epoch ${CROSS_TRAFFIC_} ${CONTINUOUS_COUNT_} ${PAIR_COUNT_}
        sleep 1s
    done
    reset_link
}
main $@