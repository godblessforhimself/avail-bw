#!/bin/bash
# author: tony
# exp4：路由器到接收端的带宽=100Mbps，探测源的带宽=100Mbps，背景流量带宽=10000Mbps，UDP大小=9000B，背景流量速率0-90Mbps，发包粒度=100us。
# SRC是探测源，DST是接收端，TRAFFIC是流量产生源
# 100Mbps，带宽控制，iperf3粒度，网卡产生时间戳
# 训练测试数据没有分开获取
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
    printf "Setting up cross traffic ..."
    if [ ${TRAFFIC} -eq 0 ]; then
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
    "pkill avail-server; nohup sudo ${PATH_DST}/build/avail-server -p -20 -M S -C 100 -L 100 -S 9000 1>${AVAIL_SERVER_LOG} 2>&1 &"
    pkill avail-client;
    mkdir -p ${PATH_SRC}/data
    sudo ${PATH_SRC}/build/avail-client -p -20 -M C -C ${CONTINOUS_COUNT} -L ${PAIR_COUNT} -S 9000 -O ${TS_FILENAME} ${IP_DST}
    printf "... finished.\n"
}
clear_all(){
    printf "Start clearing ..."
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} "pkill iperf3; pkill avail-server"
    ssh -l ${USERNAME_TRAFFIC} -o StrictHostKeyChecking=no ${IP_TRAFFIC} "pkill iperf3"
    pkill avail-client
    printf "... finished.\n"
}
run_epoch(){
    #run_epoch CROSS_TRAFFIC CONTINUOUS_COUNT PAIR_COUNT EXPERIMENT_COUNT
    CROSS_TRAFFIC_=$1
    EXPERIMENT_COUNT_=$4
    TS_FILENAME="/home/liqing/avail-bw/data/link100load${CROSS_TRAFFIC_}exp${EXPERIMENT_COUNT_}.txt"
    printf "Capacity is 100, Load is %3d\n" $1
    clear_all
    set_cross_traffic $1
    start_probing $2 $3 ${TS_FILENAME}
    clear_all
}

RECORD_FILENAME="experiment_record.txt"
init_experiment_record(){
    START_TIME=$(date)
    if [ -e ${RECORD_FILENAME} ]; then
        OLD_VALUE=$(tail -n 1 ${RECORD_FILENAME} | sed -n -e 's/^Experiment[ ]\+\([0-9]\+\):.*/\1/p')
        EXPERIMENT_COUNT=$(echo "$OLD_VALUE+1"|bc)
        printf "Experiment count: ${EXPERIMENT_COUNT}\n"
    else
        touch ${RECORD_FILENAME}
        EXPERIMENT_COUNT="1"
    fi
}
CONTINUOUS_COUNT_=100
PAIR_COUNT_=100
update_experiment_record(){
    END_TIME=$(date)
    printf "Experiment %3d: ${START_TIME} -> ${END_TIME}, continuous count ${CONTINUOUS_COUNT_}, pair count ${PAIR_COUNT_}\n" ${EXPERIMENT_COUNT} >> ${RECORD_FILENAME}
}
main(){
    init_experiment_record
    set_src_link
    set_router_link
    CROSS_TRAFFIC_RANGE=$(seq 0 1 90)
    for CROSS_TRAFFIC_ in ${CROSS_TRAFFIC_RANGE}; do
        run_epoch ${CROSS_TRAFFIC_} ${CONTINUOUS_COUNT_} ${PAIR_COUNT_} ${EXPERIMENT_COUNT}
        sleep 3s
    done
    reset_link
    update_experiment_record
}
main $@