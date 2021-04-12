bash deploy-scripts/quick-deploy.sh
ssh ubuntu5@192.168.66.20 "cd /home/ubuntu5/abw-project/avail-tools/bqr/send-recv-module/build && rm -f CMakeCache.txt && cmake ../ && make" 1>/dev/null
ssh ubuntu1@192.168.66.16 "cd /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build && rm -f CMakeCache.txt && cmake ../ && make" 1>/dev/null