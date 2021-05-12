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

plt.figure(figsize=(9,9))
offset=5000
for i,v in enumerate(traffic):
	color=pickColor(i,10)
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
	plt.annotate('High({:.0f},{:.0f})'.format(t2,y2),(t2,y2),(t2-10,y2),arrowprops={'arrowstyle':'->'},color=color)
	plt.annotate('Low({:.0f},{:.0f})'.format(t3,y3),(t3,y3),(t3-14,y3+i*10),arrowprops={'arrowstyle':'->'},color=color)
	plt.annotate('{:s}\nQueue decreasing rate: {:.2f}Mbps\nAbw: {:.2f}Mbps\nPerror: {:.2%}'.format(v,queueRate,abw,perror),xy=(0,0),xytext=(40,90-20*i),color=color,ha='center',va='center')
	plt.plot(t,y,label=v,color=color)
	plt.xlim(0,50)
	plt.xlabel('Time(ms)')
	plt.ylabel('Queue length(KB)')
	plt.grid(linestyle = "--")
	ax=plt.gca()
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	plt.legend(loc='best',framealpha=1.0)
plt.savefig('/images/ns3/exp1/ns3-exp1-queue-abw.pdf',bbox_inches='tight')
plt.savefig('/images/ns3/exp1/ns3-exp1-queue-abw.svg',bbox_inches='tight')
plt.show()
#plt.clf()
#code.interact(local=dict(globals(),**locals()))