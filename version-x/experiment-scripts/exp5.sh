# 参数调整进行测试
# 不平滑gout改进了效果
mainDirectory="data/exp5"
logFilename="${mainDirectory}/log"
outputFilename="${mainDirectory}/predict"
rate_set=(0 200 400 600 800)
# bash experiment-scripts/exp5.sh
f1(){
	rm -rf ${mainDirectory}
	mkdir -p ${mainDirectory}
	for rate in ${rate_set[@]};do
		printf "finding best data for ${rate}\n"
		bash experiment-scripts/param-update.sh ${rate} ${mainDirectory}/${rate}
	done
}
f2(){
	rm -f ${logFilename} ${outputFilename}
	for rate in ${rate_set[@]};do
		printf "predicting for ${rate}\n"
		echo "${rate}" >> ${outputFilename}
		python prediction-model/predict.py --file ${mainDirectory}/${rate}/lastRun --ln 100 --psz 1472 --isz 1472 --log ${logFilename} --output ${outputFilename}
	done
}
if [ $# -eq 0 ];then
	f1
fi
if [[ $# -eq 1 && $1 == "1" ]];then
	f1
elif [[ $# -eq 1 && $1 == "2" ]];then
	f2
fi
