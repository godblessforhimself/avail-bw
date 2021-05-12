import code,copy,matplotlib
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(suppress=True,precision=2)
pathFmt='/data/experiment/ns3/exp2/{:s}'
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
owd={}
for v in traffic:
	l1=len(r[v])
	l2=len(s[v])
	l=min(l1,l2)
	owd[v]=r[v][:l]-s[v][:l]
qi=5
q=[queue[v][qi] for i,v in enumerate(traffic)]

for v in traffic:
	fig=plt.figure(figsize=(9,9))
	if v!='pareto':
		for qi in range(1,4):
			color=pickColor(qi,10)
			q=queue[v][qi]
			t,y=q[:,0]/1000-qi*5,q[:,1]/1024	
			plt.plot(t,y,label='queue-{:d}'.format(qi),color=color)
	else:
		for qi in range(1,6):
			color=pickColor(qi,10)
			q=queue[v][qi]
			t,y=q[:,0]/1000-qi*5,q[:,1]/1024	
			plt.plot(t,y,label='queue-{:d}'.format(qi),color=color)
	plt.xlim(0,100)
	plt.xlabel('Time(ms)')
	plt.ylabel('Queue length(KB)')
	plt.grid(linestyle = "--")
	ax=plt.gca()
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	plt.legend(loc='best')
	plt.savefig('/images/ns3/exp2/ns3-exp2-queue-{:s}.pdf'.format(v),bbox_inches='tight')
	plt.savefig('/images/ns3/exp2/ns3-exp2-queue-{:s}.svg'.format(v),bbox_inches='tight')
	#plt.show()
	plt.close(fig)
#code.interact(local=dict(globals(),**locals()))