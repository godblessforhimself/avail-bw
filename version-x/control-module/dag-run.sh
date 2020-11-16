DAG_FILENAME="~/jintao_test/version-x/data/dag.erf"
IN_PCAP="~/jintao_test/version-x/data/in.pcap"
OUT_PCAP="~/jintao_test/version-x/data/out.pcap"
IN_FILENAME="~/jintao_test/version-x/data/in.txt"
OUT_FILENAME="~/jintao_test/version-x/data/out.txt"
LOG_FILENAME="~/jintao_test/version-x/data/log.txt"
DATA_DIR="~/jintao_test/version-x/data"
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"touch $LOG_FILENAME; sudo dagsnap -d0 -s 5 -o $DAG_FILENAME 1>>$LOG_FILENAME 2>&1 &"
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"mkdir -p ${DATA_DIR}; ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 'cd ~/jintao_test/version-x/send-recv-module/build; rm -f output.txt; nohup bash ../../deploy-tools/receiver.sh 1>${LOG_FILENAME} 2>&1 &'"
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"mkdir -p ${DATA_DIR}; ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 'cd ~/jintao_test/version-x/send-recv-module/build; nohup bash ../../deploy-tools/sender.sh 1>${LOG_FILENAME} 2>&1 &'"
sleep 5s
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"sudo dagconvert -T erf:pcap -i ${DAG_FILENAME} -b 'src host 192.168.2.3 and dst host 192.168.5.1 and udp' -f c -o ${IN_PCAP} 1>>${LOG_FILENAME} 2>&1; tshark -r ${IN_PCAP} -Tfields -e frame.time_epoch > ${DATA_DIR}/in.txt; sudo dagconvert -T erf:pcap -i ${DAG_FILENAME} -b 'src host 192.168.2.3 and dst host 192.168.5.1 and udp' -f d -o ${OUT_PCAP} 1>>${LOG_FILENAME} 2>&1; tshark -r ${OUT_PCAP} -Tfields -e frame.time_epoch > ${DATA_DIR}/out.txt;"


printf "Finish\n"