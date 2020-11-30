usage:
taskset -c 2 ./recv-main --output output.txt --port 11106
taskset -c 3 ./send-main --speed 100 --size 1472 --dest 127.0.0.1 --port 11106 --number 100 --inspect 12000 12200 13000 14000

taskset -c 2 ./recv-main --output output.txt --port 11106
taskset -c 3 ./send-main --speed 1500 --size 1472 --dest 192.168.5.1 --port 11106 --number 100 --inspect 1070 1189 1334 1516 1749 2061 2497 3150 4239 6418

for i in range(11):
	A=1100-20*i
	t=1472*8*(100+i)/A
	print(t)

taskset -c 3 ./send-main --speed 1500 --size 1472 --dest 192.168.5.1 --port 11106 --number 100 --inspect 1177.6 1188.5 1199.8 1211.6 1223.8 1236.5 1249.7 1263.5 1277.8 1292.8 1308.4

taskset -c 3 ./send-main --speed 1500 --size 1472 --dest 192.168.5.1 --port 11106 --number 100 --inspect 800 900 1000 1100 1200

* timestamp is stored in struct timestamp_packet
* when saved, precision is 6, send time-offset space recv time - offset