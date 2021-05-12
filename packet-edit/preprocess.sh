tcpdump -r /home/tony/pcapFiles/bigFlows.pcap -nN -w /home/tony/pcapFiles/bigFlows1.pcap "not ip6 and not icmp6 and not icmp"
rsync -avz /home/tony/pcapFiles/bigFlows1.pcap ubuntu2@192.168.66.17:/home/ubuntu2/pcapFiles/bigFlows1.pcap
ssh ubuntu2@192.168.66.17 "tcprewrite --dlt=enet --srcipmap=0.0.0.0/0:10.0.2.1/32 --dstipmap=0.0.0.0/0:10.0.7.1/32 --enet-smac=a4:fa:76:01:43:f8 --enet-dmac=60:12:3c:3f:bc:d3 --infile=/home/ubuntu2/pcapFiles/bigFlows1.pcap --outfile=/home/ubuntu2/pcapFiles/bigFlows2.pcap --fixlen=pad --fixcsum"

tcpdump -r /home/tony/pcapFiles/equinix-nyc.dirA.20180816-125910.UTC.anon.pcap -nN -w /home/tony/pcapFiles/caida1.pcap "not ip6 and not icmp6 and not icmp"
/home/tony/projects/avail_related/avail-bw/packet-edit/main /home/tony/pcapFiles/caida1.pcap /home/tony/pcapFiles/caida2.pcap
rsync -avz /home/tony/pcapFiles/caida2.pcap ubuntu2@192.168.66.17:/home/ubuntu2/pcapFiles/caida2.pcap
ssh ubuntu2@192.168.66.17 "tcprewrite --dlt=enet --srcipmap=0.0.0.0/0:10.0.2.1/32 --dstipmap=0.0.0.0/0:10.0.7.1/32 --enet-smac=a4:fa:76:01:43:f8 --enet-dmac=60:12:3c:3f:bc:d3 --infile=/home/ubuntu2/pcapFiles/caida2.pcap --outfile=/home/ubuntu2/pcapFiles/caida3.pcap --fixlen=pad --fixcsum"