#### linux network optimization
1. interrupt coalescing
sudo ethtool -c enp27s0f0 
sudo ethtool -C enp27s0f0 rx-usecs 0
2. busy-poll in user space

#### 8.1
两跳 有背景流量时，单向延迟测量
两跳 有背景流量时，单向延迟变化
ns3 应用
负载阶段
包大小、包速率、包数量
探测阶段
包大小、间隔、数量
#### 7.23
可用带宽=探测包/探测总时间(探测时间+回复时间)
* 无背景流量
估计为957Mbps。
2000Mbps速率探测，3000个探测包
探测时间为17647us=17ms，回复时间约19285us=19ms

* 背景流量=500Mbps
估计值456-469，没使用拟合算法
17646:59614

* 800Mbps
3000个包发生丢包，减小到2000包
估计值226->205->207->...->212
问题：delay2没有回复到水平线
以4us作为delay的正常值，估计值为166->150->152->...156

* 添加测量delay正常值的步骤
* 添加自动拟合下降直线的步骤
* 添加自动选取发包数的步骤
#### 7.22

500Mps背景流量 10000个探测包（约1000Mbps速率）实际接收了8949个包，发生丢包
10000*1500B=15MB
使用iperf3以最大速率发6MB丢包，推测路由缓冲区大小=6MB。
6MB/1500B=4K。实际探测包可以更多，最大数量=缓冲区大小/背景流量速率/瓶颈链路发一个包时间
#### 7.17
设置路由到服务器的带宽1kMbps
iperf3 traffic -> server 900Mbps
prober -> server 1000Mbps
sudo ethtool enp27s0f0
sudo ethtool -s enp27s0f0 speed 1000 duplex full autoneg off

show vlan 100
configure terminal
interface eth-0-45
speed 1000

测试速率
iperf3 -sfm
iperf3 -c192.168.5.1 -fm -V
iperf3 -c192.168.5.1 -ub1000M -fmV

sudo tcpdump -i enp27s0f1 -nN 'src host 192.168.2.3 and dst host 192.168.5.1 and udp'

client以1000Mbps向server发送10000个大小为1472B的UDP包（12us间隔）
traffic设置0-1000Mbps流量
DAG捕捉离开client和到达server的包


####
先用dagsnap抓包erf
    ssh zhufengtian@192.168.5.1 "cd ~/jintao_test/dag_version/build && nohup ./server &" 1>run.log 2>&1
	sudo dagsnap -d0 -s 20 -o traffic.erf 1>run.log 2>&1 &
    ssh amax@192.168.2.3 "cd ~/jintao_test/dag_version/build && nohup ./client &" 1>>run.log 2>&1

再导出为pcap文件分析时间戳
	sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f c -o in.pcap
	sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f d -o out.pcap
    sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f c,d -o all.pcap
查看dt
    sudo tcpdump -ttt -nN -r in.pcap | less
#### 阶段目标
* mtu、send、clock_gettime
* 测量单向延迟 client以指定间隔发探测包
* client能以1000Mbps（指定速率）发1472B的UDP包直到server丢包或超过指定时间
* client能以指定间隔发探测包测量单向延迟

sudo tcpdump -i enp27s0f1 -nN 'src host 192.168.2.3 and dst host 192.168.5.1 and udp and greater 100'
#### 问题集
* TCP 包头最小20字节，启用时间戳时额外12字节；因此1500-20-20-12=1448，为默认MSS
* client enp27s0f1 网卡使用iperf3 TCP发包时使用MTU=1500时最大速率2000Mbps；使用MTU越大，最大速率越大。
* 如何配置盛科路由交换机
terminal length 0
show vlan 100
show interface eth-0-45
configure terminal
interface eth-0-45
speed 1000
* 如何测试能否修改端口速率
sudo ethtool -s enp27s0f1 speed 1000 duplex full autoneg off
sleep 1m
sudo ethtool -s enp27s0f1 speed 10000 duplex full autoneg on

