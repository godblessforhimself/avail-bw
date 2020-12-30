# dagrun-fetch.sh [traffic rate] [client data file] [dag in data] [dag out data]
# bash control-module/dagrun-fetch.sh 0 data/c1.txt data/c2.txt data/c3.txt [dag-time [script [bpf]]] 
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/set-up-traffic.sh $1" >/dev/null
bash control-module/dag-run.sh ${@:5}
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/clean-up-traffic.sh" >/dev/null
bash fetch-tools/fetch-data.sh $2 $3 $4