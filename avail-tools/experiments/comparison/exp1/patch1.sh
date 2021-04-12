# patch1 重新运行所有BQR
# BQR：
# 旧：前10个包将可用带宽区间均匀划分，
# 当第9、第10个包队列实际清空，但是OWD大于后10个单向延迟+50时
# 将会陷入低估可用带宽的局部
# 新：前n1个包将可用带宽区间均匀划分，后n2个包间隔均匀分布在恢复时间x两侧。n1=60 n2=40
source experiments/comparison/exp1/common.sh
rates=($(seq 0 100 900))
for ((loop1=0;loop1<${#rates[@]};loop1++));do
	rate=${rates[${loop1}]}
	name="/home/ubuntu6/data/comparison/exp1/${rate}-${rate}-${rate}"
	taskWithOne ${rate} ${rate} ${rate} 0 ${name} BQR
done
x=(900 400 400)
y=(400 900 400)
z=(400 400 900)
for ((loop1=0;loop1<${#x[@]};loop1++));do
	vx=${x[${loop1}]}
	vy=${y[${loop1}]}
	vz=${z[${loop1}]}
	name="/home/ubuntu6/data/comparison/exp1/${vx}-${vy}-${vz}"
	taskWithOne ${vx} ${vy} ${vz} 0 ${name} BQR
done