使用cdf图表达分布
rsync -avz -e 'ssh -p 3970' amax@aliyun.ylxdzsw.com:/home/amax/catch_traffic_dir/ catch_traffic_dir
rsync -avz -e 'ssh -p 3970' amax@aliyun.ylxdzsw.com:/home/amax/jintao_test/dag_version/draw_cdf.ipynb draw_cdf.ipynb
sudo dagconvert -d0 -T dag:pcap -o outfile.pcap -b ""
####
aliyun.ylxdzsw.com
traffic->router->server
设置链路速率
* 如何修改端口MTU
sudo ip link set dev enp27s0f1 mtu 9710
sudo ip link set dev enp27s0f1 mtu 1500
* iperf3参数解释
-l length；-w windowsize；每次把length的数据发送到socketbuffer中，socketbuffer大小为windowsize
* 如何修改最大socketbuffer
sysctl -p | grep mem
/proc/sys/net/ipv4/tcp_mem
iperf3 -fm -M 9200 -V -c 192.168.2.4 -l 1m -w 32m
iperf3 -fm -M 9200 -V -c 192.168.2.3 -l 1m -w 32m
sysctl -w net.ipv4.tcp_rmem="4096 16777216 16777216"
cat /proc/net/ipv4/tcp_rmem
使用ping或者iperf3 UDP的最大MTU=9582，对应UDP数据大小=9554
* 路由交换机端口说明：有物理l2口port和虚拟口vlan。物理口使用no switchport变成l3口。物理l2口无MTU，只有最大帧限制9600B。虚拟口和l3口有MTU，最大9216B。如果包超过9216B，会被路由器分块；如果包超过9600B，会无法发送。
* udp发包接收全为0：iperf3获得的MTU不正确，UDP包大小=9658
* udp发包速率7000Mbps-9000Mbps，丢包率从小于1%-10%-20%

1. client->server traffic Iperf3发包+DAG抓包
   iperf3 -c 192.168.5.1 -ub 50M -l 1472 --pacing-timer 10 -t 10
   或Iperf3自动选取包大小
   iperf3 -c 192.168.5.1 -ub 50M --pacing-timer 10 -t 1
   iperf3 -s -f m
    dagconvert -T erf:pcap -i test.erf -o test.pcap
    tshark -r test.pcap | less
    sudo tcpdump -i enp96s0f1 -nN 'host 192.168.5.1 and not port 22'
    dagsnap -d0 -o a.erf -s 10 -v
    设备 文件 时间 调试

#### 带宽测量
1. 变长分组
Pathchar，Pchar
2. 数据包对
Bprobe、Sprobe、Capprobe
3. SLoPS
Spruce,Pipechar,pathneck
#### 各种因素
Iperf3
设置UDP包大小，避免分包(UDP包拆分消耗CPU资源、增大丢包率)
设置pacing-timer 10us-100us

高速网卡
gso和tso：使用iperf3测量链路带宽时，用tcp能测至10000Mbps，tso降低了cpu的负载 (为什么gso对udp无效-没有显著降低cpu负载)
硬件时间戳支持：可能支持硬件时间戳，但不能每个包都获取硬件时间戳

应用层send
每次send至少需要c的时间，则最大探测速率为MTU+28/c，
如果其间发生了进程切换，实际探测速率会更低
send只是将数据提交到skb中，实际需要等网卡发送
#### exp9 pathload效果测评
6.22
修改pathload_snd_fun里发送包间隔的时间
pathload发包间隔控制——偏大，导致实际速率一直小于目标速率
pathload没能正确估计链路容量
pathload估计了send recv平均时延、MTU、最小包间隔、最大发送速率等链路参数，
send平均时延：发送端调用一次send需要的时间
recv平均时延：接收端调用一次recv需要的时间
最小包间隔：2*Max(send,recv)
最大发送速率：(MTU+28)/最小包间隔

发送速率控制：
t1-send-t2-select(sleep_time)-while
tm_remaining=80us-14us=66us
sleep_tm_usec = tm_remaining - (tm_remaining%min_timer_intr)-min_timer_intr<200?2*min_timer_intr:min_timer_intr;
min_sleep_interval：sleep 1us需要的时间 = 60us
tm：min_sleep_interval+min_sleep_interval/4  75us
min_timer_intr：sleep tm微秒需要的时间-min_sleep_interval  75us

