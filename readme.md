#### Using tc control link capacity
tc filter add dev enp2s0 parent ffff: u32 match u32 0 0 police rate 50mbit burst 100k
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

sudo tcpdump -i enp3s0 "src 192.168.0.8 and dst port 11106" > snd.pcap
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