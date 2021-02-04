# 多次重复以减小随机性，重复次数为
# 测量相同背景流量时不关闭iperf3
mainDirectory="data/exp6"
rate_set=$(seq 0 50 900)
sampleNumber=100
# bash experiment-scripts/exp6.sh
f1(){
	rm -rf ${mainDirectory}
	mkdir -p ${mainDirectory}
	ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/clean-up-traffic.sh" >/dev/null
	for rate in ${rate_set[@]};do
		printf "data for %4s: $(date)\n" ${rate}
		ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/set-up-traffic.sh ${rate}" >/dev/null
		for (( i=1; i<= ${sampleNumber}; ++i));do
			bash experiment-scripts/param-update.sh -1 ${mainDirectory}/${rate}/${i}
		done
		ssh -p 3970 amax@aliyun.ylxdzsw.com \
"cd ~/jintao_test/version-x; bash control-module/clean-up-traffic.sh" >/dev/null
	done
}
f2(){
	for rate in ${rate_set[@]};do
		logFilename="${mainDirectory}/${rate}/log"
		outputFilename="${mainDirectory}/${rate}/predict"
		rm -f ${logFilename} ${outputFilename}
		printf "predicting for ${rate}\n"
		for (( i=1; i<= ${sampleNumber}; ++i));do
			echo "$i" >> ${logFilename}
			python prediction-model/predict.py --file ${mainDirectory}/${rate}/${i}/lastRun --ln 100 --psz 1472 --isz 1472 --log ${logFilename} --output ${outputFilename}
		done
	done
}

if [[ $# -eq 1 && $1 == "1" ]];then
	f1
elif [[ $# -eq 1 && $1 == "2" ]];then
	f2
fi
