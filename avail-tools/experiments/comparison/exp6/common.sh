# 观察tcpreplay以不同速率发送的流量间隔
# 使用DAG抓包，转换成(t[i],len[i])
setDAG(){
	echo "setDAG $1"
	sudo dagsnap -d0 -s $1 -o /tmp/dag/dagsnap.erf 1>/tmp/dag/dagsnap.log 2>&1 &
}
setTraffic(){
	echo "traffic $1 Mbps"
	ssh ubuntu2@192.168.66.17 "nohup bash /home/ubuntu2/pcapFiles/send.sh $1 1>/tmp/pcap/send.log 2>&1 &"
}
stop(){
	echo "stop $1"
	sleep ${1}s
	sudo pkill dagsnap
	ssh ubuntu2@192.168.66.17 bash <<\EOF
pid=$(ps aux | grep '[b]ash /home/ubuntu2/pcapFiles/send.sh' | awk '{print $2}')
[ -z ${pid} ] || kill -9 ${pid}
EOF
}
convert(){
	echo "convert"
	sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "src host 10.0.2.1" -f c -o ${1}/traffic.pcap 1>/dev/null 2>&1
	tshark -r ${1}/traffic.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/traffic.len
}
runAtRate(){
	local dirname="/home/ubuntu6/data/comparison/exp6/${1}"
	echo "${dirname}"
	mkdir -p ${dirname}
	setDAG $2
	setTraffic $1
	stop $3
	convert ${dirname}
}