# 实验一
# 平均估计值、平均误差 去掉首尾各10个
# /data/comparison/exp1
# x-y-z
# BQR assolo igi pathload spruce
import numpy as np
import pandas as pd
import matplotlib
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
def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
color=[pickColor(i, 10) for i in range(10)]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
matplotlib.rcParams['hatch.linewidth']=0.3
plt.rcParams.update({'font.size':7})
marker=['d','.','*','<','p'] #5
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1))] #4
hatch=['/','\\','x','o','-|'] #5
imgDir='/home/tony/Files/available_bandwidth/thesis-svn/IMC2021/BurstQueueRecovery-jintao/images'

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
	# 横坐标：背景流量
	# 纵坐标：AbsError
	err=abw-truth[:,np.newaxis,np.newaxis]
	meanError=np.mean(err,axis=2)
	absError=np.mean(np.abs(err),axis=2)

	fig=plt.figure(figsize=(3.4,1.1))
	location=np.arange(0,5*N,5)
	width=3/M
	label=['BQR','ASSOLO','PTR','pathload','Spruce']
	for j in range(M):
		item=absError[:,j]
		plt.bar(location+j*width,item,color=color[j],width=width,label=label[j],hatch=hatch[j])
	plt.ylim(0,250)
	plt.xticks(location+0.5*M*width,['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(N)],rotation=25)
	plt.legend()
	title='Absolute Error Comparison'
	plt.title(title)
	plt.xlabel('Traffic Settings(Mbps)')
	plt.ylabel('Absolute Error(Mbps)')
	plt.close(fig)

	# 横坐标：背景流量
	# 纵坐标：AbsPerror
	perror=np.abs(abw-truth[:,np.newaxis,np.newaxis])/truth[:,np.newaxis,np.newaxis]
	absPerror_0=np.mean(perror,axis=2)
	me,yerr=mean_confidence_interval(perror,0.95)
	absPerror=absPerror_0[1:9+1:2,:]
	location=np.arange(0,5*len(absPerror),5)
	fig=plt.figure(figsize=(3.4,1.1))
	for j in range(M):
		plt.bar(location+j*width,me[1:9+1:2,j]*100+10,bottom=-10,width=width,label=label[j],edgecolor=color[j],hatch=hatch[j]*5,fill=False,linewidth=.5)
	bqrMax=np.max(absPerror[:,0])
	#plt.text(0.3,0.95,'BQR\'s Max Error is {:.2%}'.format(bqrMax),transform=ax.transAxes)
	#plt.xticks(location+0.5*M*width,['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(1,9+1,2)],rotation=0)
	plt.xticks(location+0.5*(M-1)*width,['{}'.format(x[i]) for i in range(1,9+1,2)],rotation=0)
	ax=plt.gca()
	ax.tick_params('both',length=2,width=1,which='major',pad=1)
	plt.legend(loc='upper center',framealpha=.5,ncol=5,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=6)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	plt.xlabel('Traffic Settings(Mbps)',labelpad=0)
	plt.ylabel('Absolute Percentage Error(%)',labelpad=0)
	plt.savefig('{:s}/exp1-AbsPerror.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp1-AbsPerror.eps'.format(imgDir),bbox_inches='tight')
	plt.show()
	plt.close(fig)

	# csv
	index=['{:d}-{:d}-{:d}({:.0f})'.format(x[i],y[i],z[i],truth[i]) for i in range(N)]
	df=pd.DataFrame(meanError,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-csv/exp1-error.csv',float_format='%.2f')
	df=pd.DataFrame(np.mean(abw,axis=2),index=index,columns=label)
	df.to_csv('/data/comparison/exp1-csv/exp1-abw.csv',float_format='%.2f')
	df=pd.DataFrame(absError,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-csv/exp1-absError.csv',float_format='%.2f')
	df=pd.DataFrame(absPerror_0*100,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-csv/exp1-absPerror.csv',float_format='%.2f')
	#code.interact(local=dict(globals(),**locals()))
