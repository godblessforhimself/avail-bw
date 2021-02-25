# 测量1Gbps的实际带宽大小
# 因为只有10Gbps的光纤能使用DAG，使用iperf3从node5向node1发送连续的UDP包
# 问题：当初只接了正向的两个端口，反向的端口不能使用
# 跳过本实验
stopCmd="mkdir -p /tmp/iperf; pkill iperf3"
rxCmd="nohup iperf3 -sfm -V -i5 -A 0 1>/tmp/iperf/rx.log 2>/tmp/iperf/rx.error &"
txCmd="nohup iperf3 -c 10.0.1.1 -ub 0 --pacing-timer 0 -l 1472 -i5 -fm -t 3600 -A 1 1>/tmp/iperf/tx.log 2>/tmp/iperf/tx.error &"
setIperf(){
	ssh ubuntu1@192.168.66.16 "${stopCmd}; ${rxCmd}"
	ssh ubuntu5@192.168.66.20 "${stopCmd}; ${txCmd}"
}
stopIperf(){
	ssh ubuntu1@192.168.66.16 "${stopCmd}"
	ssh ubuntu5@192.168.66.20 "${stopCmd}"
}
setDAG(){
	time=$1
	mkdir -p /tmp/dag
	sudo dagsnap -d0 -s ${time} -o /tmp/dag/dag.erf 1>/tmp/dag/dagsnap.log 2>/tmp/dag/dagsnap.error &
	pid=$!
	echo ${pid}
}
waitDAG(){
	timeout $1 tail -f /dev/null --pid=$2 1>/dev/null
	sudo dagconvert -T erf:pcap -i /tmp/dag/dag.erf -b "src host 10.0.7.1 and dst host 10.0.1.1 and udp and len>=1400" -f a -o /tmp/dag/dag.pcap 1>/dev/null 2>/tmp/dag/dagconvert.log
	tshark -r /tmp/dag/dag.pcap -Tfields -e frame.time_epoch -e frame.len 1>${5}
}
main(){
	setIperf
	setDAG
	waitDAG
	stopIperf
}
main $@