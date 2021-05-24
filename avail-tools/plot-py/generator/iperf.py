import matplotlib.pyplot as plt
import numpy as np
import code,time,copy,csv,io,os,matplotlib
delta=lambda x: x[...,1:]-x[...,:-1]
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
def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
np.set_printoptions(suppress=True,precision=2)
color=[pickColor(i, 10) for i in range(10)]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
plt.rcParams.update({'font.size':7})
matplotlib.rcParams['hatch.linewidth']=0.3
marker=['d','.','*','<','p'] #5
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1)),(0,(3,1,1,1,1,1))] #5
hatch=['/','\\','x','o','-|'] #5
imgDir='/home/tony/Files/available_bandwidth/thesis-svn/IMC2021/BurstQueueRecovery-jintao/images'

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
	times=[1e-3,10e-3,100e-3]
	p,v=1472,500
	err1=[error(txs[0],time,p,v) for time in times]
	err2=[error(txs[1],time,p,v) for time in times]
	err=[err1,err2]
	label=[]
	s=['iperf3-{:.0f}ms','D-ITG-{:.0f}ms']
	for m in range(2):
		l=[]
		for i in range(len(times)):
			l.append(s[m].format(times[i]*1e3))
		label.append(l)
	fig,ax=plt.subplots(figsize=(3.4,1.1))
	for m in range(2):
		for i in range(len(times)):
			x,y=cdf(err[m][i])
			if len(x)>500:
				step=len(x)//100
				x,y=x[::step],y[::step]
			print(len(x))
			ax.plot(x,y,label=label[m][i],color=color[i+m*len(times)],linestyle=linestyle[(i)%len(linestyle)])
	dx,dy=-9.5,50
	ax.annotate('D-ITG',(dx,dy),xytext=(dx+3,dy),arrowprops={'arrowstyle':'->'},ha='center',va='center',fontsize=7)
	dx,dy=0,50
	ax.annotate('iperf3',(dx,dy),xytext=(dx-2.5,dy),arrowprops={'arrowstyle':'->'},ha='center',va='center',fontsize=7)
	plt.xlim(-15,5)
	plt.yticks(np.arange(0,100+1,20))
	plt.legend(loc='upper left',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)

	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)

	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)

	plt.xlabel('Error(Mbps)',labelpad=0)
	plt.ylabel('Percentage(%)',labelpad=0)
	plt.savefig('{:s}/traffic-generator-comparison.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/traffic-generator-comparison.eps'.format(imgDir),bbox_inches='tight')
	plt.show()
	plt.close(fig)
	#code.interact(local=dict(globals(),**locals()))