# 在DAG机器上执行本脚本
# 本实验证明，在三跳情况下，BQR的清空时间只与紧链路可用带宽有关，不随非紧链路可用带宽/背景流量变化。
# node2->node3 xMbps
# node3->node4 yMbps
# node4->node5 zMbps
# 低可用带宽800Mbps流量；中可用带宽400Mbps；高可用带宽200Mbps
# 实验     x   y   z loadRate recovertime
# 实验41 800   0   0     1500      7500us
# 实验42 800 700   0     1500      7500us
# 实验43 800   0 700     1500      7500us
# 实验44 800 700 700     1500      7500us
# 实验45   0 800   0     1500      7500us
# 实验46 700 800   0     1500      7500us
# 实验47   0 800 700     1500      7500us
# 实验48 700 800 700     1500      7500us
# 实验49   0   0 800     1500      7500us
# 实验50 700   0 800     1500      7500us
# 实验51   0 700 800     1500      7500us
# 实验52 700 700 800     1500      7500us
setIC(){
	ic=$1
	ssh ubuntu5@192.168.66.20 "sudo ethtool -C ens1f1 rx-usecs ${ic}" 1>/dev/null 2>&1
}
stopCmd="mkdir -p /tmp/iperf; pkill iperf3"
rxCmd="nohup iperf3 -sfm -V -i5 -A 0 1>/tmp/iperf/rx.log 2>/tmp/iperf/rx.error &"
setIperf(){
	x=$1
	y=$2
	z=$3
	# rx
	ssh ubuntu5@192.168.66.20 "${stopCmd}; ${rxCmd}"
	ssh ubuntu4@192.168.66.19 "${stopCmd}; ${rxCmd}"
	ssh ubuntu3@192.168.66.18 "${stopCmd}; ${rxCmd}"
	ssh ubuntu2@192.168.66.17 "${stopCmd}"
	# tx
	if [[ ${z} -ne 0 ]];then
		ssh ubuntu4@192.168.66.19 "nohup iperf3 -c 10.0.7.1 -ub ${z}M --pacing-timer 0 -l 1472 -fm -t 3600 -A 1 1>/tmp/iperf/tx.log 2>/tmp/iperf/tx.error &" 1>/dev/null
	fi
	if [[ ${y} -ne 0 ]];then
		ssh ubuntu3@192.168.66.18 "nohup iperf3 -c 10.0.6.1 -ub ${y}M --pacing-timer 0 -l 1472 -fm -t 3600 -A 1 1>/tmp/iperf/tx.log 2>/tmp/iperf/tx.error &" 1>/dev/null
	fi
	if [[ ${x} -ne 0 ]];then
		ssh ubuntu2@192.168.66.17 "nohup iperf3 -c 10.0.4.1 -ub ${x}M --pacing-timer 0 -l 1472 -fm -t 3600 -A 1 1>/tmp/iperf/tx.log 2>/tmp/iperf/tx.error &" 1>/dev/null
	fi
}
stopIperf(){
	for ((i=2;i<=5;i++));do
		ssh ubuntu${i}@192.168.66.$((i+15)) "${stopCmd}"
	done
}
setBQR(){
	ssh ubuntu5@192.168.66.20 "pkill recv-main; mkdir -p /tmp/bqr; rm -f /tmp/bqr/*; nohup /home/ubuntu5/abw-project/avail-tools/bqr/send-recv-module/build/recv-main --timestamp /tmp/bqr/timestamp.txt --result /tmp/bqr/result.txt --log /tmp/bqr/log.txt --polling 1 --busy-poll -1 --once 1>/tmp/bqr/rx.log 2>&1 &" 1>/dev/null
	ssh ubuntu1@192.168.66.16 "pkill send-main; mkdir -p /tmp/bqr; rm -f /tmp/bqr/*; nohup /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 1500 --loadSize 1472 --inspectSize 1472 --loadNumber 100 --inspectNumber 100 --inspectJumbo 1 --repeatNumber 1 --retryNumber 1 --preheatNumber 10 --streamGap 100 --trainGap 100 --preheatGap 100 --dest 10.0.7.1 --inspectGap 200 --loadInspectGap 200 --jumboGap 50 --noUpdate 1 1>/tmp/bqr/tx.log 2>&1 &" 1>/dev/null
}
fetchAndStop(){
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/timestamp.txt ${1} 1>/dev/null
	ssh ubuntu5@192.168.66.20 "pkill recv-main"
	ssh ubuntu1@192.168.66.16 "pkill send-main"
}
run(){
	printf "run $*\n"
	ic=$1
	x=$2
	y=$3
	z=$4
	bqrTimestamp=$5
	setIC ${ic}
	setIperf ${x} ${y} ${z}
	setBQR
	sleep 3s
	fetchAndStop ${bqrTimestamp}
	stopIperf
}
bpf="src host 10.0.1.1 and dst host 10.0.7.1 and udp and len>=1400"
dirname="/home/ubuntu6/data/bqr-optimization"
main(){
	mkdir -p ${dirname}
	begin=$(date)
	run 0 800   0   0 ${dirname}/41.txt
	run 0 800 700   0 ${dirname}/42.txt
	run 0 800   0 700 ${dirname}/43.txt
	run 0 800 700 700 ${dirname}/44.txt
	run 0   0 800   0 ${dirname}/45.txt
	run 0 700 800   0 ${dirname}/46.txt
	run 0   0 800 700 ${dirname}/47.txt
	run 0 700 800 700 ${dirname}/48.txt
	run 0   0   0 800 ${dirname}/49.txt
	run 0 700   0 800 ${dirname}/50.txt
	run 0   0 700 800 ${dirname}/51.txt
	run 0 700 700 800 ${dirname}/52.txt
	end=$(date)
	printf "${begin} -> ${end}\n"
	setIC 0
}
main $@