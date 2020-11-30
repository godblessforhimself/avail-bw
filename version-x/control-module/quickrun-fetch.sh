# !/bin/bash
# ./quickrun-fetch.sh 200 200.txt
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/set-up-traffic.sh $1"
bash control-module/quick-run.sh
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/clean-up-traffic.sh"
bash fetch-tools/fetch-output.sh $2