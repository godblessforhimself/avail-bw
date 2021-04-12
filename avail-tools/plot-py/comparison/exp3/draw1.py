# 实验3：紧链路非窄链路
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code
x=[900,900,900,900,0,400,400,0,0,0,400,400,400]
y=[0,0,0,20,0,0,20,0,20,40,0,20,40]
z=[0,400,900,900,900,900,900,0,0,0,400,400,400]
dirname='/data/comparison/exp3/{}-{}-{}/{}'
methods=['BQR','assolo','igi','pathload']
N=len(x)
M=len(methods)
Capacity1=957.14
Capacity2=95.71
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
			item.append(A.ravel())
		abw.append(item)
	abw=np.array(abw)
	# 获取ground truth
	truth=[min(Capacity1-x[i],Capacity1-z[i],Capacity2-y[i]) for i in range(N)]
	truth=np.array(truth)
	# 柱状图显示绝对误差
	fig=plt.figure(figsize=(10,10),dpi=100)
	absError=np.abs(abw-truth[:,np.newaxis])
	for i in range(N):
		for j in range(M):
			absError[i,j]=np.mean(absError[i,j])
	absError=absError.astype(dtype=np.float)
	location=np.arange(N)
	width=1/(M+1)
	color=['red','orange','green','blue']
	label=['BQR','ASSOLO','PTR','pathload']
	for j in range(M):
		item=absError[:,j]
		plt.bar(location+j*width,item,color=color[j],width=width,label=label[j])
	plt.legend()
	plt.xticks(location+0.5*M*width,['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(N)],rotation=0)
	plt.savefig('/images/comparison/exp3/absError.png',bbox_inches='tight')
	plt.close()
	# 柱状图显示预测值
	fig=plt.figure(figsize=(10,10),dpi=100)
	abwMean=abw
	for i in range(N):
		for j in range(M):
			abwMean[i,j]=np.mean(abwMean[i,j])
	abwMean=abwMean.astype(dtype=np.float)
	location=np.arange(N)
	width=1/(M+1)
	color=['red','orange','green','blue']
	label=['BQR','ASSOLO','PTR','pathload']
	for j in range(M):
		item=abwMean[:,j]
		plt.bar(location+j*width,item,color=color[j],width=width,label=label[j])
	plt.legend()
	plt.xticks(location+0.5*M*width-0.5*width,['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(N)],rotation=0)
	plt.savefig('/images/comparison/exp3/abw.png',bbox_inches='tight')
	plt.close()
	index=['{:d}-{:d}-{:d}({:.0f})'.format(x[i],y[i],z[i],truth[i]) for i in range(N)]
	df=pd.DataFrame(abwMean,index=index,columns=label)
	df.to_csv('/data/comparison/exp3-csv/exp3-abw.csv',float_format='%.2f')
	df=pd.DataFrame(absError,index=index,columns=label)
	df.to_csv('/data/comparison/exp3-csv/exp3-absError.csv',float_format='%.2f')
	error=abw-truth[:,np.newaxis]
	for i in range(N):
		for j in range(M):
			error[i,j]=np.mean(error[i,j])
	error=error.astype(dtype=np.float)
	df.to_csv('/data/comparison/exp3-csv/exp3-error.csv',float_format='%.2f')
	#code.interact(local=dict(globals(),**locals()))