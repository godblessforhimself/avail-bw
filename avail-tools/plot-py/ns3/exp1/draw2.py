# Dowd * C=Dqueue
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
for i,v in enumerate(q):
	#print('{:s}:{:.0f},{:.0f}'.format(traffic[i],np.max(v[:,1]),np.mean(v[:,1])))
	pass

fig,ax1=plt.subplots(figsize=(1.3,1.1))
offset=5000
i=2
v=traffic[i]
color1=color[i]
color2=color[2*i]
owdX=s[v]/1000
owdY=owd[v]/1000
qX,qY=q[i][:,0]/1000,q[i][:,1]/1024
n1,n2=len(owdX),len(qX)
#print(n1,n2)
step1,step2=5,50
if True:
	owdX=owdX[::step1]
	owdY=owdY[::step1]
	qX=qX[::step2]
	qY=qY[::step2]
ln1=ax1.plot(owdX,owdY,label='OWD',color=color1,linestyle=linestyle[0])
ax1.set_xlim(0,40)
ax1.set_xticks(np.arange(0,40+1,10))
min_=30
ax1.set_yticks(np.arange(min_,min_+11,3))
ax1.set_xlabel('Time(ms)',labelpad=0)
ax1.set_ylabel('One Way Delay(ms)',labelpad=0)
#ax1.tick_params(axis='y',labelcolor=color1)
#ax1.annotate('5ms',xy=(9.1,36),xytext=(11,36),va='center',arrowprops={'arrowstyle':'->'})
#ax1.annotate('',xy=(14.4,36),xytext=(12.5,36),arrowprops={'arrowstyle':'->'})
xoffset=14.2
#ax1.annotate('5ms',xy=(9.1+xoffset,36),xytext=(11+xoffset,36),va='center',arrowprops={'arrowstyle':'->'})
#ax1.annotate('',xy=(14.4+xoffset,36),xytext=(12.5+xoffset,36),arrowprops={'arrowstyle':'->'})

ax2=ax1.twinx()
ax2.set_ylabel('Queue Length(KB)',labelpad=0)
ln2=ax2.plot(qX,qY,label='QueueLength',color=color2,linestyle=linestyle[1])
ax2.set_yticks(np.arange(0,120+1,30))

lns=ln1+ln2
labels=[l.get_label() for l in lns]
ax1.legend(lns,labels,loc='lower center',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
ax1.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
ax1.tick_params('both',length=1,width=1,which='both',pad=1)
ax2.tick_params('both',length=1,width=1,which='both',pad=1)
plt.savefig('{:s}/ns3-exp1-queue-owd.pdf'.format(imgDir),bbox_inches='tight')
plt.savefig('{:s}/ns3-exp1-queue-owd.eps'.format(imgDir),bbox_inches='tight')
plt.show()
plt.close(fig)
#code.interact(local=dict(globals(),**locals()))