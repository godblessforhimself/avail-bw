if [ $# -eq 0 ]; then
	output_filename="output.txt"
else
	output_filename="$1"
fi
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"rsync -avz zhufengtian@192.168.67.5:~/jintao_test/version-x/send-recv-module/build/output.txt ~/jintao_test/version-x/data/output.txt"
rsync -avz -e 'ssh -p 3970' amax@aliyun.ylxdzsw.com:~/jintao_test/version-x/data/output.txt data/${output_filename}
