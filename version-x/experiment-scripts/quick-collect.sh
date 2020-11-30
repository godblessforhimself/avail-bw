for rate in $(seq 0 100 900);do
bash control-module/quickrun-fetch.sh $rate ${rate}.txt
done