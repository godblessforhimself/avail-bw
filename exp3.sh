#!/bin/bash
# author: tony
# SRC是探测源，DST是接收端，TRAFFIC是流量产生源
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
set_capacity(){
    CAPACITY=$1
    BUFFERSIZE=`expr ${CAPACITY} \* 50`
    printf "Setting up capacity ..."
    ssh -l ${USERNAME_ROUTER} -o StrictHostKeyChecking=no ${IP_ROUTER} \
    "sudo tc qdisc del dev vlan1 root; sudo tc qdisc add dev vlan1 root tbf rate ${CAPACITY}mbit burst ${BUFFERSIZE}kbit latency 1ms"
    if [ $? -ne 0 ]; then
        printf "Set capacity failed\n"
        exit
    fi
    printf "... finished.\n"
}
set_cross_traffic(){
    TRAFFIC=$1
    printf "Setting up cross traffic ..."
    if [ ${TRAFFIC} -eq 0 ]; then
        printf "... finished.\n"
        return 0
    fi
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} \
    "pkill iperf3; nohup iperf3 -s 1>${IPERF3_SERVER_LOG} 2>&1 &"
    ssh -l ${USERNAME_TRAFFIC} -o StrictHostKeyChecking=no ${IP_TRAFFIC} \
    "pkill iperf3; nohup iperf3 -c ${IP_DST} -u -b ${TRAFFIC}M -w 5M -l 1472 -t ${IPERF3_DURATION} 1>${IPERF3_CLIENT_LOG} 2>&1 &"
    printf "... finished.\n"
}
start_probing(){
    printf "Start probing ..."
    CONTINOUS_COUNT=$1
    PAIR_COUNT=$2
    PROBING_RATE=$3
    TS_FILENAME=$4
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} \
    "pkill avail-server; nohup ${PATH_DST}/build/avail-server 1>${AVAIL_SERVER_LOG} 2>&1 &"
    pkill avail-client;
    mkdir -p ${PATH_SRC}/data
    ${PATH_SRC}/build/avail-client -C ${CONTINOUS_COUNT} -L ${PAIR_COUNT} -R ${PROBING_RATE} -o ${PATH_SRC}/data/${TS_FILENAME} ${IP_DST}
    printf "... finished.\n"
}
clear_all(){
    printf "Start clearing ..."
    ssh -l ${USERNAME_DST} -o StrictHostKeyChecking=no ${IP_DST} "pkill iperf3; pkill avail-server"
    ssh -l ${USERNAME_TRAFFIC} -o StrictHostKeyChecking=no ${IP_TRAFFIC} "pkill iperf3"
    ssh -l ${USERNAME_ROUTER} -o StrictHostKeyChecking=no ${IP_ROUTER} \
    "sudo tc qdisc del dev vlan1 root"
    pkill avail-client
    printf "... finished.\n"
}
run_epoch(){
    #run_epoch CAPACITY CROSS_TRAFFIC CONTINIOUS_COUNT PAIR_COUNT PROBING_RATE EXPERIMENT_COUNT
    CAPACITY_=$1
    CROSS_TRAFFIC_=$2
    EXPERIMENT_COUNT=$6
    TS_FILENAME="link${CAPACITY_}load${CROSS_TRAFFIC_}exp${EXPERIMENT_COUNT}.txt"
    printf "Capacity is %5d, Load is %5d\n" $1 $2
    clear_all
    set_capacity $1
    set_cross_traffic $2
    start_probing $3 $4 $5 ${TS_FILENAME}
    clear_all
}
get_traffic_range(){
    START=$(echo 0.1*$1|bc)
    END=$(echo 0.9*$1|bc)
    STEP=${START}
    seq -f "%.0f" ${START} ${STEP} ${END}
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
CONTINIOUS_COUNT_=10
PAIR_COUNT_=1000
PROBING_RATE_=10
update_experiment_record(){
    END_TIME=$(date)
    printf "Experiment %3d: ${START_TIME} -> ${END_TIME}, Continious count ${CONTINIOUS_COUNT_}, Pair count ${PAIR_COUNT_}, Probing rate ${PROBING_RATE_}\n" ${EXPERIMENT_COUNT} >> ${RECORD_FILENAME}
}
main(){
    init_experiment_record
    CAPACITY_RANGE=$(seq 100 100 900)
    for CAPACITY_ in $CAPACITY_RANGE; do
        CROSS_TRAFFIC_RANGE=$(get_traffic_range ${CAPACITY_})
        for CROSS_TRAFFIC_ in $CROSS_TRAFFIC_RANGE; do
            run_epoch ${CAPACITY_} ${CROSS_TRAFFIC_} ${CONTINIOUS_COUNT_} ${PAIR_COUNT_} ${PROBING_RATE_} ${EXPERIMENT_COUNT}
            sleep 3s
        done
    done
    update_experiment_record
}
main $@