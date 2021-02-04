# 实际发出的流量，与iperf3对比
# 实际时间戳与用户时间戳的差异，速率、中断延迟

import matplotlib.pyplot as plt
import numpy as np
import code
delta=lambda x:x[1:]-x[:-1]
delta2=lambda x:x[:,1:]-x[:,:-1]
sendFile='/data/bqr-constant/rate-{}Mbps-IC-{}-send'
recvFile='/data/bqr-constant/rate-{}Mbps-IC-{}-recv'
bqrFile='/data/bqr-constant/rate-{}Mbps-IC-{}-bqr'
def cdf(ax,x):
    x,y=sorted(x),np.arange(len(x))/len(x)
    ax.plot(x,y*100,color='green')

def mse(x,y):
	return np.mean((x-y)**2)

def histogram(ax,x,x0,mse_,rate):
	bins=np.arange(x0-5,x0+5+1,1)
	ax.hist(x,bins=bins,weights=[100/len(x)]*len(x),histtype='bar',rwidth=.1,color='blue')
	cdf(ax,x)
	ax.text(0.6,0.5,'MSE={:.2f}'.format(mse_),transform=ax.transAxes)
	ax.text(0.1,0.8,'rate {}Mbps'.format(rate),transform=ax.transAxes)
	ax.axvline(x0,color='black',linestyle='dashed')
	ax.grid()
	ax.set_ylim(0,100)
	ax.set_xlim(x0-5,x0+5)
	ax.set_xticks(np.arange(np.around(x0-5),np.around(x0+5+1),1))

#实际发出的流量分布
def loadUser(send,recv,rates,repeat,scale=1e6):
	for rate in rates:
		for ic in [0,1]:
			f='{} {}'.format(rate,ic)
			data=np.loadtxt(bqrFile.format(rate,ic),delimiter=',')*scale
			data=data.reshape((repeat,-1,2))
			s,r=data[:,:,0],data[:,:,1]
			send[f]=s
			recv[f]=r
def loadReal(send,recv,rates,repeat,scale=1e6):
	for rate in rates:
		for ic in [0,1]:
			f='{} {}'.format(rate,ic)
			s=np.loadtxt(sendFile.format(rate,ic)).reshape((repeat,-1,2))[:,:,0]*1e6
			r=np.loadtxt(recvFile.format(rate,ic)).reshape((repeat,-1,2))[:,:,0]*1e6
			send[f]=s
			recv[f]=r

def getGapOnDic(item):
	gap={}
	for k,v in item.items():
		gap[k]=v[:,1:]-v[:,:-1]
	return gap
def getGap(*item):
	ret=[]
	for it in item:
		gap=getGapOnDic(it)
		ret.append(gap)
	return ret
def precision(ginReal):
	rates=[10,50,100,200,500,800]
	fig,axs=plt.subplots(nrows=len(rates))
	for i,rate in enumerate(rates):
		gap=1472*8/rate
		gin=ginReal['{} {}'.format(rate,0)].flatten()*1e6
		mseGin=mse(gin,gap)
		histogram(axs[i],gin,gap,mseGin,rate)
	plt.xlabel('gap(us)')
	fig.text(0.04,0.5,'percentage(%)',va='center',rotation='vertical')
	fig.suptitle('Bqr traffic precision',fontsize=10)
	plt.savefig('/images/bqr-constant/bqr-precision.png',bbox_inches='tight')

#用户态和实际的区别
def ginUserDiff(gin,ginReal):
	rates=[10,50,100,200,500,800]
	fig,axs=plt.subplots(nrows=len(rates),ncols=2,sharey=True)
	for i,rate in enumerate(rates):
		g=ginReal['{} {}'.format(rate,0)].flatten()*1e6
		ax=axs[i][0]
		ax.hist(g,weights=[100/len(g)]*len(g),histtype='bar',rwidth=.1,color='blue')
		cdf(ax,g)
		ax.text(0.1,0.8,'rate {}Mbps'.format(rate),transform=ax.transAxes)
		ax.grid()
		ax.set_ylim(0,100)
		g=gin['{} {}'.format(rate,0)].flatten()*1e6
		ax=axs[i][1]
		ax.hist(g,weights=[100/len(g)]*len(g),histtype='bar',rwidth=.1,color='blue')
		cdf(ax,g)
		ax.text(0.1,0.8,'rate {}Mbps'.format(rate),transform=ax.transAxes)
		ax.grid()
		ax.set_ylim(0,100)
