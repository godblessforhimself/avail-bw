Clean(){
    ssh haha@192.168.2.4 "pkill iperf3" >/dev/null
    ssh zhufengtian@192.168.67.5 "pkill iperf3;" >/dev/null
    printf "Clean finish\n"
}

Clean $@