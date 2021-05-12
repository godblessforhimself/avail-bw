# 用tcpreplay产生流量 caida3 4367Mbps 50s
runTcpreplay(){
	local targetRate=$1
	local duration=$2
	local multiplierV=$(echo "scale=4;${targetRate}/4367"|bc -l)
	local loopNumber=$(echo "scale=0;${targetRate}*${duration}/4367/50+1"|bc -l)
	if [[ ${loopNumber} -lt 1 ]]; then
		loopNumber=1
	fi
	echo "rate:${targetRate}Mbps,replay multiplier:${multiplierV},loop:${loopNumber}"
	time sudo tcpreplay -i ens1f0 --loop=${loopNumber} --multiplier=${multiplierV} --duration=${duration} /home/ubuntu2/pcapFiles/caida3.pcap
}
wrapRun(){
	while [ $# != 0 ];do
		runTcpreplay $1 $2
		shift 2
	done
}
wrapRun $@