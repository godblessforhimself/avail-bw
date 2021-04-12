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
	code.interact(local=dict(globals(),**locals()))