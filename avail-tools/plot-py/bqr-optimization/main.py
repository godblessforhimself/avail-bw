import matplotlib.pyplot as plt
import numpy as np
import code,time,copy
delta=lambda x: x[...,1:]-x[...,:-1]
np.set_printoptions(suppress=True)

if __name__=='__main__':
	fn='/data/bqr-optimization/{}.txt'
	
	begin=time.time()
	# more 21-28 31-38 16个
	# adr 41-52 12个
	number=[i for i in range(21,28+1)]
	number.extend([i for i in range(31,38+1)])
	number.extend([i for i in range(41,52+1)])
	data=[np.loadtxt(fn.format(i),delimiter=',') for i in number]
	end=time.time()
	tx=[d1[:,0] for d1 in data]
	rx=[d1[:,1] for d1 in data]
	tg=[delta(tx_) for tx_ in tx]
	rg=[delta(rx_) for rx_ in rx]
	owd=[d1[:,1]-d1[:,0] for d1 in data]
	print('time {:.2f}s'.format(end-begin))
	# 发送的误差
	"""
	fig,axs=plt.subplots(nrows=8,ncols=4,sharex=True)
	for i in range(8):
		for j in range(2):
			axs[i][j].plot(rg[i+j*8]*1e6)
			axs[i][2+j].plot(owd[i+j*8]*1e6)
	"""
	fig,axs=plt.subplots(nrows=3,ncols=4,sharex=True,sharey=True,figsize=(10,10))
	annotates=[
		'800 0 0','800 700 0','800 0 700','800 700 700',
		'0 800 0','700 800 0','0 800 700','700 800 700',
		'0 0 800','700 0 800','0 700 800','700 700 800'
	]
	for i in range(3):
		for j in range(4):
			axs[i][j].plot(owd[16+i*4+j]*1e6)
			axs[i][j].text(.2,.9,'traffic:'+annotates[i*4+j],transform=axs[i][j].transAxes)
			axs[i][j].axvline(152,color="black", linestyle="dotted",linewidth=1)
			axs[i][j].set_xlim(-50,250)
			axs[i][j].set_xticks(np.arange(0,200+1,50))
	plt.subplots_adjust(wspace=0,hspace=0)
	fig.suptitle('BQR ADR experiment',y=0.92)
	fig.text(0.05,0.5,'OWD(us)',va='center',rotation='vertical')
	fig.text(0.5,0.05,'packet id',va='center',rotation='horizontal')
	#plt.show()
	plt.savefig('/images/bqr-optimization/bqr-adr.png',bbox_inches='tight')

	def monotonicIncrease(rg):
		# 变换输入，使其单增
		# 检查当前元素是否小于等于下一元素，是则进一位
		# 否，则平均两个元素，并向后检查，一直平均到小于等于检查的元素。
		# 这样有个问题，当前位置可能满足单增，但是在后面的元素进行变换之后，单增不满足了。
		# 重做：检查所有相邻元素，如果不是单增的，进行一次平均，重复
		def checkAndAverage(a):
			L=len(a)
			b=[]
			# 如果奇数，最后三位一起平均
			if L%2==0:
				for i in range(0,L+1,2):
					if a[i]>a[i+1]:
						v=(a[i]+a[i+1])/2
						b.extend([v,v])
					else:
						b.extend([a[i],a[i+1]])
			else:
				# L=9 a[0]->a[8] a[0]-a[5] a[6],a[7],a[8]
				for i in range(0,L-3,2):
					if a[i]>a[i+1]:
						v=(a[i]+a[i+1])/2
						b.extend([v,v])
					else:
						b.extend([a[i],a[i+1]])
				# a[L-3],a[L-2],a[L-1]
				if a[L-3]<=a[L-2] and a[L-2]<=a[L-1]:
					b.extend([a[L-3],a[L-2],a[L-1]])
				else:
					v=(a[L-3]+a[L-2]+a[L-1])/3
					b.extend([v,v,v])
			return b
		def isMonotonic(a):
			L=len(a)
			i=0
			while i<L-1-1:
				if a[i]>a[i+1]:
					return False
				i+=1
			return True
		ret=copy.deepcopy(rg)
		while not isMonotonic(ret):
			ret=checkAndAverage(ret)
			print(ret)
		return ret
	x=rg[0]*1e6
	#y=monotonicIncrease(x)
	#code.interact(local=dict(globals(),**locals()))