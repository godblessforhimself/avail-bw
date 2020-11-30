Clean(){
    ssh haha@192.168.67.4 "pkill iperf3"
    ssh zhufengtian@192.168.67.5 "pkill iperf3;"
    printf "Clean finish\n"
}

Clean $@