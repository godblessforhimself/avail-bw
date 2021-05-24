# 实验一，Queue Length
# 片段划分
# ASSOLO：使用1ms的阈值，最后两个包无用
# spruce的测量时间其实是任意的
# pathload：大于1e5us=100ms的有99个，它们是测量间隔；大于1000us=1ms的有6699个，每次测量内平均有66次；实际为60次-120次
# igi：内间隔大于250us，测量间间隔大于1e5
# bqr：我们设定1e4us=10ms的间隔
# 片段数，每个片段的包数，每个片段的时间，每个片段的速率
# 平均一次测量的片段数量
# 实际最大包数量：根据实际可用带宽，计算测量过程中最大包数量/平均包数量
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
def sectionPrint(a,n):
	#每次输出a中的n项，回车后继续
	i=0
	while i<len(a):
		print(a[i:i+n])
		i+=n
		try:
			s=input()
		except KeyboardInterrupt:
			return
def universalSec(g,th1,th2,s):
	idx=np.where(g>th1)[0]
	ret=[]
	for i,v in enumerate(idx):
		if i==0:
			item=g[:v]
		else:
			item=g[idx[i-1]+1:v]
		if len(item)>=th2:
			ret.append(item)
		elif len(item)!=0:
			print('{} err1 {}'.format(s,len(item)))
			code.interact(local=dict(globals(),**locals()))
	item=g[idx[-1]+1:]
	if len(item)>=th2:
		ret.append(item)
	elif len(item)!=0:
		print('{} err2 {}'.format(s,len(item)))
		code.interact(local=dict(globals(),**locals()))
	return ret
def bqrSec(g):
	return universalSec(g,1e4,199,'bqr')
def assoloSec(g):
	return universalSec(g,1e3,50,'assolo')
def igiSec(g):
	return universalSec(g,250,50,'igi')
def pathloadSec(g):
	return universalSec(g,1e3,6,'pathload')
def spruceSec(g):
	return universalSec(g,1e6,0,'spruce')
def sec2Number(sec):
	return len(sec)
def sec2PacketNumber(sec):
	return [len(i)+1 for i in sec]
def sec2Time(sec):
	return [np.sum(i) for i in sec]
def sec2Rate(sec):
	return [1472*8*(len(i))/np.sum(i) for i in sec]
def sec2QueueLength(sec,abw):
	secNum=len(sec)
	ret=[]
	retmax=[]
	retmean=[]
	for i in range(secNum):
		temp=[]
		q=1
		for j in range(len(sec[i])):
			dq=abw*sec[i][j]/8/1472
			q=1+max(0,q-dq)
			temp.append(q)
		ret.append(temp)
		retmax.append(np.max(temp))
		retmean.append(np.mean(temp))
	return ret,retmax,retmean

def queueLength2queueMean(sections,queueLength):
	ret=[]
	for i in range(N):
		temp1=[]
		for j in range(M):
			temp2=[]
			sectionNumber=len(sections[i][j])
			for k in range(sectionNumber):
				totalTime=np.sum(sections[i][j][k])
				totalArea=0
				for idx,ql in enumerate(queueLength[i][j][k]):
					if idx>0:
						totalArea+=(queueLength[i][j][k][idx-1]+ql)*sections[i][j][k][idx]/2
					else:
						totalArea+=(1+ql)*sections[i][j][k][idx]/2
				meanValue=totalArea/totalTime
				temp2.append(meanValue)
			temp1.append(temp2)
		ret.append(temp1)
	return ret
def getSections(gap,truth):
	sections=[]
	sectionNumber=[]
	packetNumber=[]
	sectionTime=[]
	sectionRate=[]
	queueLength=[]
	queueMax=[]
	queueMean=[]
	secFun=[bqrSec,assoloSec,igiSec,pathloadSec,spruceSec]
	for i in range(N):
		section_=[]
		sectionNumber_=[]
		packetNumber_=[]
		sectionTime_=[]
		sectionRate_=[]
		queueLength_=[]
		queueMax_=[]
		queueMean_=[]
		for j in range(M):
			g=gap[i,j]
			sec=secFun[j](g)
			section_.append(sec)
			sectionNumber_.append(sec2Number(sec))
			packetNumber_.append(sec2PacketNumber(sec))
			sectionTime_.append(sec2Time(sec))
			sectionRate_.append(sec2Rate(sec))
			ql,qmax,qmean=sec2QueueLength(sec,truth[i])
			queueLength_.append(ql)
			queueMax_.append(qmax)
			queueMean_.append(qmean)
		sections.append(section_)
		sectionNumber.append(sectionNumber_)
		packetNumber.append(packetNumber_)
		sectionTime.append(sectionTime_)
		sectionRate.append(sectionRate_)
		queueLength.append(queueLength_)
		queueMax.append(queueMax_)
		queueMean.append(queueMean_)
	return sections,sectionNumber,packetNumber,sectionTime,sectionRate,queueLength,queueMax,queueMean

