hostname="ubuntu${1}"
n=$((${1}+15))
IP="192.168.66.${n}"
printf "${hostname}@${IP}\n"
ssh ${hostname}@${IP} "mkdir -p /home/${hostname}/abw-project/avail-tools"
rsync -avz --exclude "data/" assolo-0.9a bqr igi-ptr-2.1 pathload_1.3.2 spruce-origin D-ITG-2.8.1-r1023 ${hostname}@${IP}:/home/${hostname}/abw-project/avail-tools 1>/dev/null