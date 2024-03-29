DAG_FILENAME="~/jintao_test/version-x/data/dag.erf"
IN_PCAP="~/jintao_test/version-x/data/in.pcap"
OUT_PCAP="~/jintao_test/version-x/data/out.pcap"
IN_FILENAME="~/jintao_test/version-x/data/in.txt"
OUT_FILENAME="~/jintao_test/version-x/data/out.txt"
LOG_FILENAME="~/jintao_test/version-x/data/log.txt"
DATA_DIR="~/jintao_test/version-x/data"

DAG_CAPTURE_TIME=5
SENDER_SCRIPT="deploy-tools/sender-bak.sh"
FILTER_STRING="src host 192.168.2.3 and dst host 192.168.5.1 and udp"
if [ $# -ge 1 ]; then
	DAG_CAPTURE_TIME=$1
fi
if [ $# -ge 2 ]; then
	SENDER_SCRIPT=$2
fi
if [ $# -ge 3 ]; then
	FILTER_STRING=$3
fi
printf "time $DAG_CAPTURE_TIME, script $SENDER_SCRIPT, filter $FILTER_STRING\n"
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"touch $LOG_FILENAME; sudo dagsnap -d0 -s ${DAG_CAPTURE_TIME} -o $DAG_FILENAME 1>>$LOG_FILENAME 2>&1 &" >/dev/null

if [ ${SENDER_SCRIPT} != "-" ]; then
# receiver
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"mkdir -p ${DATA_DIR}; ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 'sudo pkill recv-main;cd ~/jintao_test/version-x/send-recv-module/build; rm -f output.txt; sudo nohup bash ../../deploy-tools/receiver.sh 1>${LOG_FILENAME} 2>&1 &'" >/dev/null
# sender
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"mkdir -p ${DATA_DIR}; ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 'sudo pkill send-main;cd ~/jintao_test/version-x/send-recv-module/build; sudo nohup bash ../../${SENDER_SCRIPT} 1>${LOG_FILENAME} 2>&1 &'" >/dev/null
fi

# wait
sleep ${DAG_CAPTURE_TIME}s
printf "sleep ${DAG_CAPTURE_TIME}s finish\n"
if [ ${SENDER_SCRIPT} != "-" ]; then
# receiver
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 'sudo pkill recv-main;cat ${LOG_FILENAME}'" >/dev/null
# sender
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 'sudo pkill send-main;cat ${LOG_FILENAME}'" >/dev/null
fi
# parse
#set -x
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"sudo dagconvert -T erf:pcap -i ${DAG_FILENAME} -b '${FILTER_STRING}' -f c -o ${IN_PCAP} 1>>${LOG_FILENAME} 2>&1; tshark -r ${IN_PCAP} -Tfields -e frame.time_epoch > ${DATA_DIR}/in.txt; sudo dagconvert -T erf:pcap -i ${DAG_FILENAME} -b '${FILTER_STRING}' -f d -o ${OUT_PCAP} 1>>${LOG_FILENAME} 2>&1; tshark -r ${OUT_PCAP} -Tfields -e frame.time_epoch > ${DATA_DIR}/out.txt;" >/dev/null
#set +x
printf "convert finish\n"