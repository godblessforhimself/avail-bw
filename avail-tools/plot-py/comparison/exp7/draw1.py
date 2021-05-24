# 实验7 tcpreplay BQR 效果
import numpy as np
import code,io,time,os,matplotlib
import matplotlib.pyplot as plt
import pandas as pd
delta=lambda x: x[...,1:,0]-x[...,:-1,0]
def loadF1(filename):
	return np.loadtxt(filename,delimiter=',')
def data2OWD(data,skip=False):
	ret=(data[:,:,1]-data[:,:,0])*1e6
	if not skip:
		ret-=np.min(ret,axis=1)[:,np.newaxis]
	return ret
def tick():
	global t1,t2
	t1=time.time()
def tock(s=''):
	global t1,t2
	t2=time.time()
	if s!='':
		s=s+' '
	print('{:s}use {:.2f} second'.format(s, t2-t1))
def loadWrapper(filename,loadFun):
	picklename=filename+'.npy'
	if os.path.exists(picklename):
		print('load: from {:s}'.format(picklename))
		return np.load(picklename,allow_pickle=True)
	else:
		t1=time.time()
		v=loadFun(filename)
		t2=time.time()
		if t2-t1>1.0:
			print('load: save {:s}'.format(picklename))
			np.save(picklename,v)
		return v
def plot(owd,i):
	v=owd[i]
	idx=0
	try:
		for idx,j in enumerate(v):
			plt.plot(j,label='{:d}'.format(idx))
			plt.legend()
			plt.pause(.5)
			plt.clf()
	except KeyboardInterrupt:
		print(idx)
	finally:
		plt.close()
def savePlot(owd,i,path):
	v=owd[i]
	for idx,j in enumerate(v):
		fig=plt.figure(figsize=(10,10))
		plt.plot(j,color=color[0],label='rate {:d}, iter {:d}'.format(i,idx))
		plt.xlabel('Packet Index')
		plt.ylabel('One Way Delay(us)')
		#plt.text(0.5,0.05,'rate {:d}, iteration {:d}'.format(i,idx))
		plt.savefig(path.format(i,idx)+'.pdf',bbox_inches='tight')
		plt.savefig(path.format(i,idx)+'.eps',bbox_inches='tight')
		plt.close(fig)

def pickColor(i,n):
	cmap=plt.cm.get_cmap('Set1',n)
	color=cmap(i/(n-1))
	return color
np.set_printoptions(suppress=True,precision=2)
color=[pickColor(i, 10) for i in range(10)]
matplotlib.rcParams['font.family']='sans-serif'
matplotlib.rcParams['font.sans-serif']='Arial'
plt.rcParams.update({'font.size': 6})
matplotlib.rcParams['hatch.linewidth']=0.3
marker=['d','.','*','<','p'] #5
linestyle=[(0,(1,1)),'solid',(0,(5,1)),(0,(3,1,1,1)),(0,(3,1,1,1,1,1))] #5
hatch=['/','\\','x','o','-|'] #5
imgDir='/home/tony/Files/available_bandwidth/thesis-svn/IMC2021/BurstQueueRecovery-jintao/images'

