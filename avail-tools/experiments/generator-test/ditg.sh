# 使用DAG捕捉DITG的constant流量，检查其间隔
runDITG(){
	mkdir -p /tmp/dag
	ssh ubuntu5@192.168.66.20 "pkill ITGRecv; nohup ITGRecv 1>/tmp/ditg/rx.log 2>&1 &"
	ssh ubuntu1@192.168.66.16 "pkill ITGSend; nohup ITGSend -poll -a 10.0.7.1 -C 42459.239130434784 -c 1472 -t 100000 -x /tmp/ditg/tmp.log 1>/tmp/ditg/tx.log 2>&1 &"
	sudo dagsnap -d0 -s 10 -o /tmp/dag/dag.erf 1>/tmp/dag/dagsnap.log 2>&1 &
	pid=$!
	timeout 11 tail -f /dev/null --pid=${pid} 1>/dev/null
	ssh ubuntu1@192.168.66.16 "pkill ITGSend"
	ssh ubuntu5@192.168.66.20 "pkill ITGRecv"
	sudo dagconvert -T erf:pcap -i /tmp/dag/dag.erf -b "src host 10.0.1.1 and dst host 10.0.7.1 and udp and len>=1400" -f a -o /tmp/dag/dag.pcap 1>/tmp/dag/dagconvert.log 2>&1
	dirname="/home/ubuntu6/data/ditg"
	mkdir -p ${dirname}
	tshark -r /tmp/dag/dag.pcap -Tfields -e frame.time_epoch -e frame.len 1>${dirname}/traffic
}
main(){
	runDITG
}
main $@