printf "start build ..."
CurrentDirname=$(pwd)
Logfilename="temp/build.log"
mkdir -p temp
cd ${CurrentDirname} && rsync -avz --exclude="temp/" ../dag_version amax@192.168.2.3:~/jintao_test 1>>${Logfilename} 2>&1
if [ $? -ne 0 ]; then
	printf "rsync to client failed.\n"
	exit
fi
ssh -l amax -o StrictHostKeyChecking=no 192.168.2.3 "cd ~/jintao_test/dag_version && mkdir -p build && cd build && rm -f CMakeCache.txt && cmake ../ && make" 1>>${Logfilename} 2>&1
if [ $? -ne 0 ]; then
	printf "client make failed.\n"
	exit
fi
cd ${CurrentDirname} && rsync -avz --exclude="temp/" ../dag_version zhufengtian@192.168.5.1:~/jintao_test 1>>${Logfilename} 2>&1
if [ $? -ne 0 ]; then
	printf "rsync to server failed.\n"
	exit
fi
ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.5.1 "cd ~/jintao_test/dag_version && mkdir -p build && cd build && rm -f CMakeCache.txt && cmake ../ && make" 1>>${Logfilename} 2>&1
if [ $? -ne 0 ]; then
	printf "Server make failed.\n"
	exit
fi
printf "... finished.\n"