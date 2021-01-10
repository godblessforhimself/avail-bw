# pathload
# 15 * 1900 / 3600= 7.9 h
mainDirectory="/home/amax/jintao_test/avail-tools/data/pathload"
tmpDirectory="/home/amax/jintao_test/avail-tools/data/temp"
receiverDirectory="/home/zhufengtian/jintao_test/avail-tools/pathload_1.3.2"
senderDirectory="/home/amax/jintao_test/avail-tools/pathload_1.3.2"
dagSnapFile="${tmpDirectory}/dagsnap.erf"
pcapFile="${tmpDirectory}/dagsnap.pcap"
estimationTmp="${tmpDirectory}/estimation.tmp"
filterString="src host 192.168.2.3 and dst host 192.168.5.1 and udp"
setIperf3(){
	cd /home/amax/jintao_test/avail-tools
	bash setUpTraffic.sh $1
}
cleanIperf3(){
	cd /home/amax/jintao_test/avail-tools
	bash cleanUpTraffic.sh
}
initTool(){
	# receiver
	echo "Initing..."
	ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 "pkill pathload_rcv; cd ${receiverDirectory}; rm -f *.data" >/dev/null
	# sender
	ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 "pkill pathload_snd; cd ${senderDirectory}; nohup ./pathload_snd -i 1>run.log 2>&1 &" >/dev/null
	echo "Init Tool End"
}
cleanTool(){
	# receiver
	echo "Cleaning..."
	ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 "pkill pathload_rcv; cd ${receiverDirectory}; rm -f *.data" >/dev/null
	# sender
	ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 "pkill pathload_snd" >/dev/null
	echo "Clean Tool End"
}
t1=10
t2=8
t3=12
runTool(){
	prefix=$1
	repeat=$2
	estimationFile="${prefix}-estimation"
	packetLengthFile="${prefix}-packetLength"
	rm -f ${estimationFile} ${packetLengthFile}
	for ((i=1;i<=${repeat};i++));do
		sudo dagsnap -d0 -s ${t1} -o ${dagSnapFile} 1>/dev/null &
		pid=$!
		timeout ${t3} ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 "pkill pathload_rcv; cd ${receiverDirectory}; ./pathload_rcv -s 192.168.2.3 -t ${t2} 1>output.data 2>&1" >/dev/null
		if [[ $? -eq 0 ]]; then
			rsync -avz zhufengtian@192.168.67.5:${receiverDirectory}/output.data ${estimationTmp} 1>/dev/null && cat ${estimationTmp} 1>>${estimationFile}
			timeout ${t3} tail -f /dev/null --pid=${pid} 1>/dev/null &&	sudo dagconvert -T erf:pcap -i ${dagSnapFile} -b "${filterString}" -f c -o ${pcapFile} 1>/dev/null 2>&1 && echo "" >> ${packetLengthFile} && tshark -r ${pcapFile} -Tfields -e frame.time_epoch -e frame.len 1>>${packetLengthFile}
		else
			i=$((i-1))
			echo "receiver timeout, restarting..."
			cleanTool
			initTool
		fi
	done
}
main(){
	if [[ $# -gt 0 ]];then
		mainDirectory=$1
		if [[ $# -gt 1 ]];then
			bash experiment-scripts/icswitch.sh $2
		fi
	fi
	rm -rf ${mainDirectory}
	mkdir -p ${mainDirectory}
	rateList=$(seq 0 100 900)
	repeatNumber=100
	initTool
	for rate in ${rateList[@]};do
		begin=$(date)
		setIperf3 ${rate}
		runTool ${mainDirectory}/$rate ${repeatNumber}
		cleanIperf3
		end=$(date)
		echo -e "Rate ${rate}:${begin}->${end}"
	done
	cleanTool
}
main $@