150+60=240us
检测context switch、interrupt_coalescence
#### 6.15 包大小实验总结

因为tc的burst必须大于9KB，因此小包的前几个包的间隔会显著的小
7%：包含tc的影响——9000B相对1500B的提升
20%：消除了tc影响——9000B相对1500B的提升
-10%：仅使用接收时间的降低

#### 6.8 包大小的作用
实验一：使用9000B的包是否提升了测量效果？
在100Mbps的链路上，流量包1500B，探测包range(1500,9000,500)
训练数据+测试数据
problem to solve: 
    - 收集测试数据时间过长，900,30,100<<9000,3,100
    - 训练参数
需要：实验脚本exp6.sh、修改hwts.cpp

实验二：使用9000B的包是否提升了传统方法的测量效果？
传统方法：pathload&igi
100Mbps带宽，背景包1500B，load0-90Mbps，探测包range(1500,9000,500)，探测n次保存输出，计算平均值

背景流量由三个参数决定：速率v、包大小l、粒度g
在100Mbps、1000Mbps下，探测包大小1500-9000B，背景包大小1500-9000B，进行试验

探测端：
将包放入skb等待网卡发送，网卡发送包并不占用cpu，但发送完一个包后会用一段时间调度下一个包(?)
因此包越多，调度次数越多，

流量端：
减小包大小会使n个包在一起发送，增加突发性 n取决于vlg n=fun(v,l,g)
在100Mbps，1500B，100us下不会发生：1500B/100us=120Mbps

控制背景流量的粒度g iperf3 -c 192.168.1.21 -ub 1000M -l 9000 --pacing-timer 1 -f m

#### 6.3
数据分析
间隔均值72us左右。列车的第一个间隔特别小，在30-60us间
解释：tc控制带宽，在突然到来一个包时，可以超过带宽；即src的前几个包间隔略小；
sudo tcpdump -i vlan0 --time-stamp-precision=nano "src host 192.168.0.19 and dst host 192.168.1.21 and udp" -w traffic.pcap
可能1：
src发送第一个包和第二个包的间隔小
可能2：
router发送第一个和第二包的间隔小

第二个间隔4us，第三个间隔100us(或68us)

设置分析：
tc等待区大于1000*9KB=9MB

应用层提交包到套接字缓冲区skb，使用tbf调度，使用网卡发送包。
网卡接收包，进入skb缓冲区，使用tbf调度，使用网卡发送包
网卡接收包，进入skb缓冲区，应用层接收
套接字缓冲区大小、tbf等待缓冲区大小均应大于列车大小
前者过小，发包时会阻塞，增加进程切换的开销，包间隔会增大

tc的rate单位默认bit=bps
control.sh
显示带宽、缓冲区、MTU

