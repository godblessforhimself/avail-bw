IP_TRAFFIC="192.168.2.3"
IP_SERVER="192.168.5.1"
Dirname="catch_traffic_dir"
catch_traffic(){
	Traffic_speed=$1
	printf "Start catch traffic at ${Traffic_speed}Mbps.\n"
	Erf_filename="${Dirname}/traffic_${Traffic_speed}.erf"
	In_filename="${Dirname}/in_traffic_${Traffic_speed}.pcap"
	Out_filename="${Dirname}/out_traffic_${Traffic_speed}.pcap"
	ssh zhufengtian@192.168.5.1 "pkill iperf3; nohup iperf3 -sfm 1>~/iperf3.log 2>&1 &"
	sudo dagsnap -d0 -s 20 -o ${Erf_filename} &
	sleep 1s
	ssh amax@192.168.2.3 "pkill iperf3; nohup iperf3 -f m -c 192.168.5.1 -l 1472 -ub ${Traffic_speed}M -k 10k --pacing-timer 1000 1>~/iperf3.log 2>&1 &"
	printf "config iperf3 and dagsnap done.\n"
	sleep 20s
	ssh zhufengtian@192.168.5.1 "pkill iperf3"
	ssh amax@192.168.2.3 "pkill iperf3"
	printf "collect traffic end.\n"
	sudo dagconvert -T erf:pcap -i ${Erf_filename} -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp and greater 100" -f c -o ${In_filename} 1>/dev/null 2>&1
	sudo dagconvert -T erf:pcap -i ${Erf_filename} -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp and greater 100" -f d -o ${Out_filename} 1>/dev/null 2>&1
	printf "catch at ${Traffic_speed}Mbps end.\n"
}
#sudo tcpdump -ttt -nNr in_traffic_1000.pcap | less
#期望间隔=包大小/速率。包大小1472，包数量10k
#速率10Mbps，期望间隔1200us=1.2ms，总时间12s
#速率100Mbps，期望间隔=120us，总时间1.2s
#速率500Mbps，期望间隔24us，总时间0.24s
#速率1000Mbps，期望间隔=12us，总时间0.12s
mkdir -p ${Dirname}
Start_time=$(date)
Traffic_array=(10 100 500 1000)
for Traffic in ${Traffic_array[*]}; do
	catch_traffic ${Traffic}
done
End_time=$(date)
printf "Program begin: ${Start_time}, end: ${End_time}\n"