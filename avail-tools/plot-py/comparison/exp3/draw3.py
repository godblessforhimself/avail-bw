# 实验3 显示BQR相对绝对时间轴的曲线；
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code,io
from matplotlib.patches import Rectangle
abnormal1='/data/comparison/exp3/900-20-900/BQR/timestamp.txt'
abnormal2='/data/comparison/exp3/400-20-900/BQR/timestamp.txt'
original='/data/comparison/exp1/900-900-900/BQR/timestamp.txt'
np.set_printoptions(suppress=True)
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
def relativeTime(a):
	return (a[:,:,0]-a[:,0,0,np.newaxis])*1e6
if __name__=='__main__':
	data1=loadTime(original)
	data2=loadTime(abnormal1)
	data3=loadTime(abnormal2)
	owd1=data2OWD(data1)
	owd2=data2OWD(data2)
	owd3=data2OWD(data3)
	time1=relativeTime(data1)
	time2=relativeTime(data2)
	time3=relativeTime(data3)
	rectx,recty,rectw,recth=181,-15,200-181+.5,130+200
	fig,axs=plt.subplots(nrows=1,ncols=2,figsize=(20,10))
	ax=axs[0]
	ax.plot(time1[-1],owd1[-1],'.-',label='900-900(1000)-900')
	ax.plot(time2[2],owd2[2],'.-',label='900-20(100)-900')
	ax.plot(time3[3],owd3[3],'.-',label='400-20(100)-900')
	ax.legend()
	ax.grid()
	ax=axs[1]
	beginIdx=160
	ax.plot(time1[-1][beginIdx:],owd1[-1][beginIdx:],'.-',label='900-900(1000)-900')
	ax.plot(time2[2][beginIdx:],owd2[2][beginIdx:],'.-',label='900-20(100)-900')
	ax.plot(time3[3][beginIdx:],owd3[3][beginIdx:],'.-',label='400-20(100)-900')
	ax.legend()
	ax.grid()
	fig.suptitle('The influence of capacity on noise',y=0.92)
	fig.text(0.05,0.5,'OWD(us)',va='center',rotation='vertical')
	fig.text(0.5,0.05,'relative time(us)',va='center',rotation='horizontal')
	plt.savefig('/images/comparison/exp3/relative-time.png',bbox_inches='tight')
	plt.close(fig)
	#code.interact(local=dict(globals(),**locals()))