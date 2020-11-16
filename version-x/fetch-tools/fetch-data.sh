ssh -p 3970 amax@aliyun.ylxdzsw.com \
"rsync -avz zhufengtian@192.168.67.5:~/jintao_test/version-x/send-recv-module/build/output.txt ~/jintao_test/version-x/data/output.txt"
rsync -avz -e 'ssh -p 3970' --exclude="*.erf" amax@aliyun.ylxdzsw.com:~/jintao_test/version-x/data/ data/
