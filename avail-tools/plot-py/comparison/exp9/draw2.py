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
	ret=(data[...,1]-data[...,0])*1e6
	if not skip:
		axis=len(data.shape)-1
		m=np.min(ret,axis=axis-1)
		ret-=m[:,np.newaxis]
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
np.set_printoptions(precision=2,suppress=True)
capacity=957.14
if __name__=='__main__':
	tick()
	d={i:loadWrapper('/data/comparison/exp9/{:d}/timestamp.txt'.format(i)) for i in range(1,4+1)}
	gin={i:(d[i][:,1:,0]-d[i][:,:-1,0])*1e6 for i in range(1,4+1)}
	gout={i:(d[i][:,1:,1]-d[i][:,:-1,1])*1e6 for i in range(1,4+1)}
	tock()
	owd0=[data2OWD(d[i],True) for i in range(1,4+1)]
	owd=[data2OWD(d[i]) for i in range(1,4+1)]
	plt.subplot(221)
	plt.plot(owd[0][0])
	plt.subplot(222)
	plt.plot(owd[1][0])
	plt.subplot(223)
	plt.plot(owd[2][0])
	plt.subplot(224)
	plt.plot(owd[3][0])
	plt.show()
	code.interact(local=dict(globals(),**locals()))