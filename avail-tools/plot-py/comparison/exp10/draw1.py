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
fmt='/data/comparison/exp10/{:d}/timestamp.txt'
rateList=[0,1000,3000,5000,7000,9000]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
if __name__=='__main__':
	tk=tickTock()
	tk.tick()
	d=[loadWrapper(fmt.format(i)) for i in rateList]
	owd=[getOWD(i) for i in d]
	tk.tock()
	rescale=lambda x:(x-x[0])*1e6
	fig,axs=plt.subplots(2,3,sharex=True,sharey=True,figsize=(15,5))
	for i,v in enumerate(rateList):
		ax=axs[i//3][i%3]
		ax.plot(owd[i][1],marker='.')
		ax.text(0.6,0.9,'traffic rate:{:.0f}Gbps'.format(v/1000),transform=ax.transAxes)
		ax.grid(linestyle='--')
	fig.text(0.09,0.5,'OWD(us)',va='center',rotation='vertical')
	fig.text(0.5,0.05,'Packet index',va='center',rotation='horizontal')
	plt.subplots_adjust(wspace=0,hspace=0)
	plt.savefig('/images/comparison/exp10/run1-exp10.svg',bbox_inches='tight')
	plt.savefig('/images/comparison/exp10/run1-exp10.pdf',bbox_inches='tight')
	o=owd[1][1]
	s=rescale(d[1][1,:,0])
	r=rescale(d[1][1,:,1])
	gin=s[1:]-s[:-1]
	gout=r[1:]-r[:-1]
	#code.interact(local=dict(globals(),**locals()))