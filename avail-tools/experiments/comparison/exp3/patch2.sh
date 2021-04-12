# 提取可用带宽
source experiments/comparison/exp3/extract-modified.sh
for dirnamei in $(ls /data/comparison/exp3/);do
	extractAll /data/comparison/exp3/${dirnamei}
done