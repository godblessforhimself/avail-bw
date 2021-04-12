# 存放所有提取函数 (与2的区别：删除pnum)
# 提取带宽预测结果为abw
fbqr(){
	# 提取result.txt非空行的第一列
	cat $1/result.txt | awk '!/^$/{printf "%.2f\n",$1}' > $1/abw
}
fpathload(){
	cat $1/rx | awk '/Available bandwidth range : ([0-9\.]+) - ([0-9\.]+) \(Mbps\)/{printf "%.2f\n",($5+$7)/2}' > $1/abw
}
figi(){
	cat $1/tx | awk '/PTR:[ ]*([0-9\.]+)[ ]*/{printf "%.2f\n",$2}' > $1/abw
}
fassolo(){
	cat $1/instbw | awk '{printf "%.2f\n",$2}' > $1/abw
}
extractAll(){
	fbqr $1/BQR
	fpathload $1/pathload
	figi $1/igi
	fassolo $1/assolo
}