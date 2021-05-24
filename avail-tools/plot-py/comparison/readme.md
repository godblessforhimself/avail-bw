##### exp1
带宽：1Gbps
方法：BQR/ASSOLO/PTR/pathload/spruce
度量：AbsPerror, PacketOverhead, MeanQueueLength, MaxQueueLength, Time

##### exp2
在两跳1Gbps，第三跳10Gbps下使用DAG时间戳验证spruce的效果
前两跳的背景流量可变，第三跳不设流量

##### exp3
第一、三跳为1Gbps，第二跳为100Mbps，运行BQR/ASSOLO/PTR/pathload

##### exp4
中断延迟

##### exp5
在node2上使用tcpreplay向node5以指定速率发送背景流量
运行BQR并使用DAG捕捉实际流量

##### exp6
node2向node5使用tcpreplay发送流量，不运行测量
使用DAG捕捉流量

##### exp7
tcpreplay发送多组流量，进行多组测试

#### exp8
draw1.py ASSOLO测量tcpreplay流量效果

#### exp9
draw1.py 对ip4.len分析不同时间单位下的速率、速率的CDF、包大小CDF
draw2.py BQR在千兆、万兆网络中以1500B和9000B发包的单向延迟曲线

#### exp10
draw1.py BQR在万兆网络中，iperf3作背景流量的测量情况

#### exp11
draw1.py BQR在千兆网络中tcpreplay播放bigFlows和caida流量的测量
draw2.py 增加时长到90秒。