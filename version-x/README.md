# 问题分析

load size 与 inspect size 不相同时，最小单向延迟是不相同的。
若采用相同，inspect packet会对路径产生影响。
若load packet中以1：10嵌入inspect packet，亦可

发送速率为vin，接收速率为vout，如果vin>vout，可知可用带宽A< vout
如果vin=vout，可知可用带宽A>vout
如果vin< vout，需要定位原因

如果inspect owd一直在增加，可知可用带宽A< inspect rate
如果inspect owd在减少仍未恢复，可知可用带宽A< P/t
如果inspect owd在减少且恢复，可知可用带宽 v1< A< v2

如何更准确的测量A：更小的测量间隔

因为恢复的前一个检查包的单向延迟非常接近恢复单向延迟，被识别成已经恢复，导致估计的恢复时间提前了一个检查点。
# deploy-tools/

deploy-run-fetch.sh
run quick-deploy.sh, quick-run.sh , fetch-output.sh

deploy-dag.sh
send version-x to dag

deploy-sender-receiver.sh
send version-x from dag to sender and receiver, and compile them using cmake and make

quick-deploy.sh
call deploy-dag.sh and deploy-sender-receiver.sh

sender.sh
run send-main at sender

receiver.sh
run receive-main at receiver


# control-module/

dag-run.sh
setup dag before running receive-main and sender-main

quick-run.sh
run receive-main and send-main

fetch-tools

fetch-timestamp.sh [filename]
use rsync to move output.txt at receiver to dag, then to local data.

fetch-data.sh [user filename] [in filename] [out filename]
transfer timestamp file from receiver, dag capture file from DAG to local data.

quickrun-fetch.sh [rate] [data filename]

# analyse-tools

> python analyse-tools/userspace-tool.py --file [filename] [--save-image] [--show-image] [--interact]

# Time Sync

> sudo ntpdate time.nist.gov

client$ iptables -I INPUT 1 --src 192.168.2.0/24 -j ACCEPT
client$ iptables -t raw -I PREROUTING 1 --src 192.168.2.0/24 -j NOTRACK
server$ iptables -I INPUT 1 --src 192.168.2.0/24 -j ACCEPT
server$ iptables -t raw -I PREROUTING 1 --src 192.168.2.0/24 -j NOTRACK