def goutUserDiff(gout,goutReal):
	rates=[10,50,100,200,500,800]
	fig,axs=plt.subplots(nrows=len(rates),ncols=2,sharey=True)
	for i,rate in enumerate(rates):
		g=goutReal['{} {}'.format(rate,0)].flatten()*1e6
		ax=axs[i][0]
		ax.hist(g,weights=[100/len(g)]*len(g),histtype='bar',rwidth=.1,color='blue')
		cdf(ax,g)
		ax.text(0.1,0.8,'rate {}Mbps'.format(rate),transform=ax.transAxes)
		ax.grid()
		ax.set_ylim(0,100)
		g=gout['{} {}'.format(rate,0)].flatten()*1e6
		ax=axs[i][1]
		ax.hist(g,weights=[100/len(g)]*len(g),histtype='bar',rwidth=.1,color='blue')
		cdf(ax,g)
		ax.text(0.1,0.8,'rate {}Mbps'.format(rate),transform=ax.transAxes)
		ax.grid()
		ax.set_ylim(0,100)

def stat(v):
	print('mean {:.2f} std {:.2f} min {:.2f} max {:.2f}'.format(np.mean(v), np.std(v), np.min(v), np.max(v)))

def plotOwd(rates,repeat,owd,owdReal):
	#owd
	label=['index(IC disabled)', 'index(IC enabled)']
	for rate in rates:
		fig,axs=plt.subplots(nrows=repeat,ncols=2,sharex=True,sharey=True,figsize=(10,10))
		for i in range(repeat):
			for j in range(2):
				f='{} {}'.format(rate,j)
				ax=axs[i][j]
				y=owd[f][i,:]-owdReal[f][i,:]
				y=y-np.mean(y)
				x=np.arange(len(y))
				ax.scatter(x,y,s=1)
				ax.set_ylim(-50,50)
				if i==repeat-1:
					ax.set_xlabel(label[j])
		fig.suptitle('owd(user-real)({}Mbps)'.format(rate),y=0.9)
		plt.savefig('/images/bqr-constant/owd-rate-{}Mbps.png'.format(rate),bbox_inches='tight')

def plotUserReal(rates,repeat,send,recv,sendReal,recvReal):
	u=[send,recv]
	v=[sendReal,recvReal]
	ds,dr={},{}
	for k,v in send.items():
		ds[k]=v-sendReal[k]
		dr[k]=recv[k]-recvReal[k]
		ds[k]=ds[k]-(np.mean(ds[k],axis=1)).reshape((-1,1))
		dr[k]=dr[k]-(np.mean(dr[k],axis=1)).reshape((-1,1))
	w=[ds,dr]
	label=['send(IC disabled)','send(IC enabled)','recv(IC disabled)','recv(IC enabled)']
	for rate in rates:
		fig,axs=plt.subplots(nrows=repeat,ncols=4,sharex=True,sharey=True,figsize=(10,10))
		for i in range(repeat):
			for ic in range(2):
				f='{} {}'.format(rate,ic)
				for j in range(2):
					ax=axs[i][j*2+ic]
					y=w[j][f][i,:]
					x=np.arange(len(y))
					ax.scatter(x,y,s=1)
					ax.set_ylim(-50,50)
					ax.set_yticks(np.arange(-40,40+1,20))
					ax.set_xlim(-250,1250)
					ax.set_xticks(np.arange(0,1000+1,250))
					if i==repeat-1:
						ax.set_xlabel(label[j*2+ic])
		plt.subplots_adjust(wspace=0.0,hspace=.0)
		fig.suptitle('timestamp(user-real)({}Mbps)'.format(rate),y=0.9)
		fig.text(0.07,0.5,'user-real(us)',va='center',rotation='vertical')
		plt.savefig('/images/bqr-constant/diff-rate-{}Mbps.png'.format(rate),bbox_inches='tight')

	fig,axs=plt.subplots(nrows=len(rates),ncols=4,sharex=True,sharey=True,figsize=(10,10))
	for i in range(len(rates)):
		rate=rates[i]
		for j in range(2):
			for ic in range(2):
				f='{} {}'.format(rate,ic)
				ax=axs[i][2*j+ic]
				y=w[j][f][0,:]
				x=np.arange(len(y))
				ax.scatter(x,y,s=1)
				ax.set_ylim(-75,75)
				ax.set_yticks(np.arange(-60,60+1,30))
				ax.set_xlim(-150,1150)
				ax.set_xticks(np.arange(0,1000+1,250))
				ax.text(0.05,0.9,'rate {:.0f}Mbps'.format(rate),transform=ax.transAxes)
				if i==len(rates)-1:
					ax.set_xlabel(label[2*j+ic])
	plt.subplots_adjust(wspace=0,hspace=0)
	fig.suptitle('timestamp(user-real)',y=0.9)
	fig.text(0.07,0.5,'user-real(us)',va='center',rotation='vertical')
	plt.savefig('/images/bqr-constant/diff.png',bbox_inches='tight')

