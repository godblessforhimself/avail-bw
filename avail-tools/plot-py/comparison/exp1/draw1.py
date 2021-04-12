# 实验一
# 平均估计值、平均误差 去掉首尾各10个
# /data/comparison/exp1
# x-y-z
# BQR assolo igi pathload spruce
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code
import scipy.stats
def mean_confidence_interval(data, confidence=0.95):
	# shape is (group,method,repeat)
    a = 1.0 * np.array(data)
    n = a.shape[2]
    m, se = np.mean(a,axis=2), scipy.stats.sem(a,axis=2)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, h
rates=range(0,900+1,100)
x=[i for i in rates]
y=[i for i in rates]
z=[i for i in rates]
x.extend([900,400,400])
y.extend([400,900,400])
z.extend([400,400,900])
dirname='/data/comparison/exp1/{}-{}-{}/{}'
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
	# abw = (13,5,80)
	# 获取13个ground-truth
	truth=[]
	for i in range(N):
		truth.append(Capacity-max(x[i],y[i],z[i]))
	truth=np.array(truth)
	# 均值；误差；百分误差；使用柱状图显示
	err=abw-truth[:,np.newaxis,np.newaxis]
	meanError=np.mean(err,axis=2)
	absError=np.mean(np.abs(err),axis=2)
	fig=plt.figure(figsize=(20,5),dpi=100)
	location=np.arange(0,5*N,5)
	width=3/M
	color=['red','orange','green','blue','black']
	label=['BQR','ASSOLO','PTR','pathload','spruce']
	for j in range(M):
		item=absError[:,j]
		plt.bar(location+j*width,item,color=color[j],width=width,label=label[j])
	plt.ylim(0,250)
	plt.xticks(location+0.5*M*width,['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(N)],rotation=25)
	plt.legend()
	title='Absolute Error Comparison'
	plt.title(title)
	plt.xlabel('traffic settings(Mbps)')
	plt.ylabel('absolute error(Mbps)')
	plt.savefig('/images/comparison/exp1/abserr.png',bbox_inches='tight')
	plt.close(fig)
	# 误差、预测值、绝对误差
	index=['{:d}-{:d}-{:d}({:.0f})'.format(x[i],y[i],z[i],truth[i]) for i in range(N)]
	df=pd.DataFrame(meanError,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-csv/exp1-error.csv',float_format='%.2f')
	df=pd.DataFrame(np.mean(abw,axis=2),index=index,columns=label)
	df.to_csv('/data/comparison/exp1-csv/exp1-abw.csv',float_format='%.2f')
	df=pd.DataFrame(absError,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-csv/exp1-absError.csv',float_format='%.2f')
	# 绝对百分比误差的对数值
	perror=np.abs(abw-truth[:,np.newaxis,np.newaxis])/truth[:,np.newaxis,np.newaxis]
	absPerror_0=np.mean(perror,axis=2)
	me,yerr=mean_confidence_interval(perror,0.95)
	absPerror=absPerror_0[1:9+1:2,:]
	location=np.arange(0,5*len(absPerror),5)
	fig=plt.figure(figsize=(10,5),dpi=300)
	for j in range(M):
		plt.bar(location+j*width,me[1:9+1:2,j]*100,width=width,label=label[j])
	bqrMax=np.max(absPerror[:,0])*100
	plt.text(0.3,0.95,'BQR outperforms others with a maximum error of {:.2f}%'.format(bqrMax),transform=plt.gca().transAxes)
	plt.xticks(location+0.5*M*width,['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(1,9+1,2)],rotation=25)
	plt.legend()
	plt.title('absolute percentage error of BQR')
	plt.xlabel('traffic setting(Mbps)')
	plt.ylabel('absolute percentage error(%)')
	plt.savefig('/images/comparison/exp1/exp1-absPerror.png',bbox_inches='tight')
	df=pd.DataFrame(absPerror_0*100,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-csv/exp1-absPerror.csv',float_format='%.2f')
	#code.interact(local=dict(globals(),**locals()))