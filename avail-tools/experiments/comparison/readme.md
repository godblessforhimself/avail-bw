##### exp1
在三跳1Gbps带宽下运行BQR/ASSOLO/PTR/pathload/spruce

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

##### exp8
tcpreplay发送多组流量，进行多组测试
使用ASSOLO测量

##### exp9
小MTU，1Gbps链路
小MTU，10Gbps链路
大MTU，10Gbps链路
大MTU，10Gbps链路，高速率
无背景流量
当链路带宽是10Gbps时，单向延迟在100微秒的范围内波动，而且存在突然降低的现象。

##### exp10
大MTU，10Gbps链路，高探测速率
使用iperf3产生背景流量
BQR在9000B的负载包数量大于50，以9500Mbps发送，且背景流量速率为5/7/9Gbps，有持续丢包的情况
持续丢包是指，无论BQR重发多少轮，一直无法成功。
提高BQR的最小带宽50Mbps-1000Mbps，可以减小测量时间。

##### exp11
在1Gbps下，使用tcpreplay发送CAIDA/bigFlows，以三种不同速率发送。
使用BQR测量，绘制以秒为单位的曲线。