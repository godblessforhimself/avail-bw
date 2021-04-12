# 使用DAG捕捉Iperf3的constant流量，检查其间隔
runIperf3(){
	rate="$1"
	mkdir -p /tmp/dag
	ssh ubuntu5@192.168.66.20 "pkill iperf3; nohup iperf3 -sfm -i0 -V 1>/tmp/iperf3.log 2>&1 &"
	ssh ubuntu1@192.168.66.16 "pkill iperf3; nohup iperf3 -fM -c 10.0.7.1 -ub ${rate}M -l 1472 -i0 --pacing-timer 0 -t 3600 1>/tmp/iperf3.log 2>&1 &"
	sudo dagsnap -d0 -s 10 -o /tmp/dag/dag.erf 1>/tmp/dag/dagsnap.log 2>&1 &
	pid=$!
	timeout 11 tail -f /dev/null --pid=${pid} 1>/dev/null
	ssh ubuntu5@192.168.66.20 "pkill iperf3"
	ssh ubuntu1@192.168.66.16 "pkill iperf3"
	sudo dagconvert -T erf:pcap -i /tmp/dag/dag.erf -b "src host 10.0.1.1 and dst host 10.0.7.1 and udp and len>=1400" -f a -o /tmp/dag/dag.pcap 1>/tmp/dag/dagconvert.log 2>&1
	dirname="/home/ubuntu6/data/iperf3"
	mkdir -p ${dirname}
	tshark -r /tmp/dag/dag.pcap -Tfields -e frame.time_epoch -e frame.len 1>${dirname}/traffic
}
main(){
	runIperf3 500
}
main $@