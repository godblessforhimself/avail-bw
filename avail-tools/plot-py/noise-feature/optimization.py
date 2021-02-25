import matplotlib.pyplot as plt
import numpy as np
import code,time
delta=lambda x: x[...,1:]-x[...,:-1]
np.set_printoptions(suppress=True)

if __name__=='__main__':
	fname='/tmp/bqr/timestamp.txt'
	begin=time.time()
	data=np.loadtxt(fname,delimiter=',')
	repeat=10
	pts=200
	data=data.reshape((repeat,pts,2))
	send,recv=data[:,:,0],data[:,:,1]
	gin,gout=delta(send*1e6),delta(recv*1e6)
	end=time.time()
	print('cost {:.2f}'.format(end-begin))
	plt.scatter(np.arange(pts-1),gout[0,:],s=1)
	plt.show()
	code.interact(local=dict(globals(),**locals()))