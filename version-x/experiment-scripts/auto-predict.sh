rm data/log.txt
touch data/log.txt
for rate in $(seq 0 100 900);do
	python prediction-model/predict.py --file data/${rate}.txt --ln 100 --psz 1472 --isz 1472 >> data/log.txt
	printf "\n" >> data/log.txt
done