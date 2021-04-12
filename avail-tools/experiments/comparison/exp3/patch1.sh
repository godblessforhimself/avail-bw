# 实验3 补充实验
# 紧链路非窄链路
# Link4 speed=1Gbps
# Link3 speed=100Mbps
# cx=cz=1Gbps,cy=100Mbps
# 900,0,0
# 900,0,400 
# 900,0,900 
# 900,20,900
# 0,0,900   
# 400,0,900 
# 400,20,900
# 0,0,0
# 0,20,0
# 0,40,0
# 400,0,400
# 400,20,400
# 400,40,400
source experiments/comparison/exp3/common-modified.sh
dirname="/home/ubuntu6/data/comparison/exp3"
tbegin=$(date)
taskWithArg 900 0 0 0 "${dirname}/900-0-0"
taskWithArg 900 0 400 0 "${dirname}/900-0-400"
taskWithArg 900 0 900 0 "${dirname}/900-0-900"
taskWithArg 900 20 900 0 "${dirname}/900-20-900"
taskWithArg 0 0 900 0 "${dirname}/0-0-900"
taskWithArg 400 0 900 0 "${dirname}/400-0-900"
taskWithArg 400 20 900 0 "${dirname}/400-20-900"

taskWithArg 0 0 0 0 "${dirname}/0-0-0"
taskWithArg 0 20 0 0 "${dirname}/0-20-0"
taskWithArg 0 40 0 0 "${dirname}/0-40-0"
taskWithArg 0 60 0 0 "${dirname}/0-60-0"
taskWithArg 400 0 400 0 "${dirname}/400-0-400"
taskWithArg 400 20 400 0 "${dirname}/400-20-400"
taskWithArg 400 40 400 0 "${dirname}/400-40-400"
taskWithArg 400 60 400 0 "${dirname}/400-60-400"
tend=$(date)
echo "${tbegin}->${tend}" >> /home/ubuntu6/data/comparison/exp3.log