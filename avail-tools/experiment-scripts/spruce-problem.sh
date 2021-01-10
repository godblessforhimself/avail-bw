# investigate the problem of SCM_TIMESTAMP
receiverDirectory="/home/zhufengtian/jintao_test/avail-tools/spruce-origin"
senderDirectory="/home/amax/jintao_test/avail-tools/spruce-origin"
mainDirectory="/home/amax/jintao_test/avail-tools/data/spruce-problem"
rm -rf ${mainDirectory}
mkdir -p ${mainDirectory}
dagSnapFile="${mainDirectory}/dagsnap.erf"
pcapFile="${mainDirectory}/dagsnap.pcap"
packetLengthFile="${mainDirectory}/packet.txt"
filterString="src host 192.168.2.3 and dst host 192.168.5.1 and udp"
setIperf3(){
	cd /home/amax/jintao_test/avail-tools
	bash setUpTraffic.sh $1
}
cleanIperf3(){
	cd /home/amax/jintao_test/avail-tools
	bash cleanUpTraffic.sh
}
cleanTool(){
	# receiver
	echo "Cleaning..."
	ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 "pkill spruce_rcv; cd ${receiverDirectory} && rm -f spruce.log spruce.data" >/dev/null
	# sender
	ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 "pkill spruce_snd" >/dev/null
	echo "Clean Tool End"
}
t1=3
t2=6
runTool-origin(){
	prefix=$1
	repeatNumber=$2
	for ((i=1;i<=${repeatNumber};i++));do
		sudo dagsnap -d0 -s ${t1} -o ${dagSnapFile} 1>/dev/null &
		pid=$!
		ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 "pkill spruce_rcv; cd ${receiverDirectory}; nohup ./spruce_rcv 1>spruce.data 2>&1 &" >/dev/null
		ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 "pkill spruce_snd; cd ${senderDirectory}; ./spruce_snd -h 192.168.5.1 -c 957M -n 100 -i 3000 1>/dev/null 2>&1" >/dev/null
		rsync -avz zhufengtian@192.168.67.5:${receiverDirectory}/spruce.log ${mainDirectory}/${prefix}-${i}.log 1>/dev/null
		rsync -avz zhufengtian@192.168.67.5:${receiverDirectory}/spruce.data ${mainDirectory}/${prefix}-${i}.data 1>/dev/null
		timeout ${t2} tail -f /dev/null --pid=${pid} 1>/dev/null &&	sudo dagconvert -T erf:pcap -i ${dagSnapFile} -b "${filterString}" -f d -o ${pcapFile} 1>/dev/null 2>&1 && tshark -r ${pcapFile} -Tfields -e frame.time_epoch 1>"${mainDirectory}/${prefix}-real-${i}.txt"
		cat ${mainDirectory}/${prefix}-${i}.log | awk 'NR>=2 && NR<=199{print $7}' > ${mainDirectory}/${prefix}-meas-${i}.txt
	done
}

begin=$(date)
rates=$(seq 0 100 900)
repeat=100
cleanTool
for rate in ${rates[@]};do
	setIperf3 ${rate}
	runTool-origin $rate $repeat
	cleanIperf3
	cleanTool
done
end=$(date)
printf "%s->%s\n" $begin $end