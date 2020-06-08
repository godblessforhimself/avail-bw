#!/bin/bash
# author: tony
# exp5：路由带宽=1000Mbps，探测带宽=1000Mbps，背景带宽=10000Mbps，UDP大小=9000B，发包粒度=100us。
# 训练数据 0-900Mbps 901*100*(0.72s)=25h
# 测试数据 0.0-900.0Mbps 9001*3*0.72s=5h
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
RECORD_FILENAME="experiment_record.txt"

EXPERIMENT_COUNT=5
CONTINUOUS_COUNT=1000
PAIR_COUNT_TEST=3
PAIR_COUNT=30
TRAIN_TRAFFIC_RANGE=$(seq 0 1 900)
TEST_TRAFFIC_RANGE=$(seq 0 0.1 900)

set_src_link(){
    sudo tc qdisc del dev enp61s0f1 root; sudo tc qdisc add dev enp61s0f1 root tbf rate 1000mbit burst 10kb limit 10000kb
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
    "pkill iperf3; nohup iperf3 -c ${IP_DST} -ub ${TRAFFIC}M -l 9000 -t ${IPERF3_DURATION} --pacing-timer 100 1>>${IPERF3_CLIENT_LOG} 2>&1 &"
    printf "... finished.\n"
}
start_probing(){
    printf "Start probing ..."
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} \
    "nohup sudo ${PATH_DST}/build/avail-server -p -20 -M S -C $1 -L $2 -S 9000 1>${AVAIL_SERVER_LOG} 2>&1 &"
    mkdir -p ${PATH_SRC}/data
    sudo ${PATH_SRC}/build/avail-client -p -20 -M C -C $1 -L $2 -S 9000 -R 100 -B 1000 -O $3 ${IP_DST}
    printf "... finished.\n"
}
clear_all(){
    printf "Start clearing ..."
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} "pkill iperf3; sudo pkill avail-server"
    ssh -l ${USERNAME_TRAFFIC} -o StrictHostKeyChecking=no ${IP_TRAFFIC} "pkill iperf3"
    sudo pkill avail-client
    printf "... finished.\n"
}
get_training_data(){
    for CROSS_TRAFFIC_RATE in ${TRAIN_TRAFFIC_RANGE}; do
        clear_all
        TS_FILENAME="/home/liqing/avail-bw/data/link1000load${CROSS_TRAFFIC_RATE}exp${EXPERIMENT_COUNT}.txt"
        printf "Training data: Load is %3.1f\n" ${CROSS_TRAFFIC_RATE}
        set_cross_traffic ${CROSS_TRAFFIC_RATE}
        sleep 0.1s
        start_probing ${CONTINUOUS_COUNT} ${PAIR_COUNT} ${TS_FILENAME}
    done
    clear_all
}
get_test_data(){
    for CROSS_TRAFFIC_RATE in ${TEST_TRAFFIC_RANGE}; do
        clear_all
        TS_FILENAME="/home/liqing/avail-bw/data/link1000load${CROSS_TRAFFIC_RATE}exp${EXPERIMENT_COUNT}test.txt"
        printf "Testing data: Load is %3.1f\n" ${CROSS_TRAFFIC_RATE}
        set_cross_traffic ${CROSS_TRAFFIC_RATE}
        sleep 0.01s
        start_probing ${CONTINUOUS_COUNT} ${PAIR_COUNT_TEST} ${TS_FILENAME}
    done
    clear_all
}
init_experiment_record(){
    START_TIME=$(date)
}
update_experiment_record(){
    END_TIME=$(date)
    printf "Experiment %3d: ${START_TIME} -> ${END_TIME}, continuous count ${CONTINUOUS_COUNT}, pair count ${PAIR_COUNT}\n" ${EXPERIMENT_COUNT} >> ${RECORD_FILENAME}
}
main(){
    init_experiment_record
    set_src_link
    set_router_link
    get_training_data
    get_test_data
    reset_link
    update_experiment_record
}
main $@