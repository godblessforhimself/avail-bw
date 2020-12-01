# !/bin/bash
# ./quickrun-fetch.sh 200 200.txt
#bash control-module/time-update.sh
#printf "Ntp updated\n"
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/set-up-traffic.sh $1"
bash control-module/quick-run.sh
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/clean-up-traffic.sh"
bash fetch-tools/fetch-timestamp.sh $2