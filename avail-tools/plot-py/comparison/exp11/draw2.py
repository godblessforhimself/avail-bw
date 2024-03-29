import numpy as np
import code,io,time,os,matplotlib
import matplotlib.pyplot as plt
import pandas as pd
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
def getOWD(x):
	r=(x[:,:,1]-x[:,:,0])*1e6
	r-=np.min(r,axis=1)[:,np.newaxis]
	return r
def removeNa(y):
	y[y==-1]=np.nan
	return pd.DataFrame(y).fillna(method='pad').to_numpy().flatten()
def averageN(y,n):
	y_=y.reshape((-1,n))
	return np.mean(y_,axis=1)
def getCurve(v,unit):
	begin,end=v[0,0],v[-1,0]
	bucketLeft=np.arange(begin,end,unit)
	n=len(bucketLeft)
	idx=np.searchsorted(v[:,0],bucketLeft)
	packetSum=[np.sum(v[idx[i]:idx[i+1],1]) for i in range(n-1)]
	rate=np.array(packetSum)*8/unit*1e-6
	return rate
def draw(x,y1,y2,label1,label2,title):
	fig=plt.figure(figsize=(3.1,1.1))
	plt.plot(x,y1,label=label1,color=color[0],linestyle=linestyle[0])
	plt.plot(x,y2,label=label2,color=color[1],linestyle=linestyle[1])
	plt.legend(loc='lower center',framealpha=.5,ncol=2,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=6)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	plt.xlabel('Time(s)',labelpad=0)
	plt.ylabel('ABW(Mbps)',labelpad=0)
	plt.xlim(0,100)
	plt.xticks(np.arange(0,100+5,10))
	plt.ylim(0,1000)
	plt.yticks(np.arange(0,1000+1,200))
	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)
	plt.savefig('{:s}/{:s}.pdf'.format(imgDir,title),bbox_inches='tight')
	plt.savefig('{:s}/{:s}.eps'.format(imgDir,title),bbox_inches='tight')
	plt.close(fig)

def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
np.set_printoptions(suppress=True,precision=2)
color=[pickColor(i, 10) for i in range(10)]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
plt.rcParams.update({'font.size': 7})
matplotlib.rcParams['hatch.linewidth']=0.3
marker=['d','.','*','<','p'] #5
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1)),(0,(3,1,1,1,1,1))] #5
hatch=['/','\\','x','o','-|'] #5
imgDir='/home/tony/Files/available_bandwidth/thesis-svn/IMC2021/BurstQueueRecovery-jintao/images'

resultFmt='/data/comparison/exp11/{:s}/result.txt'
trafficFmt='/data/comparison/exp11/{:s}/c-traffic.len'
probeFmt='/data/comparison/exp11/{:s}/c-BQR.len'
names=['test3','test4']
gran=1.0
capacity=1000
if __name__=='__main__':
	tk=tickTock()
	tk.tick()
	result=[loadWrapper(resultFmt.format(i),np.loadtxt) for i in names] #(2,400,16)
	traffic=[loadWrapper(trafficFmt.format(name),np.loadtxt) for name in names] #(2,?,2)
	bqr=[loadWrapper(probeFmt.format(name),np.loadtxt)[:,0].reshape(1200,200) for name in names] #(2,1200,200)
	tk.tock()
	bqrPrediction=[removeNa(result[i][:,1]) for i in range(2)] #(2,400)
	minTime=[min(traffic[i][0,0],bqr[i][0,0]) for i in range(2)]
	maxTime=[max(traffic[i][-1,0],bqr[i][-1,-1]) for i in range(2)]
	maxTime=[np.ceil((maxTime[i]-minTime[i])/gran)*gran+minTime[i] for i in range(2)]
	bqrBeginTime=[bqr[i][:,0] for i in range(2)] #(2,1200)
	bqrIndex=np.floor((np.array(bqrBeginTime)-np.array(minTime)[:,np.newaxis])/gran)
	maxIndex=[int((maxTime[i]-minTime[i])/gran) for i in range(2)]
	bqrPredAgg=[]
	for i in range(2):
		arr=[]
		pos=np.searchsorted(bqrIndex[i],np.arange(maxIndex[i]))
		for j in range(maxIndex[i]):
			if j+1<maxIndex[i]:
				v=bqrPrediction[i][pos[j]:pos[j+1]]
			else:
				v=bqrPrediction[i][pos[j]:]
			if len(v)>0:
				arr.append(np.mean(v))
			else:
				arr.append(capacity)
		bqrPredAgg.append(arr)
	trafficIndex=[np.floor((traffic[i][:,0]-minTime[i])/gran) for i in range(2)]
	trafficAgg=[]
	for i in range(2):
		arr=[]
		pos=np.searchsorted(trafficIndex[i],np.arange(maxIndex[i]))
		for j in range(maxIndex[i]):
			if j+1<maxIndex[i]:
				p=np.sum(traffic[i][pos[j]:pos[j+1],1])
			else:
				p=np.sum(traffic[i][pos[j]:,1])
			v=p*8e-6/gran
			arr.append(capacity-v)
		trafficAgg.append(arr)
	tk.tock()
	x=[np.arange(1,maxIndex[i]+1)*gran for i in range(2)]
	title=['bigFlows','caida']
	for i in range(2):
		draw(x[i],bqrPredAgg[i],trafficAgg[i],'BQR','GroundTruth',title[i])
	#code.interact(local=dict(globals(),**locals()))