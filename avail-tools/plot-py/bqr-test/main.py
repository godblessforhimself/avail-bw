import matplotlib.pyplot as plt
import numpy as np
import code,time,copy,csv,io
delta=lambda x: x[...,1:]-x[...,:-1]
np.set_printoptions(suppress=True)

if __name__=='__main__':
	fn='/data/bqr-test/{}-time'
	begin=time.time()
	# 0-time 9-time
	# 10-time 19-time
	number=[i for i in range(0,19+1)]
	data=[]
	for i in number:
		f=open(fn.format(i))
		string=f.read()
		f.close()
		segments=string.split('\n\n')
		for seg in segments:
			if len(seg)==0:
				continue
			f=io.StringIO(seg)
			x=np.loadtxt(f,delimiter=',')
			f.close()
			data.append(x)
	end=time.time()
	tx=[d1[:,0] for d1 in data]
	rx=[d1[:,1] for d1 in data]
	tg=[delta(tx_)*1e6 for tx_ in tx]
	rg=[delta(rx_)*1e6 for rx_ in rx]
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
		plt.plot(owd[0])
		plt.show()

	code.interact(local=dict(globals(),**locals()))