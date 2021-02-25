import matplotlib.pyplot as plt
import numpy as np
import code,time,copy
delta=lambda x: x[...,1:]-x[...,:-1]
np.set_printoptions(suppress=True)

if __name__=='__main__':
	fn='/data/bqr-optimization/{}.txt'
	
	begin=time.time()
	# 201-205 5关闭中断延迟
	# 206-210 5开启中断延迟
	number=[i for i in range(201,210+1)]
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
		# 如果有特别大的值 
		# min,max 差值 100us以内
		pos=np.where(a<np.max(a[-10:]))[0]
		p=pos[np.where(pos>99)[0]][0]
		return p
	x=[tf(o) for o in owd]
	y=[lastm(o) for o in owd]
	z=[recover(o) for o in owd]
	w=[firstLow(o) for o in owd]
	def ln(a):
		# 获取loadnumber
		c=a/(1472*8*0.02)
		x=20*c-50
		y=200*c-50
		z=400*c-50
		return (x,y,z)
	print('time {:.2f}s'.format(end-begin))
	if False:
		# owd(off) owd(on) rg(off) rg(on)
		labels=[
			'0 0 0',
			'100 100 100',
			'200 200 200',
			'300 300 300',
			'400 400 400'
		]
		fig,axs=plt.subplots(nrows=5,ncols=5,sharex=False,sharey=False,figsize=(20,20))
		for i in range(5):
			axs[i][0].plot(owd[i])
			axs[i][0].text(.1,.8,'owd traffic:'+labels[i]+'(ic off)',transform=axs[i][0].transAxes)
			axs[i][1].plot(owd[i+5])
			axs[i][1].text(.1,.8,'owd traffic:'+labels[i]+'(ic on)',transform=axs[i][1].transAxes)
			axs[i][2].scatter(np.arange(199),rg[i]*1e6,s=1)
			axs[i][2].text(.1,.8,'rg traffic:'+labels[i]+'(ic on)',transform=axs[i][2].transAxes)
			axs[i][3].scatter(np.arange(199),rg[i+5]*1e6,s=1)
			axs[i][3].text(.1,.8,'rg traffic:'+labels[i]+'(ic off)',transform=axs[i][3].transAxes)
			axs[i][4].plot(y[i])
			axs[i][4].text(.1,.8,'lastMax traffic:'+labels[i]+'(ic off)',transform=axs[i][4].transAxes)
		fig.suptitle('high-abw',y=0.92)
		fig.text(0.05,0.5,'OWD(us)/rxGap(us)',va='center',rotation='vertical')
		fig.text(0.5,0.05,'packet id',va='center',rotation='horizontal')
		plt.savefig('/images/bqr-optimization/high-abw.png',bbox_inches='tight')
		plt.close(fig)

	code.interact(local=dict(globals(),**locals()))