#### 5.28
***
要点：
* 背景流量越均匀越好
* 路径上每个节点收发包时，进程切换的时间远小于单包的传输时间——否则路径上机器负载增加时会显著减缓探测队列的传输速度即增加队列的时间。
* 时间测量的时机越接近网卡越好
***
接下来的改进点：
1. 提高带宽到1000Mbps
2. 提高测量精度到0.1Mbps
3. 缩短测量时间
4. 变化背景流量分布
***
拟合原数据集 [0.7143956043956043, 1.0, 1.0, 1.0, 0.3490176578601737, 0.4109917977350013]
测试集      [0.7480577136514983, 0.9974102848686645, 1.0, 1.0, 0.3378851855373465, 0.4132751540836887]
测试集(组)   [0.9478357380688124, 1.0, 1.0, 1.0, 0.20573080546809014, 0.25657339586705813]
***
测试igi，在100Mbps下的表现
sudo tc qdisc del dev vlan1 root; sudo tc qdisc add dev vlan1 root tbf rate 1000mbit burst 10kb limit 10000kb
sudo tc qdisc del dev enp61s0f1 root; sudo tc qdisc add dev enp61s0f1 root tbf rate 1000mbit burst 10kb limit 10000kb
***
lightgbm train use 6.116647005081177 s
xgboost train use 20.29240393638611 s
ann train use 222.26193594932556 s
lightgbm not set [0.8379578246392897, 0.9933407325194229, 1.0, 1.0, 0.2821738793012526, 0.35804045981315397]
lightgbm use set [0.9722530521642619, 1.0, 1.0, 1.0, 0.17571549016631488, 0.22106906926685294]
xgboost not set [0.8649648538660747, 0.9963004069552349, 1.0, 1.0, 0.26614928, 0.3386851]
xgboost use set [0.9844617092119867, 1.0, 1.0, 1.0, 0.16326185, 0.20568985]
ann not set [0.6677765445800962, 0.9211986681465039, 0.9974102848686645, 0.9996300406955235, 0.47988468, 2.6432664]
ann use set [0.7880133185349611, 0.974472807991121, 0.9988901220865705, 0.9988901220865705, 0.37168342, 1.5472627]
total 249.20557117462158 s
#### 5.25
回归
Lightgbm [0.984, 1.000, 1.0, 1.0, 0.122, 0.172] 6.76
Xgboost  [0.981, 1.000, 1.0, 1.0, 0.073, 0.143] 20.63
ANN      [0.914, 0.993, 1.0, 1.0, 0.202, 0.284] 225.65
分类
Bernoulli Naive Bayes 71.87% 0.0
Gaussian Naive Bayes  85.27% 0.0
Logistic regression   81.98% 5.1
Lightgbm              98.68% 44.9
Xgboost method        97.14% 29.6
ANN                   98.46% 126.0
#### 5.20
探测方法：100*100的train，如何避免流量拥塞，每个train之间空开一段时间。改进：高可用带宽时等待间隔很短，测量很快；低可用带宽时，等待间隔大，One way delay恢复很慢，测量one way delay恢复速率。
客户端首尾间隔，服务器每个包收到的时间，保存在客户端的data目录下
最长用时=100*（等待间隔+测量时间），令测量包的平均速率为10Mbps，间隔T=9000*8*100/10=720000us=720ms，一次测量100s，总共10000s，
#### 5.19
极大似然估计（多维、一维）
线性、lightgbm、xgboost、ANN、RNN

#### iperf发包原理
iperf定时执行任务：保存事件的时间，select等待这段时间。
预设的pacing-timer=1000us=1ms
#### 5.18
1. 可以使用tc控制探测机-流量源的速率；
2. train中前两个包的时间偏小
3. iperf的流量集中在2-3个相邻包间，即720us*n，n=3 4 5 一次发70个包，可以推测100ms进行一次发包
验证：
sudo tcpdump -i enp61s0f1 --time-stamp-precision=nano "src host 192.168.0.20 and dst host 192.168.1.21 and udp" -w iperf_traffic.pcap
结果iperf3包以100ms(0.1s)为周期波动，这100ms的流量在1ms内发送完毕；而100个包的时间为72ms
git clone git@github.com:esnet/iperf.git

sudo ./hardware -O timestamps.txt -p -20 -L 100 -M S -S 9000
sudo ./hardware -p -20 -L 100 -M C -S 9000 192.168.1.21
python preprocess.py -m format -o timestamps.txt timestamps_out.txt
sudo tc qdisc del dev vlan1 root; sudo tc qdisc add dev vlan1 root tbf rate 100mbit burst 10kb limit 10000kb
sudo tc qdisc del dev enp61s0f1 root; sudo tc qdisc add dev enp61s0f1 root tbf rate 100mbit burst 10kb limit 10000kb
#### 5.14
发送方一次发100包，是否有效，
随机睡眠一段时间，重复下一次
总共进行10， 50， 100轮

查看多少轮的平均接收时间

#### 5.13
如果不停发包，硬件时间戳会有不可用的情况
如果发一个包，阻塞等时间戳，延迟200us
接收方一直只能接收软件时间戳，最小间隔4us

