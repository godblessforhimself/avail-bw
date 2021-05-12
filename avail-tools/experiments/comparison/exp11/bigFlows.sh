# 用tcpreplay产生流量 bigFlows 9.466Mbps 300s
runTcpreplay(){
	local targetRate=$1
	local duration=$2
	local multiplierV=$(echo "scale=2;${targetRate}/9.466"|bc -l)
	local loopNumber=$(echo "scale=0;${targetRate}*${duration}/9.466/300+1"|bc -l)
	if [[ ${loopNumber} -lt 1 ]]; then
		loopNumber=1
	fi
	echo "rate:${targetRate}Mbps,replay multiplier:${multiplierV},loop:${loopNumber}"
	time sudo tcpreplay -i ens1f0 --loop=${loopNumber} --multiplier=${multiplierV} --duration=${duration} /home/ubuntu2/pcapFiles/bigFlows2.pcap
}
wrapRun(){
	while [ $# != 0 ];do
		runTcpreplay $1 $2
		shift 2
	done
}
wrapRun $@