#scp -r ../avail-bw liqing@10.10.114.19:~
rsync -a --exclude=".git/" --exclude="data/" --exclude="__pycache__/" --exclude=".ipynb_checkpoints/" --exclude="*.ipynb" ../avail-bw liqing@10.10.114.19:~
