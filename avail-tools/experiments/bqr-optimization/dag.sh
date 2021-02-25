# 因为DAG实际无效，把相关函数存在本文件里，供以后使用
setDAG(){
	time=$1
	mkdir -p /tmp/dag
	sudo dagsnap -d0 -s ${time} -o /tmp/dag/dag.erf 1>/tmp/dag/dagsnap.log 2>/tmp/dag/dagsnap.error &
	pid=$!
	echo ${pid}
}
convertSuccess(){
	n=$(tail -n 2 /tmp/dag/dagconvert.log | head -n 1 | awk '{print substr($6,length($6)-2)}')
	if [ "$n" == "(0)" ];then
		echo 0
	else
		echo 1
	fi
}
waitDAG(){
	timeout $1 tail -f /dev/null --pid=$2 1>/dev/null
	rm -f ${5} ${6}
	sudo dagconvert -T erf:pcap -i /tmp/dag/dag.erf -b "${4}" -f a -o /tmp/dag/dag.pcap 1>/dev/null 2>/tmp/dag/dagconvert.log
	ret=$(convertSuccess)
	if [[ $ret -eq 1 ]];then
		tshark -r /tmp/dag/dag.pcap -Tfields -e frame.time_epoch -e frame.len 1>${5}
	fi
	sudo dagconvert -T erf:pcap -i /tmp/dag/dag.erf -b "${4}" -f c -o /tmp/dag/dag.pcap 1>/dev/null 2>/tmp/dag/dagconvert.log
	ret=$(convertSuccess)
	if [[ $ret -eq 1 ]];then
		tshark -r /tmp/dag/dag.pcap -Tfields -e frame.time_epoch -e frame.len 1>${6}
	fi
}