def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
np.set_printoptions(suppress=True,precision=2)
color=[pickColor(i, 10) for i in range(10)]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
plt.rcParams.update({'font.size':6})
matplotlib.rcParams['hatch.linewidth']=0.3
marker=['d','.','*','<','p'] #5
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1)),(0,(3,1,1,1,1,1))] #5
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
		# (13,5,...) object array
		np.save(cacheFilename,gap)
	truth=[]
	for i in range(N):
		truth.append(Capacity-max(x[i],y[i],z[i]))
	if os.path.exists(cache2):
		data=np.load(cache2,allow_pickle=True)
		sections=data['sections']
		sectionNumber=data['sectionNumber']
		packetNumber=data['packetNumber']
		sectionTime=data['sectionTime']
		sectionRate=data['sectionRate']
		queueLength=data['queueLength']
		queueMax=data['queueMax']
		queueMean=data['queueMean']
		queueMean2=data['queueMean2']
	else:
		sections,sectionNumber,packetNumber,sectionTime,sectionRate,queueLength,queueMax,queueMean=getSections(gap,truth)
		queueMean2=queueLength2queueMean(sections,queueLength)	
		np.savez(cache2,sections=sections,sectionNumber=sectionNumber,packetNumber=packetNumber,sectionTime=sectionTime,sectionRate=sectionRate,queueLength=queueLength,queueMax=queueMax,queueMean=queueMean,queueMean2=queueMean2)
	end=time.time()
	print('{:.2f}'.format(end-begin))
	begin=time.time()
	# 平均一次测量段数 sectionNumber (13,5)
	measurementNumber=[]
	for i in range(N):
		temp=[]
		for j in range(M):
			prefix=dirname.format(x[i],y[i],z[i],methods[j])			
			abwfile='{}/abw'.format(prefix)
			measureNumber=len(np.loadtxt(abwfile))
			temp.append(measureNumber)
		measurementNumber.append(temp)
	measurementNumber=np.array(measurementNumber)
	sectionNumber=np.array(sectionNumber)
	averageSecNum=sectionNumber/measurementNumber
	averageSecNum[:,1]=1
	label=['BQR','ASSOLO','PTR','pathload','Spruce']
	index=['{:d}-{:d}-{:d}({:.0f})'.format(x[i],y[i],z[i],truth[i]) for i in range(N)]
	df=pd.DataFrame(averageSecNum,index=index,columns=label)
	df.index.name='Traffic Settings(Mbps)'
	df.to_csv('/data/comparison/exp1-time/exp1-sectionNumber.csv',float_format='%.2f')
	# num of iterations
	fig,ax=plt.subplots(figsize=(1.3,1.1))
	for idx in [2,3]:
		plt.plot(truth[:10],averageSecNum[:10,idx],label=label[idx],linestyle=linestyle[idx],color=color[idx])
	plt.legend(loc='best',framealpha=.5,ncol=5,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.xlabel('ABW(Mbps)',labelpad=0)
	plt.ylabel('Iteration Number',labelpad=0)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)

	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)
	plt.savefig('{:s}/exp1-iteration-number.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp1-iteration-number.eps'.format(imgDir),bbox_inches='tight')
	plt.show()
	plt.close(fig)
	# 平均每段测量时间 sectionTime (13,4,sec)
	avgSecTime=[]
	for i in range(N):
		temp=[]
		for j in range(M):
			temp.append(np.mean(sectionTime[i][j]))
		avgSecTime.append(temp)
	avgSecTime=np.array(avgSecTime)
	df=pd.DataFrame(avgSecTime,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-time/exp1-sectionMeanTime.csv',float_format='%.2f')
	# 有效测量时间
	avgTime=avgSecTime*averageSecNum
	df=pd.DataFrame(avgTime,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-time/exp1-meanTime.csv',float_format='%.2f')
	# 平均速率
	meanSecRate=[]
	for i in range(N):
		temp=[]
		for j in range(M):
			temp.append(np.mean(sectionRate[i][j]))
		meanSecRate.append(temp)
	df=pd.DataFrame(meanSecRate,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-time/exp1-sectionMeanRate.csv',float_format='%.2f')
	# 最大段速率
	maxSecRate=[]
	for i in range(N):
		temp=[]
		for j in range(M):
			temp.append(np.max(sectionRate[i][j]))
		maxSecRate.append(temp)
	df=pd.DataFrame(maxSecRate,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-time/exp1-sectionMaxRate.csv',float_format='%.2f')
	# 平均每段包数
	meanSecPacketNumber=[]
	for i in range(N):
		temp=[]
		for j in range(M):
			temp.append(np.mean(packetNumber[i][j]))
		meanSecPacketNumber.append(temp)
	df=pd.DataFrame(meanSecPacketNumber,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-time/exp1-sectionMeanPacket.csv',float_format='%.2f')
	# 平均总包数
	meanSecPacketNumber=np.array(meanSecPacketNumber)
	meanPacketNumber=averageSecNum*meanSecPacketNumber
	df=pd.DataFrame(meanPacketNumber,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-time/exp1-meanPacket.csv',float_format='%.2f')
	# 平均队列长度
	meanQueueLength=[]
	for i in range(N):
		temp=[]
		for j in range(M):
			temp.append(np.mean(queueMean2[i][j]))
		meanQueueLength.append(temp)
	df=pd.DataFrame(meanQueueLength,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-time/exp1-sectionMeanQueueLength.csv',float_format='%.2f')
	# 最大队列长度
	maxQueueLength=[]
	for i in range(N):
		temp=[]
		for j in range(M):
			temp.append(np.max(queueMax[i][j]))
		maxQueueLength.append(temp)
	df=pd.DataFrame(maxQueueLength,index=index,columns=label)
	df.to_csv('/data/comparison/exp1-time/exp1-maxQueueLength.csv',float_format='%.2f')
	end=time.time()
	print('{:.2f}'.format(end-begin))
	# 以可用带宽为横坐标，平均/最大长度为纵坐标的折线图；可用带宽为大、中、小时的包数、字节数表格
	fig=plt.figure(figsize=(1.3,1.1))
	N=len(rates)
	meanQueueLength=np.array(meanQueueLength)
	for j in range(M):
		plt.plot(truth[:N],meanQueueLength[:N,j],label=label[j],color=color[j],linestyle=linestyle[j])
	plt.legend(loc='upper right',framealpha=.5,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	plt.xticks(np.arange(0,1000,200))
	plt.ylim(0,50)
	plt.yticks(np.arange(0,50+1,10))
	plt.xlabel('ABW(Mbps)',labelpad=0)
	plt.ylabel('Mean Queue Length(pkts)',labelpad=0)
	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)
	plt.savefig('{:s}/exp1-MeanQueueLength.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp1-MeanQueueLength.eps'.format(imgDir),bbox_inches='tight')
	plt.close(fig)
	# Max queue length
	fig=plt.figure(figsize=(1.3,1.1))
	N=len(rates)
	maxQueueLength=np.array(maxQueueLength)
	for j in range(M):
		y=maxQueueLength[:N,j]
		plt.plot(truth[:N],y,label=label[j],color=color[j],linestyle=linestyle[j])
	plt.legend(loc='upper right',framealpha=.5,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	plt.xticks(np.arange(0,1000,200))
	plt.ylim(0,120)
	plt.yticks(np.arange(0,120+1,20))
	plt.xlabel('ABW(Mbps)',labelpad=0)
	plt.ylabel('Max Queue Length(pkts)',labelpad=0)
	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)
	plt.savefig('{:s}/exp1-MaxQueueLength.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp1-MaxQueueLength.eps'.format(imgDir),bbox_inches='tight')
	plt.close(fig)
	# 可用带宽为957/557/57时的MaxQueueLength和MaxQueueMB
	ABWIndex=[1,4,9]
	index=[]
	arr=[]
	for j in range(M):
		for _,i in enumerate(ABWIndex):
			arr.append([])
			name='{:s}(ABW:{:.0f}Mbps)'.format(label[j],truth[i])
			index.append(name)
			value=maxQueueLength[i,j]
			arr[-1].append(value)
			arr[-1].append(value*1500/1024)
	arr=np.array(arr)
	df=pd.DataFrame(arr,index=index,columns=['Number of MTU Packets', 'KByte'])
	df.index.name='Method(ABW)'
	df.to_csv('/data/comparison/exp1-csv/exp1-MaxQueueLength.csv',float_format='%.2f')
	#code.interact(local=dict(globals(),**locals()))