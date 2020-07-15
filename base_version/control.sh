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
show_tc(){
    printf "src bandwidth:\n"
    sudo tc qdisc show dev enp61s0f1;
    printf "router bandwidth:\n"
    ssh -l ${USERNAME_ROUTER} -o StrictHostKeyChecking=no ${IP_ROUTER} \
    "sudo tc qdisc show dev vlan1"
}
show_socket_buffer(){
    printf "src buffer:\n"
    cat /proc/sys/net/core/rmem_default
    printf "router buffer:\n"
    ssh -l ${USERNAME_ROUTER} -o StrictHostKeyChecking=no ${IP_ROUTER} \
    "cat /proc/sys/net/core/rmem_default"
}
show_MTU(){
    printf "src MTU:\n"
    cat /sys/class/net/enp61s0f1/mtu
}
show_tc
show_socket_buffer
show_MTU