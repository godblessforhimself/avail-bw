# 使用8972字节 10Gbps
stopCmd="pkill iperf3"
rxCmd="nohup iperf3 -sfm -V -i5 -A 0 1>/tmp/iperf/rx.log 2>/tmp/iperf/rx.error &"
setIperf(){
	local x=$1
	ssh ubuntu3@192.168.66.18 "${stopCmd}; ${rxCmd}"
	if [[ ${x} -ne 0 ]];then
		ssh ubuntu2@192.168.66.17 "${stopCmd}; nohup iperf3 -c 10.1.4.1 -ub ${x}M --pacing-timer 0 -l 8972 -fm -t 36000 -A 1 1>/tmp/iperf/tx.log 2>/tmp/iperf/tx.error &"
	else
		ssh ubuntu2@192.168.66.17 "${stopCmd}"
	fi
}
stopIperf(){
	local i
	for ((i=2;i<=3;i++));do
		ssh ubuntu${i}@192.168.66.$((i+15)) "${stopCmd}"
	done
}
setBQR(){
	echo "setBQR $1"
	ssh ubuntu5@192.168.66.20 "pkill recv-main; nohup /home/ubuntu5/abw-project/avail-tools/bqr/send-recv-module/build/recv-main --timestamp /tmp/bqr/timestamp.txt --result /tmp/bqr/result.txt --log /tmp/bqr/log.txt --polling 1 --busy-poll -1 --once --thres1 100 --thres2 40 --thres3 20 1>/tmp/bqr/rx.log 2>&1 &"
	ssh ubuntu1@192.168.66.16 "pkill send-main; nohup /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 9500 --loadSize 8972 --inspectSize 8972 --loadNumber $1 --inspectNumber 100 --repeatNumber 10 --streamGap 10000 --dest 10.1.7.1 --minAbw 1000 --maxAbw 9000 --minGap 40 --maxGap 10000 --Gap 400 --n1 80 --n2 20 1>/tmp/bqr/tx.log 2>&1 &"
}
stop(){
	echo "stop ${1}s"
	sleep ${1}s
	ssh ubuntu1@192.168.66.16 "pkill send-main"
	ssh ubuntu5@192.168.66.20 "pkill recv-main"
	stopIperf
}
convert(){
	echo "convert"
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/timestamp.txt ${1}/timestamp.txt 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/log.txt ${1}/log.txt 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/result.txt ${1}/result.txt 1>/dev/null
}
runWithParam(){
	# runWithParam name rate
	local dirname="/home/ubuntu6/data/comparison/exp10/${1}"
	mkdir -p ${dirname}
	echo "${dirname}" 
	setIperf $2
	setBQR $3
	stop 5
	convert ${dirname}
}