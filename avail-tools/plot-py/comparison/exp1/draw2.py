# 实验一
# 平均包开销
# /data/comparison/exp1
# x-y-z
# BQR assolo igi pathload spruce
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code
rates=range(0,900+1,100)
x=[i for i in rates]
y=[i for i in rates]
z=[i for i in rates]
x.extend([900,400,400])
y.extend([400,900,400])
z.extend([400,400,900])
dirname='/data/comparison/exp1/{}-{}-{}/{}'
methods=['BQR','assolo','igi','pathload','spruce']
N=len(x)
M=len(methods)
Capacity=957.14
Discard=10
if __name__=='__main__':
	packet=[]
	for i in range(N):
		item=[]
		for j in range(M):
			prefix=dirname.format(x[i],y[i],z[i],methods[j])
			abwfile='{}/abw'.format(prefix)
			measureNumber=len(np.loadtxt(abwfile))
			packetfile='{}/packet'.format(prefix)
			packetNumber=np.loadtxt(packetfile).ravel()[0]
			avg=packetNumber/measureNumber
			item.append(avg)
		packet.append(item)
	packet=np.array(packet)
	# 获取13个ground-truth
	truth=[]
	for i in range(N):
		truth.append(Capacity-max(x[i],y[i],z[i]))
	truth=np.array(truth).reshape((-1,1))
	# packet = (13,5) 保存到csv中
	label=['BQR','ASSOLO','PTR','pathload','spruce']
	index=['{:d}-{:d}-{:d}({:.0f})'.format(x[i],y[i],z[i],truth[i,0]) for i in range(N)]
	df=pd.DataFrame(packet,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-csv/exp1-packet.csv',float_format='%.2f')
	#code.interact(local=dict(globals(),**locals()))