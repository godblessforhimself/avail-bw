#bash control-module/time-update.sh
for rate in $(seq 0 100 900);do
	bash control-module/quickrun-fetch.sh $rate ${rate}.txt
	python analyse-tools/userspace-tool.py --file data/${rate}.txt --save-image
done
