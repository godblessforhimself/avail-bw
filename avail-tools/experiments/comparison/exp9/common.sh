# 使用1472/8972字节
# 在1Gbps/10Gbps的数据
setBQR(){
	echo "setBQR $1"
	ssh ubuntu5@192.168.66.20 "pkill recv-main; nohup /home/ubuntu5/abw-project/avail-tools/bqr/send-recv-module/build/recv-main --timestamp /tmp/bqr/timestamp.txt --result /tmp/bqr/result.txt --log /tmp/bqr/log.txt --polling 1 --busy-poll -1 --once 1>/tmp/bqr/rx.log 2>&1 &"
	if [[ $1 -eq 1 ]];then
		ssh ubuntu1@192.168.66.16 "pkill send-main; nohup /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 1500 --loadSize 1472 --inspectSize 1472 --loadNumber 100 --inspectNumber 100 --repeatNumber 10 --retryNumber 1 --preheatNumber 0 --streamGap 1000 --trainGap 0 --dest 10.0.7.1 --noUpdate 1 --minAbw 50 1>/tmp/bqr/tx.log 2>&1 &"
	elif [[ $1 -eq 2 ]];then
		ssh ubuntu1@192.168.66.16 "pkill send-main; nohup /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 1500 --loadSize 1472 --inspectSize 1472 --loadNumber 100 --inspectNumber 100 --repeatNumber 10 --retryNumber 1 --preheatNumber 0 --streamGap 1000 --trainGap 0 --dest 10.1.7.1 --noUpdate 1 --minAbw 100 1>/tmp/bqr/tx.log 2>&1 &"
	elif [[ $1 -eq 3 ]];then
		ssh ubuntu1@192.168.66.16 "pkill send-main; nohup /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 1500 --loadSize 8972 --inspectSize 8972 --loadNumber 100 --inspectNumber 100 --repeatNumber 10 --retryNumber 1 --preheatNumber 0 --streamGap 1000 --trainGap 0 --dest 10.1.7.1 --noUpdate 1 --minAbw 100 1>/tmp/bqr/tx.log 2>&1 &"
	elif [[ $1 -eq 4 ]];then
		ssh ubuntu1@192.168.66.16 "pkill send-main; nohup /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build/send-main --loadRate 9000 --loadSize 8972 --inspectSize 8972 --loadNumber 100 --inspectNumber 100 --repeatNumber 10 --retryNumber 1 --preheatNumber 0 --streamGap 1000 --trainGap 0 --dest 10.1.7.1 --noUpdate 1 --minAbw 1000 1>/tmp/bqr/tx.log 2>&1 &"
	fi
}
stop(){
	echo "stop ${1}s"
	sleep ${1}s
	sudo pkill dagsnap
	ssh ubuntu1@192.168.66.16 "pkill send-main"
	ssh ubuntu5@192.168.66.20 "pkill recv-main"
}
convert(){
	echo "convert"
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/timestamp.txt ${1}/timestamp.txt 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/log.txt ${1}/log.txt 1>/dev/null
	rsync -avz ubuntu5@192.168.66.20:/tmp/bqr/result.txt ${1}/result.txt 1>/dev/null
}
runWithParam(){
	# runWithParam 1 5
	local dirname="/home/ubuntu6/data/comparison/exp9/${1}"
	mkdir -p ${dirname}
	echo "${dirname}" 
	setBQR $1
	stop $2
	convert ${dirname}
}