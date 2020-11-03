Dirname=data/exp4
mkdir -p ${Dirname}
StartProbing(){
    ssh amax@192.168.67.3 "pkill jintao_client;cd ~/jintao_test/dag_version/build;nohup ./jintao_client 1.0 1000 1>client.log 2>&1 &"
    printf "probing start...\n"
}
SetUpDag(){
    OutFileDir=$1
    OutTrafficFilename="$1/traffic.erf"
    LogFilename="$1/dagsnap.log"
    sudo dagsnap -d0 -s 2 -o ${OutTrafficFilename} 1>${LogFilename} 2>&1 &
    printf "Dag start...\n"
}
Clear(){
    printf "clear finish\n"
}
SetUpDag ${Dirname}
StartProbing
sleep 2s
Clear
cd ${Dirname}
sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f c -o in.pcap 1>dagconvert.log 2>&1
sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f d -o out.pcap 1>dagconvert.log 2>&1