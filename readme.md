#### 今日计划
改图：
BQR framework & algorithm
iperf3 vs D-ITG
BQR in 10Gbps
#### fig
width=3.2cm
height=2.4cm
双栏绘制三副图：
3 x 2.0x1.3
fontsize 7
单栏一副图：
3.4x1.1 
fontsize 9-6
单栏两幅图
2x1.3x1.1
fontsize 6
#### common header
def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
np.set_printoptions(suppress=True,precision=2)
color=[pickColor(i, 10) for i in range(10)]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
plt.rcParams.update({'font.size':7})
matplotlib.rcParams['hatch.linewidth']=0.3
marker=['d','.','*','<','p'] #5
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1)),(0,(3,1,1,1,1,1))] #5
hatch=['/','\\','x','o','-|'] #5
imgDir='/home/tony/Files/available_bandwidth/thesis-svn/IMC2021/BurstQueueRecovery-jintao/images'

plot(x,y,color=color[i],linestyle=linestyle[i],marker=marker[i],markersize=12)
plt.bar(x,height+10,bottom=-10,width=width,label=label[i],edgecolor=color[i],hatch=hatch[i]*5,fill=False,linewidth=.5)

plt.legend(loc='upper center',framealpha=.5,ncol=5,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
ax=plt.gca()
ax.tick_params('both',length=1,width=1,which='both',pad=1)
plt.xlabel('',labelpad=0)
plt.ylabel('',labelpad=0)

####
1. Loss related mechanism RED WRED
2. Buffer related mechanism Router buffer policy

sender [113] 1120us,29720us [99]=13990us
traffic [130]=21677<[131]=43734 temp[88]=13812<temp[89]=14233
pareto在发送完100个负载包时，流量包为89个，
constant t=constant[99] np.searchsorted(traffc['constant'],t)-1 61个
poisson 56个
  o
  |
o-o-o
#### RED/WRED
华为FAQ-CE系列交换机缓存
https://support.huawei.com/enterprise/zh/knowledge/EKB1000051901
交换机缓冲区
https://community.cisco.com/t5/networking-documents/egress-qos/ta-p/3122802
缓冲区需求review
https://people.ucsc.edu/~warner/Bufs/buffer-requirements
TCP对缓冲区大小的需求
https://www.es.net/assets/pubs_presos/NANOG64mnsmitasinbltierneybuffersize.pptx.pdf
#### 路由器缓冲区大小
动态缓存+静态缓存
大缓存流量管理引擎
缺省情况下，报文进入大缓存流量管理引擎进行报文缓存和调度，此时当设备的所有接口均有大流量报文转发时，设备无法满足无丢包转发的要求
缺省情况下，接口缓存较小，接口流量如果突发达到接口带宽的50%～60%左右就会出现丢包现象。设备缓存采用“静态+动态”的方式进行分配。每个接口默认分配一部分静态缓存，以提供基本的缓存保证；剩余缓存作为设备动态缓存。当一个接口上某个队列有较大的突发流量时，可以配置qos queue buffer shared-ratio增加该队列可以占用的动态缓存的最大百分比。设备将为该队列分配较多的动态缓存，减少该队列
的丢包
display qos configuration
qos burst mode enhanced/extreme
display qos queue statistics
1Gbps,10Gbps->3000*9000B=27MB
#### 获取包大小CDF
tshark -r /home/ubuntu2/pcapFiles/caida2.pcap -n -T fields -e frame.time_epoch -e frame.len > /home/ubuntu2/pcapFiles/caida2.len
tshark -r /home/tony/pcapFiles/bigFlows1.pcap -n -T fields -e frame.time_epoch -e frame.len > /home/tony/pcapFiles/bigFlows1.len
rsync -avz ubuntu2@192.168.66.17:/home/ubuntu2/pcapFiles/caida2.len /home/tony/pcapFiles/caida2.len
#### IMC论文图片
figure(figsize=(2.8, 1.7), dpi=300)
plt.rcParams['font.sans-serif']=['Arial']
plt.grid(linestyle = "--")
ax = plt.gca()
ax.spines['top'].set_visible(False)  #去掉上边框
ax.spines['right'].set_visible(False) #去掉右边框
plt.legend(loc='lower right', prop={'family':'Times New Roman', 'size':8})
plt.xlabel('iterations', fontdict={'family' : 'Times New Roman', 'size':8})
plt.yticks(np.arange(0, 1.1, 0.2), fontproperties = 'Times New Roman', fontsize=8)
无上边框、右边框
grid是虚线
表上方、下方无标题
折线图点数较少时，使用带标记的折线
选择合理颜色
#### bigFlows效果不如CAIDA
当前使用30秒测量时间
拓展到10段变化，每段持续10秒
#### 为recv-module添加更多的信息
添加在流量突发的情况下，owd曲线的更多信息
负载包、检查包、整个阶段 最低点、最高点的值和下标
整个阶段最低点下标、值（0），最高点下标、值，负载包
./send-main --loadRate 1500 --loadSize 1472 --inspectSize 1472 --loadNumber 100 --inspectNumber 100 --repeatNumber 400 --streamGap 40000 --dest 10.0.7.1 --minAbw 50 --maxAbw 1200 --minGap 40 --maxGap 10000 --Gap 400 --n1 80 --n2 20
#### BQR更新
检查包分为n1和n2两段，n1段需要minAbw/maxAbw/minGap/maxGap限制，n2段需要Gap限制
#### 动态调整检查包数量
10Gbps/无背景流量/minAbw=50/minGap=40/maxGap=400->inspectNumber=183
owd 0 25 458
10Gbps/100Mbps背景流量/minAbw=50/minGap=40/maxGap=400->inspectNumber=183
owd 0 36 560
10Gbps/900Mbps背景流量/minAbw=50/minGap=300/maxGap=400->inspectNumber=141
owd 0 110 1178 未恢复
10Gbps/900Mbps背景流量/minAbw=50/minGap=500/maxGap=500->inspectNumber=100
owd 0 54 1196 已恢复
10Gbps/100Mbps背景流量/minAbw=50/minGap=500/maxGap=500->inspectNumber=100
owd 0 20 550 已恢复 但第一个区间太大
10Gbps/100Mbps背景流量/minAbw=50/minGap=40/maxGap=1000->inspectNumber=126
owd 0 20 550 已恢复 但第一个区间太大 862/877
10Gbps/100Mbps背景流量/minAbw=600/minGap=40/maxGap=1000->inspectNumber=126
owd 0 20 550 已恢复 但第一个区间太大 
### 做bigFlows.pcap+CAIDA的两个实验
以0.1倍速率进行播放，平均速率400Mbps
sudo tcpreplay -i ens1f0 -x 0.1 --duration=60 --stats=5 2.pcap
使用DAG捕捉流量，以秒级别进行估计
流量在毫秒级别无明显关系，在秒级别比较稳定
BQR测量结果与秒级别的均值相同，且一起变化
构造一个流量，由三部分组成，每部分的秒速率不同
30秒×3

流量预处理：去除ICMP和IPv6
bigFlows.pcap -> bigFlows2.pcap
bigFlows2.pcap 300s 9.466Mbps
equinix-nyc.dirA.20180816-125910.UTC.anon.pcap -> caida3.pcap
caida3.pcap 50s 4367Mbps

### DAG
以4431Mbps持续49秒：
sudo tcpreplay -i ens1f0 -p 6000 --pps-multi=100 --netmap 2.pcap
以443Mbps持续490秒：
sudo tcpreplay -i ens1f0 -p 6000 --pps-multi=10 --duration=10 2.pcap
-x -p -M -t -o
--pps-multi=10
awk 'NR==1{x=$1}{print $1-x,$2}' /home/ubuntu2/pcapFiles/2.len > /home/ubuntu2/pcapFiles/2-z.len
awk 'NR==1{x=$1}{print $1-x,$2}' /tmp/dag/c.len > /tmp/dag/c-z.len
head -n 1 /tmp/dag/c.pcap
tshark -r /tmp/dag/c.pcap -Y "frame.number == 15749"
sudo dagsnap -d0 -s 360 -o /tmp/dag/dagsnap.erf 1>/tmp/dag/dagsnap.log 2>&1 &
sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -f c -o /tmp/dag/c.pcap
tshark -r /tmp/dag/c.pcap -T fields -e frame.time_epoch -e frame.len > /tmp/dag/c.len
tshark -r /home/ubuntu2/pcapFiles/2.pcap -T fields -e frame.time_epoch -e frame.len > /home/ubuntu2/pcapFiles/2.len
### 10Gbps
在10Gbps下时，BQR固定阈值的参数需要修改。
10Gbps下是OWD曲线有突然降低的现象。

nohup /home/ubuntu5/abw-project/avail-tools/bqr/send-recv-module/build/recv-main --timestamp /tmp/bqr/timestamp.txt --result /tmp/bqr/result.txt --log /tmp/bqr/log.txt --polling 1 --busy-poll -1 --once 1>/tmp/bqr/rx.log 2>&1 &
/home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 1500 --loadSize 1472 --inspectSize 1472 --loadNumber 100 --inspectNumber 100 --repeatNumber 10 --retryNumber 1 --preheatNumber 0 --streamGap 1000 --trainGap 0 --dest 10.1.7.1 --noUpdate 1 --minAbw 50

# 修改链路MTU
ping -c 1 -s 1472 -M do 10.0.7.1
ping -c 1 -s 8972 -M do 10.0.7.1
ip link set <dev> mtu 9000
netplan
a4:fa:76:01:3d:f0
http://www.spin.rice.edu/Software/poisson_gen/
10Gbps的实验

rsync -avz amax@192.168.67.84:/home/amax/guohaorui/throughput_plot/equinix-nyc.dirA.20180816-125910.UTC.anon.pcap /home/tony/pcapFiles
rsync -avz /home/tony/pcapFiles/equinix-nyc.dirA.20180816-125910.UTC.anon.pcap ubuntu2@192.168.66.17:/home/ubuntu2/pcapFiles

netmap需要下载ixgbe硬件
rsync -avz /home/tony/Downloads/ixgbe-5.3.8.tar.gz ubuntu2@192.168.66.17:/home/ubuntu2/netmap/LINUX/ext-drivers

caida包长度最小=50B=46B+4B，最大=1504B=1500B+4B，先去除IPv6和ICMP6包，再将其大小-4B。
使用tcprewrite进行转换
1.tcpdump -r /home/tony/pcapFiles/equinix-nyc.dirA.20180816-125910.UTC.anon.pcap -nN -w /home/tony/pcapFiles/ip4.pcap "not ip6 and not icmp6"
2.time ./main /home/tony/pcapFiles/ip4.pcap /home/tony/pcapFiles/ip4-reduced.pcap 
3.rsync -avz /home/tony/pcapFiles/ip4-reduced.pcap ubuntu2@192.168.66.17:/home/ubuntu2/pcapFiles/ip4-reduced.pcap
4.tcprewrite --dlt=enet -i /home/ubuntu2/pcapFiles/ip4-reduced.pcap -o /home/ubuntu2/pcapFiles/1.pcap --srcipmap=0.0.0.0/0:10.0.2.1/32 --dstipmap=0.0.0.0/0:10.0.7.1/32 --enet-smac=a4:fa:76:01:43:f8 --enet-dmac=60:12:3c:3f:bc:d3 --fixlen=pad --fixcsum
tcprewrite --dlt=enet -i /home/ubuntu2/pcapFiles/ip4-reduced.pcap --srcipmap=0.0.0.0/0:10.1.2.1/32 --dstipmap=0.0.0.0/0:10.1.7.1/32 --enet-smac=a4:fa:76:01:43:f8 --enet-dmac=60:12:3c:3f:bc:d3 --fixlen=pad --fixcsum -o /home/ubuntu2/pcapFiles/2.pcap
sudo tcpreplay -i ens1f0 -t 2.pcap


#### bigFlows.pcap
total 1656538
udp 320715
tcp 1330920
icmp 10540
1655978
TCP和UDP的重复包

#### 优点 contribution
测量快。结果即测量期间的平均可用带宽。
测量准。对均匀流量特别准。对突发性、包大小接近实际的流量也尚可。
通用于多跳。在背景流量为单跳时可以通用。

#### 缺点
缺乏TCP拥塞控制的反馈机制，不能持续性测量。
需要以大于可用带宽的速率探测。
测量期间增加了包的等待时间。
测量多跳的流量效果如何。

#### 结论
对于均匀流量且包大小均最大的情况，目前的BQR效果良好
对于非均匀的现实中流量，BQR在启动时，队列中可能有缓冲包，在BQR检查到队列恢复后，也会有背景流量到来，但不会计入BQR的结果。
总体上，BQR多次有效测量平均值可反映平均流量。
就单次测量而言，BQR普遍偏小。
#### 测量
每隔100ms进行一次测量
共60秒/0.1秒=600次测量
流量为node2->node3
Link4设10Gbps使用DAG抓包
node6启动DAG
node2启动流量
node1启动BQR
清理、node6解析erf
#### 实际场景中的流量
caida流量无负载部分，且包含IPv6数据包
为了模拟实际场景流量，可以使用bigFlows.pcap、tcpreplay加速播放
duration: 300s
9.4Mbps
假如一轮测量总共300s，分为10轮，每轮持续30s
速率区间为100-900Mbps，对应倍率为10-100
sudo dagsnap -d0 -s 60 -o /tmp/dag/dagsnap.erf 1>/tmp/dag/dagsnap.log 2>&1 &
ssh ubuntu1@192.168.66.16 "nohup bash /home/ubuntu1/pcapFiles/send.sh 1>/tmp/pcap/send.log 2>&1 &"
send.sh:
time sudo tcpreplay-edit --srcipmap=0.0.0.0/0:10.0.1.1/32 --dstipmap=0.0.0.0/0:10.0.7.1/32 --enet-smac=a4:fa:76:06:1d:32 --enet-dmac=60:12:3c:3f:bc:d5 --fixcsum --intf1 ens1f1 --loop=10 --stats=1 -x 100 --duration=30 /home/ubuntu1/pcapFiles/bigFlows.pcap
time sudo tcpreplay-edit --srcipmap=0.0.0.0/0:10.0.1.1/32 --dstipmap=0.0.0.0/0:10.0.7.1/32 --enet-smac=a4:fa:76:06:1d:32 --enet-dmac=60:12:3c:3f:bc:d5 --fixcsum --intf1 ens1f1 --loop=1 --stats=1 -x 10 --duration=30 /home/ubuntu1/pcapFiles/bigFlows.pcap
sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -f a -o a.pcap
sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -f c -o c.pcap
sudo tcpdump -nN -r /tmp/dag/a.pcap > /tmp/dag/a.txt
tshark -r a.pcap -T fields -e frame.time_epoch -e frame.len > a.len

查看link-layer header type: sudo tcpdump -i ens1f1 -L [EN10MB]
link-layer header type是Raw IP,解决办法见https://github.com/appneta/tcpreplay/issues/153,另一个相关https://tcpreplay-users.narkive.com/tdgBdOmE/help-regarding-sending-raw-ip-pcap-file-to-ethernet
--dlt=enet
node1使用tcpreplay发包
DAG进行抓包，然后分析包内容，进行对比
tshark -r .pcap -c 100 -Y "frame.len==243"
#### BQR曲线对比
实验1
900-900-900
500-500-500
0-0-0
900-400-400
400-900-400
400-400-900
实验2
600-0-0
600-300-0
0-600-0
300-600-0
实验3
900-0(100)-0
0-0(100)-900
#### 实验结论
实验1：误差、包开销、时间
实验2：spruce的测量结果随着非紧链路带宽变化而变化；PTR有突然变化；其他方法无明显变化
因为实验2 0-600-0和600-0-0运行了两次，需要使用exp2/patch2.sh重复。注意实验拓扑。
实验3：补充exp3/patch1.sh
第二跳为窄链路，

迭代次数：
有效时间
实际时间
平均队列长度
最大队列长度
#### numpy
reduce使用op消去一个轴
reduceat使用op消去轴的区间
广播原则：两者的最后一个维度(trailing dimension)长度相同或为1,则是兼容的
在a[:,np.newaxis,:]可以引入维度
#### bash脚本注意
编写循环时不要使用i，父脚本和子脚本的i冲突时会发生错误！
#### BQR改进
使用10点+90点存在缺点：10、11的可用带宽差距大；第9、10个点单向延迟偏大，导致原本在第9个点的可用带宽估计变为第11个点的估计，比实际值远小，且很难从局部脱离出来。
改进为使用60点+40点。
#### 实验设计
2证明spruce的缺陷，在34中不测量spruce。
1 三跳的实验
13组 无中断延迟
cx=cy=cz=1Gbps
x=y=z=range(0,900,100)
x=900,y=z=400
x=z=400,y=900
x=y=400,z=900

2 ADR和spruce真实效果
修改Link4为XGigabytes
cx=cy=1Gbps,cz=10Gbps，启用DAG，注意记录spruce接收处的时间
x=600 y=range(0,500,100) z=0
x=range(0,500,100) y=600 z=0

3 紧链路非窄链路
修改Link3 speed为100Mbps
cx=cz=1Gbps,cy=100Mbps
x=900,y=0,z=0
x=900,y=0,z=400
x=900,y=0,z=900
x=900,y=20,z=900
x=0,y=0,z=900
x=400,y=0,z=900
x=400,y=20,z=900
900,0,0              紧链路在窄链路前
900,0,400            紧链路在窄链路前，干扰1
900,0,900            紧链路在窄链路前，干扰2
900,20,900           紧链路在窄链路前，干扰3
0,0,900              紧链路在窄链路后
400,0,900            紧链路在窄链路后，干扰1
400,20,900           紧链路在窄链路后，干扰2

4 中断延迟=0,1,2,5,10,20,50,100,200,300

#### 待解决问题
dagconvert转换后没有包
spruce 效果很差，使用两跳+DAG来进行实验
#### 跳过D-ITG
缩短脚本运行时间
减少ssh的次数->ssh用于控制iperf3设置背景流量、控制中断延迟参数、发包工具->相同背景流量和中断延迟下测量不同工具多次
->能持续多次的进程重复利用

各个方法的函数 与 背景流量（链路带宽）、中断延迟的实验分开

BQR调试信息
预测值异常->使用对应train的时间戳人工预测->人工预测正常
->方法出错->log中对应的信息

#### ground-truth 如何获取
Iperf3在长期的平均速率是稳定的趋近理想值。
D-ITG长期的平均速率是不稳定的，它与系统实现select的方式有关，且恒定偏小。
当使用D-ITG作为发包工具时，可用带宽的ground-truth改如何获取？

#### D-ITG代码不易维护，测量结果表示
arg是pps
包间距为1/pps 秒 = 1000/pps 毫秒
IntArriv=1000/arg
wait = IntArriv.next()
sec=(wait-1)/1000
usec = (wait-1)*1000 % 1e6
select(timeout)
因为clock_nanosleep返回的时间比实际的时间长，select也有类似的问题，
即包间隔会偏大，pps和包速率会偏小。D-ITG应当根据首个包开始的时间计算理论发包时间，来设置发送等待时间，这样总体的平均速率是很稳定的。
http://traffic.comics.unina.it/software/ITG/download.php
make
sudo make install PREFIX=/usr/local

我们只需要D-ITG发出constant、exponential、pareto三种分布的流量
ITGSend的IDT参数：
-C <rate> 以rate速率发送constant流量，单位是pps
-E <mean_rate> 以rate的平均速率发送指数分布的流量，单位是pps
-V <shape> <scale> pareto分布 shape=1.5 pdf=\frac{\alpha x_m^{\alpha}}{x^{\alpha+1}}
x_m scale \alpha shape
均值为\frac{\alpha x_m}{\alpha-1}
\alpha=1.5时，均值为3*x_m

500Mbps=42459pps
ITGRecv
constant：
ITGSend -poll -a 10.0.7.1 -C 42459 -c 1472 -t 1000 -x /tmp/ditg/rx-constant.log
exponential：
ITGSend -poll -a 10.0.7.1 -E 42459 -c 1472 -t 1000 -x /tmp/ditg/rx-exponential.log
pareto：（第二个参数scale的单位是毫秒）
ITGSend -poll -a 10.0.7.1 -V 1.5 7.85e-3 -c 1472 -t 1000 -x /tmp/ditg/rx-pareto.log

查看log文件
ITGDec [filename]
#### IGI/PTR
make
./ptr-server
./ptr-client -n 60 -s 1472 -k 3 10.0.7.1
#### spruce
make
./spruce_rcv
./spruce_snd -h 10.0.7.1 -c 980M -n 100 -i 3000
#### pathload
./configure && make
./pathload_snd -i
./pathload_rcv -s 10.0.1.1 -t 30
#### assolo
./configure && make
./assolo_snd
./assolo_rcv
./assolo_run -S 10.0.1.1 -R 10.0.7.1 -u 1500 -t 30 -J 6 -a 3 -p 1472
mv \$(ls *.instbw) output.instbw

#### 对比实验
对象：BQR、Pathload、IGI/PTR、Spruce（实际、理论）、ASSOLO
变量：背景流量的速率、中断延迟、背景流量的分布
因变量/捕捉特征：测量时间（DAG）、流量开销（DAG）、精度（max-v或MRTG）
脚本效率与ssh的数量有关，ssh多的脚本一定快不起来。

#### 区间有限
因为owd处于0.5x-1.5x区间
它能测量的可用带宽为2mA-2n/3A
m为负载包/负载包+0.5检查包
n为负载包/负载包+检查包
比如A=50Mbps,m=2/3,n=1/2, 测量范围为1.33A-0.33A=16.7Mbps-66.7Mbps
实际可用带宽为950Mbps，则需要迭代很多次。

改进检查包：记开始发送负载包的时间为t1，最后一个负载包的时间为t2，目标可用带宽为A，对应恢复时间为x，检查包间隔为G
设最小检查包间隔为gmin，优化检查包的前10个包
区间t2+g,x-40G的长度为L，若L>11G，则进行优化：
在tleft,tright对应的A1,A2中间插入10个值，则第一个插值为10A1/11 + A2/11
第一个插值对应的t为tx；
如果tx-tleft>gmin，则将所有的插值作为实际时间；
如果tx-tleft<=gmin，则令tx=tleft+gmin，然后令tleft=tx，进行相同的操作。

#### 误差来源
owd
100 - 101 均为150以上
102-200均为0-5
但是最后10个的最大值为4,
所以算法得到的位置是7

后10个值太过集中，最大值小于实际值
我们使用阈值f=10us，使得f+min作为恢复标准

1-log stream 1, data[4]
cond2 false

#### bqr 算法
检查包数量只有上限

runWith(LN,G)

recoverFlag
最后一个单向延迟和首个单向延迟的差小于th1=100us，最后10个单向延迟的最大值和最小值差小于th2=50us
A_L,A_H,A_E
检查包中首个单向延迟低于最后10个单向延迟最大值的第一个包

getLN_G(A,q)
选取合适的负载包数量LN和检查包间隔G。

如果正确估计A_L,A_H，则真实的A与两者的差的百分比为p1=G/(x+G),p2=G/(x-G)
设q=G/x 则p1=q/(1+q) p2=q/(1-q)
常见取值
   q    p1     p2
0.1%  0.1%   0.1%
0.2%  0.2%   0.2%
0.5%  0.5%   0.5%
  1%    1%     1%
  2% 1.96%  2.04%
  5% 4.76%  5.26%
 10% 9.09% 11.11%

检查包间隔G影响精度。G越小越精确。我们观察到，当G超过1000us时，接收包时可能延迟60us左右，为了避免该现象，G<400us；负载包发送需要时间t，t和x间可能放不下50个G，如t=800us，x=1230-1845，希望在x的前面尽可能多地发包，在x的后面至少要测得10个恢复的单向延迟。G很小时，由于进程切换，发包精度会下降，加上接收端中断延迟的误差，可能导致定位恢复的包下表错误，因此不要太小。

负载包数量影响x的大小（恢复时间）和探测开销；负载包越少，恢复时间越短，开销越小，因此负载包越少越好。但是同时G=qx会变小，单向延迟的最大改变量变小，如果它和噪声相当，就会影响估计。所以：负载包在满足条件的前提下尽量最小。前提：G足够大，单向延迟变化量足够大。

令40< G<400, 100<=LN<=400,对A in [50,950]
LN=100,q=0.01,得到G，若G<40，则令G=40,计算LN。
A_E的计算：越简单越好->恢复的包前两个包延长，和均值的交点t_x，如果t_x超出t_L和t_H，则取(t_L+t_H)/2作为恢复时间。

#### bqr-optimization
2.22 因为10.0.0.0/16使用1Gbps的网卡，所以DAG不能捕捉接收端的包

n5->n1测出带宽大小B

ADR实验验证了，无论非紧链路背景流量如何改变，时间是不变的

在可用带宽为150Mbps时测量的很明显，但可用带宽较大时，恢复的下标在检查包的很前面，
设检查包间隔为G，实际恢复时间为x，负载包为P，perror(G,x)=G/x/(2+-G/x)
在1Gbps的可用带宽下，如果发100个包的恢复时间为x=1176us，G=200us时，perror=10%，绝对误差有100Mbps
为了减小误差，是减小G好还是增加负载包数量使得恢复时间增大好？
如果增加负载包，发1000个包，恢复时间为11760us=11ms，测量时间从20.8ms增加到28.8ms，包开销从287KB增加到1581KB
如果减小G，G=20us，x=1176us，测量时间从20.8ms减少到2.8ms。
后者包开销不变，测量时间更短，看起来更好。

#### bqr
2.04 检查包间隔固定200us，动态调整的是检查包的数量。好处是检查包（在清空队列后）不会受到中断延迟和长期空闲的影响；坏处是包开销翻倍了。

#### 去噪

空闲：如果包间隔大于1ms，无论是否关闭中断延迟，所有包都有概率被延迟60us！
IC对load阶段恒定的影响
IC对inspect阶段，若间隔低于64us则有影响，高于64us无影响

如果当前检查包间隔大于500us，则每次使用50us间隔的3个包

网卡收到包，等待t时间累积下一个包，n个包，以2-3us的间隔接收到。
第一个包在网卡接收到最后一个包后等待了t时间

3 2 10 11 14 3 4 13 18 22 2 21 2 22 2 27 2 29 2 3 28 2 2 30 2 35 2 3 2 32 2 2 37 2 2 39 3 2 2 38 3 2 42 3 2 3 42 2 2 2 45 2 2 2 46 2 3 2 2 48 2 3 2 2 3 58 2 2

设定阈值，gap大于阈值的时间戳作为准确时间戳，丢弃其余时间戳

最终的目的是定位单向延迟恢复的时间。
有两种判断方法：
单向延迟不再降低（包间隔）
单向延迟处于开始时的区间。开始时的单向延迟，需要对发送时间戳和接收时间戳去噪，得到单向延迟
发送时间戳由负载阶段和检查阶段组成，每个阶段估计一个平均包间隔即可。
接收时间戳由负载阶段和检查阶段组成，负载阶段必定触发中断延迟，但是由于理论上间隔是均匀的，我们估计平均包间隔即可；平均包间隔误差来自第一个中断延迟所延迟的包到达时间；
接收的检查阶段的包间隔如果大于1ms会产生很大误差，所以如果发送检查包间隔大于500us，则发送3个50us的系列包，使用最后一个包的时间；包间隔如果小于64us，会中断延迟，

发送检查包间隔
是否大于100us
是：是否小于500us 是：误差不大 否：发送3个50us间隔包，使用最后一个包的时间
否：有中断延迟

假设检查包间隔大于100us小于500us
检查包接收间隔约等于检查包发送间隔的第一个检查包下标
检查包数量：
负载包1500Mbps 100×1472B 785us
检查包100×1472B 间隔200us 785-20785

#### linux network optimization 关闭中断延迟
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
设置路由到服务器的带宽1Gbps
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

#### dagsnap 和 dagconvert
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
sysctl -w net.ipv4.tcp_wmem="4096 16777216 16777216"
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

#### 带宽测量方法
1. 变长分组
Pathchar，Pchar
2. 数据包对
Bprobe、Sprobe、Capprobe
3. SLoPS
Spruce,Pipechar,pathneck

#### 各种误差来源因素
Iperf3：设置UDP包大小，避免分包(UDP包拆分消耗CPU资源、增大丢包率)；设置pacing-timer 10us-100us

高速网卡：gso和tso。使用iperf3测量链路带宽时，用tcp能测至10000Mbps，tso降低了cpu的负载 (为什么gso对udp无效-没有显著降低cpu负载)
硬件时间戳支持：可能支持硬件时间戳，但不能每个包都获取硬件时间戳

应用层send：每次send至少需要c的时间，则最大探测速率为MTU+28/c，如果其间发生了进程切换，实际探测速率会更低；send只是将数据提交到skb中，实际需要等网卡发送

#### 6.22 exp9 pathload
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

#### 6.3 队列首部异常
数据分析
间隔均值72us左右。队列的第一个间隔特别小，在30-60us间
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

#### 5.28 试验结果
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
#### 5.25 试验结果
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
#### 5.20 首次考虑队列恢复和可用带宽的联系
探测方法：100*100的train，如何避免流量拥塞，每个train之间空开一段时间。改进：高可用带宽时等待间隔很短，测量很快；低可用带宽时，等待间隔大，One way delay恢复很慢，测量one way delay恢复速率。
客户端首尾间隔，服务器每个包收到的时间，保存在客户端的data目录下
最长用时=100*（等待间隔+测量时间），令测量包的平均速率为10Mbps，间隔T=9000*8*100/10=720000us=720ms，一次测量100s，总共10000s，
#### 5.19 机器学习方法
极大似然估计（多维、一维）
线性、lightgbm、xgboost、ANN、RNN

#### iperf发包原理：粒度pacing-timer
iperf定时执行任务：保存事件的时间，select等待这段时间。
预设的pacing-timer=1000us=1ms
#### 5.18 发现iperf3的粒度约100ms
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

#### 5.13 网卡软硬件时间戳
如果不停发包，硬件时间戳会有不可用的情况
如果发一个包，阻塞等时间戳，延迟200us
接收方一直只能接收软件时间戳，最小间隔4us

网卡提供的硬件时间戳总结：
1. 硬件时间戳(可能)比软件时间戳精确，但是不能连续获取，软件时间戳可以连续获取
2. 接收时只能获取软件时间戳，发送时可以获取硬件时间戳
3. 使用SO_TIMESTAMPING获取时间戳的好处：尽可能接近网卡发出/接收包的时间，并且内核获取时间开销小于用户态
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

#### 5.11 iperf udp的丢包和速率和缓冲区大小
iperf udp 速率100以上开始丢包
iperf3 -c ip -u -f m -b 500M -l 1472 -w 8K
包越大，cpu负载越小，丢包概率越大；缓冲区越大，丢包概率越大；
-w 在速率为500Mbps时设为8K即可，buffer过小达不到目标速率，buffer过大丢包率过大（为什么发包越快需要的buffer越大-进程切换开销）
先在链路带宽1000Mbps的情况下试验。
#### 5.10 tcpdump抓包命令
抓包命令
sudo tcpdump -i enp61s0f1 --time-stamp-precision=nano "src host 192.168.0.19 and dst host 192.168.1.21" -w igi.pcap
sudo tcpdump -i enp61s0f1 --time-stamp-precision=nano "src host 192.168.0.19 and dst host 192.168.1.21" -w iperf.pcap
sudo tcpdump -i enp61s0f1 --time-stamp-precision=nano "src host 192.168.0.19 and dst host 192.168.1.21" -w iperfudp.pcap
udp模式需要对高带宽做出更改：受CPU限制，还是高丢包率？
大段卸载（Large Segment Offload，简称LSO）是一种在高带宽网络中用于减少CPU使用率和增加发送吞吐量的技术，该技术通过网卡对过大的数据分段，而无需协议栈参与。该技术还有一些别称，当应用于TCP时被称为TCP段卸载(TSO)
iperf3在万兆网络中实验时，TCP能达到万兆带宽，UDP只能达到3000-5000Mbps
当发送包的数量越多，cpu负载越重。在发送包大小不变时，发送速率越大，cpu负载越大。
#### 5.7 机器学习效果
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

##### 5.6 混杂
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

加入link值，
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
探测包：
每次发送两个大小为MTU的UDP包，包的间隔为单个包在瓶颈链路上通过的时间；然后休息一段时间，发送下一个包对；
设置间隔的目的：使两个包间所有背景流量都进入队列，这样可以累积背景流量包；
设置休息间隔的目的：使总体的发包速率低于瓶颈链路速率，瓶颈链路的缓冲区不会溢出。

问题1：clock_nanosleep不能精确控制发包间隔，比设置的值偏大。设置240us，实际100轮平均为346us，最小-最大区间为313-393us。
如果使用igi-ptr的循环进行间隔控制，实际间隔平均700-800us，最小最大区间260-1000us
发包间隔不精确的后果：若太大，部分两个包达到间的背景流量可能离开队列，

问题2：select是否更精确

问题3：在gin小于gB的情况下，背景流量是离散的包，因此gout-gin是离散的值，只能给出速率的区间估计

问题4：只能估计在第一个包到达瓶颈链路入口至第二个包到达瓶颈链路入口期间的背景流量；
如果背景流量的爆发性很强，包集中，有可能高估（探测集中在爆发区间）或低估（探测集中在非爆发期间）背景流量。

问题5：在入口使用tc限速没有意义；

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