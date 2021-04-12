import matplotlib.pyplot as plt
import numpy as np
import code,time,copy,csv,io,os
delta=lambda x: x[...,1:]-x[...,:-1]
np.set_printoptions(suppress=True,precision=2)
def cdf(x):
    x,y=sorted(x),np.arange(len(x))/len(x)*100
    return x,y
def getW(tx):
	n=len(tx)
	return (n-1)/(tx[n-1]-tx[0])
def getJitter(tg,avg):
	# avg is the gap value in us
	return np.mean(np.abs(tg-avg))
def get(tx,time=1e-3):
	# 将tx按time的长度进行划分
	n=np.ceil(tx[-1]-tx[0])/time
	times=np.arange(tx[0],tx[-1],time)
	idx=np.searchsorted(tx,times)
	w=(idx[1:]-idx[:-1])/(tx[idx[1:]]-tx[idx[:-1]])
	return w
def perror(tx,time,p,v):
	n=np.ceil(tx[-1]-tx[0])/time
	times=np.arange(tx[0],tx[-1],time)
	idx=np.searchsorted(tx,times)
	rate=(idx[1:]-idx[:-1])*p*8/(tx[idx[1:]]-tx[idx[:-1]])*1e-6
	perr=(rate-v)/v*100
	return perr
def error(tx,time,p,v):
	n=np.ceil(tx[-1]-tx[0])/time
	times=np.arange(tx[0],tx[-1],time)
	idx=np.searchsorted(tx,times)
	rate=(idx[1:]-idx[:-1])*p*8/(tx[idx[1:]]-tx[idx[:-1]])*1e-6
	return rate-v
if __name__=='__main__':
	f1='/data/iperf3/traffic'
	f2='/data/ditg/traffic'
	f3='/data/iperf3/pk.npz'
	begin=time.time()
	if os.path.exists(f3):
		d=np.load(f3)
		d1=d['d1']
		d2=d['d2']
	else:
		d1=np.loadtxt(f1,delimiter='\t')
		d2=np.loadtxt(f2,delimiter='\t')
		np.savez(f3,d1=d1,d2=d2)
	end=time.time()
	print('time {:.2f}s'.format(end-begin))
	txs=[d1[:,0],d2[:,0]]
	times=[1e-3,10e-3,50e-3,100e-3]
	p,v=1472,500
	err1=[error(txs[0],time,p,v) for time in times]
	err2=[error(txs[1],time,p,v) for time in times]
	fig,axs=plt.subplots(nrows=len(times),ncols=2,figsize=(10,10))
	for i in range(len(times)):
		x,y=cdf(err1[i])
		axs[i][0].plot(x,y)
		axs[i][0].text(.05,.8,'{:.0f}ms iperf3'.format(times[i]*1e3),transform=axs[i][0].transAxes)
		axs[i][0].text(.05,.7,'n:{:d}'.format(len(err1[i])),transform=axs[i][0].transAxes)
		x,y=cdf(err2[i])
		axs[i][1].plot(x,y)
		axs[i][1].text(.05,.8,'{:.0f}ms D-ITG'.format(times[i]*1e3),transform=axs[i][1].transAxes)
		axs[i][1].text(.05,.7,'n:{:d}'.format(len(err2[i])),transform=axs[i][1].transAxes)
		if i==len(times)-1:
			axs[i][0].set_xlabel('Error of iperf3(Mbps)')
			axs[i][1].set_xlabel('Error of D-ITG(Mbps)')
	fig.text(0.07,0.5,'Percentage(%)',va='center',rotation='vertical')
	fig.suptitle('CDF(Traffic Generator Error for 500Mbps)',y=0.92)
	plt.savefig('/images/generator/comparison.png',bbox_inches='tight')
	plt.close(fig)
	#code.interact(local=dict(globals(),**locals()))