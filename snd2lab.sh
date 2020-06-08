#!/bin/bash
rsync -avz --exclude=".git/" --exclude="__pycache__/" --exclude=".ipynb_checkpoints/" --exclude="*.ipynb" --exclude="*.pcap" ../avail-bw jintao@219.223.189.204:~
