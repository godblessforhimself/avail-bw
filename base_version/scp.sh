#scp -r ../avail-bw liqing@10.10.114.19:~
rsync -avz --exclude=".git/" --exclude="data/" --exclude="temp/" --exclude="__pycache__/" --exclude=".ipynb_checkpoints/" --exclude="*.ipynb" ../avail-bw liqing@10.10.114.19:~
