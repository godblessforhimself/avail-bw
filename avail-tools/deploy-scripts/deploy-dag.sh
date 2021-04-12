printf "ubuntu6@192.168.66.21\n"
ssh ubuntu6@192.168.66.21 "mkdir -p /home/ubuntu6/abw-project/avail-tools"
rsync -avz --exclude "data/" experiments ubuntu6@192.168.66.21:/home/ubuntu6/abw-project/avail-tools 1>/dev/null