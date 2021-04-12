# BQR对tcpreplay流量的效果
# BQR不变，且测量次数增加
setDAG(){
	echo "setDAG $1"
	sudo dagsnap -d0 -s $1 -o /tmp/dag/dagsnap.erf 1>/tmp/dag/dagsnap.log 2>&1 &
}
setTraffic(){
	echo "traffic $1 Mbps"
	ssh ubuntu2@192.168.66.17 "nohup bash /home/ubuntu2/pcapFiles/send.sh $1 1>/tmp/pcap/send.log 2>&1 &"
}
setBQR(){
	echo "setBQR $1"
	ssh ubuntu5@192.168.66.20 "pkill recv-main; nohup /home/ubuntu5/abw-project/avail-tools/bqr/send-recv-module/build/recv-main --timestamp /tmp/bqr/timestamp.txt --result /tmp/bqr/result.txt --log /tmp/bqr/log.txt --polling 1 --busy-poll -1 --once 1>/tmp/bqr/rx.log 2>&1 &"
	ssh ubuntu1@192.168.66.16 "pkill send-main; nohup /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 1500 --loadSize 1472 --inspectSize 1472 --loadNumber 100 --inspectNumber 100 --repeatNumber $1 --retryNumber 1 --preheatNumber 0 --streamGap 1000 --trainGap 0 --dest 10.0.7.1 --noUpdate 1 1>/tmp/bqr/tx.log 2>&1 &"
}
stop(){
	echo "stop ${1}s"
	sleep ${1}s
	sudo pkill dagsnap
	ssh ubuntu2@192.168.66.17 bash <<\EOF
pid=$(ps aux | grep '[b]ash /home/ubuntu2/pcapFiles/send.sh' | awk '{print $2}')
[ -z ${pid} ] || kill -9 ${pid}
EOF
	ssh ubuntu1@192.168.66.16 "pkill send-main"
	ssh ubuntu5@192.168.66.20 "pkill recv-main"
}
convert(){
	echo "convert"
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/timestamp.txt ${1}/timestamp.txt 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/log.txt ${1}/log.txt 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/result.txt ${1}/result.txt 1>/dev/null
	sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "src host 10.0.1.1 and len>=1000" -f a -o ${1}/a.pcap 1>/dev/null 2>&1
	sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "src host 10.0.2.1" -f c -o ${1}/c-traffic.pcap 1>/dev/null 2>&1
	sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "src host 10.0.1.1 and len>=1000" -f c -o ${1}/c-BQR.pcap 1>/dev/null 2>&1
	tshark -r ${1}/a.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/a.len
	tshark -r ${1}/c-traffic.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/c-traffic.len
	tshark -r ${1}/c-BQR.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/c-BQR.len
}
runWithParam(){
	local dirname="/home/ubuntu6/data/comparison/exp7/${1}"
	mkdir -p ${dirname}
	echo "${dirname}" 
	setDAG $2
	setTraffic $1
	setBQR $3
	stop $4
	convert ${dirname}
}