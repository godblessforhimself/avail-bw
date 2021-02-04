# bash experiment-scripts/param-update.sh trafficRate mainDirectory
# bash experiment-scripts/param-update.sh 800 data/800
# bash experiment-scripts/param-update.sh -1 data/800 -> don't set traffic!
# input param
trafficRate=$1
mainDirectory=$2
# constant
runIteration=1
iterationMax=5
defaultParam="deploy-tools/sender-bak.sh"
suggestDirectory="${mainDirectory}/suggest"
paramList="${mainDirectory}/parameter.txt"
metricFilename="${mainDirectory}/metric"
dataDirectory="${mainDirectory}/dataStorage"
tempScript="deploy-tools/temp.sh"
# directory
rm -rf ${mainDirectory}
mkdir -p ${mainDirectory} ${dataDirectory} ${suggestDirectory}
echo "param-update: create ${mainDirectory}"
cp ${defaultParam} ${paramList}
cp ${defaultParam} ${suggestDirectory}/${runIteration}
cp ${defaultParam} ${tempScript}


run_once(){
	# copy param to sender
	bash deploy-tools/quick-deploy.sh 2>&1 >/dev/null
	# run and fetch data
	latestData=${dataDirectory}/${runIteration}
	if [[ "${trafficRate}" != "-1" ]];then
		bash control-module/quickrun-fetch.sh ${trafficRate} ${latestData} ${tempScript} 2>&1 >/dev/null
	elif [[ "${trafficRate}" == "-1" ]];then
		bash control-module/quick-run-no-traffic.sh ${latestData} ${tempScript} 2>&1 >/dev/null
	fi
	# update iteration
	prevIteration=${runIteration}
	runIteration=$((${runIteration}+1))
}
suggest(){
	oldParam=${suggestDirectory}/${prevIteration}
	newParam=${suggestDirectory}/${runIteration}
	python suggestion-model/suggest.py --old-param ${oldParam} --data ${latestData} --new-param ${newParam} --metric ${metricFilename} 2>&1 >/dev/null
	result=$?
	echo "" >> ${paramList}
	cat ${newParam} >> ${paramList}
	cp ${newParam} ${tempScript}
	echo $result
}
#printf "iteration ${runIteration}\n"

run_once
cond=$(suggest)

while [[ $cond -ne 0 && $runIteration -le $iterationMax ]];
do
	#printf "iteration ${runIteration}\n"
	run_once
	cond=$(suggest)
done

cp ${dataDirectory}/${prevIteration} ${mainDirectory}/lastRun