# deploy-tools:

deploy-run-fetch.sh
run quick-deploy.sh, quick-run.sh , fetch-output.sh

deploy-dag.sh
send version-x to dag

deploy-sender-receiver.sh
send version-x from dag to sender and receiver, and compile them using cmake and make

quick-deploy.sh
call deploy-dag.sh and deploy-sender-receiver.sh

sender.sh
run send-main at sender

receiver.sh
run receive-main at receiver


# control-module

dag-run.sh
setup dag before running receive-main and sender-main

quick-run.sh
run receive-main and send-main

fetch-tools

fetch-timestamp.sh [filename]
use rsync to move output.txt at receiver to dag, then to local data.

fetch-data.sh
transfer timestamp file from receiver, dag capture file from DAG to local data.

quickrun-fetch.sh [rate] [data filename]

# analyse-tools

> python analyse-tools/userspace-tool.py --file [filename] [--save-image] [--show-image] [--interact]

# Time Sync

> sudo ntpdate time.nist.gov

client$ iptables -I INPUT 1 --src 192.168.2.0/24 -j ACCEPT
client$ iptables -t raw -I PREROUTING 1 --src 192.168.2.0/24 -j NOTRACK
server$ iptables -I INPUT 1 --src 192.168.2.0/24 -j ACCEPT
server$ iptables -t raw -I PREROUTING 1 --src 192.168.2.0/24 -j NOTRACK