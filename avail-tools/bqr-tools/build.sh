bash deploy-scripts/quick-deploy.sh
ssh -p 18743 ubuntu5@39.108.129.28 "cd /home/ubuntu5/abw-project/avail-tools/bqr/send-recv-module/build && rm -f CMakeCache.txt && cmake ../ && make" 1>/dev/null
ssh -p 18739 ubuntu1@39.108.129.28 "cd /home/ubuntu1/abw-project/avail-tools/bqr/send-recv-module/build && rm -f CMakeCache.txt && cmake ../ && make" 1>/dev/null