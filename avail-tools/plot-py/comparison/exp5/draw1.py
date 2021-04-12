# random traffic
import numpy as np
import code,io,time,os
import matplotlib.pyplot as plt
delta=lambda x: x[...,1:,0]-x[...,:-1,0]
def loadTime(tsfile):
	data=[]
	f=open(tsfile)
	string=f.read()
	f.close()
	segments=string.split('\n\n')
	for seg in segments:
		if len(seg)==0:
			continue
		f=io.StringIO(seg)
		x=np.loadtxt(f,delimiter=',')
		f.close()
		data.append(x)
	data=np.array(data)
	return data
def data2OWD(data,skip=False):
	ret=(data[:,1]-data[:,0])*1e6
	if not skip:
		ret-=np.min(ret,axis=0)
	return ret
def tick():
	global t1,t2
	t1=time.time()
def tock(s=''):
	global t1,t2
	t2=time.time()
	if s!='':
		s=s+' '
	print('{:s}use {:.2f} second'.format(s, t2-t1))
def loadWrapper(filename,loadFun=loadTime):
	picklename=filename+'.npy'
	if os.path.exists(picklename):
		print('load: quick')
		return np.load(picklename,allow_pickle=True)
	else:
		print('load: init')
		v=loadFun(filename)
		np.save(picklename,v)
		return v
def splitByThreshold(vec,dvec,threshold):
	idx=np.where(dvec>threshold)[0]
	beginIdx,endIdx=[],[]
	beginTx,endTx=[],[]
	beginIdx.append(0)
	endIdx.append(idx[0])
	beginTx.append(vec[0,0])
	endTx.append(vec[idx[0],0])
	for i in range(1,len(idx)):
		beginTx.append(vec[idx[i-1]+1,0])
		endTx.append(vec[idx[i],0])
		beginIdx.append(idx[i-1]+1)
		endIdx.append(idx[i])
	beginTx.append(vec[idx[-1]+1,0])
	endTx.append(vec[-1,0])
	beginIdx.append(idx[-1]+1)
	endIdx.append(len(vec)-1)
	return np.array(beginTx),np.array(endTx),np.array(beginIdx,dtype=np.int32),np.array(endIdx,dtype=np.int32)
def getOWD2(tx,rx,beginIdx,endIdx):
	L=len(beginIdx)
	ret=[]
	for i in range(L):
		owd=rx[beginIdx[i]:endIdx[i]+1,0]-tx[beginIdx[i]:endIdx[i]+1,0]
		owd-=np.min(owd)
		ret.append(owd*1e6)
	return ret
np.set_printoptions(suppress=True)
# result[0]
# rx split by threshold=100ms
capacity=957.14
if __name__=='__main__':
	tick()
	result=np.loadtxt('/data/comparison/exp5/result.txt')
	data=loadWrapper('/data/comparison/exp5/timestamp.txt')
	rx=np.loadtxt('/data/comparison/exp5/c-BQR.len')
	tx=np.loadtxt('/data/comparison/exp5/a.len')
	traffic=loadWrapper('/data/comparison/exp5/c-traffic.len',np.loadtxt)
	tock()
	owd0=[data2OWD(item,True) for item in data]
	owd=[data2OWD(item) for item in data]
	gout=delta(rx)
	threshold1=9e4*1e-6
	# beginIdx_,endIdx_ 100个BQR的开始和结束的下标
	beginTx,endTx,beginIdx_,endIdx_=splitByThreshold(rx,gout,threshold1)
	owd2=getOWD2(tx,rx,beginIdx_,endIdx_)
	validIdx=result[:,0].astype(np.int32)
	# beginIdx,endIdx 100个BQR内的流量开始、结束的下标
	beginIdx=np.searchsorted(traffic[:,0],beginTx)
	endIdx=np.searchsorted(traffic[:,0],endTx)
	# beginIdx2,endIdx2 有效的BQR内的流量开始、结束的下标
	beginIdx2=beginIdx[validIdx]
	endIdx2=endIdx[validIdx]
	packetSum=[np.sum(traffic[beginIdx2[i]:endIdx2[i],1]) if endIdx2[i]<=len(traffic) else 0 for i in range(len(validIdx))]
	packetSum=np.array(packetSum)
	tSum=endTx[validIdx]-beginTx[validIdx]
	tfRate=packetSum*8/tSum*1e-6
	gt=capacity-tfRate
	estimate=result[:,1]
	#plt.plot(gt,'.-',label='ground truth')
	#plt.plot(estimate,'.-',label='BQR')
	#plt.legend()
	def plot(i):
		plt.plot(owd[i],'.-',label='user')
		plt.plot(owd2[i],'.-',label='real')
		plt.legend()
		plt.show()
	def rplt(i,gran=None):
		fig,axs=plt.subplots(nrows=2,ncols=1,sharex=True)
		axs[0].plot(rx[beginIdx_[i]:endIdx_[i]+1,0],owd2[i],'.-')
		b,e=beginIdx[i],endIdx[i]+1
		print(e-b+1)
		if gran==None:
			gran=int((e-b)/5)
		for j in np.arange(b,e,gran):
			axs[1].hlines(np.mean(traffic[j:j+gran,1]),traffic[j,0],traffic[j+gran,0])
		axs[1].set_ylim(0,1500)
		plt.show()
		plt.close(fig)
	print(validIdx)
	rplt(0)
	code.interact(local=dict(globals(),**locals()))