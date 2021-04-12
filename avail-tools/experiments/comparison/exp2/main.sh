# ADR和spruce真实效果
# 修改Link4为XGigabytes
# cx=cy=1Gbps,cz=10Gbps，启用DAG，注意记录spruce接收处的时间
# x=600 y=range(0,500,100) z=0
# x=range(0,500,100) y=600 z=0
source experiments/comparison/exp2/common-modified.sh
rates=($(seq 0 100 500))
x=600
z=0
for ((loopi=0;loopi<${#rates[@]};loopi++));do
	y=${rates[${loopi}]}
	name="/home/ubuntu6/data/comparison/exp2/${x}-${y}-${z}"
	taskWithArg ${x} ${y} ${z} 0 ${name}
done
y=600
for ((loopi=0;loopi<${#rates[@]};loopi++));do
	x=${rates[${loopi}]}
	name="/home/ubuntu6/data/comparison/exp2/${x}-${y}-${z}"
	taskWithArg ${x} ${y} ${z} 0 ${name}
done