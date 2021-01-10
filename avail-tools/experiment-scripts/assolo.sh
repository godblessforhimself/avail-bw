#!/bin/bash
# usage: bash assolo.sh /home/amax/jintao_test/avail-tools/data/assolo-noIC 0
toolDirectory2="/home/zhufengtian/jintao_test/avail-tools/assolo-0.9a/Bin/x86_64"
toolDirectory3="/home/amax/jintao_test/avail-tools/assolo-0.9a/Bin/x86_64"
tmpDirectory="/home/amax/jintao_test/avail-tools/data/temp"
mainDirectory="/home/amax/jintao_test/avail-tools/data/assolo"
dagSnapFile="${tmpDirectory}/dagsnap.erf"
pcapFile="${tmpDirectory}/dagsnap.pcap"
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
	ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 "pkill assolo_rcv; pkill assolo_run; cd ${toolDirectory2}; rm -f *.instbw; nohup ./assolo_rcv 1>/dev/null 2>&1 &" >/dev/null
	# sender
	ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 "pkill assolo_snd;cd ${toolDirectory3}; nohup ./assolo_snd 1>/dev/null 2>&1 &" >/dev/null
	echo "Init Tool End"
}
cleanTool(){
	# receiver
	echo "Cleaning..."
	ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 "pkill assolo_rcv; pkill assolo_run" >/dev/null
	# sender
	ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 "pkill assolo_snd" >/dev/null
	echo "Clean Tool End"
}
t1=65
t2=60
t3=70
runTool(){
	prefix=$1
	echo -e "${prefix}"
	estimationFile="${prefix}-estimation"
	packetLengthFile="${prefix}-packetLength"
	sudo dagsnap -d0 -s ${t1} -o ${dagSnapFile} 1>/dev/null &
	pid=$!
	ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 "pkill assolo_run; cd ${toolDirectory2}; rm -f *.instbw; ./assolo_run -S 192.168.2.3 -R 192.168.5.1 -u 1500 -t ${t2} -J 6 -a 3 -p 1472; mv \$(ls *.instbw) output.instbw" >/dev/null
	rsync -avz zhufengtian@192.168.67.5:${toolDirectory2}/output.instbw ${estimationFile} 1>/dev/null && sort ${estimationFile} -o ${estimationFile} 1>/dev/null
	timeout ${t3} tail -f /dev/null --pid=${pid} 1>/dev/null &&	sudo dagconvert -T erf:pcap -i ${dagSnapFile} -b "${filterString}" -f c -o ${pcapFile} 1>/dev/null 2>&1 && tshark -r ${pcapFile} -Tfields -e frame.time_epoch -e frame.len 1>${packetLengthFile}
}
main(){
	if [[ $# -gt 0 ]];then
		mainDirectory=$1
		if [[ $# -gt 1 ]];then
			bash experiment-scripts/icswitch.sh $2
		fi
	fi
	rm -rf $mainDirectory
	mkdir -p $mainDirectory
	rateList=$(seq 0 100 900)
	initTool
	for rate in ${rateList[@]};do
		begin=$(date)
		setIperf3 ${rate}
		runTool ${mainDirectory}/$rate
		cleanIperf3
		end=$(date)
		echo -e "Rate ${rate}:${begin}->${end}"
	done
	cleanTool
}
main $@