总结：
1. 硬件时间戳(可能)比软件时间戳精确，但是不能连续获取，软件时间戳可以连续获取
2. 接收时只能获取软件时间戳
3. 使用SO_TIMESTAMPING选项获取时间戳的好处：尽可能接近网卡发出/接收包的时间，并且在内核获取时间开销小于用户态获取时间
4. 获取软件时间戳可能增加发送单个包的时间
5. 获取软件时间戳对发包的影响：接收端不变，发送端控制变量，观察接收端的软件时间戳
6. 发送100个1500B的包，浮动大600-700us，浮动小550-580us

#### 5.12
1. 探测机和流量源会相互影响：会，但在总流量没到网卡带宽时影响较小，可能是交换机内缓冲区的作用。
2. 探测机-目标机 抓包
./fake-client -C 10 -L 1000 -R 10 192.168.1.21
sudo tcpdump -i enp61s0f1 --time-stamp-precision=nano "src host 192.168.0.19 and dst host 192.168.1.21 and udp" -w s2.pcap
tcpdump通过调用libpcap获取包，如果网卡支持
ethtool -T ethX

#### 5.11
iperf udp 速率100以上开始丢包
iperf3 -c ip -u -f m -b 500M -l 1472 -w 8K
包越大，cpu负载越小，丢包概率越大
缓冲区越大，丢包概率越大
-w 在速率为500Mbps时设为8K即可，buffer过小达不到目标速率，buffer过大丢包率过大（为什么发包越快需要的buffer越大-进程切换开销）

先在链路带宽1000Mbps的情况下试验
#### 5.10
数据分析
IGI/PTR
pathload
pathchirp
抓包
sudo tcpdump -i enp61s0f1 --time-stamp-precision=nano "src host 192.168.0.19 and dst host 192.168.1.21" -w igi.pcap
sudo tcpdump -i enp61s0f1 --time-stamp-precision=nano "src host 192.168.0.19 and dst host 192.168.1.21" -w iperf.pcap
sudo tcpdump -i enp61s0f1 --time-stamp-precision=nano "src host 192.168.0.19 and dst host 192.168.1.21" -w iperfudp.pcap

udp模式需要对高带宽做出更改：受CPU限制，还是高丢包率？
大段卸载（Large Segment Offload，简称LSO）是一种在高带宽网络中用于减少CPU使用率和增加发送吞吐量的技术，该技术通过网卡对过大的数据分段，而无需协议栈参与。该技术还有一些别称，当应用于TCP时被称为TCP段卸载(TSO)
iperf3在万兆网络中实验时，TCP能达到万兆带宽，UDP只能达到3000-5000Mbps
当发送包的数量越多，cpu负载越重。在发送包大小不变时，发送速率越大，cpu负载越大。
#### 5.7
10000Mbps
以1000Mbps为档位划分负载

link，目标精度，样本精度，验证精度
第一次试验81组数据
第二次试验901组数据

method logistic_regression use 23.313542366027832 seconds, acc 0.18205915813424345
method lightgbm use 31.82629632949829 seconds, acc 0.23943117178612058
method xgboost use 355.07950234413147 seconds, acc 0.29997259328741244
method keras_ann use 615.4858946800232 seconds, acc 0.2558589306029579

allow_width=10
method logistic_regression use 7.59083366394043 seconds, acc 0.2060655737704918
method lightgbm use 14.44516921043396 seconds, acc 0.3749726775956284
method xgboost use 103.5573456287384 seconds, acc 0.48150907573537505
method keras_ann use 406.1221754550934 seconds, acc 0.3857377049180328
original size 880000
filtered size 183000
allow_width=5
method logistic_regression use 4.132546901702881 seconds, acc 0.21610526315789474
method lightgbm use 7.257874965667725 seconds, acc 0.48736842105263156
method xgboost use 56.56231474876404 seconds, acc 0.6065656456247457
method keras_ann use 223.57213878631592 seconds, acc 0.4787368421052632
original size 880000
filtered size 95000
allow_width=1
method logistic_regression use 2.008631706237793 seconds, acc 0.415
method lightgbm use 4.2167277336120605 seconds, acc 0.7730769230769231
method xgboost use 7.597692489624023 seconds, acc 0.8177627558486471
method keras_ann use 42.27103638648987 seconds, acc 0.6303846153846154
allow_width=0
method logistic_regression use 1.3524019718170166 seconds, acc 0.7166666666666667
method lightgbm use 0.6158597469329834 seconds, acc 0.93
method xgboost use 1.3926689624786377 seconds, acc 0.9334794364085991
method keras_ann use 16.581727981567383 seconds, acc 0.8366666666666667
original size 880000
filtered size 9000

