exp6Filename="data/exp6/all.txt"
groundTruthFilename="data/ground-truth/abw.txt"
groundTruthOutputFilename="data/exp6/gt.txt"
numberFilename="data/exp6/runNumber.txt"
timeFilename="data/exp6/finalTime.txt"
rm -f ${numberFilename}
touch ${numberFilename}
rm -f ${timeFilename}
touch ${timeFilename}
rm -f ${groundTruthOutputFilename}
touch ${groundTruthOutputFilename}
rm -f ${exp6Filename}
touch ${exp6Filename}
for rate in $(seq 0 50 900);do
	dataDir="data/exp6/${rate}"
	if [ -d "${dataDir}" ]; then
		awk '{print $2, $4, $6}' ${dataDir}/predict >> ${exp6Filename}
	else
		echo "Lack ${dataDir}"
	fi
done

cat ${groundTruthFilename} | sed -r 's/.*:(.*)M.*/\1/g' >> ${groundTruthOutputFilename}

# rate,idx,count,time
# (0,1,)count,time

for rate in $(seq 0 50 900);do
	dataDir="data/exp6/${rate}"
	for ((i=1;i<=100;i++));do
		paramFilename="${dataDir}/${i}/parameter.txt"
		number=$(wc -l ${paramFilename}|cut -f 1 -d " ")
		maxTime=$(cat ${paramFilename}|awk 'BEGIN{a=2600}{a=b;b=$NF}END{print a}')
		echo "${number}" >> $numberFilename
		echo "${maxTime}" >> $timeFilename
	done
done
