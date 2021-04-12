import matplotlib.pyplot as plt
import numpy as np
import code,time,copy,csv,io
delta=lambda x: x[...,1:]-x[...,:-1]
np.set_printoptions(suppress=True)
def cdf(x):
    x,y=sorted(x),np.arange(len(x))/len(x)*100
    plt.plot(x,y,color='green')
if __name__=='__main__':
	fn='/data/ditg/traffic'
	begin=time.time()
	data=np.loadtxt(fn,delimiter='\t')
	end=time.time()
	tx=data[:,0]
	tg=delta(tx)*1e6
	print('time {:.2f}s'.format(end-begin))
	#cdf(tg)
	t=[]
	for i in range(0, len(tx)-3000):
		v=3000/(tx[i+3000]-tx[i])
		t.append(v)
	code.interact(local=dict(globals(),**locals()))