import matplotlib.pyplot as plt
import numpy as np
import code,time,copy
delta=lambda x: x[...,1:]-x[...,:-1]
np.set_printoptions(suppress=True)

if __name__=='__main__':
	fn='/data/bqr-optimization/{}.txt'
	
	begin=time.time()
	# adr2 61-108 48个关闭中断延迟
	# adr2 109-156 48个开启中断延迟
	number=[i for i in range(61,156+1)]
	data=[np.loadtxt(fn.format(i),delimiter=',') for i in number]
	end=time.time()
	tx=[d1[:,0] for d1 in data]
	rx=[d1[:,1] for d1 in data]
	tg=[delta(tx_) for tx_ in tx]
	rg=[delta(rx_) for rx_ in rx]
	def removeOffset(x):
		return x-np.min(x)
	owd=[removeOffset(d1[:,1]-d1[:,0])*1e6 for d1 in data]
	def tf(a):
		# recover degree
		ret=np.copy(a[100:])
		ret=(ret-ret[-1])/(ret[0]-ret[-1])
		return ret
	def lastm(a):
		# lastmax
		ret=np.copy(a[100:])
		for i in range(len(ret)-2,0-1,-1):
			if ret[i]<ret[i+1]:
				ret[i]=ret[i+1]
		return ret
	def recover(a):
		# owd last - first
		return a[-1]-a[0]
	def firstLow(a):
		# first low than -10:
		# 存在性
		pos=np.where(a<np.max(a[-10:]))[0]
		p=pos[np.where(pos>99)[0]][0]
		return p
	x=[tf(o) for o in owd]
	y=[lastm(o) for o in owd]
	z=[recover(o) for o in owd]
	w=[firstLow(o) for o in owd]
	if False:
		print('time {:.2f}s'.format(end-begin))
		rate=[0,200,400,600]
		annotates=['800-{}-{}','{}-800-{}','{}-{}-800']
		for pos in range(3):
			for i in range(2):#i是不变的位置
				for j in range(4):#j是不变的值
					const=rate[j]
					fig,axs=plt.subplots(nrows=4,ncols=4,sharex=True,sharey=False,figsize=(20,10))
					for k in range(4):#k是变的值
						idx=16*pos
						if i==0:#不变的在前面
							idx+=k*4+j
							text=annotates[pos].format(rate[j],rate[k])
						else:
							idx+=j*4+k
							text=annotates[pos].format(rate[k],rate[j])
						axs[k][0].plot(owd[idx])
						axs[k][0].text(.1,.9,'owd: '+text+'(ic off)',transform=axs[k][0].transAxes)
						axs[k][0].axvline(152,color="black", linestyle="dotted",linewidth=1)

						axs[k][1].plot(owd[idx+48])
						axs[k][1].text(.1,.9,'owd: '+text+'(ic on)',transform=axs[k][1].transAxes)
						axs[k][1].axvline(152,color="black", linestyle="dotted",linewidth=1)
						
						y1=rg[idx]*1e6
						y2=rg[idx+48]*1e6
						M=max(np.max(y1),np.max(y2))
						axs[k][2].plot(y1)
						axs[k][2].text(.1,.9,'rx gap: '+text+'(ic off)',transform=axs[k][2].transAxes)
						axs[k][2].axvline(152,color="black", linestyle="dotted",linewidth=1)
						axs[k][2].set_ylim(0,M)

						axs[k][3].plot(y2)
						axs[k][3].text(.1,.9,'rx gap: '+text+'(ic on)',transform=axs[k][3].transAxes)
						axs[k][3].axvline(152,color="black", linestyle="dotted",linewidth=1)
						axs[k][3].set_ylim(0,M)
					if i==0:
						title=annotates[pos].format(rate[j],'X')
					else:
						title=annotates[pos].format('X',rate[j])
					fig.suptitle(title,y=0.92)
					fig.text(0.05,0.5,'OWD(us)/rxGap(us)',va='center',rotation='vertical')
					fig.text(0.5,0.05,'packet id',va='center',rotation='horizontal')
					plt.savefig('/images/bqr-optimization/{}.png'.format(title),bbox_inches='tight')
					plt.close(fig)
	
	code.interact(local=dict(globals(),**locals()))