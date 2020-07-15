#set src link
#set router link
main(){
sudo tc qdisc del dev enp61s0f1 root; sudo tc qdisc add dev enp61s0f1 root tbf rate ${1}mbit burst 10kb limit 10000kb
ssh -l liqing -o StrictHostKeyChecking=no 192.168.0.22 \
    "sudo tc qdisc del dev vlan1 root; sudo tc qdisc add dev vlan1 root tbf rate ${2}mbit burst 10kb limit 10000kb"
}
main $@
