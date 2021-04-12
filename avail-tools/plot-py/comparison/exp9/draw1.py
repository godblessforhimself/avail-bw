# ip4.len
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
path='/home/tony/pcapFiles/ip4.len'
if __name__=='__main__':
	tick()
	d=loadWrapper(path,np.loadtxt)
	tock()
	# 平均速率
	meanRate=np.sum(d[:,1])*8/(d[-1,0]-d[0,0])*1e-6
	# 以unit为单位速率曲线绘制
	unit=50e-3
	rateCurve=getCurve(d,unit)
	if False:
		fig=plt.figure(figsize=(10,5))
		plt.plot(rateCurve,'.-')
		plt.xlabel('time index')
		plt.ylabel('traffic rate(Mbps)')
		plt.title('traffic rate ({})'.format(smartUnit(unit)))
		plt.show()
	# CDF速率
	if False:
		fig=plt.figure(figsize=(10,10))
		for unit in [5e-4,1e-3,10e-3,50e-3,100e-3]:
			rateCurve=getCurve(d,unit)
			x,y=cdf(rateCurve)
			plt.plot(x,y*100,label=smartUnit(unit))
		plt.legend()
		plt.title('CDF of rate in different time granularity')
		plt.xlabel('rate(Mbps)')
		plt.ylabel('percentage(%)')
		plt.show()
	# 包大小
	if True:
		x,y=cdf(d[:,1])
		plt.plot(x,y*100)
		plt.xlabel('packet size(Byte)')
		plt.ylabel('percentage(%)')
		plt.title('CDF of flow\'s packet size')
		plt.show()
	#code.interact(local=dict(globals(),**locals()))