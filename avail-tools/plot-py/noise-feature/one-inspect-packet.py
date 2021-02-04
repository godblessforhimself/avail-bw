import matplotlib.pyplot as plt
import numpy as np
import code,time
delta=lambda x: x[1:]-x[:-1]
np.set_printoptions(suppress=True)

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
			temp=np.loadtxt(sendFile.format(duration,ic))[:,0]*1e6
			sendReal.append(temp.reshape((repeat,n)))
			temp=np.loadtxt(recvFile.format(duration,ic))[:,0]*1e6
			recvReal.append(temp.reshape((repeat,n)))
			temp=np.loadtxt(bqrFile.format(duration,ic),delimiter=',')*1e6
			send.append(temp[:,0].reshape((repeat,n)))
			recv.append(temp[:,1].reshape((repeat,n)))
	end=time.time()
	print('time {:.2f}'.format(end-begin))
	#(duration*ic,repeat,n)
	send=np.array(send)
	recv=np.array(recv)
	sendReal=np.array(sendReal)
	recvReal=np.array(recvReal)
	ds=send-sendReal
	ds=ds-np.mean(ds,axis=2).reshape((-1,repeat,1))
	dr=recv-recvReal
	dr=dr-np.mean(dr,axis=2).reshape((-1,repeat,1))
	loadNumber=100
	inspectNumber=100
	# 发送负载长度误差在第一个包
	x=send[:,:,100-1]-send[:,:,0]
	y=sendReal[:,:,100-1]-sendReal[:,:,0]
	gapx=send[:,:,1:]-send[:,:,:-1]
	gapy=sendReal[:,:,1:]-sendReal[:,:,:-1]
	error=np.mean((y-x)**2)
	z=send[:,:,100-1]-send[:,:,1]
	z=z+np.mean(gapx[:,:,1:99],axis=2)
	error2=np.mean((y-z)**2)
	print('发送负载误差 {:.2f} 舍去第一个包间隔 {:.2f}'.format(error,error2))
	# 发送检查长度误差很小
	x=send[:,:,loadNumber+inspectNumber-1]-send[:,:,loadNumber-1]
	y=sendReal[:,:,loadNumber+inspectNumber-1]-sendReal[:,:,loadNumber-1]
	error=np.mean((y-x)**2)
	print('发送检查误差 {:.2f}'.format(error))
	# 接收负载长度误差
	x=recv[:,:,100-1]-recv[:,:,0]
	y=recvReal[:,:,100-1]-recvReal[:,:,0]
	gapx=recv[:,:,1:100]-recv[:,:,:100-1]
	idxGap=np.argsort(gapx,axis=2)
	error=np.mean((y-x)**2)
	thres=(recv[:,:,100-1]-recv[:,:,0])/99
	z=[]	
	for i in range(len(durations)*2):
		for j in range(repeat):
			idx=np.where(gapx[i,j,:]>=thres[i,j])[0]
			left=idx[0]
			right=idx[-1]
			v=(loadNumber-1)*(recv[i,j,right]-recv[i,j,left])/(right-left)
			#print('{} {} {}'.format(left,right,v))
			z.append(v)
	z=np.array(z).reshape((-1,repeat))
	error2=np.mean((y-z)**2)
	print('接收负载误差 {:.2f} 校准后误差 {:.2f}'.format(error,error2))
	# 接收检查长度误差
	left,right=loadNumber-1,loadNumber+inspectNumber
	x=recv[1::2,:,right-1]-recv[1::2,:,left]
	y=recvReal[1::2,:,right-1]-recvReal[1::2,:,left]
	gapx=recv[1::2,:,left+1:right]-recv[1::2,:,left:right-1]
	gapy=recvReal[1::2,:,left+1:right]-recvReal[1::2,:,left:right-1]
	d=x-y
	lim=25
	x=x[:lim,:]
	y=y[:lim,:]
	error=np.mean((y-x)**2)
	print('接收检查误差 {:.2f}'.format(error))
	end=time.time()
	print('time {:.2f}'.format(end-begin))
	#code.interact(local=dict(globals(),**locals()))