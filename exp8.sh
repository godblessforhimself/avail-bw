#!/bin/bash
# author: tony
# exp8：包大小对准确率的影响1000Mbps
# 1500,9000,1500 6
# continuous count 由探测包大小决定
# 训练 背景流量0-900 30轮
# 测试 背景流量0-900 0.3 5*3

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
IPERF3_DURATION=1500
IPERF3_SERVER_LOG="~/iperfserver.log"
IPERF3_CLIENT_LOG="~/iperfclient.log"
AVAIL_SERVER_LOG="${PATH_DST}/build/server.log"
RECORD_FILENAME="experiment_record.txt"

EXPERIMENT_COUNT=8
LOAD_PACKET_SIZE=1472
PAIR_COUNT=30
PAIR_COUNT_TEST=3
TEST_REPEAT_COUNT=5
TRAIN_TRAFFIC_RANGE=$(seq 0 1 900)
TEST_TRAFFIC_RANGE=$(seq 0 1 900) #在不同时间测量，反映模型泛化性能；并不需要粒度更细

DATA_DIR="/home/liqing/avail-bw/data/exp8"

set_src_link(){
    BURST_SIZE=$(echo $1/1000|python3 -c "import math;print('{}kb'.format(math.ceil(eval(input()))+1))")
    sudo tc qdisc del dev enp61s0f1 root; sudo tc qdisc add dev enp61s0f1 root tbf rate 1000mbit burst ${BURST_SIZE} limit 10000kb
}
set_router_link(){
    ssh -l ${USERNAME_ROUTER} -o StrictHostKeyChecking=no ${IP_ROUTER} \
    "sudo tc qdisc del dev vlan1 root; sudo tc qdisc add dev vlan1 root tbf rate 1000mbit burst 10kb limit 10000kb"
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
    "pkill iperf3; nohup iperf3 -c ${IP_DST} -ub ${TRAFFIC}M -l ${LOAD_PACKET_SIZE} -t ${IPERF3_DURATION} --pacing-timer 100 1>>${IPERF3_CLIENT_LOG} 2>&1 &"
    printf "... finished.\n"
}
start_probing(){
    printf "Start probing ..."
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} \
    "nohup sudo ${PATH_DST}/build/avail-server -p -20 -M S -C $1 -L $2 -S $3 1>${AVAIL_SERVER_LOG} 2>&1 &"
    mkdir -p ${PATH_SRC}/data
    sudo ${PATH_SRC}/build/avail-client -p -20 -M C -C $1 -L $2 -S $3 -R 100 -B 1000 -O $4 ${IP_DST}
    printf "... finished.\n"
}
clear_probing(){
    printf "Clearing probing ..."
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} "sudo pkill avail-server"
    sudo pkill avail-client
    printf "... finished.\n"
}
clear_all(){
    printf "Start clearing ..."
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} "pkill iperf3; sudo pkill avail-server"
    ssh -l ${USERNAME_TRAFFIC} -o StrictHostKeyChecking=no ${IP_TRAFFIC} "pkill iperf3"
    sudo pkill avail-client
    printf "... finished.\n"
}
get_data(){
    for PROBING_PACKET_SIZE in $(seq 1500 1500 9000); do
        set_src_link ${PROBING_PACKET_SIZE}
        CONTINUOUS_COUNT=$(echo 1500*1000/${PROBING_PACKET_SIZE} | python3 -c "import math;print(math.ceil(eval(input())))")
        #train data
        for CROSS_TRAFFIC_RATE in ${TRAIN_TRAFFIC_RANGE}; do
            clear_all
            TS_FILENAME="${DATA_DIR}/link1000load${CROSS_TRAFFIC_RATE}packetsize${PROBING_PACKET_SIZE}exp${EXPERIMENT_COUNT}.txt"
            printf "Training: Load is %3.1f, Packet size is %d\n" ${CROSS_TRAFFIC_RATE} ${PROBING_PACKET_SIZE}
            set_cross_traffic ${CROSS_TRAFFIC_RATE}
            sleep 0.1s
            start_probing ${CONTINUOUS_COUNT} ${PAIR_COUNT} ${PROBING_PACKET_SIZE} ${TS_FILENAME}
        done
        clear_all    
        #test data
        for CROSS_TRAFFIC_RATE in ${TEST_TRAFFIC_RANGE}; do
            printf "Testing: Load is %3.1f, Packet size is %d\n" ${CROSS_TRAFFIC_RATE} ${PROBING_PACKET_SIZE}
            set_cross_traffic ${CROSS_TRAFFIC_RATE}
            for TEST_I in $(seq 1 $TEST_REPEAT_COUNT); do
                clear_probing
                TS_FILENAME="${DATA_DIR}/link1000load${CROSS_TRAFFIC_RATE}packetsize${PROBING_PACKET_SIZE}exp${EXPERIMENT_COUNT}test${TEST_I}.txt"
                sleep 0.01s
                start_probing ${CONTINUOUS_COUNT} ${PAIR_COUNT_TEST} ${PROBING_PACKET_SIZE} ${TS_FILENAME}
            done
            clear_all
        done
    done
}
init_experiment_record(){
    START_TIME=$(date)
}
update_experiment_record(){
    END_TIME=$(date)
    printf "Experiment %3d: ${START_TIME} -> ${END_TIME}, train ${PAIR_COUNT}, test ${PAIR_COUNT_TEST}, test repeat ${TEST_REPEAT_COUNT}\n" ${EXPERIMENT_COUNT} >> ${RECORD_FILENAME}
}
main(){
    mkdir -p ${DATA_DIR}
    init_experiment_record
    set_router_link
    get_data
    reset_link
    update_experiment_record
}
main