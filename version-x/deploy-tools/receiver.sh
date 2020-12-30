nice -n -20 taskset -c 8 ./recv-main --output output.txt --port 11106 --polling 1 --busy-poll -1
#./recv-main --output output.txt --port 11106