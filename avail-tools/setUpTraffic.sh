SetUpIperf3(){
    #Iperf3以特定速率发包
    #服务器
    if [ $# -eq 0 ]; then
        return 0;
    fi
    COMP=$(echo "${1}==0"|bc)
    if [ ${COMP} -eq 1 ]; then
        printf "SetUpTraffic 0\n"
        return 0
    fi
    ssh zhufengtian@192.168.67.5 "pkill iperf3;nohup iperf3 -sfm -V 1>~/jintao_test/iperf.log 2>&1 &" >/dev/null
    ssh haha@192.168.2.4 "pkill iperf3; nohup iperf3 -c 192.168.5.1 -ub ${1}M -l 1472 -t 36000 --pacing-timer 0 1>~/jintao_test/iperf.log 2>&1 &" >/dev/null
    printf "SetUpTraffic ${1}Mbps\n"
}

SetUpIperf3 $@