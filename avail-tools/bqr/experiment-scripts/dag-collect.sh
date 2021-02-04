for rate in $(seq 0 100 900);do
	bash control-module/dagrun-fetch.sh $rate data/dag-${rate}.txt data/dagin-${rate}.txt data/dagout-${rate}.txt
done
