# bigFlows1.len caida2.len
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
def getCurve(v,unit):
	begin,end=v[0,0],v[-1,0]
	bucketLeft=np.arange(begin,end,unit)
	n=len(bucketLeft)
	idx=np.searchsorted(v[:,0],bucketLeft)
	packetSum=[np.sum(v[idx[i]:idx[i+1],1]) for i in range(n-1)]
	rate=np.array(packetSum)*8/unit*1e-6
	return rate
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
def packetCDF(datas,names):
	fig=plt.figure(figsize=(8,6))
	for i,data in enumerate(datas):
		x,y=cdf(data[:,1])
		y*=100
		plt.plot(x,y,label=names[i],color=pickColor(i,10))
	plt.grid(linestyle="--")
	ax=plt.gca()
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	plt.xlabel('Packet size(Byte)')
	plt.ylabel('Percentage(%)')
	plt.xlim(0,1550)
	plt.xticks(np.arange(0,1550,100))
	plt.ylim(0,105)
	plt.yticks(np.arange(0,105,10))
	plt.legend(loc='best')
	name=names[0]+'-'+names[1]
	plt.savefig('/images/comparison/exp9/{:s}.pdf'.format(name),bbox_inches='tight')
	plt.savefig('/images/comparison/exp9/{:s}.svg'.format(name),bbox_inches='tight')
	#plt.show()
	plt.close(fig)

np.set_printoptions(suppress=True)
capacity=957.14
path=['/home/tony/pcapFiles/bigFlows1.len','/home/tony/pcapFiles/caida2.len']
name=['bigFlows1','caida2']
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
if __name__=='__main__':
	tk=tickTock()
	lenFile=[loadWrapper(p,np.loadtxt) for p in path]
	tk.tock()
	# 包大小
	packetCDF(lenFile,name)
	tk.tock()
	#code.interact(local=dict(globals(),**locals()))