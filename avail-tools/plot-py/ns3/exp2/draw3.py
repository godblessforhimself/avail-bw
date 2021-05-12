import code,copy,matplotlib
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(suppress=True,precision=2)
pathFmt='/data/experiment/ns3/exp2/{:s}'
n=11
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
q=[queue[v][1] for i,v in enumerate(traffic)]

fig,ax=plt.subplots(figsize=(9,9))
offset=5*2 # 相差两跳
for i,v in enumerate(traffic):
	color=pickColor(i,10)
	owdY=owd[v]/1e3
	owdX=s[v][:len(owdY)]/1e3
	index=np.argmax(owdY)
	thres=np.min(owdY[-10:])+.5
	position=index+np.where(owdY[index:]<thres)[0][0]
	t1=owdX[0]
	t2=owdX[position]
	y1=owdY[0]
	y2=owdY[position]
	trafficNumber=numberPacket(tf[v]*1e-3-offset,t1,t2)
	probeNumber=numberPacket(owdX,t1,t2)
	realAbw=100-trafficNumber*1502*8e-3/(t2-t1+1e-5)
	bqrAbw=probeNumber*1502*8e-3/(t2-t1+1e-5)
	perror=np.abs(bqrAbw-realAbw)/realAbw
	plt.plot(owdX,owdY,marker='.',label=v,color=color)
	#plt.scatter(owdX,owdY,s=1,label=v,color=color)
	if i!=0:
		plt.annotate('Recover({:.0f},{:.0f})'.format(t2,y2),(t2,y2),(t2-15,y2),arrowprops={'arrowstyle':'->'},color=color,ha='center',va='center')
	else:
		plt.annotate('Recover({:.0f},{:.0f})'.format(t2,y2),(t2,y2),(t2,y2+3),arrowprops={'arrowstyle':'->'},color=color,ha='center',va='center')
	plt.annotate('{:s}\nRealAbw: {:.2f}Mbps\nBQRAbw: {:.2f}Mbps\nPerror: {:.2%}'.format(v,realAbw,bqrAbw,perror),xy=(30,35),xytext=(70,52-4*i),color=color,va='center',ha='center')
plt.grid(linestyle='--')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xlim(0,100)
plt.ylim(30,57)
plt.legend(loc='best')
plt.xlabel('Time(ms)')
plt.ylabel('One way delay(ms)')
plt.savefig('/images/ns3/exp2/ns3-exp2-bqr.pdf',bbox_inches='tight')
plt.savefig('/images/ns3/exp2/ns3-exp2-bqr.svg',bbox_inches='tight')
#plt.show()
plt.clf()
#code.interact(local=dict(globals(),**locals()))