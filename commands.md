#### 常用命令
1. **将本项目复制到探测源**
scp -r . liqing@10.10.114.19:~
2. 安装tmux
sudo apt install tmux
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
https://github.com/tmux-plugins/tpm
set -g mouse on
set -g @plugin 'tmux-plugins/tmux-yank'
set -g @plugin 'tmux-plugins/tmux-resurrect'
set-window-option -g mode-keys vi
set -g @yank_selection 'primary'
set -g @shell_mode 'vi'
source ~/.tmux.conf
* ubuntu apt
更换Tsinghua源 https://mirror.tuna.tsinghua.edu.cn/help/ubuntu/
sudo tc qdisc del dev enp61s0f0 handle ffff: ingress; sudo tc qdisc add dev enp61s0f0 handle ffff: ingress; sudo tc filter add dev enp61s0f0 parent ffff: handle 800::800 u32 match u32 0 0 action police rate 100mbit burst 5000kb mtu 1500 conform-exceed drop; tc filter show dev enp61s0f0 parent ffff: handle 800::800;
* 设置网卡为混杂模式
ip link set eth1 promisc on/off
* 查看网卡混杂模式
ip a show eth1 | grep -i promisc
* 开启软路由
sudo sysctl net.ipv4.ip_forward=1 + NAT(上网)
sudo iptables -t nat -A POSTROUTING -s "192.168.2.0/24" -o enp96s0f0 -j MASQUERADE
* tcpdump抓包 -i接口名 -nN不显示主机名
sudo tcpdump -i enp61s0f1 -nN 'src host 192.168.0.19 and dst host 192.168.0.21'
sudo tcpdump -i enp96s0f1 -nN 'host 192.168.2.7 and not port 22'
* 启用硬件时间戳：
sudo hwstamp_ctl -i enp61s0f1 -t 1 -r 3
sudo hwstamp_ctl -i enp61s0f1 -t 0 -r 0
* 改变网卡速率
sudo ethtool -s enp61s0f1 speed 1000 duplex full autoneg off
sudo ethtool -s enp61s0f1 speed 1000 duplex full autoneg on
sudo ethtool -s enp61s0f1 advertise 0x020
* 远程sudo命令
https://stackoverflow.com/questions/10310299/proper-way-to-sudo-over-ssh
https://jeromejaglale.com/doc/unix/ubuntu_sudo_without_password
通过ssh -t手动输入password
从文件读取
* 显示网卡信息
sudo lspci | grep Network
sudo lshw -class network
sudo ethtool -s enp61s0f1 advertise 0x020
sudo ethtool -k enp61s0f1 #查看tso gso状态
sudo ethtool -T enp61s0f1 #查看硬件时间戳支持
* 修改接口MTU
sudo ip link set dev enp61s0f1 mtu 9702
* 测试路径MTU
ping -c 3 -s 4972 -M do 192.168.1.21
* 修改socket buffer
sudo vi /etc/sysctl.conf
net.core.rmem_default=16777216
net.core.wmem_default=16777216
net.core.rmem_max=16777216
net.core.wmem_max=16777216
2097152=2MB
1000*9000B<9MB<16MB=16777216
* 使用pathload
发送端
./pathload_snd -i
接收端
rm pathload.txt
./pathload_rcv -s 192.168.0.19 -w 1 -O pathload.txt
* tc设置速率
sudo tc qdisc del dev vlan1 root; sudo tc qdisc add dev vlan1 root tbf rate 100mbit burst 10kb limit 10000kb
* ssh 代理 jupyter
ssh -N -L 8080:localhost:8080 <remote_user>@<remote_host>
* dagconvert
  
sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.4 and dst host 192.168.5.1 and udp" -f c -o in.pcap
* 显示网卡速率
sudo ethtool enp27s0f0
* 设置网卡速率
sudo ethtool -s enp27s0f0 speed 1000 duplex full autoneg off
sudo ethtool -s enp27s0f0 speed 10000 duplex full autoneg off
* 设置switch速率
show vlan 100
configure terminal
interface eth-0-45
speed 1000
* 设置DAG
receive protocols/line rates(page 20)
  sudo dagconfig -d0 --portd 1000
  sudo dagconfig -d0 --portd 10G_lan
关闭自动协商
sudo dagconfig -d0 --portd nonic
打开自动协商
sudo dagconfig -d0 --portd nic

#### dag抓包
```
sudo dagsnap -d0 -s 5 -o tf.erf
```

#### dag导出pcap
```
sudo dagconvert -T erf:pcap -i tf.erf -f d -o tf.pcap
```

#### tcpdump查看
```
sudo tcpdump -nN -r tf.pcap | less
```
#### tcpdump添加-e查看mac地址
```
sudo tcpdump -i eth1 -e
```
#### tcpdump 捕捉以太网地址
```
sudo tcpdump -nN -e -c 10 -i enp96s0f1 "ether host 02:00:00:00:00:00"
```
#### 禁用IPv6
``` 
  sudo vi /etc/sysctl.conf
  net.ipv6.conf.all.disable_ipv6=1
  net.ipv6.conf.default.disable_ipv6=1
  net.ipv6.conf.lo.disable_ipv6=1
```

#### 开启、关闭网卡
```
ip link set eth1 up/down
```

#### 检查当前是否ip转发
```
sudo cat /proc/sys/net/ipv4/ip_forward
```

#### 删除网卡IP
```
ip addr del 10.22.30.44/16 dev eth0
ip addr flush dev eth0
```