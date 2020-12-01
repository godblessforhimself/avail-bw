rm data/log.txt
touch data/log.txt
for rate in $(seq 0 100 900);do
	python prediction-model/predict.py --file data/${rate}.txt --ln 100 --psz 1472 --isz 24 >> data/log.txt
done