mkdir -p data/exp2
rm -f data/exp2/log.txt
touch data/exp2/log.txt
rate_set=$(seq 0 50 900)
f1(){
	for rate in ${rate_set};do
		bash control-module/quickrun-fetch.sh $rate data/exp2/${rate}.txt deploy-tools/sender-exp2.sh
	done
}
f2(){
	for rate in ${rate_set};do
		python prediction-model/predict.py --file data/exp2/${rate}.txt --ln 100 --psz 1472 --isz 1472 >> data/exp2/log.txt
		printf "\n" >> data/exp2/log.txt
	done
}
f3(){
	python analyse-tools/multi-plot.py --file-ranger 0 50 350 --prefix-suffix data/exp2/ .txt --width 4 --save-image data/exp2/p1.png
	python analyse-tools/multi-plot.py --file-ranger 400 50 700 --prefix-suffix data/exp2/ .txt --width 3 --save-image data/exp2/p2.png
	python analyse-tools/multi-plot.py --file-ranger 750 50 900 --prefix-suffix data/exp2/ .txt --width 2 --save-image data/exp2/p3.png
}
if [ $# -eq 0 ];then
	f1
	f2
	f3
fi
if [[ $# -eq 1 && $1 == "1" ]];then
	f1
elif [[ $# -eq 1 && $1 == "2" ]];then
	f2
fi
