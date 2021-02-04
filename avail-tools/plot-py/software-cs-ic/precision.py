import matplotlib.pyplot as plt
import numpy as np
import code
delta=lambda x:x[1:]-x[:-1]
def cdf(ax,x):
    x,y=sorted(x),np.arange(len(x))/len(x)
    ax.plot(x,y*100,color='green')

def mse(x,y):
	return np.mean((x-y)**2)
def histogram(ax,x,x0,mse_,rate):
	#ax.hist(x,bins=50,weights=[100/len(x)]*len(x),histtype='bar',rwidth=1)
	bins=np.arange(x0-5,x0+5+1,1)
	ax.hist(x,bins=bins,weights=[100/len(x)]*len(x),histtype='bar',rwidth=.2,color='blue')
	cdf(ax,x)
	ax.text(0.6,0.5,'MSE={:.2f}'.format(mse_),transform=ax.transAxes)
	ax.text(0.1,0.8,'rate {}Mbps'.format(rate),transform=ax.transAxes)
	ax.axvline(x0,color='black',linestyle='dashed')
	ax.grid()
	ax.set_ylim(0,100)
	ax.set_xlim(x0-5,x0+5)
	ax.set_xticks(np.arange(np.around(x0-5),np.around(x0+5+1),1))

def plotAll(ax,rate,n,sendFile,recvFile):
	Gin=[]
	for i in range(n):
		send=np.loadtxt(sendFile.format(rate,i+1))[:,0]
		gin=delta(send)*1e6
		Gin.append(gin)
	Gin=np.array(Gin).flatten()
	gap=1472*8/rate
	mseGin=mse(gin,gap)
	histogram(ax,gin,gap,mseGin,rate)

if __name__=='__main__':
	rates=[10,100,500,800]
	nRepeat=10
	sendFile='/data/iperf3-exp1/rate-{}Mbps-{}-send'
	recvFile='/data/iperf3-exp1/rate-{}Mbps-{}-recv'
	send,recv={},{}
	for rate in rates:
		for i in range(nRepeat):
			s1='{} {}'.format(rate,i)
			send[s1]=np.loadtxt(sendFile.format(rate,i+1))[:,0]*1e6
			recv[s1]=np.loadtxt(recvFile.format(rate,i+1))[:,0]*1e6
	def getGapOnDic(dic):
		ret={}
		for k,v in dic.items():
			ret[k]=v[1:]-v[:-1]
		return ret
	gin,gout=getGapOnDic(send),getGapOnDic(recv)
	v=[gin,gout]
	for rate in rates:
		fig,axs=plt.subplots(nrows=nRepeat,ncols=2,sharex=True,figsize=(10,10))
		gap=1472*8/rate
		for i in range(nRepeat):
			s1='{} {}'.format(rate,i)
			for j in range(2):
				y=v[j][s1]-gap
				x=np.arange(len(y))
				axs[i][j].scatter(x,y,s=1)
				axs[i][j].set_ylim(-20,20)
		plt.savefig('/images/iperf3-exp1/rate-{}Mbps.png'.format(rate),bbox_inches='tight')
	
	#fig,axs=plt.subplots(nrows=len(rates))
	#for i,rate in enumerate(rates):
	#plotAll(axs[i],rate,nRepeat,sendFile,recvFile)
	#plt.xlabel('gap(us)')
	#fig.text(0.04,0.5,'percentage(%)',va='center',rotation='vertical')
	#plt.savefig('/images/iperf3-exp1/precision.png',bbox_inches='tight')
	#code.interact(local=dict(globals(),**locals()))