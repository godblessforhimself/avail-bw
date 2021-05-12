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
def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
color=[pickColor(i, 10) for i in range(10)]
plt.rcParams.update({'font.size': 15})

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
	label=['BQR','ASSOLO','PTR','pathload','Spruce']
	index=['{:d}-{:d}-{:d}({:.0f})'.format(x[i],y[i],z[i],truth[i,0]) for i in range(N)]
	df=pd.DataFrame(packet,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-csv/exp1-packet.csv',float_format='%.2f')
	fig=plt.figure(figsize=(10,10))
	l1,l2=packet.shape
	xtick=np.arange(1,10,2)
	width=1.6/l2
	for i in range(l2):
		plt.bar(xtick+i*width,packet[1:10:2,i]*1500/1024/1024,width=width,label=label[i],color=color[i])
	plt.xticks(xtick+(l2-1)*width/2,['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(1,10,2)],rotation=0)
	ax=plt.gca()
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	plt.legend()
	plt.grid(axis='y',linestyle="--")
	plt.xlabel('Traffic Settings(Mbps)')
	plt.ylabel('Packet Cost(MB)')
	plt.savefig('/images/comparison/exp1/exp1-PacketCost.eps',bbox_inches='tight')
	plt.savefig('/images/comparison/exp1/exp1-PacketCost.pdf',bbox_inches='tight')
	#code.interact(local=dict(globals(),**locals()))