capacity=957.14
if __name__=='__main__':
	fmt='/data/comparison/exp7/{:d}/{:s}'
	rateList=[10,100,300,500,700,900]
	tick()
	d={i:loadWrapper(fmt.format(i,'timestamp.txt'),loadF1).reshape((-1,200,2)) for i in rateList}
	# 120,200,2
	arrivalBQR={i:loadWrapper(fmt.format(i,'c-BQR.len'),np.loadtxt).reshape((120,200,2)) for i in rateList}
	# l1,2
	arrivalTraffic={i:loadWrapper(fmt.format(i,'c-traffic.len'),np.loadtxt) for i in rateList}
	# 1 920 914 934
	result=[np.loadtxt(fmt.format(i,'result.txt')) for i in rateList]
	validNumber=np.array([len(i) for i in result])
	validIdx={v:result[i][:,0] for i,v in enumerate(rateList)}
	prediction={v:result[i][:,1] for i,v in enumerate(rateList)}
	tock()
	owd={k:data2OWD(v) for k,v in d.items()}
	figPath='/images/comparison/exp7/{:d}/{:d}'
	if False:
		#for i in rateList:
		#	savePlot(owd,i,figPath)
		savePlot(owd,900,figPath)

	fig=plt.figure(figsize=(1.3,1.1))
	for i,index in enumerate([77,25]):
		y=owd[900][index]
		plt.plot(y/1000,label='Case {:d}'.format(i+1),color=color[i],linestyle=linestyle[i])
	plt.xlabel('Packet Index',labelpad=0)
	plt.ylabel('One Way Delay(ms)',labelpad=0)
	plt.xlim(0,200)
	plt.xticks(np.arange(0,200+1,50))
	plt.ylim(-0.5,2)
	plt.yticks(np.arange(0,2+0.1,0.5))
	plt.legend(loc='upper center',framealpha=.5,ncol=2,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)

	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)

	plt.savefig('{:s}/exp7-BQR-examples-a.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp7-BQR-examples-a.eps'.format(imgDir),bbox_inches='tight')
	plt.close(fig)

	fig=plt.figure(figsize=(1.3,1.1))
	for i,index in enumerate([6,32]):
		y=owd[900][index]
		plt.plot(y/1000,label='Case {:d}'.format(i+3),color=color[i+2],linestyle=linestyle[i+2])
	plt.xlabel('Packet Index',labelpad=0)
	plt.ylabel('One Way Delay(ms)',labelpad=0)
	plt.xlim(0,200)
	plt.xticks(np.arange(0,200+1,50))
	plt.ylim(-0.5,5)
	plt.yticks(np.arange(0,5+0.1,1.0))

	plt.legend(loc='lower center',framealpha=.5,ncol=2,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	ax=plt.gca()
	ax.tick_params('both',length=1,width=1,which='both',pad=1)

	plt.savefig('{:s}/exp7-BQR-examples-b.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp7-BQR-examples-b.eps'.format(imgDir),bbox_inches='tight')
	plt.close(fig)
	# 有效数量表
	label=[str(i) for i in rateList]
	df=pd.DataFrame(validNumber[np.newaxis,:],columns=label)
	if False:
		df.to_csv('/data/comparison/exp7-csv/exp7-validNumber.csv',float_format='%.0f',index=False)
	# 带宽
	truthTraffic={}
	truthAbw={}
	truthMeanAbw={}
	for i,v in enumerate(rateList):
		idxTemp=validIdx[v]
		searchTarget=arrivalTraffic[v]
		truthMeanAbw[v]=capacity-np.sum(searchTarget[:,1])*8/(searchTarget[-1,0]-searchTarget[0,0])*1e-6
		meanTraffic=[]
		meanAbw=[]
		for idx in idxTemp:
			arrivalTemp=arrivalBQR[v][int(idx),:,:]
			beginTime=arrivalTemp[0,0]
			endTime=arrivalTemp[-1,0]
			beginIdx=np.searchsorted(searchTarget[:,0],beginTime)+1
			endIdx=np.searchsorted(searchTarget[:,0],endTime)
			if beginIdx+1>=endIdx:
				packetSum=0
			else:
				packetSum=np.sum(searchTarget[beginIdx:endIdx,1])
			meanRate=packetSum*8/(endTime-beginTime)*1e-6
			meanTraffic.append(meanRate)
			meanAbw.append(capacity-meanRate)
		truthTraffic[v]=meanTraffic
		truthAbw[v]=np.array(meanAbw)
	# 可用带宽预测和实际对比
	figPath='/images/comparison/exp7/{:d}.png'
	if False:
		fig=plt.figure(figsize=(10,7))
		for i,v in enumerate(rateList):
			real=truthAbw[v]
			pred=prediction[v]
			plt.plot(real,'.-',label='ground truth')
			plt.plot(pred,'.-',label='BQR prediction')
			plt.xlabel('prediction index')
			plt.ylabel('abw(Mbps)')
			plt.ylim(0,1000)
			plt.title('BQR/ground truth(rough traffic rate {}Mbps)'.format(v))
			plt.legend(loc='lower left')
			plt.text(.50,.05,'mean: truth {:.0f}, pred {:.0f}'.format(truthMeanAbw[v],np.mean(pred)),transform=plt.gca().transAxes)
			plt.savefig(figPath.format(v),bbox_inches='tight')
			plt.clf()
	
	#code.interact(local=dict(globals(),**locals()))