# 实验二
# 去掉首尾各10个
# 绝对误差柱状图
# 平均误差表格
# /data/comparison/exp2
# x-y-z
# BQR assolo igi pathload spruce
import numpy as np
import pandas as pd
import matplotlib
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
	tt=truth[:,np.newaxis,np.newaxis]
	abserr=np.abs(abw-tt)
	abserr=np.mean(abserr,axis=2)
	AbsPerror=np.mean(np.abs((abw-tt)/tt),axis=2)
	fig=plt.figure(figsize=(3.4,1.1))
	location=np.arange(0,5*N,5)
	width=3/M
	label=['BQR','ASSOLO','PTR','pathload','Spruce']
	for j in range(M):
		item=abserr[:,j]
		plt.bar(location+j*width,item,color=color[j],width=width,label=label[j])
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	plt.xticks(location+0.5*M*width,['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(N)],rotation=25)
	plt.legend(loc='upper center',framealpha=.5,ncol=5,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.xlabel('Traffic Settings(Mbps)')
	plt.ylabel('Absolute Error(Mbps)')
	#plt.savefig('{:s}/exp2-AbsError.pdf'.format(imgDir),bbox_inches='tight')
	#plt.savefig('{:s}/exp2-AbsError.eps'.format(imgDir),bbox_inches='tight')
	plt.close(fig)
	# AbsPerror
	# BQR,pathload | ASSOLO PTR Spruce
	fig=plt.figure(figsize=(1.3,1.1))
	for j in [0,3]:
		plt.plot(rates,AbsPerror[:N//2,j]*100,label='{:s}-tight1'.format(label[j]),color=color[j],linestyle=linestyle[j])
		plt.plot(rates,AbsPerror[N//2:,j]*100,label='{:s}-tight2'.format(label[j]),color=color[j+M],linestyle=linestyle[(j+M)%len(linestyle)])
	plt.legend(loc='upper left',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.xlabel('Traffic(Mbps)',labelpad=0)
	plt.ylabel('Absolute Percentage Error(%)',labelpad=0)
	plt.xlim(0,525)
	plt.xticks(np.arange(0,500+1,100))
	plt.ylim(1.5,4)
	plt.yticks(np.arange(1.5,4+.5,0.5))
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)
	plt.savefig('{:s}/exp2-AbsPerror1.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp2-AbsPerror1.eps'.format(imgDir),bbox_inches='tight')
	plt.close(fig)
	# ASSOLO PTR Spruce
	fig=plt.figure(figsize=(1.3,1.1))
	for j in [1,2,4]:
		plt.plot(rates,AbsPerror[:N//2,j]*100,label='{:s}-tight1'.format(label[j]),color=color[j],linestyle=linestyle[j])
		plt.plot(rates,AbsPerror[N//2:,j]*100,label='{:s}-tight2'.format(label[j]),color=color[j+M],linestyle=linestyle[(j+M)%len(linestyle)])
	plt.legend(loc='upper left',framealpha=.5,ncol=1,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.xlabel('Traffic(Mbps)',labelpad=0)
	plt.ylabel('Absolute Percentage Error(%)',labelpad=0)
	plt.xlim(0,525)
	plt.xticks(np.arange(0,500+1,100))
	plt.ylim(0,120)
	plt.yticks(np.arange(0,120+1,20))
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)
	plt.savefig('{:s}/exp2-AbsPerror2.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp2-AbsPerror2.eps'.format(imgDir),bbox_inches='tight')
	plt.close(fig)
	# 保存绝对误差
	index=['{:d}-{:d}-{:d}'.format(x[i],y[i],z[i]) for i in range(N)]
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
	index.append('Mean')
	std2=np.std(abw,axis=2)
	figure,ax=plt.subplots(figsize=(3.4,1.1))
	for i in range(M):
		x=rates
		y1,y2=std2[:N//2,i],std2[N//2:,i]
		plt.plot(x,y1,label=label[i]+'-tight1',linestyle=linestyle[i],color=color[i])
		plt.plot(x,y2,label=label[i]+'-tight2',linestyle=linestyle[i],color=color[i+M])
	plt.legend(loc='best',framealpha=.5,ncol=2,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)

	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)

	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)

	plt.xlabel('ABW(Mbps)',labelpad=0)
	plt.ylabel('Standard Deviation(Mbps)',labelpad=0)
	
	plt.savefig('{:s}/exp2-std.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp2-std.eps'.format(imgDir),bbox_inches='tight')
	plt.show()
	plt.close(fig)

	std2=np.concatenate((std2,np.mean(std2,axis=0)[np.newaxis,:]),axis=0)
	df=pd.DataFrame(std2,index=index,columns=label)
	df.index.name='Traffic Settings'
	df.to_csv('/data/comparison/exp2-csv/exp2-specific-std.csv',float_format='%.2f')
	#code.interact(local=dict(globals(),**locals()))