# dagrun-fetch.sh [traffic rate] [user filename] [dag in filename] [dag out filename]
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/set-up-traffic.sh $1"
bash control-module/dag-run.sh
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/clean-up-traffic.sh"
bash fetch-tools/fetch-data.sh $2 $3 $4