import code,copy,matplotlib
import numpy as np
import matplotlib.pyplot as plt
pathFmt='/data/experiment/ns3/exp2/{:s}'
n=6
traffic=['constant','poisson','pareto']
def wrapLoader(name):
	return np.loadtxt(pathFmt.format(name))
def segmentRate(data,bucket,packetSize=None):
	gran=bucket[1]-bucket[0]
	if packetSize is None:
		x=data[:,0]
		y=data[:,1]
	else:
		x=data
		y=[packetSize]*len(x)
	index=np.searchsorted(x,bucket)
	ret=[]
	for i,v in enumerate(index[:-1]):
		p=np.sum(y[v:index[i+1]])
		rate=p*8/gran
		ret.append(rate)
	return ret
def numberPacket(target,t1,t2):
	ret=np.searchsorted(target,[t1,t2])
	return ret[1]-ret[0]

def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
np.set_printoptions(suppress=True,precision=2)
color=[pickColor(i, 10) for i in range(10)]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
plt.rcParams.update({'font.size':6})
matplotlib.rcParams['hatch.linewidth']=0.3
marker=['d','.','*','<','p'] #5
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1)),(0,(3,1,1,1,1,1))] #5
hatch=['/','\\','x','o','-|'] #5
imgDir='/home/tony/Files/available_bandwidth/thesis-svn/IMC2021/BurstQueueRecovery-jintao/images'

queue={v:[wrapLoader('{:s}/queue-{:d}'.format(v,i)) for i in range(n)] for v in traffic}
s={v:wrapLoader('{:s}/sender'.format(v)) for v in traffic}
r={v:wrapLoader('{:s}/receiver'.format(v)) for v in traffic}
tf={v:wrapLoader('{:s}/traffic'.format(v)) for v in traffic}
tfRate={v:segmentRate(tf[v],np.arange(tf[v][0],tf[v][-1],100e3),1472) for v in traffic}
owd={}
for v in traffic:
	l1=len(r[v])
	l2=len(s[v])
	l=min(l1,l2)
	owd[v]=r[v][:l]-s[v][:l]
qi=5
q=[queue[v][qi] for i,v in enumerate(traffic)]

for v in traffic:
	if v!='pareto':
		fig,ax=plt.subplots(figsize=(1.3,1.1))
		for qi in range(1,4):
			q=queue[v][qi]
			t,y=q[:,0]/1000-qi*5,q[:,1]/1024
			idx=np.searchsorted(t,120)
			t,y=t[:idx:idx//200],y[:idx:idx//200]
			print(len(t))
			plt.plot(t,y,label='queue-{:d}'.format(qi),color=color[qi],linestyle=linestyle[qi])
		plt.ylim(0,80)
		plt.yticks(np.arange(0,80+1,20))
	else:
		fig,ax=plt.subplots(figsize=(3.4,1.1))
		for qi in range(1,6):
			q=queue[v][qi]
			t,y=q[:,0]/1000-qi*5,q[:,1]/1024
			idx=np.searchsorted(t,120)
			t,y=t[:idx:idx//200],y[:idx:idx//200]
			print(len(t))
			plt.plot(t,y,label='queue-{:d}'.format(qi),color=color[qi],linestyle=linestyle[qi%len(linestyle)])
		plt.ylim(0,120)
		plt.yticks(np.arange(0,120+1,20))
	plt.xlim(0,120)
	plt.xticks(np.arange(0,120+1,20))
	
	plt.xlabel('Time(ms)',labelpad=0)
	plt.ylabel('Queue Length(KB)',labelpad=0)
	
	plt.legend(loc='upper right',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)

	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)

	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)

	plt.savefig('{:s}/ns3-exp2-queue-{:s}.pdf'.format(imgDir,v),bbox_inches='tight')
	plt.savefig('{:s}/ns3-exp2-queue-{:s}.eps'.format(imgDir,v),bbox_inches='tight')
	plt.show()
	plt.close(fig)

#code.interact(local=dict(globals(),**locals()))