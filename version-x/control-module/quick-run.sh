ssh -p 3970 amax@aliyun.ylxdzsw.com \
"ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 'cd ~/jintao_test/version-x/send-recv-module/build; rm -f output.txt; nohup bash ../../deploy-tools/receiver.sh 1>log.txt 2>&1 &'"
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 'cd ~/jintao_test/version-x/send-recv-module/build; bash ../../deploy-tools/sender.sh 1>log.txt 2>&1'"
printf "Finish\n"