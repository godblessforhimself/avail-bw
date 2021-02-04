import numpy as np
import code
import matplotlib.pyplot as plt
def cdf(x, plot=True, *args, **kwargs):
    x, y = sorted(x), np.arange(len(x)) / len(x)
    return plt.plot(x, y, *args, **kwargs) if plot else (x, y)
def rmse(x,y):
	xFlattend=x.flatten()
	yRepeat=len(xFlattend)//len(y)
	yExpanded=np.repeat(y,yRepeat)
	rmse=((xFlattend-yExpanded)**2).mean()**0.5
	return rmse
def mae(x,y):
	xFlattend=x.flatten()
	yRepeat=len(xFlattend)//len(y)
	yExpanded=np.repeat(y,yRepeat)
	mae=np.mean(np.abs(xFlattend-yExpanded))
	return mae
def mape(x,y):
	xFlattend=x.flatten()
	yRepeat=len(xFlattend)//len(y)
	yExpanded=np.repeat(y,yRepeat)
	mape=np.mean(np.abs(xFlattend-yExpanded)/yExpanded)
	return mape
abwFilename='data/exp6/all.txt'
gtFilename='data/exp6/gt.txt'
numberFilename='data/exp6/runNumber.txt'
timeFilename='data/exp6/finalTime.txt'
x=np.arange(0,900+1,50)
n=len(x)
nSample=100
nColumn=3
boxprops = dict(linestyle='-', linewidth=2, color='black')
flierprops = dict(marker='o', markerfacecolor='white', markersize=5,
                  linestyle='none')
medianprops = dict(linestyle='solid', linewidth=1.5, color='black')
meanpointprops = dict(marker='D', markeredgecolor='black',
                      markerfacecolor='firebrick')
meanlineprops = dict(linestyle='--', linewidth=2.5, color='purple')
def draw_plot(data,x,y,metric):
	error=[metric(data[i],[y[i]])*100 for i in range(n)]
	plt.scatter(x,np.around(error,2))
	
if __name__=='__main__':
	data=np.loadtxt(abwFilename,delimiter=' ')
	gt=np.loadtxt(gtFilename)
	numberData=np.loadtxt(numberFilename)
	timeData=np.loadtxt(timeFilename)
	numberData=np.reshape(numberData,(n,nSample))
	timeData=np.reshape(timeData,(n,nSample))
	data=np.reshape(data,(n,nSample,nColumn))
	estimate_list=[data[i,:,0] for i in range(n)]
	cdf_list=[data[i,:,0]-gt[i] for i in range(n)]
	#fig1, ax1 = plt.subplots(figsize=(10,5))
	#box_data=[timeData[i,:]/1000 for i in range(n)]
	box_data=[numberData[i,:] for i in range(n)]
	plt.boxplot(box_data,medianprops=medianprops,flierprops=flierprops,labels=x)
	plt.ylim(0,6)
	plt.yticks(np.arange(0,6,1))
	#plt.xticks(np.arange(0,901,50))
	#plt.xlim(-25,925)
	ax1.set_title('Boxplot of stream number')
	plt.xlabel('traffic(Mbps)')
	plt.ylabel('stream number')
	#draw_plot(estimate_list,x,gt,mape)
	#cdf(timeData[10,:])
	#for i in range(n):
		#cdf(cdf_list[i])
	#	cdf(timeData[i,:])
		#cdf(numberData[i,:])
	plt.grid()
	#plt.show()
	plt.savefig('data/exp6/streamNumber.png',bbox_inches='tight')
	#draw_plot(ub_list,x,gt,mape)
	#ax1.axhline(gt[i],i/n,(i+1)/n)
	#code.interact(local=dict(globals(),**locals()))