# 流量的突发性
import code,copy,matplotlib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
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
	return np.sort(ret)
def numberPacket(target,t1,t2):
	ret=np.searchsorted(target,[t1,t2])
	return ret[1]-ret[0]
def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
def cdf(a,p=100):
	x,y=np.sort(a),np.arange(len(a))/len(a)*p
	return x,y
def pareto(a,mean=171):
	scale=mean*(a-1)/a
	r=scale*(np.random.pareto(a,1000)+1)
	print(r.mean())

queue={v:[wrapLoader('{:s}/queue-{:d}'.format(v,i)) for i in range(n)] for v in traffic}
s={v:wrapLoader('{:s}/sender'.format(v)) for v in traffic}
r={v:wrapLoader('{:s}/receiver'.format(v)) for v in traffic}
tf={v:wrapLoader('{:s}/traffic'.format(v)) for v in traffic}
granularity=40e3
rate={v:segmentRate(tf[v],np.arange(tf[v][0],tf[v][-1],granularity),1472) for v in traffic}
rateList=[rate[v] for v in traffic]
print(len(rateList[0]))
p1,p2=10,90
head=[np.percentile(r,p1) for r in rateList]
tail=[np.percentile(r,p2) for r in rateList]
mean=[np.mean(r) for r in rateList]
data=np.array([head,tail,mean]).T
v1=(data[1,0]-70)/70*100
v2=(data[1,1]-70)/70*100
print(v1,v2)
column=['{:d}%'.format(p1),'{:d}%'.format(p2),'mean']
index=['constant','poisson','pareto']
df=pd.DataFrame(data,index=index,columns=column)
df.index.name='type'
df.to_csv('/data/ns3-csv/ns3-exp2-traffic.csv',float_format='%.2f')

fig=plt.figure(figsize=(9,9))
for i,v in enumerate(traffic):
	x,y=cdf(rate[v])
	plt.plot(x,y,color=pickColor(i,10),label=v)
plt.xlabel('Rate(Mbps)')
plt.ylabel('Percentage(%)')
plt.grid(linestyle='--')
ax=plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.legend(loc='best')
plt.savefig('/images/ns3/exp2/ns3-exp2-traffic-cdf.pdf',bbox_inches='tight')
plt.savefig('/images/ns3/exp2/ns3-exp2-traffic-cdf.svg',bbox_inches='tight')

#code.interact(local=dict(globals(),**locals()))