# avail-bw extraction
plenExtract(){
	# packetLength
	# t1,t2, n, total bytes, avg bytes, avg rate
	methodType=$1
	dirname=$2
	for rate in ${rates[@]};do
		case "${methodType}" in
			"assolo")
				cat data/$dirname/$rate-packetLength|awk 'NR==1{t1=$1}{n++;bytes+=$2}END{printf "%.6f,%d,%d,%d\n",$1-t1,n,bytes,bytes/n}'>data/$dirname/$rate-statistic-packetLength
			;;
			*)
				cat data/$dirname/$rate-packetLength|awk '/^$/ && NR!=1{nn++;printf "%d,%.6f,%d,%d,%d\n",nn,t2-t1,n,bytes,bytes/n} END{nn++;printf "%d,%.6f,%d,%d,%d\n",nn,t2-t1,n,bytes,bytes/n} !/^$/{t2=$1;n++;bytes+=$2} /^$/{getline;t1=$1;n=1;bytes=$2}'>data/$dirname/$rate-statistic-packetLength
			;;
		esac
	done
}
# pathload Low,Up,Mean
# igi      PTR,IGI
# spruce   A
# assolo   A
abwExtract(){
	methodType=$1
	dirname=$2
	for rate in ${rates[@]};do
		case "$methodType" in
			"pathload") cat data/${dirname}/$rate-estimation | awk '/Available bandwidth range : ([0-9\.]+) - ([0-9\.]+) \(Mbps\)/{printf "%.2f,%.2f,%.2f\n",$5,$7,($5+$7)/2}' > data/${dirname}/$rate-statistic-estimation
			;;
			"igi") cat data/${dirname}/$rate-estimation | awk '/PTR:[ ]*([0-9\.]+)[ ]*/{ptr=$2;getline;igi=$2;printf "%.3f,%.3f\n",ptr,igi}' > data/${dirname}/$rate-statistic-estimation
			;;
			"spruce") cat data/${dirname}/$rate-estimation | awk '{print substr($5,2)}' > data/${dirname}/$rate-statistic-estimation
			;;
			"assolo") cat data/${dirname}/$rate-estimation | awk '{print $2}' > data/${dirname}/$rate-statistic-estimation
			;;
		esac
	done
}
main(){
	rates=$(seq 0 100 900)
	methodType=("pathload" "igi" "spruce" "assolo")
	for method in ${methodType[@]};do
		noIC=${method}-noIC
		IC=${method}-IC
		abwExtract $method $noIC
		abwExtract $method $IC
		plenExtract $method $noIC
		plenExtract $method $IC
	done
}
main $@
