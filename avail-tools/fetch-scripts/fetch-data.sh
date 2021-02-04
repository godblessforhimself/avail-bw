ping -c 1 -W 0.1 192.168.66.21 1>/dev/null 2>&1
if [[ $? -eq 0 ]];then
	rsync -avz ubuntu6@192.168.66.21:/home/ubuntu6/data / 1>/dev/null
else
	rsync -avz -e "ssh -p 18744" ubuntu6@39.108.129.28:/home/ubuntu6/data / 1>/dev/null
fi

