# note: link speed and dag config should change simutaneously
# set tight link as 1Gbps, gap value ranges from 6us to 36us, total 31 samples.
# use iperf3 to generate cross traffic rate 500Mbps
# use dag capture gap in and gap out
Dirname=data/exp5
mkdir -p ${Dirname}
SetUpIperf3(){
    #Iperf3以特定速率发包
    #服务器
    COMP=$(echo "${1}==0"|bc)
    if [ ${COMP} -eq 1 ]; then
        printf "traffic is zero, skip\n"
        return 0
    fi
    ssh zhufengtian@192.168.67.5 "pkill iperf3;nohup iperf3 -sfm -V 1>~/jintao_test/iperf.log 2>&1 &"
    ssh haha@192.168.67.4 "pkill iperf3; nohup iperf3 -c 192.168.5.1 -ub ${1}M -l 1472 -t 1000 --pacing-timer 0 1>~/jintao_test/iperf.log 2>&1 &"
    printf "SetUpIperf3 ${1}Mbps\n"
}
Clear(){
    ssh haha@192.168.67.4 "pkill iperf3"
    ssh zhufengtian@192.168.67.5 "pkill iperf3;pkill jintao_server;"
    printf "clear finish\n"
}
OneMeasurement(){
	# n,G,GGI
	time=$(python3 -c "print(int($1 * ($2 + $3) / 1e6) + 2)")
	printf "Time is %d, G is $2 us\n" $time
	Clear
	SetUpIperf3 500
	SetUpDag ${Dirname} ${time}
	StartProbing $@
	sleep ${time}s
	Clear
	path_store=$(pwd)
	cd ${Dirname}
	sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f c -o temp.pcap 1>dagconvert.log 2>&1
	tshark -r temp.pcap -Tfields -e frame.time_epoch > in-${2}.txt
	sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f d -o temp.pcap 1>dagconvert.log 2>&1
	tshark -r temp.pcap -Tfields -e frame.time_epoch > out-${2}.txt
	cd $path_store
}
StartProbing(){
	receive_count=$(($1*2))
	printf "receive count %d\n" $receive_count
    ssh zhufengtian@192.168.67.5 "pkill jintao_server;cd ~/jintao_test/dag_version/build;nohup ./jintao_server 6 $receive_count 1>server.log 2>&1 &"

    ssh amax@192.168.67.3 "pkill jintao_client;cd ~/jintao_test/dag_version/build;nohup ./jintao_client 6 $1 $2 $3 1>client.log 2>&1 &"
    printf "probing start...\n"
}
SetUpDag(){
    OutFileDir=$1
    OutTrafficFilename="$1/traffic.erf"
    LogFilename="$1/dagsnap.log"
	last_time=$2
    sudo dagsnap -d0 -s ${last_time} -o ${OutTrafficFilename} 1>${LogFilename} 2>&1 &
    printf "Dag starts for ${last_time}s\n"
}

for i in $(seq 6 1 40)
do
	OneMeasurement 10000 $i 300.7
done
for i in 48 60 72 84 96 120 240 360
do
	OneMeasurement 10000 $i 300.7
done
