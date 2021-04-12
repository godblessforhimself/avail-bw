# 存放所有提取函数
# 为了方便python读取
# 提取带宽预测结果为abw
# 100次发送的包数量packet
# 发包时间具有一定复杂性
pnum(){
	cat $1 | awk '!/^$/{pnum+=1}END{print pnum}'
}
fbqr(){
	# 提取result.txt非空行的第一列
	cat $1/result.txt | awk '!/^$/{printf "%.2f\n",$1}' > $1/abw
	pnum $1/dagsnap.txt > $1/packet
}
fpathload(){
	cat $1/rx | awk '/Available bandwidth range : ([0-9\.]+) - ([0-9\.]+) \(Mbps\)/{printf "%.2f\n",($5+$7)/2}' > $1/abw
	pnum $1/dagsnap > $1/packet
}
figi(){
	cat $1/tx | awk '/PTR:[ ]*([0-9\.]+)[ ]*/{printf "%.2f\n",$2}' > $1/abw
	pnum $1/dagsnap > $1/packet
}
fassolo(){
	cat $1/instbw | awk '{printf "%.2f\n",$2}' > $1/abw
	pnum $1/dagsnap.txt > $1/packet
}
fspruce(){
	cat $1/rx | awk '{printf "%.2f\n",$3/1000}' > $1/abw
	pnum $1/dagsnap > $1/packet
}
extractAll(){
	fbqr $1/BQR
	fpathload $1/pathload
	figi $1/igi
	fassolo $1/assolo
	fspruce $1/spruce
}