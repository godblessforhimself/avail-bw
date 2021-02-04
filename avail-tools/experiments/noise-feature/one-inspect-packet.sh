# 测试只用单个检查包的接收和真实时间戳误差
# recv-main --timestamp /tmp/bqr/timestamp.txt --result /tmp/bqr/result.txt --log /tmp/bqr/log.txt --polling 1 --busy-poll -1
# time ./send-main --loadRate 1500 --loadSize 1472 --inspectSize 1472 --loadNumber 100 --inspectNumber 100 --inspectJumbo 1 --repeatNumber 10 --retryNumber 1 --preheatNumber 0 --duration 200000 --streamGap 10000 --trainGap 0 --preheatGap 0 --dest 10.0.7.1 --noUpdate 1
runBqr() {
	read -r t loadNumber inspectNumber repeat duration waitTime bqrFile sendFile recvFile bpf <<<$@
	ssh ubuntu5@192.168.66.20 "pkill recv-main; rm -f /tmp/bqr/timestamp.txt; nohup /home/ubuntu5/abw-project/avail-tools/bqr/send-recv-module/build/recv-main --timestamp /tmp/bqr/timestamp.txt --result /tmp/bqr/result.txt --log /tmp/bqr/log.txt --polling 1 --busy-poll -1 1>/tmp/bqr/recv.log 2>&1 &" 1>/dev/null
	sudo dagsnap -d0 -s $t -o /tmp/dag.erf 1>/dev/null &
	pid=$!
	ssh ubuntu1@192.168.66.16 "pkill send-main; nohup /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 1500 --loadSize 1472 --inspectSize 1472 --loadNumber ${loadNumber} --inspectNumber ${inspectNumber} --inspectJumbo 1 --repeatNumber ${repeat} --retryNumber 1 --preheatNumber 0 --duration ${duration} --streamGap 10000 --trainGap 0 --preheatGap 0 --dest 10.0.7.1 --noUpdate 1 1>/tmp/bqr/send.log 2>&1 &" 1>/dev/null
	timeout ${waitTime} tail -f /dev/null --pid=${pid} 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/timestamp.txt ${bqrFile} 1>/dev/null
	ssh ubuntu5@192.168.66.20 "pkill recv-main; rm -f /tmp/bqr/timestamp.txt"
	ssh ubuntu1@192.168.66.16 "pkill send-main"
	sudo dagconvert -T erf:pcap -i /tmp/dag.erf -b "${bpf}" -f a -o /tmp/dag.pcap 1>/dev/null 2>/tmp/dagconvert.log &&\
	tshark -r /tmp/dag.pcap -Tfields -e frame.time_epoch -e frame.len 1>${sendFile}
	sudo dagconvert -T erf:pcap -i /tmp/dag.erf -b "${bpf}" -f c -o /tmp/dag.pcap 1>/dev/null 2>/tmp/dagconvert.log &&\
	tshark -r /tmp/dag.pcap -Tfields -e frame.time_epoch -e frame.len 1>${recvFile}
}
main() {
	dirname='/home/ubuntu6/data/noise/one-inspect-packet'
	rm -rf ${dirname}
	mkdir -p ${dirname}
	loadNumber=100
	inspectNumber=100
	repeat=3
	ics=(0 1)
	t=5
	waitTime=5
	bpf="src host 10.0.1.1 and dst host 10.0.7.1 and udp and len>=1400"
	durations=$(seq 2000 4000 200000)
	ssh ubuntu5@192.168.66.20 "mkdir -p /tmp/bqr; rm -f /tmp/bqr/*"
	ssh ubuntu1@192.168.66.16 "mkdir -p /tmp/bqr; rm -f /tmp/bqr/*"
	begin=$(date)
	for ic in ${ics[@]};do
		ssh ubuntu5@192.168.66.20 "sudo ethtool -C ens1f1 rx-usecs ${ic}" 1>/dev/null
		for duration in ${durations[@]};do
			printf "${duration}\n"
			prefix="${dirname}/duration-${duration}-IC-${ic}"
			bqrFile="${prefix}-bqr"
			sendFile="${prefix}-send"
			recvFile="${prefix}-recv"
			runBqr $t $loadNumber $inspectNumber $repeat $duration $waitTime $bqrFile $sendFile $recvFile "${bpf}"
		done
	done
	end=$(date)
	printf "${begin}->${end}\n"
	ssh ubuntu5@192.168.66.20 "sudo ethtool -C ens1f1 rx-usecs 0" 1>/dev/null
}
main $@