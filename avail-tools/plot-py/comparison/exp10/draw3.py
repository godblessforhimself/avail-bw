import numpy as np
import code,io,time,os,matplotlib
import matplotlib.pyplot as plt
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
def loadWrapper(filename,loadFun=loadTime):
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
fmt='/data/comparison/exp10/run3-{:d}/timestamp.txt'
rateList=[1000,3000,5000,7000]

def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
np.set_printoptions(suppress=True,precision=2)
color=[pickColor(i, 10) for i in range(10)]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
plt.rcParams.update({'font.size': 9})
matplotlib.rcParams['hatch.linewidth']=0.3
marker=['d','.','*','<','p'] #5
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1)),(0,(3,1,1,1,1,1))] #5
hatch=['/','\\','x','o','-|'] #5
imgDir='/home/tony/Files/available_bandwidth/thesis-svn/IMC2021/BurstQueueRecovery-jintao/images'

if __name__=='__main__':
	tk=tickTock()
	d=[loadWrapper(fmt.format(i)) for i in rateList]
	owd=[getOWD(i) for i in d]
	tk.tock()
	rescale=lambda x:(x-x[0])*1e6
	fig,ax=plt.subplots(figsize=(3.4,1.1))
	j=-1
	label=['{:.0f} Gbps'.format(v/1000) for v in rateList]
	for i,v in enumerate(rateList):
		ax.plot(owd[i][j],color=color[i],label=label[i],linestyle=linestyle[i])
	
	plt.xlabel('Packet Index',labelpad=0)
	plt.ylabel('One Way Delay(us)',labelpad=0)
	plt.xlim(0,35)
	plt.xticks(np.arange(0,35,10))
	plt.ylim(-10,120)
	plt.yticks(np.arange(0,120,20))

	plt.legend(loc='upper right',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=8)

	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)

	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)

	plt.savefig('{:s}/run3-exp10.eps'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/run3-exp10.pdf'.format(imgDir),bbox_inches='tight')
	#plt.show()
	i,j=-1,-1
	o=owd[i][j]
	s=rescale(d[i][j,:,0])
	r=rescale(d[i][j,:,1])
	gin=s[1:]-s[:-1]
	gout=r[1:]-r[:-1]
	#code.interact(local=dict(globals(),**locals()))