# 用tcpreplay产生流量
# bigFlows 7.6Mbps 300s
runTcpreplay(){
	# 以指定速率播放
	local targetRate
	if [[ $# -eq 0 ]]; then
		targetRate=100
	else
		targetRate=$1
	fi
	local multiplierV=$(echo "scale=2;${targetRate}/7.6"|bc -l)
	local loopNumber=$(echo "scale=0;${multiplierV}/20"|bc -l)
	if [[ ${loopNumber} -lt 1 ]]; then
		loopNumber=1
	fi
	local srcMacAddress="a4:fa:76:01:43:f8"
	local dstMacAddress="60:12:3c:3f:bc:d3"
	local srcIPAddress="10.0.2.1/32"
	local dstIPAddress="10.0.7.1/32"
	local interfaceName="ens1f0"
	local pcapFilename="/home/ubuntu2/pcapFiles/bigFlows.pcap"
	echo "rate:${targetRate}Mbps,replay multiplier:${multiplierV},loop:${loopNumber}"
	time sudo tcpreplay-edit --srcipmap=0.0.0.0/0:${srcIPAddress} --dstipmap=0.0.0.0/0:${dstIPAddress} --enet-smac=${srcMacAddress} --enet-dmac=${dstMacAddress} --fixcsum --intf1 ${interfaceName} --stats=1 --loop=${loopNumber} --multiplier=${multiplierV} --duration=15 ${pcapFilename}
}
runTcpreplay $@