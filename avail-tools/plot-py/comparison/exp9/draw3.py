# caida2.len
import numpy as np
import pandas as pd
import code,io,time,os,matplotlib
import matplotlib.pyplot as plt
delta=lambda x: x[...,1:,0]-x[...,:-1,0]
class tickTock:
	def __init__(self):
		self.t1=time.time()
	def tick(self):
		self.t1=time.time()
	def tock(self,s=''):
		self.t2=time.time()
		if s!='':
			s=s+' '
		print('{:s}use {:.2f} second'.format(s, self.t2-self.t1))
def getModifiedTime(filename):
	return os.path.getmtime(filename)
def loadWrapper(filename,loadFun):
	picklename=filename+'.npy'
	usePickle=False
	if os.path.exists(picklename):
		t1=getModifiedTime(filename)
		t2=getModifiedTime(picklename)
		if t1<t2:
			usePickle=True
	if usePickle:
		return np.load(picklename,allow_pickle=True)
	else:
		t1=time.time()
		v=loadFun(filename)
		t2=time.time()
		if t2-t1>1.0:
			print('load: save {:s}'.format(picklename))
			np.save(picklename,v)
		return v
def cdf(x):
	x=np.sort(x)
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

def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
np.set_printoptions(suppress=True,precision=2)
color=[pickColor(i, 10) for i in range(10)]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
plt.rcParams.update({'font.size': 6})
matplotlib.rcParams['hatch.linewidth']=0.3
marker=['d','.','*','<','p'] #5
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1)),(0,(3,1,1,1,1,1))] #5
hatch=['/','\\','x','o','-|'] #5
imgDir='/home/tony/Files/available_bandwidth/thesis-svn/IMC2021/BurstQueueRecovery-jintao/images'

capacity=957.14
path='/home/tony/pcapFiles/caida2.len'
name='caida2'
def getSamples(timestamp,packet,duration):
	binLeft=np.arange(timestamp[0],timestamp[-1],duration)
	idx=np.searchsorted(timestamp,binLeft)
	ret=[]
	for i in range(len(idx)-1):
		ret.append(np.sum(packet[idx[i]:idx[i+1]]))
	ret=np.array(ret)
	rate=ret*8e-6/duration
	return len(ret),ret,rate
if __name__=='__main__':
	tk=tickTock()
	data=loadWrapper(path,np.loadtxt)
	timestamp,packet=data[:,0],data[:,1]
	meanRate=np.sum(data[:,1])*8e-6/(data[-1,0]-data[0,0])
	print('meanRate is {:.2f}'.format(meanRate))
	tk.tock()
	# 什么是Long Range Dependency
	# 使用不同的采样时间和采样次数
	repeatNumber,samplingNumber=1000,[10,50,100,200]
	samplingDuration=[1e-3,1e-2,1e-1]
	for sn in samplingNumber:
		fig,ax=plt.subplots(figsize=(1.3,1.1))
		for i,duration in enumerate(samplingDuration):
			n,p,rate=getSamples(timestamp,packet,duration)
			samples=[]
			for j in range(repeatNumber):
				mean=np.mean(np.random.choice(rate,sn,replace=False))
				samples.append(mean)
			x,y=cdf(samples)
			if len(x)>500:
				step=len(x)//500
				x,y=x[::step],y[::step]
			plt.plot((x-meanRate)/meanRate*100,y*100,label='t = {:.0f} ms'.format(duration*1e3),color=color[i],linestyle=linestyle[i])
		plt.xlabel('Relative Error(%)',labelpad=0)
		plt.ylabel('CDF(%)',labelpad=0)
		plt.yticks(np.arange(0,100+1,20))
		plt.xlim(-20,20)
		plt.xticks(np.arange(-20,20+1,10))
		plt.legend(loc='upper left',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
		plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
		ax.tick_params('both',length=1,width=1,which='both',pad=1)
		plt.savefig('{:s}/exp9-sample-number-{:d}.pdf'.format(imgDir,sn),bbox_inches='tight')
		#plt.show()
		plt.close(fig)
	tk.tock()
	#code.interact(local=dict(globals(),**locals()))