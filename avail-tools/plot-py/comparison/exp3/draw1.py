# 实验3：紧链路非窄链路
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code,matplotlib
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
def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
np.set_printoptions(suppress=True,precision=2)
color=[pickColor(i, 10) for i in range(10)]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
plt.rcParams.update({'font.size':7})
matplotlib.rcParams['hatch.linewidth']=0.3
marker=['d','.','*','<','p'] #5
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1)),(0,(3,1,1,1,1,1))] #5
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
			item.append(A.ravel())
		abw.append(item)
	abw=np.array(abw)
	# 获取ground truth
	truth=[min(Capacity1-x[i],Capacity1-z[i],Capacity2-y[i]) for i in range(N)]
	truth=np.array(truth)
	settings=['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(N)]
	# 柱状图显示绝对误差
	fig=plt.figure(figsize=(10,10),dpi=100)
	absError=np.abs(abw-truth[:,np.newaxis])
	for i in range(N):
		for j in range(M):
			absError[i,j]=np.mean(absError[i,j])
	absError=absError.astype(dtype=np.float)
	location=np.arange(N)
	width=1/(M+1)
	label=['BQR','ASSOLO','PTR','pathload']
	for j in range(M):
		item=absError[:,j]
		plt.bar(location+j*width,item,color=color[j],width=width,label=label[j])
	plt.legend()
	plt.xticks(location+0.5*M*width,settings,rotation=0)
	plt.savefig('/images/comparison/exp3/exp3-AbsError.pdf',bbox_inches='tight')
	plt.close(fig)
	# 柱状图显示预测值
	fig=plt.figure(figsize=(10,10),dpi=100)
	abwMean=abw
	for i in range(N):
		for j in range(M):
			abwMean[i,j]=np.mean(abwMean[i,j])
	abwMean=abwMean.astype(dtype=np.float)
	location=np.arange(N)
	width=1/(M+1)
	label=['BQR','ASSOLO','PTR','pathload']
	for j in range(M):
		item=abwMean[:,j]
		plt.bar(location+j*width,item,color=color[j],width=width,label=label[j])
	plt.legend()
	plt.xticks(location+0.5*M*width-0.5*width,['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(N)],rotation=0)
	plt.savefig('/images/comparison/exp3/exp3-Abw.pdf',bbox_inches='tight')
	plt.close(fig)
	# AbsPerror
	AbsPerror=absError/truth[:,np.newaxis]
	# [0,0,0]-[0,40,0] + [400,0,400]-[400,40,400]
	# S1 - S13
	fig,ax=plt.subplots(figsize=(3.4,1.1))
	for j in range(M):
		plt.plot(AbsPerror[:,j]*100,color=color[j],label=label[j],linestyle=linestyle[j],marker=marker[j],markersize=3)
	
	plt.legend(loc='upper left',framealpha=.5,ncol=5,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)
	plt.xlabel('Settings(Mbps)',labelpad=0)
	plt.ylabel('AbsPerror(%)',labelpad=0)
	plt.ylim(0,150)
	plt.yticks(np.arange(0,150+1,30))
	plt.xlim(-.5,12.5)
	plt.xticks(np.arange(0,12+.5,1),labels=['Set{:d}'.format(i+1) for i in range(13)],fontsize=5)
	#plt.show()
	plt.savefig('{:s}/exp3-AbsPerror.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp3-AbsPerror.eps'.format(imgDir),bbox_inches='tight')
	plt.close(fig)

	index=['{:d}-{:d}-{:d}({:.0f})'.format(x[i],y[i],z[i],truth[i]) for i in range(N)]
	df=pd.DataFrame(AbsPerror*100,index=index,columns=label)
	df.index.name='Settings'
	df.to_csv('/data/comparison/exp3-csv/exp3-AbsPerror.csv',float_format='%.2f%%')
	df=pd.DataFrame(abwMean,index=index,columns=label)
	df.to_csv('/data/comparison/exp3-csv/exp3-Abw.csv',float_format='%.2f')
	df=pd.DataFrame(absError,index=index,columns=label)
	df.to_csv('/data/comparison/exp3-csv/exp3-AbsError.csv',float_format='%.2f')
	error=abw-truth[:,np.newaxis]
	for i in range(N):
		for j in range(M):
			error[i,j]=np.mean(error[i,j])
	error=error.astype(dtype=np.float)
	df.to_csv('/data/comparison/exp3-csv/exp3-Error.csv',float_format='%.2f')
	#code.interact(local=dict(globals(),**locals()))