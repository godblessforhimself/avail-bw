# 实验一，实际的时间
# ASSOLO：使用1ms的阈值，最后两个包无用
# pathload：大于1e5us=100ms的有99个，它们是测量间隔；
# igi：测量间间隔大于1e5
# bqr：1e4us=10ms的间隔
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code,time,os,matplotlib
delta=lambda a: a[...,1:]-a[...,:-1]
rates=range(0,900+1,100)
x=[i for i in rates]
y=[i for i in rates]
z=[i for i in rates]
x.extend([900,400,400])
y.extend([400,900,400])
z.extend([400,400,900])
dirname='/data/comparison/exp1/{}-{}-{}/{}'
methods=['BQR','assolo','igi','pathload','spruce']
suffix=['dagsnap.txt','dagsnap.txt','dagsnap','dagsnap','dagsnap']
N=len(x)
M=len(methods)
Capacity=957.14
Discard=10
cacheFilename='/data/comparison/exp1-cache/gap.npy'
cache2='/data/comparison/exp1-cache/draw3.npz'
th1=[1e4,1e3,1e5,1e5]
th2=[10,10,10,6]
def getTimeFun(g,th1,th2):
	idx=np.where(g>th1)[0]
	lidx=len(idx)
	ret=[]
	for i in range(lidx):
		if i==0:
			item=g[:idx[0]]
		else:
			item=g[idx[i-1]+1:idx[i]]
		if len(item)>th2:
			ret.append(np.sum(item))
	item=g[idx[-1]+1:]
	if len(item)>th2:
		ret.append(np.sum(item))
	return ret

def getTime(gap):
	ret=[]
	retMean=[]
	for i in range(N):
		temp=[]
		tempMean=[]
		for j in range(M):
			if methods[j]=='spruce':
				continue
			t_=getTimeFun(gap[i][j],th1[j],th2[j])
			temp.append(t_)
			tempMean.append(np.mean(t_))
		ret.append(temp)
		retMean.append(tempMean)
	return ret,retMean

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
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1))] #4
hatch=['/','\\','x','o','-|'] #5
imgDir='/home/tony/Files/available_bandwidth/thesis-svn/IMC2021/BurstQueueRecovery-jintao/images'

if __name__=='__main__':
	begin=time.time()
	if os.path.exists(cacheFilename):
		gap=np.load(cacheFilename,allow_pickle=True)
	else:
		gap=[]
		for i in range(N):
			v1=[]
			for j in range(M):
				f1=dirname.format(x[i],y[i],z[i],methods[j])+'/'+suffix[j]
				tx=np.loadtxt(f1)[:,0]
				v1.append(delta(tx)*1e6)
			gap.append(v1)
		gap=np.array(gap)
		np.save(cacheFilename,gap)
	truth=[]
	for i in range(N):
		truth.append(Capacity-max(x[i],y[i],z[i]))
	mT,mmT=getTime(gap)
	end=time.time()
	print('use {:.2f} s'.format(end-begin))
	label=['BQR','ASSOLO','PTR','pathload']
	index=['{:d}-{:d}-{:d}({:.0f})'.format(x[i],y[i],z[i],truth[i]) for i in range(N)]
	df=pd.DataFrame(mmT,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-time/exp1-time.csv',float_format='%.2f')
	mmT=np.array(mmT)
	fig,(ax1,ax2)=plt.subplots(2,1,sharex=True,figsize=(3.4,1.1))
	l2=mmT.shape[1]
	M=M-1
	N=len(mmT[1:10:2,0])
	xtick=np.arange(0,N,1)
	width=1/(M+1)
	for i in range(M):
		xpos=xtick+i*width
		time=mmT[1:10:2,i]/1000
		ax1.bar(xpos,time,width=width,label=label[i],edgecolor=color[i],hatch=hatch[i]*5,fill=False,linewidth=.5)
		ax2.bar(xpos,time+10,bottom=-10,width=width,label=label[i],edgecolor=color[i],hatch=hatch[i]*5,fill=False,linewidth=.5)
	xindex=['{}'.format(x[i]) for i in range(1,10,2)]
	ax1.spines['bottom'].set_visible(False)
	ax2.spines['top'].set_visible(False)
	ax1.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	ax2.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	ax2.set_xlabel('Traffic Settings(Mbps)',labelpad=0)
	
	fig.text(0.025,0.5,'Time(ms)',va='center',rotation='vertical')

	ax1.set_ylim(1000,7000)
	ax1.set_yticks(np.arange(2000,7000,2000))
	ax1.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False)
	ax2.set_ylim(-10,200)
	ax2.set_yticks(np.arange(0,200+1,40))
	d=1.0 #proportion of vertical to horizontal extent of the slanted line
	kwargs=dict(marker=[(-1,-d),(1,d)],markersize=10,linestyle="none",color='k',mec='k',mew=1,clip_on=False)
	ax1.plot([0,1],[0,0],transform=ax1.transAxes,**kwargs)
	ax2.plot([0,1],[1,1],transform=ax2.transAxes,**kwargs)

	plt.subplots_adjust(wspace=0,hspace=.25)
	ax1.legend(loc='upper center',framealpha=.5,ncol=4,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=6)
	ax2.set_xticks(xtick+(M-1)*width/2)
	ax2.set_xticklabels(xindex)
	ax1.tick_params('both',length=1,width=1,which='both',pad=1)
	ax2.tick_params('both',length=1,width=1,which='both',pad=1)

	plt.savefig('{:s}/exp1-RealTime.eps'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp1-RealTime.pdf'.format(imgDir),bbox_inches='tight')
	plt.show()