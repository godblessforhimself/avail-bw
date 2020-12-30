if [[ $# -eq 0 ]]; then
	SCRIPT="deploy-tools/sender-bak.sh"
else
	SCRIPT="$1"
fi
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 'sudo pkill recv-main;cd ~/jintao_test/version-x/send-recv-module/build; rm -f output.txt; sudo nohup bash ../../deploy-tools/receiver.sh 1>log.txt 2>&1 &'" >/dev/null
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 'sudo pkill send-main;cd ~/jintao_test/version-x/send-recv-module/build; sudo bash ../../${SCRIPT} 1>log.txt 2>&1'" >/dev/null