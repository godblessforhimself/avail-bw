# IGI/PTR tool
# 1900 * 15 / 3600 = 7.9 h
mainDirectory="/home/amax/jintao_test/avail-tools/data/igi-ptr"
receiverDirectory="/home/zhufengtian/jintao_test/avail-tools/igi-ptr-2.1"
senderDirectory="/home/amax/jintao_test/avail-tools/igi-ptr-2.1"
tmpDirectory="/home/amax/jintao_test/avail-tools/data/temp"
dagSnapFile="${tmpDirectory}/dagsnap.erf"
pcapFile="${tmpDirectory}/dagsnap.pcap"
filterString="src host 192.168.2.3 and dst host 192.168.5.1 and udp"
estimationTmp="${tmpDirectory}/estimation.tmp"
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
	ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 "pkill ptr-server; cd ${receiverDirectory}; rm -f *.data; nohup ./ptr-server 1>/dev/null 2>&1 &" >/dev/null
	# sender
	ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 "pkill ptr-client;cd ${senderDirectory}" >/dev/null
	echo "Init Tool End"
}
cleanTool(){
	# receiver
	echo "Cleaning..."
	ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 "pkill ptr-server" >/dev/null
	# sender
	ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 "pkill ptr-client; cd ${senderDirectory}; rm *.data" >/dev/null
	echo "Clean Tool End"
}
t1=10
t2=15
runTool(){
	prefix=$1
	repeat=$2
	estimationFile="${prefix}-estimation"
	packetLengthFile="${prefix}-packetLength"
	rm -f ${estimationFile} ${packetLengthFile}
	for ((i=1;i<=${repeat};i++));do
		sudo dagsnap -d0 -s ${t1} -o ${dagSnapFile} 1>/dev/null &
		pid=$!
		ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 "pkill ptr-client; cd ${senderDirectory}; ./ptr-client -n 60 -s 1472 -k 3 192.168.5.1 1>output.data" >/dev/null
		rsync -avz amax@192.168.67.3:${senderDirectory}/output.data ${estimationTmp} 1>/dev/null && cat ${estimationTmp} 1>>${estimationFile}
		timeout ${t2} tail -f /dev/null --pid=${pid} 1>/dev/null &&	sudo dagconvert -T erf:pcap -i ${dagSnapFile} -b "${filterString}" -f c -o ${pcapFile} 1>/dev/null 2>&1 && echo "" >> ${packetLengthFile} && tshark -r ${pcapFile} -Tfields -e frame.time_epoch -e frame.len 1>>${packetLengthFile}
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