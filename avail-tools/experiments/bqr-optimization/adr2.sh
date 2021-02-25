# 流量设置：一项为800Mbps，其他两项为(0 200 400 600)
# 实验验证：恢复时间与其他两项取值无关
# node2->node3 xMbps
# node3->node4 yMbps
# node4->node5 zMbps
# 低可用带宽800Mbps
# 取值 800 (0 200 400 600)
# 实验     x   y   z loadRate recovertime
#  61   800   0   0     1500      7500us
#  76   800 600 600
#  77     0 800   0
#  92   600 800 600
#  93     0   0 800
# 108   600 600 800
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
	for ((i_=2;i_<=5;i_++));do
		ssh ubuntu${i_}@192.168.66.$((i_+15)) "${stopCmd}"
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
range=(0 200 400 600)
main(){
	mkdir -p ${dirname}
	begin=$(date)
	# 61-108 当关闭中断延迟时
	ic=0
	startValue=61
	for ((i=0;i<4;i++));do
		for ((j=0;j<4;j++));do
			number=$((${startValue}+$i*4+$j))
			run ${ic} 800 ${range[$i]} ${range[$j]} ${dirname}/${number}.txt
		done
	done
	for ((i=0;i<4;i++));do
		for ((j=0;j<4;j++));do
			number=$((${startValue}+16+$i*4+$j))
			run ${ic} ${range[$i]} 800 ${range[$j]} ${dirname}/${number}.txt
		done
	done
	for ((i=0;i<4;i++));do
		for ((j=0;j<4;j++));do
			number=$((${startValue}+32+$i*4+$j))
			run ${ic} ${range[$i]} ${range[$j]} 800 ${dirname}/${number}.txt
		done
	done
	# 109-156 开启终端延迟
	ic=1
	startValue=109
	for ((i=0;i<4;i++));do
		for ((j=0;j<4;j++));do
			number=$((${startValue}+$i*4+$j))
			run ${ic} 800 ${range[$i]} ${range[$j]} ${dirname}/${number}.txt
		done
	done
	for ((i=0;i<4;i++));do
		for ((j=0;j<4;j++));do
			number=$((${startValue}+16+$i*4+$j))
			run ${ic} ${range[$i]} 800 ${range[$j]} ${dirname}/${number}.txt
		done
	done
	for ((i=0;i<4;i++));do
		for ((j=0;j<4;j++));do
			number=$((${startValue}+32+$i*4+$j))
			run ${ic} ${range[$i]} ${range[$j]} 800 ${dirname}/${number}.txt
		done
	done
	end=$(date)
	printf "${begin} -> ${end}\n"
	setIC 0
}
main $@