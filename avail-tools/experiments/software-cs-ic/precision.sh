# part 1: illustrate the precision of software traffic generator
# tool: iperf3 bqr
# target rate: 10Mbps, 100Mbps, 1000Mbps
# repeat,point: 10, 1000
# no cross traffic, no interrupt coalescing
# show: histogram with MSE
# conclusion: precision decreases at higher rate, but acceptable

# DAG
# /tmp/dag.erf
# /tmp/dag.pcap
# 
rates=(10 100 500 800)
times=(5 3 3 3)
waitTime=5
runIperf3(){
	rate=$1; point=$2; t=$3; waitTime=$4; sendFile=$5; recvFile=$6; bpf=$7
	bytes=$((1472*${point}))
	sudo dagsnap -d0 -s $t -o /tmp/dag.erf 1>/dev/null &
	pid=$!
	ssh ubuntu5@192.168.66.20 "pkill iperf3; nohup iperf3 -sfm -i0 -V 1>/tmp/iperf3.log 2>&1 &" 1>/dev/null
	ssh ubuntu1@192.168.66.16 "pkill iperf3; nohup iperf3 -fM -c 10.0.7.1 -ub ${rate}M -l 1472 -i0 --pacing-timer 0 -n ${bytes} 1>/tmp/iperf3.log 2>&1 &" 1>/dev/null
	timeout ${waitTime} tail -f /dev/null --pid=${pid} 1>/dev/null
	sudo dagconvert -T erf:pcap -i /tmp/dag.erf -b "${bpf}" -f a -o /tmp/dag.pcap 1>/dev/null 2>/tmp/dagconvert.log &&\
	tshark -r /tmp/dag.pcap -Tfields -e frame.time_epoch -e frame.len 1>${sendFile}
	sudo dagconvert -T erf:pcap -i /tmp/dag.erf -b "${bpf}" -f c -o /tmp/dag.pcap 1>/dev/null 2>/tmp/dagconvert.log &&\
	tshark -r /tmp/dag.pcap -Tfields -e frame.time_epoch -e frame.len 1>${recvFile}
	ssh ubuntu5@192.168.66.20 "pkill iperf3"
	ssh ubuntu1@192.168.66.16 "pkill iperf3"
}
main(){
	if [[ $# -eq 0 ]];then
		dirname="/home/ubuntu6/data/iperf3-exp1"
	else
		dirname=$1
	fi
	rm -rf $dirname
	mkdir -p $dirname
	point=1000
	bpf="src host 10.0.1.1 and dst host 10.0.7.1 and udp and len>=1400"
	begin=$(date)
	for ((i=0;i<${#rates[@]};i++));do
		for ((j=1;j<=10;j++));do
			rate=${rates[i]}
			sendFile="${dirname}/rate-${rate}Mbps-${j}-send"
			recvFile="${dirname}/rate-${rate}Mbps-${j}-recv"
			runIperf3 ${rate} ${point} ${times[i]} ${waitTime} ${sendFile} ${recvFile} "${bpf}"
		done
	done
	end=$(date)
	printf "${begin}->${end}\n"
}
main $@