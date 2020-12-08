# fetch-data.sh [user-filename] [dag-portc filename] [dag-portd filename]
if [ $# -eq 0 ]; then
	output_filename="output.txt"
	in_filename="in.txt"
	out_filename="out.txt"
elif [ $# -eq 3 ]; then
	output_filename="$1"
	in_filename="$2"
	out_filename="$3"
fi
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"rsync -avz zhufengtian@192.168.67.5:~/jintao_test/version-x/send-recv-module/build/output.txt ~/jintao_test/version-x/data/output.txt"
rsync -avz -e 'ssh -p 3970' amax@aliyun.ylxdzsw.com:~/jintao_test/version-x/data/in.txt data/${in_filename}
rsync -avz -e 'ssh -p 3970' amax@aliyun.ylxdzsw.com:~/jintao_test/version-x/data/out.txt data/${out_filename}
rsync -avz -e 'ssh -p 3970' amax@aliyun.ylxdzsw.com:~/jintao_test/version-x/data/output.txt data/${output_filename}