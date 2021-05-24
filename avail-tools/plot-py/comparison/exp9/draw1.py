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
def packetCDF(datas,names):
	fig=plt.figure(figsize=(1.3,1.1))
	percentages=[]
	for i,data in enumerate(datas):
		x,y=cdf(data[:,1])
		idx=np.searchsorted(x,[200,1400])
		p1,p2=idx[0]/len(x),idx[1]/len(x)
		tmp=[p1,p2-p1,1-p2,np.mean(x)]
		percentages.append(tmp)
		y*=100
		N=len(x)//200
		x,y=x[::N],y[::N]
		plt.plot(x,y,label=names[i],color=color[i],linestyle=linestyle[i])
	cellText=[]
	for i in range(4):
		tmp=[]
		for j in range(2):
			if i<3:
				s='{:.2%}'.format(percentages[j][i])
			else:
				s='{:.2f}'.format(percentages[j][i])
			tmp.append(s)
		cellText.append(tmp)
	rowLabels=[
		'Small(<200B)',
		'Medium(200-1400B)',
		'Large(>1400B)',
		'Mean(B)'
	]
	colLabels=['bigFlows','caida']
	#table=plt.table(cellText=cellText,rowLabels=rowLabels,colLabels=colLabels,colWidths=[0.15,0.15],cellLoc='center',rowLoc='center',bbox=[0.7,0.02,0.25,0.25])
	#table.auto_set_font_size(False)
	#table.set_fontsize(15)
	plt.xlabel('Packet Size(B)',labelpad=0)
	plt.ylabel('Percentage(%)',labelpad=0)
	plt.xlim(0,1550)
	plt.xticks(np.arange(0,1550,300))
	plt.ylim(0,105)
	plt.yticks(np.arange(0,105,20))
	
	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)
	plt.legend(loc='lower center',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	name=names[0]+'-'+names[1]
	plt.savefig('{:s}/exp9-packetSize-{:s}.pdf'.format(imgDir,name),bbox_inches='tight')
	plt.savefig('{:s}/exp9-packetSize-{:s}.eps'.format(imgDir,name),bbox_inches='tight')
	plt.close(fig)

capacity=957.14
path=['/home/tony/pcapFiles/bigFlows1.len','/home/tony/pcapFiles/caida2.len']
name=['bigFlows1','caida2']

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

if __name__=='__main__':
	tk=tickTock()
	lenFile=[loadWrapper(p,np.loadtxt) for p in path]
	tk.tock()
	# 包大小
	packetCDF(lenFile,name)
	tk.tock()
	#code.interact(local=dict(globals(),**locals()))