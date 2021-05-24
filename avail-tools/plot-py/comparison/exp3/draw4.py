# 实验3 BQR 固定阈值 低链路带宽 高延迟抖动
# exp3-OWD-index-full
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code,io,matplotlib
from matplotlib.patches import Rectangle
abnormal1='/data/comparison/exp3/900-20-900/BQR/timestamp.txt'
abnormal2='/data/comparison/exp3/400-20-900/BQR/timestamp.txt'
original='/data/comparison/exp1/900-900-900/BQR/timestamp.txt'
def loadTime(tsfile):
	data=[]
	f=open(tsfile)
	string=f.read()
	f.close()
	segments=string.split('\n\n')
	for seg in segments:
		if len(seg)==0:
			continue
		f=io.StringIO(seg)
		x=np.loadtxt(f,delimiter=',')
		f.close()
		data.append(x)
	data=np.array(data)
	return data
def data2OWD(data):
	ret=(data[:,:,1]-data[:,:,0])*1e6
	ret-=np.min(ret,axis=1)[:,np.newaxis]
	return ret
def lastRange(owd):
	seg=owd[:,-10:]
	return np.max(seg,axis=1)-np.min(seg,axis=1)
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

if __name__=='__main__':
	data1=loadTime(original)
	data2=loadTime(abnormal1)
	data3=loadTime(abnormal2)
	owd1=data2OWD(data1)
	owd2=data2OWD(data2)
	owd3=data2OWD(data3)
	range1=lastRange(owd1)
	range2=lastRange(owd2)
	range3=lastRange(owd3)
	rectx,recty,rectw,recth=181,-15,200-181+.5,130+200
	#label=['900-900(1000)-900','900-20(100)-900','400-20(100)-900']
	label=['Set1','Set2','Set3']
	idx=[-1,3,3]
	fig=plt.figure(figsize=(1.3,1.1))
	ax=plt.gca()
	ax.plot(np.arange(200),owd1[idx[0]]/1000,color=color[0],label=label[0],linestyle=linestyle[0])
	ax.plot(np.arange(200),owd2[idx[1]]/1000,color=color[1],label=label[1],linestyle=linestyle[1])
	ax.plot(np.arange(200),owd3[idx[2]]/1000,color=color[2],label=label[2],linestyle=linestyle[2])
	ax.add_patch(Rectangle((rectx,recty/1000),rectw,recth/1000,fill=False,edgecolor='black',linewidth=1))
	ax.tick_params('both',length=1,width=1,which='both',pad=1)
	plt.legend(loc='upper center',framealpha=.5,ncol=5,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	plt.xlabel('Packet Index',labelpad=0)
	plt.ylabel('One Way Delay(ms)',labelpad=0)
	plt.xlim(0,200)
	plt.xticks(np.arange(0,200+1,50))
	plt.ylim(0,20)
	plt.yticks(np.arange(0,20+1,5))
	plt.savefig('{:s}/exp3-OWD-index-full.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp3-OWD-index-full.eps'.format(imgDir),bbox_inches='tight')
	plt.show()
	plt.close(fig)

	fig=plt.figure(figsize=(1.3,1.1))
	ax=plt.gca()
	beginIdx=160
	recth=130+50
	x=np.arange(beginIdx,200)
	ax.plot(x,owd1[idx[0]][beginIdx:],color=color[0],label=label[0],linestyle=linestyle[0])
	ax.plot(x,owd2[idx[1]][beginIdx:],color=color[1],label=label[1],linestyle=linestyle[1])
	ax.plot(x,owd3[idx[2]][beginIdx:],color=color[2],label=label[2],linestyle=linestyle[2])
	ax.add_patch(Rectangle((rectx,recty),rectw,recth,fill=False,edgecolor='black',linewidth=1))
	ax.tick_params('both',length=1,width=1,which='both',pad=1)
	plt.legend(loc='upper center',framealpha=.5,ncol=5,labelspacing=0,columnspacing=0.5,handletextpad=0.25,fontsize=5)
	plt.grid(axis='both',linestyle=(0,(1,1)),linewidth=.1)
	plt.xlabel('Packet Index',labelpad=0)
	plt.ylabel('One Way Delay(us)',labelpad=0)
	plt.xlim(beginIdx,200)
	plt.xticks(np.arange(beginIdx,200+1,10))
	plt.ylim(0,500)
	plt.yticks(np.arange(0,500+1,100))
	plt.savefig('{:s}/exp3-OWD-index-part.pdf'.format(imgDir),bbox_inches='tight')
	plt.savefig('{:s}/exp3-OWD-index-part.eps'.format(imgDir),bbox_inches='tight')
	plt.show()
	plt.close(fig)

	#code.interact(local=dict(globals(),**locals()))