for rate in $(seq 0 100 900);do
	bash control-module/dagrun-fetch.sh $rate dag-${rate}.txt dagin-${rate}.txt dagout-${rate}.txt
done
