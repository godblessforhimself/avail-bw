# run in 'avail-tools'
rsync -avz --exclude "*.gz" --exclude "*.tgz" --exclude "*.tar" --exclude "data/" -e "ssh -p 3970" ../avail-tools amax@aliyun.ylxdzsw.com:~/jintao_test #>/dev/null