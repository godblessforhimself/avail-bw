import code,copy,matplotlib
import numpy as np
import matplotlib.pyplot as plt
pathFmt='/data/experiment/ns3/exp2/{:s}'
n=11
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
q=[queue[v][1] for i,v in enumerate(traffic)]

label=['Constant','Poisson','Pareto']
fig,ax=plt.subplots(figsize=(1.3,1.1))
offset=5*2 # 相差两跳
xlim=100
for i,v in enumerate(traffic):
	owdY=owd[v]/1e3
	owdX=s[v][:len(owdY)]/1e3
	index=np.argmax(owdY)
	thres=np.max(owdY[-200:])+.5
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
	idx=np.searchsorted(owdX,xlim)
	print(idx)
	plt.plot(owdX[:idx],owdY[:idx],linestyle=linestyle[i],label=label[i],color=color[i])
	if i!=0:
		pass
		#plt.annotate('Recover({:.0f},{:.0f})'.format(t2,y2),(t2,y2),(t2-14,y2),arrowprops={'arrowstyle':'->'},color=color[i],ha='center',va='center')
	else:
		pass
		#plt.annotate('Recover({:.0f},{:.0f})'.format(t2,y2),(t2,y2),(t2,y2+3),arrowprops={'arrowstyle':'->'},color=color[i],ha='center',va='center')
	#plt.annotate('{:s}\nRealABW: {:.2f}Mbps\nBQRABW: {:.2f}Mbps\nPError: {:.2%}'.format(v,realAbw,bqrAbw,perror),xy=(30,35),xytext=(70,52-4*i),color=color[i],va='center',ha='center')
plt.xlim(0,xlim+1)
plt.xticks(np.arange(0,xlim+1,20))
plt.ylim(30,57)
plt.yticks(np.arange(30,56,5))
plt.legend(loc='upper right',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
ax=plt.gca()
ax.tick_params('both',length=1,width=1,which='both',pad=1)
plt.xlabel('Time(ms)',labelpad=0)
plt.ylabel('One Way Delay(ms)',labelpad=0)
plt.savefig('{:s}/ns3-exp2-bqr.pdf'.format(imgDir),bbox_inches='tight')
plt.savefig('{:s}/ns3-exp2-bqr.eps'.format(imgDir),bbox_inches='tight')
plt.show()
plt.close(fig)
#code.interact(local=dict(globals(),**locals()))