sendtime
method logistic_regression use 1.0876355171203613 seconds, acc 0.6166666666666667
method lightgbm use 0.47572779655456543 seconds, acc 0.8655555555555555
method xgboost use 0.8717546463012695 seconds, acc 0.8865361611791924
method keras_ann use 14.700949668884277 seconds, acc 0.7266666666666667
original size 880000
filtered size 9000

recvtime
method logistic_regression use 1.051814079284668 seconds, acc 0.5311111111111111
method lightgbm use 0.47074127197265625 seconds, acc 0.7755555555555556
method xgboost use 1.0122950077056885 seconds, acc 0.7808939492656078
method keras_ann use 15.728285789489746 seconds, acc 0.5966666666666667
original size 880000
filtered size 9000

第一次试验在路由器上进行，第二次试验在软路由上进行，第三次试验使用81组数据
method logistic_regression use 14.42025375366211 seconds, acc 0.283875
method lightgbm use 12.104907035827637 seconds, acc 0.899875
method xgboost use 82.78582715988159 seconds, acc 0.9260096562484487
method keras_ann use 739.4592387676239 seconds, acc 0.86675

##### 5.6
redirect host new nexthop
一个mac地址多个IP：ip aliasing
一个物理网卡虚拟多个mac地址：ip link add vlan0 link eth0 type macvlan mode private
监听经过虚拟网卡的所有流量-打开混杂模式：ip link set vlan0 promisc on或ifconfig eth1 promisc
查看网卡是否处于混杂模式：netstat -i，P表示混杂模式

使用IPerf3 udp模式，发包速率最大为3600Mbps
UDP发包速率越大丢包率越高

##### 5.5
1. 进行预测link的实验 
2. sendtime数据分析 x
3. 增加单组数据量
    一组10个点，1000组，单组时间为11.776s
    一组50个点，1000组，单组时间为58.8s
4. 





##### 5.3
输入：sendtime recvtime link，对输入正则化
输出：load的分类
方法：Logistic Regression、lightgbm、xgboost、keras
效果最好的是xgboost，在使用了sendtime,recvtime,link后，准确率为91%
sendtime和recvtime哪个重要？sendtime

多层模型，更细粒度预测load，要怎么做？

测量的数据如何改进，能提升准确率？


使用sendtime recvtime预测link，准确率50%


##### 5.2
对X不进行归一化，使用mae：
 loss: 132.2161 - mae: 132.2161 - mean_absolute_percentage_error: 122.8296 - mean_squared_logarithmic_error: 0.7741 - 
 val_loss: 152.5215 - val_mae: 152.5215 - val_mean_absolute_percentage_error: 117.7666 - val_mean_squared_logarithmic_error: 0.9795
keras_method takes 273.57273149490356 s, acc 168.5266902155964

对X进行归一化，mae：
loss: 92.2718 - mae: 92.2718 - mean_absolute_percentage_error: 87.1505 - mean_squared_logarithmic_error: 0.5395 - 
val_loss: 114.9291 - val_mae: 114.9291 - val_mean_absolute_percentage_error: 132.6119 - val_mean_squared_logarithmic_error: 0.7219
keras_method takes 279.66000270843506 s, acc 115.22706412474314

结论：使用StandardScaler对每一维分别归一化比所有维一起归一化效果好，比不归一化效果好
损失函数使用mae和mape，则另一个会变大。


