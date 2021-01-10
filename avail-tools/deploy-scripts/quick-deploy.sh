bash deploy-scripts/copy2dag.sh
ssh -p 3970 amax@aliyun.ylxdzsw.com "cd ~/jintao_test/avail-tools; bash deploy-scripts/dag2sender.sh; bash deploy-scripts/dag2receiver.sh" 1>/dev/null