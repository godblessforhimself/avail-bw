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