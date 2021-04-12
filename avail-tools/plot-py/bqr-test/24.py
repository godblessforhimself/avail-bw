import matplotlib.pyplot as plt
import numpy as np
import code,time,copy,io
delta=lambda x: x[...,1:]-x[...,:-1]
np.set_printoptions(suppress=True)
if __name__=='__main__':
	fn='/data/bqr-test/24-time'
	begin=time.time()
	data=[]
	f=open(fn)
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
	end=time.time()
	tx=[d1[:,0] for d1 in data]
	rx=[d1[:,1] for d1 in data]
	tg=[delta(tx_)*1e6 for tx_ in tx]
	rg=[delta(rx_)*1e6 for rx_ in rx]
	def removeOffset(x):
		return x-np.min(x)
	owd=[removeOffset(d1[:,1]-d1[:,0])*1e6 for d1 in data]
	o=owd[0]
	t=(tx[0]-tx[0][0])*1e6
	print(o[100:])
	code.interact(local=dict(globals(),**locals()))