x引入link值后
loss: 0.2308 - accuracy: 0.9123 - val_loss: 0.3638 - val_accuracy: 0.8706
keras_method takes 219.7703788280487 s, acc 0.8711111111111111

loss: 31.0009 - mae: 31.0009 - mean_absolute_percentage_error: 20.7613 - mean_squared_logarithmic_error: 0.1257 - val_loss: 41.3469 - val_mae: 41.3469 - val_mean_absolute_percentage_error: 29.9190 - val_mean_squared_logarithmic_error: 0.1564
keras_method takes 293.5805263519287 s, acc 213.07654469091216

x不使用link值
loss: 1.2040 - accuracy: 0.5579 - val_loss: 1.3938 - val_accuracy: 0.5053
keras_method takes 247.89426159858704 s, acc 0.4883950617283951

loss: 92.9981 - mae: 92.9982 - mean_absolute_percentage_error: 89.0349 - mean_squared_logarithmic_error: 0.5549 - 
val_loss: 113.9996 - val_mae: 113.9996 - val_mean_absolute_percentage_error: 136.4761 - val_mean_squared_logarithmic_error: 0.7415
keras_method takes 300.25889444351196 s, acc 198.6261189934901

按link分类后，对load预测
keras_method takes 28.17873191833496 s, acc 0.9622222222222222
keras_method takes 34.230164766311646 s, acc 29.2304036856616
keras_method takes 26.77443218231201 s, acc 0.9444444444444444
keras_method takes 33.98090076446533 s, acc 59.07641046851829
keras_method takes 26.510547876358032 s, acc 0.8611111111111112
keras_method takes 33.988789081573486 s, acc 84.72911766438425
keras_method takes 26.53454613685608 s, acc 0.8666666666666667
keras_method takes 33.60531449317932 s, acc 117.42903623778732
keras_method takes 27.246195793151855 s, acc 0.7744444444444445
keras_method takes 34.13440418243408 s, acc 136.40321543477376
keras_method takes 27.13450837135315 s, acc 0.9333333333333333
keras_method takes 34.35671544075012 s, acc 186.71767472897753
keras_method takes 26.84077787399292 s, acc 0.9
keras_method takes 34.11403560638428 s, acc 205.11904161550262
keras_method takes 26.98635172843933 s, acc 0.8133333333333334
keras_method takes 34.123430013656616 s, acc 218.93726828812964
keras_method takes 25.894376754760742 s, acc 0.9277777777777778
keras_method takes 32.45923590660095 s, acc 259.7786279764811
对应的linkset为：
[100, 200, 300, 400, 500, 600, 700, 800, 900]

X加入link值，
keras_method takes 30.258543729782104 s, acc 0.9622222222222222
keras_method takes 34.03348708152771 s, acc 29.982100479921883
keras_method takes 27.074655771255493 s, acc 0.9377777777777778
keras_method takes 33.74241399765015 s, acc 59.8336317097346
keras_method takes 28.024274826049805 s, acc 0.8655555555555555
keras_method takes 34.47195887565613 s, acc 86.10727921377111
keras_method takes 26.76796317100525 s, acc 0.8688888888888889
keras_method takes 32.63080406188965 s, acc 117.03573853842653
keras_method takes 26.92050266265869 s, acc 0.7755555555555556
keras_method takes 33.65020442008972 s, acc 137.87771230278486
keras_method takes 26.651753187179565 s, acc 0.9277777777777778
keras_method takes 32.5246205329895 s, acc 179.00755919928844
keras_method takes 26.162548065185547 s, acc 0.9
keras_method takes 34.10996103286743 s, acc 211.11757220093526
keras_method takes 25.74867033958435 s, acc 0.8144444444444444
keras_method takes 33.40885019302368 s, acc 220.48154115103262
keras_method takes 26.446345567703247 s, acc 0.9355555555555556
keras_method takes 34.02566981315613 s, acc 253.49034163121354
##### 2020.4.30

