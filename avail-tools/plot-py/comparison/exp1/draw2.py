# 实验一
# 平均包开销 PacketOverhead
# /data/comparison/exp1
# x-y-z
# BQR assolo igi pathload spruce
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code,matplotlib
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
np.set_printoptions(suppress=True,precision=2)
color=[pickColor(i, 10) for i in range(10)]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
plt.rcParams.update({'font.size':7})
matplotlib.rcParams['hatch.linewidth']=0.3
marker=['d','.','*','<','p'] #5
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1))] #4
hatch=['/','\\','x','o','-|'] #5
imgDir='/home/tony/Files/available_bandwidth/thesis-svn/IMC2021/BurstQueueRecovery-jintao/images'


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
	fig=plt.figure(figsize=(3.4,1.1))
	l1,l2=packet.shape
	xtick=np.arange(1,10,2)
	width=1.6/l2
	for i in range(l2):
		plt.bar(xtick+i*width,packet[1:10:2,i]*1500/1024/1024+10,bottom=-10,width=width,label=label[i],edgecolor=color[i],fill=False,hatch=hatch[i]*5,linewidth=0.5)
	#plt.xticks(xtick+(l2-1)*width/2,['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(1,10,2)],rotation=0)
	plt.xticks(xtick+(l2-1)*width/2,['{}'.format(x[i]) for i in range(1,10,2)],rotation=0)
	plt.ylim(-5,20)
	plt.yticks(np.arange(0,15+1,5))
	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='major',pad=1)
	plt.legend(loc='upper center',framealpha=.5,ncol=5,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=6)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	plt.xlabel('Traffic Settings(Mbps)',labelpad=0)
	plt.ylabel('Packet Cost(MB)',labelpad=0)
	plt.savefig('{:s}/exp1-PacketCost.eps'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp1-PacketCost.pdf'.format(imgDir),bbox_inches='tight')
	plt.show()
	plt.close(fig)
	#code.interact(local=dict(globals(),**locals()))