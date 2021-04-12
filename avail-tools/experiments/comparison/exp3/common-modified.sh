# 实验三
# 不使用DAG、不使用spruce
stopCmd="pkill iperf3"
rxCmd="nohup iperf3 -sfm -V -i5 -A 0 1>/tmp/iperf/rx.log 2>/tmp/iperf/rx.error &"
setIperf(){
	local x=$1
	local y=$2
	local z=$3
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
	local i
	for ((i=2;i<=5;i++));do
		ssh ubuntu${i}@192.168.66.$((i+15)) "${stopCmd}"
	done
}
setIC(){
	local ic=$1
	ssh ubuntu5@192.168.66.20 "sudo ethtool -C ens1f1 rx-usecs ${ic}" 1>/dev/null 2>&1
}
# 所有方法的函数
runBQR(){
	# 一次测量100组
	# 测量x=y=z=900时，运行时间5.57s
	begin=$(date)
	mkdir -p ${1}
	ssh ubuntu5@192.168.66.20 "pkill recv-main; nohup /home/ubuntu5/abw-project/avail-tools/bqr/send-recv-module/build/recv-main --timestamp /tmp/bqr/timestamp.txt --result /tmp/bqr/result.txt --log /tmp/bqr/log.txt --polling 1 --busy-poll -1 --once 1>/tmp/bqr/rx.log 2>&1 &"
	# 同步等待
	ssh ubuntu1@192.168.66.16 "pkill send-main; /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 1500 --loadSize 1472 --inspectSize 1472 --loadNumber 100 --inspectNumber 100 --repeatNumber 100 --retryNumber 1 --preheatNumber 0 --streamGap 10000 --trainGap 100 --dest 10.0.7.1 --noUpdate 0 1>/tmp/bqr/tx.log 2>&1"
	ssh ubuntu1@192.168.66.16 "pkill send-main"
	ssh ubuntu5@192.168.66.20 "pkill recv-main"
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/timestamp.txt ${1}/timestamp.txt 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/log.txt ${1}/log.txt 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/result.txt ${1}/result.txt 1>/dev/null
	end=$(date)
	printf "BQR:${begin}->${end}\n"
}
runPathload(){
	# 重复运行pathload_rcv
	begin=$(date)
	mkdir -p ${1}
	ssh ubuntu1@192.168.66.16 "pkill pathload_snd; nohup /home/ubuntu1/abw-project/avail-tools/pathload_1.3.2/pathload_snd -i 1>/tmp/pathload/tx.log 2>&1 &"
	local i
	for ((i=1;i<=100;i++));do
		printf "${i}"
		if [[ ${i} -ne 100 ]];then
			printf "|"
		fi
		timeout 25 ssh ubuntu5@192.168.66.20 "pkill pathload_rcv; /home/ubuntu5/abw-project/avail-tools/pathload_1.3.2/pathload_rcv -s 10.0.1.1 -t 10 1>/tmp/pathload/rx.txt 2>&1" 1>/dev/null
		if [[ $? -eq 0 ]]; then
			rsync -avz ubuntu5@192.168.66.20:/tmp/pathload/rx.txt ${1}/rx.txt 1>/dev/null
			cat ${1}/rx.txt >> ${1}/rx
			echo "${i}" >> ${1}/rx
		else
			i=$((i-1))
			printf "pathload timeout"
			ssh ubuntu5@192.168.66.20 "pkill pathload_rcv"
			ssh ubuntu1@192.168.66.16 "pkill pathload_snd; nohup /home/ubuntu1/abw-project/avail-tools/pathload_1.3.2/pathload_snd -i 1>/tmp/pathload/tx.log 2>&1 &"
		fi
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
	local i
	for ((i=1;i<=100;i++));do
		printf "${i}"
		if [[ ${i} -ne 100 ]];then
			printf "|"
		fi
		# 阻塞
		ssh ubuntu1@192.168.66.16 "pkill ptr-client; /home/ubuntu1/abw-project/avail-tools/igi-ptr-2.1/ptr-client -n 60 -s 1472 -k 3 10.0.7.1 1>/tmp/igi/tx.txt 2>&1"
		rsync -avz ubuntu1@192.168.66.16:/tmp/igi/tx.txt ${1}/tx.txt 1>/dev/null
		cat ${1}/tx.txt >> ${1}/tx
		echo "${i}" >> ${1}/tx
	done
	ssh ubuntu1@192.168.66.16 "pkill ptr-client"
	ssh ubuntu5@192.168.66.20 "pkill ptr-server"
	end=$(date)
	printf "IGI:${begin}->${end}\n"
}
runASSOLO(){
	# 运行一次assolo_run
	begin=$(date)
	mkdir -p ${1}
	txDir="/home/ubuntu1/abw-project/avail-tools/assolo-0.9a/Bin/x86_64"
	rxDir="/home/ubuntu5/abw-project/avail-tools/assolo-0.9a/Bin/x86_64"
	ssh ubuntu1@192.168.66.16 "pkill assolo_snd; nohup ${txDir}/assolo_snd 1>/tmp/assolo/tx.txt 2>&1 &"
	# 阻塞
	ssh ubuntu5@192.168.66.20 "pkill assolo_rcv; pkill assolo_run; rm -f ${rxDir}/*.instbw; nohup ${rxDir}/assolo_rcv 1>/tmp/assolo/rx.txt 2>&1 & cd ${rxDir}; sleep 1s; ./assolo_run -S 10.0.1.1 -R 10.0.7.1 -u 1500 -t 70 -J 6 -a 3 -p 1472 1>/tmp/assolo/run.txt 2>&1; mv \$(ls *.instbw) /tmp/assolo/instbw"
	ssh ubuntu1@192.168.66.16 "pkill assolo_snd"
	ssh ubuntu5@192.168.66.20 "pkill assolo_run; pkill assolo_rcv"
	rsync -avz ubuntu5@192.168.66.20:/tmp/assolo/rx.txt ${1}/rx 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/assolo/run.txt ${1}/run 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/assolo/instbw ${1}/instbw 1>/dev/null
	rsync -avz ubuntu1@192.168.66.16:/tmp/assolo/tx.txt ${1}/tx 1>/dev/null
	end=$(date)
	printf "ASSOLO:${begin}->${end}\n"
}
runAllTools(){
	local t1=$(date)
	local dirname="$1"
	runBQR ${dirname}/BQR
	runASSOLO ${dirname}/assolo
	runPathload ${dirname}/pathload
	runIGI ${dirname}/igi
	local t2=$(date)
	printf "Total: ${t1}->${t2}\n"
}
taskWithArg(){
	printf "taskWithArg $*\n"
	local x=${1}
	local y=${2}
	local z=${3}
	local ic=${4}
	local taskDirname=${5}
	setIC ${ic}
	setIperf ${x} ${y} ${z}
	mkdir -p ${taskDirname}
	runAllTools ${taskDirname} | tee ${taskDirname}/script.log
	stopIperf
	setIC 0
}