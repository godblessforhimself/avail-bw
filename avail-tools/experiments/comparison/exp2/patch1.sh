# 提取可用带宽、包数量
source experiments/comparison/exp2/extract-modified.sh
for dirnamei in $(ls /data/comparison/exp2/);do
	extractAll /data/comparison/exp2/${dirnamei}
done