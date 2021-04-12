# 实验8 tcpreplay ASSOLO 效果
import numpy as np
import code,io,time,os
import matplotlib.pyplot as plt
import pandas as pd
delta=lambda x: x[...,1:,0]-x[...,:-1,0]
def loadF1(filename):
	return np.loadtxt(filename,delimiter=',')
def data2OWD(data,skip=False):
	ret=(data[:,:,1]-data[:,:,0])*1e6
	if not skip:
		ret-=np.min(ret,axis=1)[:,np.newaxis]
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
def loadWrapper(filename,loadFun):
	picklename=filename+'.npy'
	if os.path.exists(picklename):
		print('load: from {:s}'.format(picklename))
		return np.load(picklename,allow_pickle=True)
	else:
		t1=time.time()
		v=loadFun(filename)
		t2=time.time()
		if t2-t1>1.0:
			print('load: save {:s}'.format(picklename))
			np.save(picklename,v)
		return v
def plot(owd,i):
	v=owd[i]
	idx=0
	try:
		for idx,j in enumerate(v):
			plt.plot(j,label='{:d}'.format(idx))
			plt.legend()
			plt.pause(.5)
			plt.clf()
	except KeyboardInterrupt:
		print(idx)
	finally:
		plt.close()
def savePlot(owd,i,path):
	v=owd[i]
	for idx,j in enumerate(v):
		plt.plot(j)
		plt.xlabel('packet index')
		plt.ylabel('one way delay(us)')
		plt.title('one way delay of BQR')
		plt.text(0.5,0.05,'rate {:d}, iteration {:d}'.format(i,idx))
		plt.savefig(path.format(i,idx),bbox_inches='tight')
		plt.clf()
	plt.close()
np.set_printoptions(suppress=True)
capacity=957.14
if __name__=='__main__':
	fmt='/data/comparison/exp8/{:d}/{:s}'
	rateList=[10,100,300,500,700,900]
	tick()
	arr1={i:loadWrapper(fmt.format(i,'c-ASSOLO.len'),np.loadtxt) for i in rateList}
	arr2={i:loadWrapper(fmt.format(i,'c-traffic.len'),np.loadtxt) for i in rateList}
	result={i:np.sort(loadWrapper(fmt.format(i,'instbw'),np.loadtxt),axis=0) for i in rateList}
	gap1={i:(arr1[i][1:,0]-arr1[i][:-1,0])*1e6 for i in rateList}
	tock()
	figPath='/images/comparison/exp7/{:d}/{:d}'
	code.interact(local=dict(globals(),**locals()))