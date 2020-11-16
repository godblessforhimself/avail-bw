# run it outside its directory
# send to sender 
rsync -avz ../version-x --exclude="data/" amax@192.168.67.3:~/jintao_test 1>/dev/null 2>&1
if [ $? -ne 0 ]; then
	printf "rsync to client failed.\n"
	exit
fi
# compile in sender
ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 "cd ~/jintao_test/version-x/send-recv-module && mkdir -p build && cd build && rm -f CMakeCache.txt && cmake ../ && make" 1>/dev/null 2>&1
if [ $? -ne 0 ]; then
	printf "client make failed.\n"
	exit
fi
# send to receiver
rsync -avz ../version-x --exclude="data/" zhufengtian@192.168.67.5:~/jintao_test 1>/dev/null 2>&1
if [ $? -ne 0 ]; then
	printf "rsync to server failed.\n"
	exit
fi
# compile in receiver
ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 "cd ~/jintao_test/version-x/send-recv-module && mkdir -p build && cd build && rm -f CMakeCache.txt && cmake ../ && make" 1>/dev/null 2>&1
if [ $? -ne 0 ]; then
	printf "Server make failed.\n"
	exit
fi
printf "... finished.\n"