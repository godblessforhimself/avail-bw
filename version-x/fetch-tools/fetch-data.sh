# fetch-data.sh [user-filename] [dag-portc filename] [dag-portd filename]
#/dev/null
printf "Fetching\n"
if [ $# -eq 0 ]; then
	output_filename="data/output.txt"
	in_filename="data/in.txt"
	out_filename="data/out.txt"
elif [ $# -eq 3 ]; then
	output_filename="$1"
	in_filename="$2"
	out_filename="$3"
fi

exec >/dev/null
if [ $1 != "-" ]; then
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"rsync -avz zhufengtian@192.168.67.5:~/jintao_test/version-x/send-recv-module/build/output.txt ~/jintao_test/version-x/data/output.txt"
rsync -avz -e 'ssh -p 3970' amax@aliyun.ylxdzsw.com:~/jintao_test/version-x/data/output.txt ${output_filename}
fi
rsync -avz -e 'ssh -p 3970' amax@aliyun.ylxdzsw.com:~/jintao_test/version-x/data/in.txt ${in_filename}
rsync -avz -e 'ssh -p 3970' amax@aliyun.ylxdzsw.com:~/jintao_test/version-x/data/out.txt ${out_filename}
exec &>/dev/tty

printf "Fetch End\n"