##### 2020.4.29
读取数据，相邻时间戳作差，作boxplot
对link进行预测
使用sendtime
logistic_regression 25s 21.4%
lightgbm 
使用数值预测时，16%；概率预测时，386.6952431201935 s, rate 0.44
Epoch 200/200
65610/65610 [==============================] - 1s 14us/step - loss: 1.4502 - accuracy: 0.4254 - val_loss: 7.5941 - val_accuracy: 0.0143
使用recvtime
X=X[:,:,1]
logistic regression takes 26.197437047958374 s, rate 0.14004938271604941
lightgbm takes 191.83219146728516 s, rate 0.19803703703703707
XGBoost(RF)
keras
使用sendrecvtime
Epoch 200/200
65610/65610 [==============================] - 1s 17us/step - loss: 1.3974 - accuracy: 0.4364 - val_loss: 7.8312 - val_accuracy: 0.0036

数据=sendtime,recvtime
全部数据->load，全部数据+link->load
分组数据->load
##### 2020.4.28
1. iperf3 -c 10.10.114.21 -u -b 50M -w 5M -l 1472
2. while size < report_buffer
3. padding for structure
变动链路带宽和负载，得到多组文件 link50-load10-exp1.txt
测得的数据
第一行 sendto 时间戳 1588050327.087352738 [CONTINOUS_COUNT_, PAIR_COUNT_]
第二行 recvfrom 时间戳 1588050327.088288681 [CONTINOUS_COUNT_, PAIR_COUNT_]
第三行 报文的顺序index [CONTINOUS_COUNT_* PAIR_COUNT_]

##### 2020.4.22
探测包是这样的：
每次发送两个大小为MTU的UDP包，包的间隔为单个包在瓶颈链路上通过的时间；然后休息一段时间，发送下一个包对；
设置间隔的目的：使两个包间所有背景流量都进入队列，这样可以累积背景流量包；
设置休息间隔的目的：使总体的发包速率低于瓶颈链路速率，瓶颈链路的缓冲区不会溢出。

问题1：
clock_nanosleep不能精确控制发包间隔，如设置240us，实际100轮平均为346us，最小-最大区间为313-393us。
如果使用igi-ptr的循环进行间隔控制，实际间隔平均700-800us，最小最大区间260-1000us

发包间隔不精确的后果：若太大，部分两个包达到间的背景流量可能离开队列，

问题2：
select是否更精确

问题3：
在gin小于gB的情况下，背景流量是离散的包，因此gout-gin是离散的值，只能给出速率的区间估计

问题4：
只能估计在第一个包到达瓶颈链路入口至第二个包到达瓶颈链路入口期间的背景流量；
如果背景流量的爆发性很强，包集中，有可能高估（探测集中在爆发区间）或低估（探测集中在非爆发期间）背景流量。

问题5：
在入口使用tc限速没有意义；

##### 2020.4.23
探测源以100Mbps发两个探测包
瓶颈链路带宽100Mbps
探测包的gin认为都是gB
统计gout
影响gout的因素：背景流量、接收端的进程切换
A1：测量服务器从buffer中取出第一个包，获取时间，
A2：取出第二个包，获取时间
B：iperf服务器从buffer中取出背景流量，获取时间
事件顺序为：A1-B-A2

sudo tcpdump -i enp3s0 "src 192.168.0.8 and dst port 11106"
tcpdump的结果都是17us

./run.sh --capacity 100 --traffic 90 --rate 10 --filename c100t90r10.txt
./run.sh --capacity 100 --traffic 80 --rate 10 --filename c100t80r10.txt
./run.sh --capacity 100 --traffic 70 --rate 10 --filename c100t70r10.txt
./run.sh --capacity 100 --traffic 60 --rate 10 --filename c100t60r10.txt
./run.sh --capacity 100 --traffic 50 --rate 10 --filename c100t50r10.txt
./run.sh --capacity 100 --traffic 40 --rate 10 --filename c100t40r10.txt
./run.sh --capacity 100 --traffic 30 --rate 10 --filename c100t30r10.txt
./run.sh --capacity 100 --traffic 20 --rate 10 --filename c100t20r10.txt
./run.sh --capacity 100 --traffic 10 --rate 10 --filename c100t10r10.txt