def plotRealGap(rates,repeat,ginReal,goutReal):
	u=[ginReal,goutReal]
	label=['gin(IC disabled)','gout(IC disabled)']
	for rate in rates:
		fig,axs=plt.subplots(nrows=repeat,ncols=2,sharex=True,sharey=True,figsize=(10,10))
		gap=1472*8/rate
		for i in range(repeat):
			f='{} {}'.format(rate,0)
			for j in range(2):
				ax=axs[i][j]
				y=u[j][f][i,:]-gap
				x=np.arange(len(y))
				ax.scatter(x,y,s=1)
				ax.set_ylim(-30,30)
				ax.set_yticks(np.arange(-20,20+1,10))
				if i==repeat-1:
					ax.set_xlabel(label[j])
		plt.subplots_adjust(wspace=0.0,hspace=.0)
		fig.text(0.07,0.5,'real-target(us)',va='center',rotation='vertical')
		fig.suptitle('gap(real-target)({}Mbps)'.format(rate),y=0.9)
		plt.savefig('/images/bqr-constant/precision-{}Mbps.png'.format(rate),bbox_inches='tight')
	fig,axs=plt.subplots(nrows=len(rates),ncols=2,sharex=True,sharey=True,figsize=(10,10))
	for i in range(len(rates)):
		rate=rates[i]
		gap=1472*8/rate
		f='{} {}'.format(rate,0)
		for j in range(2):
			ax=axs[i][j]
			y=u[j][f][0,:]-gap
			x=np.arange(len(y))
			ax.scatter(x,y,s=1)
			ax.set_ylim(-30,30)
			ax.set_yticks(np.arange(-20,20+1,10))
			ax.text(0.05,0.9,'rate {:.0f}Mbps'.format(rate),transform=ax.transAxes)
			if i==len(rates)-1:
				ax.set_xlabel(label[j])
	plt.subplots_adjust(wspace=0,hspace=0)
	fig.suptitle('gap(real-target)',y=0.9)
	fig.text(0.07,0.5,'real-target(us)',va='center',rotation='vertical')
	plt.savefig('/images/bqr-constant/precision.png',bbox_inches='tight')

if __name__=='__main__':
	rates=[10,50,100,200,500,800]
	repeat=10
	# 'rate ic'
	send={}
	recv={}
	sendReal={}
	recvReal={}
	loadUser(send,recv,rates,repeat)
	loadReal(sendReal,recvReal,rates,repeat)
	gin,gout,ginReal,goutReal=getGap(send,recv,sendReal,recvReal)
	#precision(ginReal)
	#ginUserDiff(gin,ginReal)
	#goutUserDiff(gout,goutReal)
	#plt.show()
		
	owd={}
	owdReal={}
	def norm(v):
		offset=np.mean(v,axis=1).reshape((-1,1))
		return v-offset
	for rate in rates:
		for ic in [0,1]:
			f='{} {}'.format(rate,ic)
			owd[f]=(recv[f]-send[f])
			owdReal[f]=(recvReal[f]-sendReal[f])
	#plotOwd(rates,repeat,owd,owdReal)
	plotUserReal(rates,repeat,send,recv,sendReal,recvReal)
	plotRealGap(rates,repeat,ginReal,goutReal)

	#               10 50 100 200 500 800
	# 50Gap ic off  Y  N   N   N   N   N
	# 50Gap ic on   Y  N   N   Y   Y   +-50
	#code.interact(local=dict(globals(),**locals()))
