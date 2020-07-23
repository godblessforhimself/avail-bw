# 满速率发包，背景流量大小、发包时间对单向延迟的影响
mkdir -p data/exp2
mkdir -p temp
SetUpIperf3(){
    #Iperf3以特定速率发包
    #服务器
    ssh zhufengtian@192.168.67.5 "pkill iperf3;nohup iperf3 -sfm -V 1>~/jintao_test/iperf.log 2>&1 &"
    ssh haha@192.168.67.4 "pkill iperf3; nohup iperf3 -c 192.168.5.1 -ub ${1}M -l 1472 -t 1000 --pacing-timer 1 1>~/jintao_test/iperf.log 2>&1 &"
    printf "SetUpIperf3 ${1}Mbps\n"
}
SetUpDag(){
    sudo dagsnap -d0 -s 2 -o data/exp2/traffic.erf 1>temp/dagsnap.log 2>&1 &
    printf "Dag start...\n"
}
StartProbing(){
    ssh zhufengtian@192.168.67.5 "pkill jintao_server;cd ~/jintao_test/dag_version/build;nohup ./jintao_server ${1} 1>server.log 2>&1 &"
    ssh amax@192.168.67.3 "pkill jintao_client;cd ~/jintao_test/dag_version/build;nohup ./jintao_client 2000.0 ${1} 1>client.log 2>&1 &"
    printf "probing start...\n"
}
Clear(){
    ssh haha@192.168.67.4 "pkill iperf3"
    ssh zhufengtian@192.168.67.5 "pkill iperf3"
    printf "clear finish\n"
}
test_fun(){
    #输入：背景流量速率、发包数量
    #步骤：iperf3以特定速率发包
    #dag开始抓包
    #探测程序开始发包
    Traffic=$1
    PacketNum=$2
    #SetUpIperf3 $Traffic
    SetUpDag
    StartProbing $PacketNum
    sleep 2s
    Clear
}
test_fun 500 3000
cd ~/jintao_test/dag_version/data/exp2
sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f c,d -o all.pcap
sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f c -o in.pcap
sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f d -o out.pcap

tcpdump -nN -ttt -r all.pcap > all.txt
tcpdump -nN -ttt -r in.pcap > in.txt
tcpdump -nN -ttt -r all.pcap > out.txt
