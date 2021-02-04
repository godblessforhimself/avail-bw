# part 2: the influence of CS and interrupt coalescing on constant rate train
# tool: bqr
# target rate: 10-800
# repeat,point: 10, 1000
# interrupt coalescing: off, on
# show: histogram with MSE
# show: send, recv(ic off), recv(ic on)
# deep analysis
# conclusion: there is pattern, IC adds error, we can reduce noise
rates=(10 50 100 200 500 800)
times=(15 5 2 2 2 2)
waitTime=16
runBqr(){
	read -r rate point repeat t waitTime sendFile recvFile bqrFile bpf <<<$@
	ssh ubuntu5@192.168.66.20 "pkill recv-main; rm -f /tmp/bqr/timestamp.txt; nohup /home/ubuntu5/abw-project/avail-tools/bqr/send-recv-module/build/recv-main --timestamp /tmp/bqr/timestamp.txt --result /tmp/bqr/result.txt --log /tmp/bqr/log.txt --polling 1 --busy-poll -1 1>/tmp/bqr/recv.log 2>&1 &" 1>/dev/null
	sudo dagsnap -d0 -s $t -o /tmp/dag.erf 1>/dev/null &
	pid=$!
	ssh ubuntu1@192.168.66.16 "pkill send-main; nohup /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate ${rate} --loadSize 1472 --inspectSize 1472 --loadNumber ${point} --inspectNumber 0 --inspectJumbo 0 --repeatNumber ${repeat} --retryNumber 1 --preheatNumber 0 --duration 0 --streamGap 10000 --trainGap 0 --preheatGap 0 --dest 10.0.7.1 1>/tmp/bqr/send.log 2>&1 &" 1>/dev/null
	timeout ${waitTime} tail -f /dev/null --pid=${pid} 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/timestamp.txt ${bqrFile} 1>/dev/null
	ssh ubuntu5@192.168.66.20 "pkill recv-main; rm -f /tmp/bqr/timestamp.txt"
	ssh ubuntu1@192.168.66.16 "pkill send-main"
	sudo dagconvert -T erf:pcap -i /tmp/dag.erf -b "${bpf}" -f a -o /tmp/dag.pcap 1>/dev/null 2>/tmp/dagconvert.log &&\
	tshark -r /tmp/dag.pcap -Tfields -e frame.time_epoch -e frame.len 1>${sendFile}
	sudo dagconvert -T erf:pcap -i /tmp/dag.erf -b "${bpf}" -f c -o /tmp/dag.pcap 1>/dev/null 2>/tmp/dagconvert.log &&\
	tshark -r /tmp/dag.pcap -Tfields -e frame.time_epoch -e frame.len 1>${recvFile}
}
main(){
	if [[ $# -eq 0 ]];then
		dirname="/home/ubuntu6/data/bqr-constant"
	else
		dirname=$1
	fi
	rm -rf $dirname
	mkdir -p $dirname
	point=1000
	repeat=10
	ics=(0 1)
	bpf="src host 10.0.1.1 and dst host 10.0.7.1 and udp and len>=1400"
	begin=$(date)
	ssh ubuntu5@192.168.66.20 "mkdir -p /tmp/bqr; rm -f /tmp/bqr/*"
	ssh ubuntu1@192.168.66.16 "mkdir -p /tmp/bqr; rm -f /tmp/bqr/*"
	for ic in ${ics[@]};do
		ssh ubuntu5@192.168.66.20 "sudo ethtool -C ens1f1 rx-usecs ${ic}" 1>/dev/null
		for ((i=0;i<${#rates[@]};i++));do
			rate=${rates[i]}
			sendFile="${dirname}/rate-${rate}Mbps-IC-${ic}-send"
			recvFile="${dirname}/rate-${rate}Mbps-IC-${ic}-recv"
			bqrFile="${dirname}/rate-${rate}Mbps-IC-${ic}-bqr"
			runBqr ${rate} ${point} ${repeat} ${times[i]} ${waitTime} ${sendFile} ${recvFile} ${bqrFile} "${bpf}"
		done
	done
	end=$(date)
	ssh ubuntu5@192.168.66.20 "sudo ethtool -C ens1f1 rx-usecs 0" 1>/dev/null
	printf "${begin}->${end}\n"
}
main $@