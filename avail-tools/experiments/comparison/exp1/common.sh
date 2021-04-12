bpf="src host 10.0.1.1 and dst host 10.0.7.1 and udp and len>=1400"
stopCmd="pkill iperf3"
rxCmd="nohup iperf3 -sfm -V -i5 -A 0 1>/tmp/iperf/rx.log 2>/tmp/iperf/rx.error &"
setIperf(){
	x=$1
	y=$2
	z=$3
	# rx
	ssh ubuntu5@192.168.66.20 "${stopCmd}; ${rxCmd}"
	if [[ ${z} -ne 0 ]];then
		ssh ubuntu4@192.168.66.19 "${stopCmd}; ${rxCmd} nohup iperf3 -c 10.0.7.1 -ub ${z}M --pacing-timer 0 -l 1472 -fm -t 36000 -A 1 1>/tmp/iperf/tx.log 2>/tmp/iperf/tx.error &"
	else
		ssh ubuntu4@192.168.66.19 "${stopCmd}; ${rxCmd}"
	fi
	if [[ ${y} -ne 0 ]];then
		ssh ubuntu3@192.168.66.18 "${stopCmd}; ${rxCmd} nohup iperf3 -c 10.0.6.1 -ub ${y}M --pacing-timer 0 -l 1472 -fm -t 36000 -A 1 1>/tmp/iperf/tx.log 2>/tmp/iperf/tx.error &"
	else
		ssh ubuntu3@192.168.66.18 "${stopCmd}; ${rxCmd}"
	fi
	if [[ ${x} -ne 0 ]];then
		ssh ubuntu2@192.168.66.17 "${stopCmd}; nohup iperf3 -c 10.0.4.1 -ub ${x}M --pacing-timer 0 -l 1472 -fm -t 36000 -A 1 1>/tmp/iperf/tx.log 2>/tmp/iperf/tx.error &"
	else
		ssh ubuntu2@192.168.66.17 "${stopCmd}"
	fi
}
stopIperf(){
	for ((loopi=2;loopi<=5;loopi++));do
		ssh ubuntu${loopi}@192.168.66.$((loopi+15)) "${stopCmd}"
	done
}
setIC(){
	ic=$1
	ssh ubuntu5@192.168.66.20 "sudo ethtool -C ens1f1 rx-usecs ${ic}" 1>/dev/null 2>&1
}
# 所有方法的函数
runBQR(){
	# 一次运行，测量多组
	# 需要测量x=y=z=900时，运行时间5.57s
	begin=$(date)
	mkdir -p ${1}
	sudo dagsnap -d0 -s 8 -o /tmp/dag/dagsnap.erf 1>/dev/null &
	pid=$!
	ssh ubuntu5@192.168.66.20 "pkill recv-main; nohup /home/ubuntu5/abw-project/avail-tools/bqr/send-recv-module/build/recv-main --timestamp /tmp/bqr/timestamp.txt --result /tmp/bqr/result.txt --log /tmp/bqr/log.txt --polling 1 --busy-poll -1 --once 1>/tmp/bqr/rx.log 2>&1 &"
	ssh ubuntu1@192.168.66.16 "pkill send-main; /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 1500 --loadSize 1472 --inspectSize 1472 --loadNumber 100 --inspectNumber 100 --repeatNumber 100 --retryNumber 1 --preheatNumber 0 --streamGap 10000 --trainGap 100 --dest 10.0.7.1 --noUpdate 0 1>/tmp/bqr/tx.log 2>&1"
	timeout 8 tail -f /dev/null --pid=${pid} 1>/dev/null
	ssh ubuntu1@192.168.66.16 "pkill send-main"
	ssh ubuntu5@192.168.66.20 "pkill recv-main"
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/timestamp.txt ${1}/timestamp.txt 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/log.txt ${1}/log.txt 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/result.txt ${1}/result.txt 1>/dev/null
	sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "${bpf}" -f a -o /tmp/dag/dagsnap.pcap 1>/dev/null 2>&1
	tshark -r /tmp/dag/dagsnap.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/dagsnap.txt
	sudo pkill dagsnap
	sudo pkill dagconvert
	end=$(date)
	printf "BQR:${begin}->${end}\n"
}
runPathload(){
	# 重复运行pathload_rcv
	begin=$(date)
	mkdir -p ${1}
	ssh ubuntu1@192.168.66.16 "pkill pathload_snd; nohup /home/ubuntu1/abw-project/avail-tools/pathload_1.3.2/pathload_snd -i 1>/tmp/pathload/tx.log 2>&1 &"
	for ((loopi=1;loopi<=100;loopi++));do
		printf "${loopi}"
		if [[ ${loopi} -ne 100 ]];then
			printf "|"
		fi
		sudo pkill dagsnap
		sudo pkill dagconvert
		sudo dagsnap -d0 -s 15 -o /tmp/dag/dagsnap.erf 1>/tmp/dag/dagsnap.log 2>&1 &
		pid=$!
		timeout 15 ssh ubuntu5@192.168.66.20 "pkill pathload_rcv; /home/ubuntu5/abw-project/avail-tools/pathload_1.3.2/pathload_rcv -s 10.0.1.1 -t 10 1>/tmp/pathload/rx.txt 2>&1" 1>/dev/null
		if [[ $? -eq 0 ]]; then
			rsync -avz ubuntu5@192.168.66.20:/tmp/pathload/rx.txt ${1}/rx.txt 1>/dev/null
			cat ${1}/rx.txt >> ${1}/rx
			echo "${loopi}" >> ${1}/rx
			timeout 15 tail -f /dev/null --pid=${pid} 1>/dev/null
			sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "${bpf}" -f a -o /tmp/dag/dagsnap.pcap 1>/dev/null 2>&1
			tshark -r /tmp/dag/dagsnap.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/dagsnap.txt
			cat ${1}/dagsnap.txt >> ${1}/dagsnap
			echo "" >> ${1}/dagsnap
		else
			loopi=$((loopi-1))
			printf "pathload timeout"
			ssh ubuntu5@192.168.66.20 "pkill pathload_rcv"
			ssh ubuntu1@192.168.66.16 "pkill pathload_snd; nohup /home/ubuntu1/abw-project/avail-tools/pathload_1.3.2/pathload_snd -i 1>/tmp/pathload/tx.log 2>&1 &"
		fi
		sudo pkill dagsnap
		sudo pkill dagconvert
	done
	end=$(date)
	printf "Pathload:${begin}->${end}\n"
}
runIGI(){
	# 重复运行ptr-client
	# 测量x=y=z=900时，运行时间5.377s
	begin=$(date)
	mkdir -p ${1}
	ssh ubuntu5@192.168.66.20 "pkill ptr-server; nohup /home/ubuntu5/abw-project/avail-tools/igi-ptr-2.1/ptr-server 1>/tmp/igi/rx.log 2>&1 &"
	for ((loopi=1;loopi<=100;loopi++));do
		printf "${loopi}"
		if [[ ${loopi} -ne 100 ]];then
			printf "|"
		fi
		sudo dagsnap -d0 -s 8 -o /tmp/dag/dagsnap.erf 1>/tmp/dag/dagsnap.log 2>&1 &
		pid=$!
		ssh ubuntu1@192.168.66.16 "pkill ptr-client; /home/ubuntu1/abw-project/avail-tools/igi-ptr-2.1/ptr-client -n 60 -s 1472 -k 3 10.0.7.1 1>/tmp/igi/tx.txt 2>&1"
		rsync -avz ubuntu1@192.168.66.16:/tmp/igi/tx.txt ${1}/tx.txt 1>/dev/null
		cat ${1}/tx.txt >> ${1}/tx
		echo "${loopi}" >> ${1}/tx
		timeout 10 tail -f /dev/null --pid=${pid} 1>/dev/null
		sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "${bpf}" -f a -o /tmp/dag/dagsnap.pcap 1>/dev/null 2>&1
		tshark -r /tmp/dag/dagsnap.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/dagsnap.txt
		cat ${1}/dagsnap.txt >> ${1}/dagsnap
		echo "" >> ${1}/dagsnap
	done
	ssh ubuntu1@192.168.66.16 "pkill ptr-client"
	ssh ubuntu5@192.168.66.20 "pkill ptr-server"
	sudo pkill dagsnap
	sudo pkill dagconvert
	end=$(date)
	printf "IGI:${begin}->${end}\n"
}
runSpruce(){
	# 重复运行spruce_rcv和spruce_snd
	# 测量x=y=z=900时，运行时间2.26s
	begin=$(date)
	mkdir -p ${1}
	for ((loopi=1;loopi<=100;loopi++));do
		printf "${loopi}"
		if [[ ${loopi} -ne 100 ]];then
			printf "|"
		fi
		ssh ubuntu5@192.168.66.20 "pkill spruce_rcv; nohup /home/ubuntu5/abw-project/avail-tools/spruce-origin/spruce_rcv 1>/tmp/spruce/rx.txt 2>&1 &"
		sudo dagsnap -d0 -s 5 -o /tmp/dag/dagsnap.erf 1>/tmp/dag/dagsnap.log 2>&1 &
		pid=$!
		ssh ubuntu1@192.168.66.16 "pkill spruce_snd; /home/ubuntu1/abw-project/avail-tools/spruce-origin/spruce_snd -h 10.0.7.1 -c 957M -n 100 -i 3000 1>/tmp/spruce/tx.txt 2>&1"
		rsync -avz ubuntu1@192.168.66.16:/tmp/spruce/tx.txt ${1}/tx.txt 1>/dev/null
		cat ${1}/tx.txt >> ${1}/tx
		echo "${loopi}" >> ${1}/tx
		rsync -avz ubuntu5@192.168.66.20:/tmp/spruce/rx.txt ${1}/rx.txt 1>/dev/null
		cat ${1}/rx.txt >> ${1}/rx
		echo "${loopi}" >> ${1}/rx
		timeout 5 tail -f /dev/null --pid=${pid} 1>/dev/null
		sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "${bpf}" -f a -o /tmp/dag/dagsnap.pcap 1>/dev/null 2>&1
		tshark -r /tmp/dag/dagsnap.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/dagsnap.txt
		cat ${1}/dagsnap.txt >> ${1}/dagsnap
		echo "" >> ${1}/dagsnap
	done
	ssh ubuntu1@192.168.66.16 "pkill spruce_snd"
	ssh ubuntu5@192.168.66.20 "pkill spruce_rcv"
	sudo pkill dagsnap
	sudo pkill dagconvert
	end=$(date)
	printf "Spruce:${begin}->${end}\n"
}
runASSOLO(){
	# 运行一次assolo_run
	begin=$(date)
	mkdir -p ${1}
	sudo dagsnap -d0 -s 80 -o /tmp/dag/dagsnap.erf 1>/tmp/dag/dagsnap.log 2>&1 &
	pid=$!
	txDir="/home/ubuntu1/abw-project/avail-tools/assolo-0.9a/Bin/x86_64"
	rxDir="/home/ubuntu5/abw-project/avail-tools/assolo-0.9a/Bin/x86_64"
	ssh ubuntu1@192.168.66.16 "pkill assolo_snd; nohup ${txDir}/assolo_snd 1>/tmp/assolo/tx.txt 2>&1 &"
	ssh ubuntu5@192.168.66.20 "pkill assolo_rcv; pkill assolo_run; rm -f ${rxDir}/*.instbw; nohup ${rxDir}/assolo_rcv 1>/tmp/assolo/rx.txt 2>&1 & cd ${rxDir}; sleep 1s; ./assolo_run -S 10.0.1.1 -R 10.0.7.1 -u 1500 -t 70 -J 6 -a 3 -p 1472 1>/tmp/assolo/run.txt 2>&1; mv \$(ls *.instbw) /tmp/assolo/instbw"
	timeout 80 tail -f /dev/null --pid=${pid} 1>/dev/null
	ssh ubuntu1@192.168.66.16 "pkill assolo_snd"
	ssh ubuntu5@192.168.66.20 "pkill assolo_run; pkill assolo_rcv"
	rsync -avz ubuntu5@192.168.66.20:/tmp/assolo/rx.txt ${1}/rx 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/assolo/run.txt ${1}/run 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/assolo/instbw ${1}/instbw 1>/dev/null
	rsync -avz ubuntu1@192.168.66.16:/tmp/assolo/tx.txt ${1}/tx 1>/dev/null
	sudo dagconvert -T erf:pcap -i /tmp/dag/dagsnap.erf -b "${bpf}" -f a -o /tmp/dag/dagsnap.pcap 1>/dev/null 2>&1
	tshark -r /tmp/dag/dagsnap.pcap -Tfields -e frame.time_epoch -e frame.len 1>${1}/dagsnap.txt
	sudo pkill dagsnap
	sudo pkill dagconvert
	end=$(date)
	printf "ASSOLO:${begin}->${end}\n"
}
runAllTools(){
	t1=$(date)
	dirname="$1"
	runBQR ${dirname}/BQR
	runASSOLO ${dirname}/assolo
	runSpruce ${dirname}/spruce
	runPathload ${dirname}/pathload
	runIGI ${dirname}/igi
	t2=$(date)
	printf "Total: ${t1}->${t2}\n"
}
taskWithOne(){
	# 用于某方法重新运行
	# 方法名 BQR pathload spruce igi assolo
	printf "taskWithOne $*\n"
	x=${1}
	y=${2}
	z=${3}
	ic=${4}
	taskDirname=${5}
	method="${6}"
	setIC ${ic}
	setIperf ${x} ${y} ${z}
	mkdir -p ${taskDirname}
	if [[ ${method} == "BQR" ]];then
		runBQR ${taskDirname}/BQR
	elif [[ ${method} == "pathload" ]];then
		echo "pathload"
	elif [[ ${method} == "spruce" ]];then
		echo "spruce"
	elif [[ ${method} == "igi" ]];then
		echo "igi"
	elif [[ ${method} == "assolo" ]];then
		echo "assolo"
	fi
	stopIperf
	setIC 0
}
taskWithArg(){
	printf "taskWithArg $*\n"
	x=${1}
	y=${2}
	z=${3}
	ic=${4}
	taskDirname=${5}
	setIC ${ic}
	setIperf ${x} ${y} ${z}
	mkdir -p ${taskDirname}
	runAllTools ${taskDirname} | tee ${taskDirname}/script.log
	stopIperf
	setIC 0
}