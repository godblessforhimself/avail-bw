# 因为0-600-0和600-0-0运行了两次，结果累积了
# 重新运行
source experiments/comparison/exp2/common-modified.sh
x=600
y=0
z=0
name="/home/ubuntu6/data/comparison/exp2/${x}-${y}-${z}"
rm -rf ${name}/*
taskWithArg ${x} ${y} ${z} 0 ${name}
x=0
y=600
z=0
name="/home/ubuntu6/data/comparison/exp2/${x}-${y}-${z}"
rm -rf ${name}/*
taskWithArg ${x} ${y} ${z} 0 ${name}