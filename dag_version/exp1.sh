#iperf3发包的包间隔分布数据采集
#抓包
ssh zhufengtian@192.168.5.1 "pkill jintao_server;cd ~/jintao_test/dag_version/build; nohup ./jintao_server 1>run.log 2>&1 &"
sudo dagsnap -d0 -s 3 -o traffic.erf 1>run.log 2>&1 &
ssh amax@192.168.2.3 "pkill jintao_client;cd ~/jintao_test/dag_version/build;nohup ./jintao_client 1>run.log 2>&1 &"
#pcap
sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f c -o in.pcap 1>>run.log 2>&1
sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f d -o out.pcap 1>>run.log 2>&1
sudo dagconvert -T erf:pcap -i traffic.erf -b "src host 192.168.2.3 and dst host 192.168.5.1 and udp" -f c,d -o all.pcap 1>>run.log 2>&1
#dtime
tcpdump -ttt -nN -r in.pcap > in.dtime
tcpdump -ttt -nN -r out.pcap > out.dtime
tcpdump -ttt -nN -r all.pcap > all.dtime
#result
#in.dtime 165
#out.dtime 165
#all.dtime 4
#expecting
#in 12
#out 12
#dt 6-8
printf "end\n"