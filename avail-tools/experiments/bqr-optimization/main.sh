# 在DAG机器上执行本脚本
# 测量三跳均存在流量时，时间戳的特征
# 设置接收网卡的中断延迟
# 设置iperf3流量x y z
# 使用BQR发包
# node2->node3 xMbps
# node3->node4 yMbps
# node4->node5 zMbps
# 实验 x y z loadRate loadNumber recovertime inspect
# 实验1 800 700 600 1500 100 7500us 1000 15000 200
# 实验2 600 800 700 1500 100 7500us 1000 15000 200
# 实验3 600 700 800 1500 100 7500us 1000 15000 200
# 每次时长15ms，等待3秒以防DAG延迟
# 1472B*100/157Mbps=7500us
# 1472B*100/1500Mbps=785us

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
	run 0 800 700 600 ${dirname}/1.txt
	run 0 600 800 700 ${dirname}/2.txt
	run 0 600 700 800 ${dirname}/3.txt
	run 1 800 700 600 ${dirname}/4.txt
	run 1 600 800 700 ${dirname}/5.txt
	run 1 600 700 800 ${dirname}/6.txt
	end=$(date)
	printf "${begin} -> ${end}\n"
	setIC 0
}
main $@