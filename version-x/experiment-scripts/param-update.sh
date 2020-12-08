rate=700
cp deploy-tools/sender-bak.sh deploy-tools/sender.sh
bash deploy-tools/quick-deploy.sh
bash control-module/quickrun-fetch.sh $rate iter-1.txt

python suggestion-model/suggest.py --data data/iter-1.txt --old-param deploy-tools/sender.sh --new-param deploy-tools/sender.sh --metric data/metric

bash deploy-tools/quick-deploy.sh
bash control-module/quickrun-fetch.sh $rate iter-2.txt

python suggestion-model/suggest.py --data data/iter-2.txt --old-param deploy-tools/sender.sh --metric data/metric

python analyse-tools/multi-plot.py --file data/iter-1.txt data/iter-2.txt --raw-compare --width 2 --show-image