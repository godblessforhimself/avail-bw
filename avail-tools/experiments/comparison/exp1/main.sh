# 实验1 三跳的实验
# 13组 无中断延迟 一个实验1小时，13小时
# cx=cy=cz=1Gbps
# x=y=z=range(0,900,100)
# x=900,y=z=400
# x=z=400,y=900
# x=y=400,z=900
# 命名：comparison/exp1/x-y-z
source experiments/comparison/exp1/common.sh
rates=($(seq 0 100 900))
for ((loop1=0;loop1<${#rates[@]};loop1++));do
	rate=${rates[${loop1}]}
	name="/home/ubuntu6/data/comparison/exp1/${rate}-${rate}-${rate}"
	taskWithArg ${rate} ${rate} ${rate} 0 ${name}
done
x=(900 400 400)
y=(400 900 400)
z=(400 400 900)
for ((loop1=0;loop1<${#x[@]};loop1++));do
	vx=${x[${loop1}]}
	vy=${y[${loop1}]}
	vz=${z[${loop1}]}
	name="/home/ubuntu6/data/comparison/exp1/${vx}-${vy}-${vz}"
	taskWithArg ${vx} ${vy} ${vz} 0 ${name}
done