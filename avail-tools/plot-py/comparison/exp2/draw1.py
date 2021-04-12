# 实验二
# 去掉首尾各10个
# 绝对误差柱状图
# 平均误差表格
# /data/comparison/exp2
# x-y-z
# BQR assolo igi pathload spruce
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
	truth=[]
	for i in range(N):
		truth.append(Capacity-max(x[i],y[i],z[i]))
	truth=np.array(truth)
	# 柱状图显示绝对误差
	abserr=np.abs(abw-truth[:,np.newaxis,np.newaxis])
	abserr=np.mean(abserr,axis=2)
	fig=plt.figure(figsize=(20,5),dpi=100)
	location=np.arange(0,5*N,5)
	width=3/M
	color=['red','orange','green','blue','black']
	label=['BQR','ASSOLO','PTR','pathload','spruce']
	for j in range(M):
		item=abserr[:,j]
		plt.bar(location+j*width,item,color=color[j],width=width,label=label[j])
	#plt.ylim(0,250)
	plt.xticks(location+0.5*M*width,['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(N)],rotation=25)
	plt.legend()
	title='Absolute Error Comparison'
	plt.title(title)
	plt.xlabel('traffic settings(Mbps)')
	plt.ylabel('absolute error(Mbps)')
	plt.savefig('/images/comparison/exp2-absError.png',bbox_inches='tight')
	plt.close(fig)
	# 保存绝对误差
	index=['{:d}-{:d}-{:d}({:.0f})'.format(x[i],y[i],z[i],truth[i]) for i in range(N)]
	df=pd.DataFrame(abserr,index=index,columns=label)
	df.to_csv('/data/comparison/exp2-csv/exp2-absError.csv',float_format='%.2f')
	# 保存平均预测值
	df=pd.DataFrame(np.mean(abw,axis=2),index=index,columns=label)
	df.to_csv('/data/comparison/exp2-csv/exp2-abw.csv',float_format='%.2f')
	# 保存平均误差
	error=np.mean(abw-truth[:,np.newaxis,np.newaxis],axis=2)
	df=pd.DataFrame(error,index=index,columns=label)
	df.to_csv('/data/comparison/exp2-csv/exp2-error.csv',float_format='%.2f')
	# 保存各方法的标准差
	std=np.std(np.mean(abw,axis=2),axis=0)
	df=pd.DataFrame(std[np.newaxis,:],columns=label)
	df.to_csv('/data/comparison/exp2-csv/exp2-std.csv',index=False,float_format='%.2f')
	# 标准差
	std=np.std(abw,axis=2)
	df=pd.DataFrame(std,index=index,columns=label)
	df.to_csv('/data/comparison/exp2-csv/exp2-specific-std.csv',float_format='%.2f')
	code.interact(local=dict(globals(),**locals()))