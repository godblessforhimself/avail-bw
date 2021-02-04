for rate in $(seq 0 100 900);do
	filename=data/spruce-problem/${rate}.txt
	rm -f ${filename} && touch ${filename}
	for ((i=1;i<=100;i++));do
		cat "data/spruce-problem/${rate}-${i}.data" | awk '{print substr($5,2)}' >> ${filename}
	done
done