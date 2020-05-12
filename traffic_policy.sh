#!/bin/bash
IP_DST="192.168.0.21"
IP_SRC="192.168.0.19"
IP_TRAFFIC="192.168.0.20" 
IP_ROUTER="192.168.0.22"
IFACE_SRC="enp61s0f1"
IFACE_TRAFFIC="enp61s0f1"
# sudo 权限问题，可以在目标机上配置
set_policy(){
    # Src 
    # sudo route add -host 192.168.0.21 gw 192.168.0.22 dev enp61s0f1
    sudo route add -host ${IP_DST} gw ${IP_ROUTER} dev ${IFACE_SRC}
    # Traffic
    # sudo route add -host 192.168.0.21 gw 192.168.0.22 dev enp61s0f1
    ssh -l ${USERNAME_TRAFFIC} -o StrictHostKeyChecking=no ${IP_TRAFFIC} \
    "sudo route add -host ${IP_DST} gw ${IP_ROUTER} dev ${IFACE_TRAFFIC}"
    # Router
    # sudo sysctl net.ipv4.ip_forward=1
    ssh -l ${USERNAME_ROUTER} -o StrictHostKeyChecking=no ${IP_ROUTER} \
    "sudo sysctl net.ipv4.ip_forward=1"
}
SRC     192.168.0.19/24
TRAFFIC 192.168.0.20/24
ROUTER  192.168.0.22/24 192.168.1.22/24
DST     192.168.1.21/24

SRC的route
sudo route add -host 192.168.0.22 gw 192.168.0.19 dev enp61s0f1
sudo route add -net 192.168.1.0/24 gw 192.168.0.22 dev enp61s0f1
sudo route add -host 192.168.0.20 gw 192.168.0.19 dev enp61s0f1

TRAFFIC的route
sudo route add -host 192.168.0.22 gw 192.168.0.20 dev enp61s0f1
sudo route add -net 192.168.1.0/24 gw 192.168.0.22 dev enp61s0f1
sudo route add -host 192.168.0.19 gw 192.168.0.20 dev enp61s0f1

ROUTER的route
ip link add vlan0 link enp61s0f1 type macvlan mode private
sudo ifconfig vlan0 192.168.0.22/24
ip link add vlan1 link enp61s0f1 type macvlan mode private
sudo ifconfig vlan1 192.168.1.22/24
sudo route add -net 192.168.0.0/24 gw 192.168.0.22 dev vlan0
sudo route add -net 192.168.1.0/24 gw 192.168.1.22 dev vlan1

DST的route
sudo route add -host 192.168.1.22 gw 192.168.1.21 dev enp61s0f1
sudo route add -net 192.168.0.0/16 gw 192.168.1.22 dev enp61s0f1

ip link set vlan0 promisc on
sudo tcpdump -i vlan0 -nN 'src host 192.168.0.19 and dst host 192.168.1.21'
sudo tcpdump -i vlan0 -nN 'src host 192.168.0.20 and dst host 192.168.1.21'

# 如何设置Router->Dst的链路带宽
sudo tc qdisc del dev vlan1 root;
sudo tc qdisc add dev vlan1 root handle 100::100 tbf rate 1mbit burst 50kbit latency 1ms
tc qdisc show dev vlan1

sudo route add -host 192.168.0.21 gw 192.168.0.22 dev enp61s0f1