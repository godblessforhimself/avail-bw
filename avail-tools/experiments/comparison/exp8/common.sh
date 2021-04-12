# ASSOLO对tcpreplay流量的效果
# ASSOLO不变，且测量次数增加
setDAG(){
	echo "setDAG $1"
	sudo dagsnap -d0 -s $1 -o /tmp/dag/dagsnap.erf 1>/tmp/dag/dagsnap.log 2>&1 &
}
setTraffic(){
	echo "traffic $1 Mbps"
	ssh ubuntu2@192.168.66.17 "nohup bash /home/ubuntu2/pcapFiles/send.sh $1 1>/tmp/pcap/send.log 2>&1 &"
}
setASSOLO(){
	echo "setASSOLO $1"
	local txDir="/home/ubuntu1/abw-project/avail-tools/assolo-0.9a/Bin/x86_64"
	local rxDir="/home/ubuntu5/abw-project/avail-tools/assolo-0.9a/Bin/x86_64"
	ssh ubuntu1@192.168.66.16 "pkill assolo_snd; nohup ${txDir}/assolo_snd 1>/tmp/assolo/tx.txt 2>&1 &"
	ssh ubuntu5@192.168.66.20 "pkill assolo_rcv; pkill assolo_run; rm -f ${rxDir}/*.instbw; nohup ${rxDir}/assolo_rcv 1>/tmp/assolo/rx.txt 2>&1 & cd ${rxDir}; sleep 1s; ./assolo_run -S 10.0.1.1 -R 10.0.7.1 -u 1500 -t $1 -J 6 -a 3 -p 1472 1>/tmp/assolo/run.txt 2>&1; mv \$(ls *.instbw) /tmp/assolo/instbw"
}
stop(){
	echo "stop ${1}s"
	sleep ${1}s
	sudo pkill dagsnap
	ssh ubuntu2@192.168.66.17 bash <<\EOF
pid=$(ps aux | grep '[b]ash /home/ubuntu2/pcapFiles/send.sh' | awk '{print $2}')
[ -z ${pid} ] || kill -9 ${pid}
EOF
	ssh ubuntu1@192.168.66.16 "pkill assolo_snd"
	ssh ubuntu5@192.168.66.20 "pkill assolo_rcv"
}
convert(){
	echo "convert"
	rsync -avz ubuntu5@192.168.66.20:/tmp/assolo/rx.txt ${1}/rx 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/assolo/run.txt ${1}/run 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/assolo/instbw ${1}/instbw 1>/dev/null
	rsync -avz ubuntu1@192.168.66.16:/tmp/assolo/tx.txt ${1}/tx 1>/dev/null
	sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "src host 10.0.1.1 and len>=1000" -f a -o ${1}/a.pcap 1>/dev/null 2>&1
	sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "src host 10.0.2.1" -f c -o ${1}/c-traffic.pcap 1>/dev/null 2>&1
	sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "src host 10.0.1.1 and len>=1000" -f c -o ${1}/c-ASSOLO.pcap 1>/dev/null 2>&1
	tshark -r ${1}/a.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/a.len
	tshark -r ${1}/c-traffic.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/c-traffic.len
	tshark -r ${1}/c-ASSOLO.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/c-ASSOLO.len
}
runWithParam(){
	# runWithParam 100 15 10 15
	local dirname="/home/ubuntu6/data/comparison/exp8/${1}"
	mkdir -p ${dirname}
	echo "${dirname}" 
	setDAG $2
	setTraffic $1
	setASSOLO $3
	stop $4
	convert ${dirname}
}