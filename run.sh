#!/bin/bash
# author: 
# params: capacity, cross-traffic, gap-value, probing-rate
usage(){
    printf "%s\n" "Avail-bw estimator:" "    Usage:"
    printf "\t%s\n" \
    "-c [capacity]          set capacity of tight link" \
    "-b [cross-traffic]     set cross-traffic that passes tight link" \
    "-r [probing-rate]      set probing-rate" \
    "-d                     clear previous jobs." \
    "-M                     clean an make." \
    "-log [file]            set log filename" \
    "example:" \
    "./run.sh -c 50 -b 25 -r 10 or ./run.sh --capacity 100 --traffic 50 --rate 10 --filename c100t50r10.txt" \
    "./run.sh -d or ./run.sh --stop" \
    "./run.sh -M or ./run.sh --make --log log.txt"
    exit
}
SHORT=c:b:r:l:dMf:
LONG=capacity:,traffic:,rate:,stop,make,log:,filename:
FILENAME="timestamp.txt"
print_args(){
    if [ -z "${CAPACITY}" ]; then
        printf "Capacity not set\n"
        return 1
    elif [ -z ${TRAFFIC} ]; then
        printf "Traffic not set\n"
        return 1
    elif [ -z ${RATE} ]; then
        printf "Probing rate not set\n"
        return 1
    else
        return 0
    fi
}
parse_args(){
    OPTS=$(getopt --options $SHORT -l $LONG --name "$0" -- "$@")
    if [ $? != 0 ]
    then 
        printf "Failed to parse args, exit.\n"
        usage
    fi
    eval set -- "$OPTS" # args=opts
    while true
    do
    case "$1" in
        -f | --filename )
            FILENAME="$2"
            shift 2
            ;;
        -l | --log )
            DETAILED_LOG="$2"
            shift 2
            ;;
        -c | --capacity )
            CAPACITY="$2"
            if [ ${CAPACITY} -lt 1 ]; then
                printf "Capacity can't be less than 1Mbps\n"
                usage
            elif [ ${CAPACITY} -gt 100 ]; then
                printf "Capacity can't be more than 100Mbps\n"
                usage
            else
                :
            fi
            shift 2
            ;;
        -b | --traffic )
            TRAFFIC="$2"
            shift 2
            ;;
        -r | --rate )
            RATE="$2"
            shift 2
            ;;
        -d | --stop )
            clear_all
            exit
            ;;
        -M | --make )
            MAKE_MODE=1
            shift 1
            ;;
        -- )
            # parse finish
            break
            ;;
        * )
            printf "Unknown args\n"
            usage
            ;;
    esac
    done
    if [ -z ${MAKE_MODE} ]; then
        :
    else
        quick_make
        exit
    fi
    print_args
    if [[ $? -eq 1 ]]; then
        usage
    fi
    if [ ${TRAFFIC} -lt 1 ]; then
        printf "Cross traffic can't be less than 1Mbps\n"
        usage
    elif [ ${TRAFFIC} -gt ${CAPACITY} ]; then
        printf "Cross traffic can't be more than capacity(${CAPACITY}Mbps)\n"
        usage
    else
        :
    fi
    if [ ${RATE} -le 0 ]; then
        printf "Rate should be positive\n"
        usage
    elif [ ${RATE} -gt ${CAPACITY} ]; then
        printf "Rate too large\n"
        usage
    else
        :
    fi
}
get_buffersize(){
    BUFFERSIZE=`expr ${CAPACITY} \* 50`
    printf "Buffersize is %skb\n" ${BUFFERSIZE}
}
IP="192.168.0.24"
USERNAME="root"
set_capacity(){
    get_buffersize
    printf "Setting up capacity ..."
    ssh -l ${USERNAME} -o StrictHostKeyChecking=no ${IP} \
    "tc qdisc del dev enp2s0 handle ffff: ingress; tc qdisc add dev enp2s0 handle ffff: ingress; tc filter add dev enp2s0 parent ffff: handle 800::800 u32 match u32 0 0 action police rate ${CAPACITY}mbit burst ${BUFFERSIZE}k mtu 1500 conform-exceed drop; tc filter show dev enp2s0 parent ffff: handle 800::800;"
    printf "... finished.\n"
    if [ $? -ne 0 ]; then
        printf "Set capacity failed\n"
        exit
    fi
}
IP2="192.168.0.16"
USERNAME2="tonyold"
set_cross_traffic(){
    printf "Setting up cross traffic ..."
    if [ ${TRAFFIC} -eq 0 ]; then
        return 0
    fi
    ssh -l ${USERNAME} -o StrictHostKeyChecking=no ${IP} \
    "pkill iperf3; nohup iperf3 -s > ~/iperfserver.log 2>/dev/null &"
    ssh -l ${USERNAME2} -o StrictHostKeyChecking=no ${IP2} \
    "pkill iperf3; nohup iperf3 -c ${IP} -u -b ${TRAFFIC}M -t 300 > ~/iperfclient.log 2>/dev/null &"
    printf "... finished.\n"
    if [ $? -ne 0 ]; then
        printf "Set cross traffic failed\n"
        exit
    fi
}
SERVER_PATH="~/avail-tools/simple-testbed/build"
CLIENT_PATH="/home/tony/Downloads/avail-tools/simple-testbed/build"
start_probing(){
    printf "Start probing ..."
    ssh -l ${USERNAME} -o StrictHostKeyChecking=no ${IP} \
    "pkill avail-server; nohup ${SERVER_PATH}/avail-server > ${SERVER_PATH}log.txt 2>&1 &"
    pkill avail-client;
    #nohup ${CLIENT_PATH}/avail-client -c ${CAPACITY} -r ${RATE} -o ${CLIENT_PATH}/timestamp.txt ${IP} > ${CLIENT_PATH}/log.txt 2>&1 &
    ${CLIENT_PATH}/avail-client -c ${CAPACITY} -r ${RATE} -o ${CLIENT_PATH}/${FILENAME} ${IP}
    printf "... finished.\n"
    if [ $? -ne 0 ]; then
        printf "Start probing failed\n"
        exit
    fi
}
clear_all(){
    printf "Start clearing ..."
    ssh -l ${USERNAME} -o StrictHostKeyChecking=no ${IP} "pkill iperf3; pkill avail-server"
    ssh -l ${USERNAME2} -o StrictHostKeyChecking=no ${IP2} "pkill iperf3"
    pkill avail-client
    printf "... finished.\n"
    if [ $? -ne 0 ]; then
        printf "Clear failed\n"
        exit
    fi
}
SERVER_PROJ="/root/avail-tools/simple-testbed"
CLIENT_PROJ="/home/tony/Downloads/avail-tools/simple-testbed"
quick_make(){
    printf "Quick clean and make ..."
    cd $CLIENT_PATH && make clean && rm -f CMakeCache.txt && cmake ../ 1>/dev/null && make 1>/dev/null
    if [ $? -ne 0 ]; then
        printf "Client remake failed.\n"
        exit
    fi
    scp -r $CLIENT_PROJ/* ${USERNAME}@${IP}:${SERVER_PROJ} 1>/dev/null
    if [ $? -ne 0 ]; then
        printf "Source code transmission failed.\n"
        exit
    fi
    ssh -l ${USERNAME} -o StrictHostKeyChecking=no ${IP} "cd ${SERVER_PROJ}/build && make clean && rm -f CMakeCache.txt && cmake ../ && make" 1>/dev/null 2>/dev/null
    if [ $? -ne 0 ]; then
        printf "Server remake failed.\n"
        exit
    fi
    printf "... finished.\n"
}
main(){
    parse_args $@
    #set_capacity
    set_cross_traffic
    start_probing
    clear_all
}
main $@