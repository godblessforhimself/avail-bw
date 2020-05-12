#### 常用命令
1. 将本项目复制到探测源
scp -r . liqing@10.10.114.19:~

2. 安装tmux
sudo apt install tmux
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
https://github.com/tmux-plugins/tpm
set -g mouse on
set -g @plugin 'tmux-plugins/tmux-yank'
set -g @plugin 'tmux-plugins/tmux-resurrect'
source ~/.tmux.conf

3. ubuntu apt
更换Tsinghua源 https://mirror.tuna.tsinghua.edu.cn/help/ubuntu/
sudo apt install make cmake g++ iperf3 -y

ssh -l liqing -o StrictHostKeyChecking=no 10.10.114.19 'sudo ls'

sudo tc qdisc del dev enp61s0f0 handle ffff: ingress; sudo tc qdisc add dev enp61s0f0 handle ffff: ingress; sudo tc filter add dev enp61s0f0 parent ffff: handle 800::800 u32 match u32 0 0 action police rate 100mbit burst 5000kb mtu 1500 conform-exceed drop; tc filter show dev enp61s0f0 parent ffff: handle 800::800;

4. 设置网卡为混杂模式
ip link set [interface] promisc on
查看
ip a show [interface] | grep -i promisc
sudo sysctl net.ipv4.ip_forward=1
sudo tcpdump -i enp61s0f1 -nN 'src host 192.168.0.19 and dst host 192.168.0.21'

LiQ_P1c!l@

远程sudo命令：https://stackoverflow.com/questions/10310299/proper-way-to-sudo-over-ssh
配置命令不需要sudo
https://jeromejaglale.com/doc/unix/ubuntu_sudo_without_password
通过ssh -t手动输入password
手动输入改为从文件读取