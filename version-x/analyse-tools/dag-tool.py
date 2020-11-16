import code,sys
import numpy as np
import matplotlib.pyplot as plt

def diff(x):
	return x[1:]-x[:-1]

din,dout=np.loadtxt('data/in.txt'), np.loadtxt('data/out.txt')
const=din[0]
din=din-const
dout=dout-const
din=din*1e6
dout=dout*1e6
gin=diff(din)
gout=diff(dout)
owd=dout-din
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
code.interact(local=dict(globals(),**locals()))