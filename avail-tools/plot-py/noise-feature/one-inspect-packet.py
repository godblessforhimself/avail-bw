import matplotlib.pyplot as plt
import numpy as np
import code,time,matplotlib
delta=lambda x: x[1:]-x[:-1]
def key(d,i):
	return '{} {}'.format(d,i)
def plot(durations,u,idx,label):
	fig,axs=plt.subplots(nrows=len(durations),ncols=4,sharex=True,sharey=True,figsize=(10,100))
	for i,duration in enumerate(durations):
		for j in range(2):
			for ic in range(2):
				s=key(duration,ic)
				ax=axs[i][j*2+ic]
				y=u[j][s][idx,:]
				x=np.arange(len(y))
				ax.scatter(x,y,s=1)
				ax.set_ylim(-80,80)
				ax.set_yticks(np.arange(-40,40+1,40))
				ax.set_xlim(-100,300)
				ax.set_xticks(np.arange(0,200+1,100))
				ax.text(0.1,0.8,'duration {:.0f}us'.format(duration),transform=ax.transAxes)
				if i==len(durations)-1:
					ax.set_xlabel(label[j*2+ic])
	plt.subplots_adjust(wspace=0,hspace=0)
	fig.suptitle('t(user-physical)',y=0.9)
	fig.text(0.07,0.5,'user-physical(us)',va='center',rotation='vertical')
	plt.savefig('/images/noise-feature/one-inspect-packet/{}.png'.format(idx),bbox_inches='tight')
	plt.close(fig)
