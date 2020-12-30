# 如果网卡在5ms内没有包，它接收到的包会被延迟50us。
# 一段时间内没有收到包时，网卡到用户态的延迟会有增加。
mkdir -p data/exp3
rm -f data/exp3/log.txt
touch data/exp3/log.txt
rate_set=(0 200 400 600 800)
# bash experiment-scripts/exp3.sh 1
f1(){
	for rate in ${rate_set[@]};do
		bash control-module/dagrun-fetch.sh $rate data/exp3/${rate}.txt data/exp3/in-${rate}.txt data/exp3/out-${rate}.txt 5 deploy-tools/sender-exp3.sh
	done
}
f3(){
	python analyse-tools/multi-plot.py --file-ranger 0 50 350 --prefix-suffix data/exp3/ .txt --width 4 --save-image data/exp3/p1.png
	python analyse-tools/multi-plot.py --file-ranger 400 50 700 --prefix-suffix data/exp3/ .txt --width 3 --save-image data/exp3/p2.png
	python analyse-tools/multi-plot.py --file-ranger 750 50 900 --prefix-suffix data/exp3/ .txt --width 2 --save-image data/exp3/p3.png
}
if [ $# -eq 0 ];then
	f1
	f3
fi
if [[ $# -eq 1 && $1 == "1" ]];then
	f1
elif [[ $# -eq 1 && $1 == "2" ]];then
	f3
fi
