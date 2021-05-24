import code,copy,matplotlib
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(suppress=True,precision=2)
pathFmt='/data/experiment/ns3/exp1/{:s}'
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
owd={v:r[v]-s[v] for v in traffic}
q=[queue[v][1] for i,v in enumerate(traffic)]
label=['Constant','Poisson','Pareto']

fig=plt.figure(figsize=(1.3,1.1))
offset=5000
for i,v in enumerate(traffic):
	temp=q[i]
	t,y=temp[:,0]/1000,temp[:,1]/1024
	index=np.argmax(y)
	t1=t[0]
	t2=t[index]
	y2=y[index]
	index2=index+np.where(y[index:]<3004/1024)[0][0]
	t3=t[index2]
	y3=y[index2]
	pSender=[numberPacket((s[v]+offset)/1000,t1,t2),numberPacket((s[v]+offset)/1000,t2,t3)]
	pTraffic=[numberPacket((tf[v]+offset)/1000,t1,t2),numberPacket((tf[v]+offset)/1000,t2,t3)]
	totalPacket=pSender[1]+pTraffic[1]
	trafficRate=totalPacket*1502*8e-3/(t3-t2)
	abw=100-trafficRate
	queueRate=(y2-y3)*1024*8e-3/(t3-t2)
	perror=np.abs(queueRate-abw)/abw
	#plt.annotate('High({:.0f},{:.0f})'.format(t2,y2),(t2,y2),(t2-18,y2),arrowprops={'arrowstyle':'->'},color=color[i])
	#plt.annotate('Low({:.0f},{:.0f})'.format(t3,y3),(t3,y3),(t3-18,y3+i*10),arrowprops={'arrowstyle':'->'},color=color[i])
	#plt.annotate('{:s}\nQueue Decreasing Rate: {:.2f}Mbps\nABW: {:.2f}Mbps\nPError: {:.2%}'.format(v,queueRate,abw,perror),xy=(0,0),xytext=(50,80-20*i),color=color[i],ha='center',va='center')
	print(len(t))
	t=t[::50]
	y=y[::50]
	plt.plot(t,y,label=label[i],color=color[i],linestyle=linestyle[i])
plt.xlim(0,70)
plt.xticks(np.arange(0,70+1,10))
plt.yticks(np.arange(0,100+1,20))
plt.xlabel('Time(ms)',labelpad=0)
plt.ylabel('Queue Length(KB)',labelpad=0)
plt.legend(loc='upper right',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
ax=plt.gca()
ax.tick_params('both',length=1,width=1,which='both',pad=1)
plt.savefig('{:s}/ns3-exp1-queue-abw.pdf'.format(imgDir),bbox_inches='tight')
plt.savefig('{:s}/ns3-exp1-queue-abw.eps'.format(imgDir),bbox_inches='tight')
plt.show()
plt.close(fig)
#code.interact(local=dict(globals(),**locals()))