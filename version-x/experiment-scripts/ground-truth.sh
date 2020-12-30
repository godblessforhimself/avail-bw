# get ground-truth
# 1. send load packets, DAG average/min packet gap
# 2. send Iperf3 packets at certain rate, DAG get rate
# use 1 and Set value to get ground truth
# use 1 and 2 to get ground truth

SENDER_SCRIPT="deploy-tools/sender-ground-truth.sh"
FILTER_STRING="src host 192.168.2.3 and dst host 192.168.5.1 and udp"
GROUND_DIR="ground-truth"
mkdir -p data/${GROUND_DIR}
printf "start\n"
bash control-module/dag-run.sh 4 "$SENDER_SCRIPT" "$FILTER_STRING"
bash fetch-tools/fetch-data.sh - "data/${GROUND_DIR}/in-0.txt" "data/${GROUND_DIR}/out-0.txt"
printf "end\n"
collect_iperf3(){
# param: iperf3_rate, capture_time
# run iperf3
printf "collect $1\n"
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/set-up-traffic.sh $1"
# run DAG
bash control-module/dag-run.sh $2 - "src host 192.168.2.4 and dst host 192.168.5.1 and udp"
# stop iperf3
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/clean-up-traffic.sh"

bash fetch-tools/fetch-data.sh - data/${GROUND_DIR}/in-${1}.txt data/${GROUND_DIR}/out-${1}.txt
}

rate_list=$(seq 50 50 900)
for rate in ${rate_list}; do
	collect_iperf3 $rate 4
done

