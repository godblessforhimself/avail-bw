# 探究不同链路带宽、不同背景流量下，BQR的曲线特征
# 实验1
# 900-900-900
# 500-500-500
# 0-0-0
# 900-400-400
# 400-900-400
# 400-400-900
# 实验2
# 600-0-0
# 600-300-0
# 0-600-0
# 300-600-0
# 实验3
# 900-0(100)-0
# 0-0(100)-900
import numpy as np
import code,io
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
dataset1=['900-900-900','500-500-500','0-0-0','900-400-400','400-900-400','400-400-900']
dataset2=['600-0-0','600-300-0','0-600-0','300-600-0']
dataset3=['900-0-0','0-0-900']
prefix1='/data/comparison/exp1'
prefix2='/data/comparison/exp2'
prefix3='/data/comparison/exp3'
fmt='{}/{}/BQR/timestamp.txt'
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
def data2OWD(data):
	ret=(data[:,:,1]-data[:,:,0])*1e6
	ret-=np.min(ret,axis=1)[:,np.newaxis]
	return ret
def relativeTime(a):
	return (a[:,:,0]-a[:,0,0,np.newaxis])*1e6
np.set_printoptions(suppress=True)
if __name__=='__main__':
	data1=[]
	data2,data3=[],[]
	for i in dataset1:
		data1.append(loadTime(fmt.format(prefix1,i)))
	for i in dataset2:
		data2.append(loadTime(fmt.format(prefix2,i)))
	for i in dataset3:
		data3.append(loadTime(fmt.format(prefix3,i)))
	owd=[]
	for data in [data1,data2,data3]:
		for item in data:
			owd.append(data2OWD(item))
	fig,axs=plt.subplots(nrows=3,ncols=4,figsize=(20,10))
	for i,v in enumerate(owd):

	code.interact(local=dict(globals(),**locals()))