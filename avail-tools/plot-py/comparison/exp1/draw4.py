# 实验一，实际的时间
# ASSOLO：使用1ms的阈值，最后两个包无用
# pathload：大于1e5us=100ms的有99个，它们是测量间隔；
# igi：测量间间隔大于1e5
# bqr：1e4us=10ms的间隔
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code,time,os
np.set_printoptions(suppress=True)
delta=lambda a: a[...,1:]-a[...,:-1]
rates=range(0,900+1,100)
x=[i for i in rates]
y=[i for i in rates]
z=[i for i in rates]
x.extend([900,400,400])
y.extend([400,900,400])
z.extend([400,400,900])
dirname='/data/comparison/exp1/{}-{}-{}/{}'
methods=['BQR','assolo','igi','pathload','spruce']
suffix=['dagsnap.txt','dagsnap.txt','dagsnap','dagsnap','dagsnap']
N=len(x)
M=len(methods)
Capacity=957.14
Discard=10
cacheFilename='/data/comparison/exp1-cache/gap.npy'
cache2='/data/comparison/exp1-cache/draw3.npz'
th1=[1e4,1e3,1e5,1e5]
th2=[10,10,10,6]
def getTimeFun(g,th1,th2):
	idx=np.where(g>th1)[0]
	lidx=len(idx)
	ret=[]
	for i in range(lidx):
		if i==0:
			item=g[:idx[0]]
		else:
			item=g[idx[i-1]+1:idx[i]]
		if len(item)>th2:
			ret.append(np.sum(item))
	item=g[idx[-1]+1:]
	if len(item)>th2:
		ret.append(np.sum(item))
	return ret

def getTime(gap):
	ret=[]
	retMean=[]
	for i in range(N):
		temp=[]
		tempMean=[]
		for j in range(M):
			if methods[j]=='spruce':
				continue
			t_=getTimeFun(gap[i][j],th1[j],th2[j])
			temp.append(t_)
			tempMean.append(np.mean(t_))
		ret.append(temp)
		retMean.append(tempMean)
	return ret,retMean

def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
color=[pickColor(i, 10) for i in range(10)]
plt.rcParams.update({'font.size': 15})

if __name__=='__main__':
	begin=time.time()
	if os.path.exists(cacheFilename):
		gap=np.load(cacheFilename,allow_pickle=True)
	else:
		gap=[]
		for i in range(N):
			v1=[]
			for j in range(M):
				f1=dirname.format(x[i],y[i],z[i],methods[j])+'/'+suffix[j]
				tx=np.loadtxt(f1)[:,0]
				v1.append(delta(tx)*1e6)
			gap.append(v1)
		gap=np.array(gap)
		np.save(cacheFilename,gap)
	truth=[]
	for i in range(N):
		truth.append(Capacity-max(x[i],y[i],z[i]))
	mT,mmT=getTime(gap)
	end=time.time()
	print('use {:.2f} s'.format(end-begin))
	label=['BQR','ASSOLO','PTR','pathload']
	index=['{:d}-{:d}-{:d}({:.0f})'.format(x[i],y[i],z[i],truth[i]) for i in range(N)]
	df=pd.DataFrame(mmT,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-time/exp1-time.csv',float_format='%.2f')
	mmT=np.array(mmT)
	fig,(ax1,ax2)=plt.subplots(2,1,sharex=True,figsize=(10,10))
	l2=mmT.shape[1]
	xtick=np.arange(0,25,5)
	width=2
	lines=[]
	for i in range(2):
		xpos=xtick+i*width
		line=ax1.bar(xpos,mmT[1:10:2,i]/1000,width=width,label=label[i],color=color[i])
		lines.append(line)
		line=ax2.bar(xpos,mmT[1:10:2,i+2]/1000/1000,width=width,label=label[i+2],color=color[i+2])
		lines.append(line)
	xindex=['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(1,10,2)]
	ax1.spines['right'].set_visible(False)
	ax2.spines['top'].set_visible(False)
	ax2.spines['right'].set_visible(False)
	ax1.grid(axis='both',linestyle="--")
	ax2.grid(axis='both',linestyle="--")
	ax2.set_xlabel('Traffic Settings(Mbps)')
	ax1.set_ylabel('Time(ms)')
	ax2.set_ylabel('Time(s)')
	ax1.xaxis.tick_top()
	ax1.tick_params(labeltop='off')
	ax2.set_ylim(0,6)
	ax2.set_yticks(np.arange(1,6))
	ax2.invert_yaxis()
	plt.xticks(xtick+0.5*width,xindex)
	plt.subplots_adjust(wspace=0,hspace=0)
	ax1.legend(lines,label)
	plt.savefig('/images/comparison/exp1/exp1-RealTime.eps',bbox_inches='tight')
	plt.savefig('/images/comparison/exp1/exp1-RealTime.pdf',bbox_inches='tight')