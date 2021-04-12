# 3 紧链路非窄链路
# Link4 speed=1Gbps
# Link3 speed=100Mbps
# cx=cz=1Gbps,cy=100Mbps
# 900,0,0              紧链路在窄链路前
# 900,0,400            紧链路在窄链路前，干扰1
# 900,0,900            紧链路在窄链路前，干扰2
# 900,20,900           紧链路在窄链路前，干扰3
# 0,0,900              紧链路在窄链路后
# 400,0,900            紧链路在窄链路后，干扰1
# 400,20,900           紧链路在窄链路后，干扰2
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
tend=$(date)
echo "${tbegin}->${tend}" > /home/ubuntu6/data/comparison/exp3.log