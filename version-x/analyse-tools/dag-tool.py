import code,sys
import numpy as np
import matplotlib.pyplot as plt

def diff(x):
	return x[1:]-x[:-1]

send,recv=np.loadtxt('data/in.txt'), np.loadtxt('data/out.txt')
const=send[0]
send=send-const
recv=recv-const
send=send*1e6
recv=recv*1e6
send=send.astype(np.int32)
recv=recv.astype(np.int32)
gin=diff(send)
gout=diff(recv)
owd=recv-send
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