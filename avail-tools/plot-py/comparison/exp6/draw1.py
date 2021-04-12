# bigFlows.pcap
import numpy as np
import pandas as pd
import code,io,time,os
import matplotlib.pyplot as plt
delta=lambda x: x[...,1:,0]-x[...,:-1,0]
def tick():
	global t1,t2
	t1=time.time()
def tock(s=''):
	global t1,t2
	t2=time.time()
	if s!='':
		s=s+' '
	print('{:s}use {:.2f} second'.format(s, t2-t1))
def loadWrapper(filename,loadFun):
	picklename=filename+'.npy'
	if os.path.exists(picklename):
		print('load: quick')
		return np.load(picklename,allow_pickle=True)
	else:
		print('load: init')
		v=loadFun(filename)
		np.save(picklename,v)
		return v
def getCurve(v,unit):
	begin,end=v[0,0],v[-1,0]
	bucketLeft=np.arange(begin,end,unit)
	n=len(bucketLeft)
	idx=np.searchsorted(v[:,0],bucketLeft)
	packetSum=[np.sum(v[idx[i]:idx[i+1],1]) for i in range(n-1)]
	rate=np.array(packetSum)*8/unit*1e-6
	return rate
def getRateCurve(d,unit):
	ret={}
	for k,v in d.items():
		ret[k]=getCurve(v,unit)
	return ret
def cdf(x):
	x=sorted(x)
	y=np.arange(len(x))/len(x)
	return x,y
def smartUnit(t):
	# represent t(s) smartly
	if t<1e-6:
		return '{:.0f}ns'.format(t*1e9)
	elif t<1e-3:
		return '{:.0f}us'.format(t*1e6)
	elif t<1:
		return '{:.0f}ms'.format(t*1e3)
	else:
		return '{:.0f}s'.format(t)
np.set_printoptions(suppress=True)
capacity=957.14
pathFmt='/data/comparison/exp6/{:d}/traffic.len'
if __name__=='__main__':
	tick()
	rateList=[10,100,300,500,700,900]
	d={i:loadWrapper(pathFmt.format(i),np.loadtxt) for i in rateList}
	tock()
	gap={i:delta(d[i])*1e6 for i in rateList}
	# 包间隔
	if False:
		for i in rateList:
			x,y=cdf(gap[i])
			plt.plot(x,y*100,label='{:d}'.format(i))
		plt.xlim(-5,200)
		plt.xlabel('packet gap(us)')
		plt.ylabel('percentage(%)')
		plt.legend(loc='lower right')
		plt.savefig('/images/comparison/exp6/exp6-cdf-gap.png',bbox_inches='tight')
	# 平均速率
	meanRate={k:np.sum(v[:,1])*8/(v[-1,0]-v[0,0])*1e-6 for k,v in d.items()}
	# 以BQR的测量时间50ms为单位进行速率曲线绘制
	unit=50e-3
	rateCurve=getRateCurve(d,unit)
	arr=[]
	for k,v in rateCurve.items():
		r=np.percentile(v,[5,95])
		arr.append([k,r[0],meanRate[k],r[1]])
		#print('{:d}:{:.2f},{:.2f},{:.2f}'.format(k,r[0],meanRate[k],r[1]))
	cols=['rate','5% percentile','mean','95% percentile']
	df=pd.DataFrame(arr,columns=cols)
	df.to_csv('/data/comparison/exp6-csv/exp6-rate.csv',index=False,float_format='%.1f')
	abwCurve={k:capacity-v for k,v in rateCurve.items()}
	if False:
		rates=[10,100,900]
		fig=plt.figure(figsize=(10,5))
		for rate in rates:
			plt.plot(rateCurve[rate],'.-',label='{:d}'.format(rate))
		plt.legend()
		plt.xlabel('time index')
		plt.ylabel('traffic rate(Mbps)')
		plt.title('traffic rate (50ms)')
		plt.savefig('/images/comparison/exp6/exp6-rate.png',bbox_inches='tight')
	# CDF速率
	if False:
		rate=900
		fig=plt.figure(figsize=(10,10))
		for unit in [5e-4,1e-3,10e-3,50e-3,100e-3]:
			rateCurve=getRateCurve(d,unit)
			x,y=cdf(rateCurve[rate])
			plt.plot(x,y*100,label=smartUnit(unit))
		plt.legend()
		plt.title('CDF of rate in different time granularity')
		plt.xlabel('rate(Mbps)')
		plt.xlim(0,1000)
		plt.ylabel('percentage(%)')
		plt.savefig('/images/comparison/exp6/exp6-cdf-rate.png',bbox_inches='tight')
	# 包大小
	if False:
		x=d[900][:,1]
		x,y=cdf(x)
		plt.plot(x,y*100)
		plt.xlabel('packet size(Byte)')
		plt.ylabel('percentage(%)')
		plt.title('CDF of flow\'s packet size')
		plt.savefig('/images/comparison/exp6/exp6-cdf-packetsize.png',bbox_inches='tight')
	code.interact(local=dict(globals(),**locals()))