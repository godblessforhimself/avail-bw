# 在SRC和DST编译代码
IP_DST='10.10.114.21'
USERNAME='liqing'
SERVER_PROJ='~'
quick_make(){
    printf "Quick clean and make ..."
    CURRENT_DIRNAME=$(pwd)
    mkdir -p build && cd build && rm -f CMakeCache.txt && cmake ../ 1>deploy.log 2>&1 && make 1>>deploy.log 2>&1
    if [ $? -ne 0 ]; then
        printf "Client remake failed.\n"
        exit
    fi
    cd ${CURRENT_DIRNAME} && rsync -a --exclude=".git/" --exclude="data/" --exclude="__pycache__/" --exclude=".ipynb_checkpoints/" --exclude="*.ipynb" ../avail-bw ${USERNAME}@${IP_DST}:~ 1>>deploy.log 2>&1
    if [ $? -ne 0 ]; then
        printf "Source code transmission failed.\n"
        exit
    fi
    ssh -l ${USERNAME} -o StrictHostKeyChecking=no ${IP_DST} "cd ~/avail-bw/build && rm -f CMakeCache.txt && cmake ../ && make" 1>>deploy.log 2>&1
    if [ $? -ne 0 ]; then
        printf "Server remake failed.\n"
        exit
    fi
    printf "... finished.\n"
}
quick_make