# !/bin/bash
# ./quickrun-fetch.sh traffic_rate data_filename [send_script]
# send_script should be like "deploy-tools/sender.sh"
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/set-up-traffic.sh $1" >/dev/null
if [[ $# -eq 3 ]]; then
	bash control-module/quick-run.sh $3
else
	bash control-module/quick-run.sh
fi
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/clean-up-traffic.sh" >/dev/null
bash fetch-tools/fetch-timestamp.sh $2