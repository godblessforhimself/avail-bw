import code,sys
import numpy as np
import matplotlib.pyplot as plt
def smooth(x,thres=10):
	# x[0]>thres
	# x[k]>thres
	# x[0]<thres x[k]>thres
	ret=np.zeros(x.shape,dtype=x.dtype)
	if x[0]<thres:
		pass
	return ret
	
path='data/output.txt'
#if len(sys.argv)==2:
#	path=sys.argv[1]
data=np.loadtxt(path)
data=data*1e6
load_number=100
inspect_number=data.shape[0]-load_number
if False:
	load_send=data[:load_number,0]
	load_receive=data[:load_number,1]
	load_send=smooth(load_send)
	load_receive=smooth(load_receive)
	data[:load_number,0]=load_send
	data[:load_number,1]=load_receive

def diff(x):
	return x[1:]-x[:-1]

gin=diff(data[:,0])
gout=diff(data[:,1])
owd=data[:,1]-data[:,0]

if False:
	plt.subplot(2,2,1)
	plt.plot(gin)
	plt.subplot(2,2,2)
	plt.plot(gout)
	plt.subplot(2,2,3)
	plt.plot(owd)
	plt.show()

array=[gin.mean(),gin.std(),gout.mean(),gout.std()]
print('gin  {:.2f},{:.2f}\ngout {:.2f},{:.2f}\n'.format(*array))

if len(sys.argv)>=2 and sys.argv[1]=='-i':
	code.interact(local=dict(globals(),**locals()))