def plotDenoise(durations,u,idx):
	label=['recv(IC disabled,Raw)','recv(IC disabled,Denoised)','recv(IC enabled,Raw)','recv(IC enabled,Denoised)']
	fig,axs=plt.subplots(nrows=len(durations),ncols=4,sharex=True,sharey=True,figsize=(10,100))
	for i,duration in enumerate(durations):
		for ic in range(2):
			s=key(duration,ic)
			for j in range(2):
				ax=axs[i][j+ic*2]
				y=u[j][s][idx,:]
				x=np.arange(len(y))
				ax.scatter(x,y,s=1)
				ax.set_ylim(-80,80)
				ax.set_yticks(np.arange(-40,40+1,40))
				ax.set_xlim(-100,300)
				ax.set_xticks(np.arange(0,200+1,100))
				ax.text(0.1,0.8,'duration {:.0f}us'.format(duration),transform=ax.transAxes)
				if i==len(durations)-1:
					ax.set_xlabel(label[j+ic*2])
	plt.subplots_adjust(wspace=0,hspace=0)
	fig.suptitle('t(user-physical)',y=0.9)
	fig.text(0.07,0.5,'user-physical(us)',va='center',rotation='vertical')
	plt.savefig('/images/noise-feature/one-inspect-packet/denoise-{}.png'.format(idx),bbox_inches='tight')
	plt.close(fig)
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
	# send-real(IC disabled, IC enabled); recv-real(IC-disabled,IC enables)
	# duration 1200 - 12000
	begin=time.time()
	sendFile='/data/noise/one-inspect-packet/duration-{}-IC-{}-send'
	recvFile='/data/noise/one-inspect-packet/duration-{}-IC-{}-recv'
	bqrFile='/data/noise/one-inspect-packet/duration-{}-IC-{}-bqr'
	send,recv=[],[]
	sendReal=[]
	recvReal=[]
	repeat=3
	n=200
	durations=range(2000, 200000+1,4000)
	for duration in durations:
		for ic in range(2):
			s=key(duration,ic)
			temp=np.loadtxt(sendFile.format(duration,ic))[:,0]
			sendReal.append(temp.reshape((repeat,n)))
			temp=np.loadtxt(recvFile.format(duration,ic))[:,0]
			recvReal.append(temp.reshape((repeat,n)))
			temp=np.loadtxt(bqrFile.format(duration,ic),delimiter=',')
			send.append(temp[:,0].reshape((repeat,n)))
			recv.append(temp[:,1].reshape((repeat,n)))
	end=time.time()
	print('time {:.2f}'.format(end-begin))
	#(duration,ic,repeat,n)
	send=np.array(send).reshape((len(durations),2,repeat,n))
	recv=np.array(recv).reshape((len(durations),2,repeat,n))
	owd=recv-send
	sendReal=np.array(sendReal).reshape((len(durations),2,repeat,n))
	recvReal=np.array(recvReal).reshape((len(durations),2,repeat,n))
	owdReal=recvReal-sendReal
	ds=send-sendReal
	ds=ds-np.mean(ds,axis=3)[:,:,:,np.newaxis]
	dr=recv-recvReal
	dr=dr-np.mean(dr,axis=3)[:,:,:,np.newaxis]
	loadNumber=100
	inspectNumber=100
	# OWD user & real
	'''
	for i,duration in enumerate(durations):
		for ic in range(2):
			for r in range(repeat):
				y1=owd[i,ic,r,:]*1e6
				y2=owdReal[i,ic,r,:]*1e6
				y1=y1-np.mean(y1)+np.mean(y2)
				fig,ax=plt.subplots(figsize=(10,10))
				plt.plot(y1,label='User Time',color=color[0],linestyle=linestyle[0])
				plt.plot(y2,label='Real Time',color=color[1],linestyle=linestyle[1])
				plt.legend(loc='upper left',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
				plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
				ax.tick_params('both',length=1,width=1,which='both',pad=1)
				plt.xlabel('Packet Index',labelpad=0)
				plt.ylabel('One Way Delay(us)',labelpad=0)
				plt.savefig('/images/noise-feature/OWD/{}-{}-{}.png'.format(duration,ic,r),bbox_inches='tight')
				plt.close(fig)
	end=time.time()
	print('time {:.2f}'.format(end-begin))
	# send-sendReal 
	for i,duration in enumerate(durations):
		for ic in range(2):
			for r in range(repeat):
				y1=send[i,ic,r,:]
				y2=sendReal[i,ic,r,:]
				y=y1-y2
				y=(y-np.mean(y))*1e6
				fig,ax=plt.subplots(figsize=(10,10))
				plt.plot(y,label='xxx',color=color[0],linestyle=linestyle[0])
				plt.legend(loc='upper left',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
				plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
				ax.tick_params('both',length=1,width=1,which='both',pad=1)
				plt.xlabel('Packet Index',labelpad=0)
				plt.ylabel('Send Time(us)',labelpad=0)
				plt.savefig('/images/noise-feature/sendtime/{}-{}-{}.png'.format(duration,ic,r),bbox_inches='tight')
				plt.close(fig)
	end=time.time()
	print('time {:.2f}'.format(end-begin))
	# recv-recvReal
	for i,duration in enumerate(durations):
		for ic in range(2):
			for r in range(repeat):
				y1=recv[i,ic,r,:]
				y2=recvReal[i,ic,r,:]
				y=y1-y2
				y=(y-np.mean(y))*1e6
				fig,ax=plt.subplots(figsize=(10,10))
				plt.plot(y,label='x',color=color[0],linestyle=linestyle[0])
				plt.legend(loc='upper left',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
				plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
				ax.tick_params('both',length=1,width=1,which='both',pad=1)
				plt.xlabel('Packet Index',labelpad=0)
				plt.ylabel('Recv Time(us)',labelpad=0)
				plt.savefig('/images/noise-feature/recvtime/{}-{}-{}.png'.format(duration,ic,r),bbox_inches='tight')
				plt.close(fig)
	'''
	# 将duration=2000,114000,198000;ic=0,1;r=0的绘制出来
	targets=[2000,114000,198000]
	for i,duration in enumerate(durations):
		if duration in targets:
			for ic in range(2):
				r=0
				y1=owd[i,ic,r,:]*1e6
				y2=owdReal[i,ic,r,:]*1e6
				y1=y1-np.mean(y1)+np.mean(y2)
				fig,ax=plt.subplots(figsize=(1.3,1.1))
				x=np.arange(len(y1))
				plt.scatter(x,y1,s=1,label='User Time',color=color[0])
				#plt.plot(y1,label='User Time',color=color[0],linestyle=linestyle[0])
				plt.plot(y2,label='Real Time',color=color[1],linestyle=linestyle[1])
				plt.xlim(-10,210)
				plt.xticks(np.arange(0,200+1,40))
				plt.ylim(0,650)
				plt.yticks(np.arange(0,600+1,100))
				plt.legend(loc='upper center',framealpha=.5,ncol=2,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=4)
				plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
				ax.tick_params('both',length=1,width=1,which='both',pad=1)
				plt.xlabel('Packet Index',labelpad=0)
				plt.ylabel('One Way Delay(us)',labelpad=0)
				plt.savefig('{:s}/noise-OWD-{}-{}.pdf'.format(imgDir,duration,ic),bbox_inches='tight')
				plt.close(fig)
	for i,duration in enumerate(durations):
		if duration in targets:
			for ic in range(2):
				r=0
				y1=send[i,ic,r,:]
				y2=sendReal[i,ic,r,:]
				y=y1-y2
				y=(y-np.mean(y))*1e6
				fig,ax=plt.subplots(figsize=(1.3,1.1))
				x=np.arange(len(y))
				plt.scatter(x,y,s=1,color=color[0])
				plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
				ax.tick_params('both',length=1,width=1,which='both',pad=1)
				plt.xlim(-10,210)
				plt.xticks(np.arange(0,200+1,40))
				plt.ylim(-60,60)
				plt.yticks(np.arange(-60,60+1,20))
				plt.xlabel('Packet Index',labelpad=0)
				plt.ylabel('Send(User - Real) (us)',labelpad=0)
				plt.savefig('{:s}/noise-sendtime-{}-{}.pdf'.format(imgDir,duration,ic),bbox_inches='tight')
				plt.close(fig)
	for i,duration in enumerate(durations):
		if duration in targets:
			for ic in range(2):
				r=0
				y1=recv[i,ic,r,:]
				y2=recvReal[i,ic,r,:]
				y=y1-y2
				y=(y-np.mean(y))*1e6
				fig,ax=plt.subplots(figsize=(1.3,1.1))
				x=np.arange(len(y))
				plt.scatter(x,y,s=1,color=color[0])
				plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
				ax.tick_params('both',length=1,width=1,which='both',pad=1)
				plt.xlim(-10,210)
				plt.xticks(np.arange(0,200+1,40))
				#plt.ylim(-60,60)
				#plt.yticks(np.arange(-60,60+1,20))
				plt.xlabel('Packet Index',labelpad=0)
				plt.ylabel('Recv(User-Real) (us)',labelpad=0)
				plt.savefig('{:s}/noise-recvtime-{}-{}.pdf'.format(imgDir,duration,ic),bbox_inches='tight')
				plt.close(fig)
	end=time.time()
	print('time {:.2f}'.format(end-begin))
	#code.interact(local=dict(globals(),**locals()))