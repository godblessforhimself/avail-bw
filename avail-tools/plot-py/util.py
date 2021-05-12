import numpy as np
import code,io,time,os
import matplotlib.pyplot as plt
import argparse
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
def removeOffset(x):
	x=x-np.min(x)
	return x
def delta(x):
	return x[1:]-x[:-1]
np.set_printoptions(suppress=True,precision=2)
if __name__=='__main__':
	parser = argparse.ArgumentParser(description='parser')
	parser.add_argument('--file', type=str, help='filename')
	parser.add_argument('--index', type=int, help='the i th owd')
	parser.add_argument('--interact', action='store_true')
	args = parser.parse_args()
	tk=tickTock()
	if args.file:
		tk.tick()
		d=loadWrapper(args.file)
		owds=removeOffset(d[:,:,1]-d[:,:,0])*1e6
		tk.tock()
		if args.index!=None:
			data=d[args.index]
			s,r=data[:,0],data[:,1]
			gin,gout=delta(s)*1e6,delta(r)*1e6
			owd=removeOffset(r-s)*1e6
			x=removeOffset(s)*1e6
			plt.scatter(x,owd,s=1)
			plt.show()
			plt.clf()
	if args.interact:
		code.interact(local=dict(globals(),**locals()))