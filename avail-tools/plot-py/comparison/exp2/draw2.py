# 实验2,单独绘制Spruce的估计曲线
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code
rates=[i for i in range(0,500+1,100)]
x=[600]*len(rates)
x.extend(rates)
y=[i for i in rates]
y.extend([600]*len(rates))
z=[0]*2*len(rates)
dirname='/data/comparison/exp2/{}-{}-{}/{}'
methods=['BQR','assolo','igi','pathload','spruce']
N=len(x)
M=len(methods)
Capacity=957.14
Discard=10
if __name__=='__main__':
	abw=[]
	for i in range(N):
		item=[]
		for j in range(M):
			prefix=dirname.format(x[i],y[i],z[i],methods[j])
			abwfile='{}/abw'.format(prefix)
			A=np.loadtxt(abwfile)[:100]
			A=np.sort(A)
			A=A[Discard:-Discard]
			item.append(A.ravel())
		abw.append(item)
	abw=np.array(abw)
	# 获取ground truth
	truth=Capacity-600
	# 折线图显示预测值
	fig=plt.figure(figsize=(10,10),dpi=100)
	abw=np.mean(abw,axis=2)
	plt.plot(rates,abw[:N//2,4],'.-',color='red',label='the first is tight link')
	plt.plot(rates,abw[N//2:,4],'.-',color='green',label='the second is tight link')
	plt.hlines(y=truth,xmin=rates[0],xmax=rates[-1],color='blue',label='ground truth')
	plt.yticks(np.arange(-50,360,50))
	plt.legend(loc='lower left')
	plt.grid()
	title='Spruce Abw Prediction'
	plt.title(title)
	plt.xlabel('non tight link traffic(Mbps)')
	plt.ylabel('abw prediction(Mbps)')
	plt.savefig('/images/comparison/exp2-spruce.png',bbox_inches='tight')
	plt.close(fig)

	#code.interact(local=dict(globals(),**locals()))