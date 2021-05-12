# Dowd * C=Dqueue
import code,copy,matplotlib
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(suppress=True,precision=2)
pathFmt='/data/experiment/ns3/exp1/{:s}'
n=6
traffic=['constant','poisson','pareto']
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
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
queue={v:[wrapLoader('{:s}/queue-{:d}'.format(v,i)) for i in range(n)] for v in traffic}
s={v:wrapLoader('{:s}/sender'.format(v)) for v in traffic}
r={v:wrapLoader('{:s}/receiver'.format(v)) for v in traffic}
tf={v:wrapLoader('{:s}/traffic'.format(v)) for v in traffic}
tfRate={v:segmentRate(tf[v],np.arange(tf[v][0],tf[v][-1],100e3),1472) for v in traffic}
owd={v:r[v]-s[v] for v in traffic}
q=[queue[v][1] for i,v in enumerate(traffic)]
for i,v in enumerate(q):
	print('{:s}:{:.0f},{:.0f}'.format(traffic[i],np.max(v[:,1]),np.mean(v[:,1])))

fig,ax1=plt.subplots(figsize=(9,9))
offset=5000
i=2
v=traffic[i]
color1=pickColor(i,10)
color2=pickColor(i*2,10)
owdX=s[v]/1000
owdY=owd[v]/1000
qX,qY=q[i][:,0]/1000,q[i][:,1]/1024
ln1=ax1.plot(owdX,owdY,label='owd-{:s}'.format(v),color=color1)
ax1.set_xlim(0,40)
ax1.set_xlabel('Time(ms)')
ax1.set_ylabel('One way delay(ms)',color=color1)
ax1.tick_params(axis='y',labelcolor=color1)
ax1.annotate('5ms',xy=(9.1,36),xytext=(11,36),va='center',arrowprops={'arrowstyle':'->'})
ax1.annotate('',xy=(14.4,36),xytext=(12.5,36),arrowprops={'arrowstyle':'->'})
xoffset=14.2
ax1.annotate('5ms',xy=(9.1+xoffset,36),xytext=(11+xoffset,36),va='center',arrowprops={'arrowstyle':'->'})
ax1.annotate('',xy=(14.4+xoffset,36),xytext=(12.5+xoffset,36),arrowprops={'arrowstyle':'->'})

ax2=ax1.twinx()
ax2.set_ylabel('Queue length(KB)',color=color2)
ln2=ax2.plot(qX,qY,label='queue-{:s}'.format(v),color=color2)
ax2.tick_params(axis='y',labelcolor=color2)

lns=ln1+ln2
labels=[l.get_label() for l in lns]
ax1.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax1.legend(lns,labels,loc='best')
ax1.grid(linestyle='--')
plt.savefig('/images/ns3/exp1/ns3-exp1-queue-owd.pdf',bbox_inches='tight')
plt.savefig('/images/ns3/exp1/ns3-exp1-queue-owd.svg',bbox_inches='tight')
plt.clf()
#code.interact(local=dict(globals(),**locals()))