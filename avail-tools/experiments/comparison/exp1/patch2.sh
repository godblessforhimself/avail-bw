# 在本地运行
# 提取关键内容
source experiments/comparison/exp1/extract.sh
for dirnamei in $(ls /data/comparison/exp1/);do
	extractAll /data/comparison/exp1/${dirnamei}
done