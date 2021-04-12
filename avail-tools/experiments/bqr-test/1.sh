# 测试多个速率

# node2->node3 xMbps
# node3->node4 yMbps
# node4->node5 zMbps
#
#     x    y    z    A
#     0    0    0  957
#   200  200  200  757
#   400  400  400  557
#   600  600  600  357
#   800  800  800  157
# 0 900 100

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
	ssh ubuntu1@192.168.66.16 "pkill send-main; mkdir -p /tmp/bqr; rm -f /tmp/bqr/*; /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 1500 --loadSize 1472 --inspectSize 1472 --loadNumber 100 --inspectNumber 100 --inspectGap 350 --loadInspectGap 40 --repeatNumber 10 --retryNumber 1 --preheatNumber 0 --streamGap 1000 --trainGap 100 --dest 10.0.7.1 --noUpdate 0 1>/tmp/bqr/tx.log 2>&1" 1>/dev/null
}
fetchAndStop(){
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/timestamp.txt ${1} 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/log.txt ${2} 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/result.txt ${3} 1>/dev/null
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
	logFile=$6
	resultFile=$7
	setIC ${ic}
	setIperf ${x} ${y} ${z}
	setBQR
	fetchAndStop ${bqrTimestamp} ${logFile} ${resultFile}
	stopIperf
}
bpf="src host 10.0.1.1 and dst host 10.0.7.1 and udp and len>=1400"
dirname="/home/ubuntu6/data/bqr-test"
rates=($(seq 0 100 900))
main(){
	mkdir -p ${dirname}
	begin=$(date)
	# 1-10
	for ((i=0;i<${#rates[@]};i++));do
		rate=${rates[$i]}
		label=$((i+${#rates[@]}))
		run 0 $rate $rate $rate ${dirname}/${i}-time ${dirname}/${i}-log ${dirname}/${i}-result
		run 1 $rate $rate $rate ${dirname}/${label}-time ${dirname}/${label}-log ${dirname}/${label}-result
	done
	end=$(date)
	printf "${begin} -> ${end}\n"
	setIC 0
}
main $@