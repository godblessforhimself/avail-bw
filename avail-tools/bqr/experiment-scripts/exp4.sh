# 用户态发包和实际的差距
rm -rf data/exp4
mkdir -p data/exp4
rate_set=(0 200 400 600 800)
# bash experiment-scripts/exp4.sh
f1(){
	for rate in ${rate_set[@]};do
		bash control-module/dagrun-fetch.sh $rate data/exp4/${rate}.txt data/exp4/in-${rate}.txt data/exp4/out-${rate}.txt 5 deploy-tools/sender-bak.sh
	done
}
if [ $# -eq 0 ];then
	f1
fi
