#### tools
Tools are collected from Internet.

Those can work:
ASSOLO
IGI/PTR
pathChirp
pathload
spruce
STAB
yaz

pathChirp/yaz/spruce gives low abw estimation
yaz never stops
spruce improves results by adding -i option




pathChirp->STAB->ASSOLO 

pathChirp didn't work well

pathload->yaz
yaz didn't work well

IGI/PTR
work well

spruce
didn't work well without -i option


#### sync all code to remote sender and receiver
bash deploy-scripts/quick-deploy.sh
#### fetch bqr data to data/bqr
bash fetch-scripts/fetch-bqr.sh