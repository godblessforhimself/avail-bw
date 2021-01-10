import numpy as np
import code,argparse
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import scipy.stats
gtFilename='../version-x/data/exp6/gt.txt'
myMethod='../version-x/data/exp6/all.txt'	
def load(prefix,rates):
	ret=[]
	for rate in rates:
		d=np.loadtxt('data/{}/{}-statistic-estimation'.format(prefix,int(rate)),delimiter=',')
		ret.append(d)
	return ret
def loadPacketInformation(prefix,rates):
	ret=[]
	for rate in rates:
		d=np.loadtxt('data/{}/{}-statistic-packetLength'.format(prefix,int(rate)),delimiter=',')
		ret.append(d)
	return ret
def getMinPts(array):
	return min([len(a) for a in array])

def getError(array,gt,n):
	# arr (nRate,nSample,nDim) or (nRate,nSample)
	# gt (nRate)
	nDim=1 if len(array[0].shape)==1 else array[0].shape[1]
	arr=np.array([a[:n,:] if nDim>1 else a[:n] for a in array])
	gtBroad=np.reshape(gt,(-1,1) if nDim==1 else (-1,1,1))
	return (arr-gtBroad)
def getPercentageError(array,gt,n):
	# arr (nRate,nSample,nDim) or (nRate,nSample)
	# gt (nRate)
	nDim=1 if len(array[0].shape)==1 else array[0].shape[1]
	arr=np.array([a[:n,:] if nDim>1 else a[:n] for a in array])
	gtBroad=np.reshape(gt,(-1,1) if nDim==1 else (-1,1,1))
	return (arr-gtBroad)/gtBroad

def meanConfidenceInterval(data, confidence=0.95):
	# nrate,nsample
    nSample=data.shape[1]
    m,se=np.mean(data,axis=1),scipy.stats.sem(data,axis=1)
    h=se*scipy.stats.t.ppf((1 + confidence) / 2., nSample-1)
    return m, m-h, m+h

def drawPathloadError(errorList,n,path=None):
	labelList=['pathloadLow','pathloadHigh','pathloadMean']
	nBar=len(labelList)
	fig,ax=plt.subplots(figsize=(10,10))
	width=realStep//(nBar+2)
	for i in range(nBar):
		xPos=rates+(i-1)*width
		yHeight,l,h=meanConfidenceInterval(errorList[i],0.95)
		ax.bar(xPos,yHeight,width=width,yerr=(yHeight-l,h-yHeight),label=labelList[i],capsize=5)
	plt.xticks(rates)
	plt.title('pathload error')
	plt.xlabel('traffic rate(Mbps)')
	plt.text(.05,.95,'95% CI errorbar(n:{})'.format(n),transform=ax.transAxes)
	plt.ylabel('error(Mbps)')
	plt.legend()
	plt.grid()
	if path:
		plt.savefig(path,bbox_inches='tight')
	else:
		plt.show()

def drawPathloadPerror(perrorList,n,path=None):
	labelList=['pathloadLow','pathloadHigh','pathloadMean']
	nBar=len(labelList)
	fig,ax=plt.subplots(figsize=(10,10))
	width=realStep//(nBar+2)
	for i in range(nBar):
		xPos=rates+(i-1)*width
		yHeight,l,h=meanConfidenceInterval(perrorList[i]*100,0.95)
		ax.bar(xPos,yHeight,width=width,yerr=(yHeight-l,h-yHeight),label=labelList[i],capsize=5)
	plt.xticks(rates)
	plt.title('pathload relative error')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('relative error(%)')
	plt.text(.25,.95,'95% CI errorbar(n:{})'.format(n),transform=ax.transAxes)
	plt.legend()
	plt.grid()
	if path:
		plt.savefig(path,bbox_inches='tight')
	else:
		plt.show()

def drawIGIError(errorList,n,path=None):
	labelList=['PTR','IGI']
	nBar=2
	fig,ax=plt.subplots(figsize=(10,10))
	width=realStep//4
	for i in range(nBar):
		xPos=rates+(i-0.5)*width
		y,l,h=meanConfidenceInterval(errorList[4+i])
		ax.bar(xPos,y,width=width,yerr=(y-l,h-y),label=labelList[i],capsize=5)
	plt.title('IGI/PTR error')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('error(Mbps)')
	plt.xticks(rates)
	plt.text(.15,.95,'95% CI errorbar(n:{})'.format(n),transform=ax.transAxes)
	plt.legend()
	plt.grid()
	if path:
		plt.savefig(path,bbox_inches='tight')
	else:
		plt.show()

def drawIGIPerror(perrorList,n,path=None):
	labelList=['PTR','IGI']
	nBar=2
	fig,ax=plt.subplots(figsize=(10,10))
	width=realStep//4
	for i in range(nBar):
		xPos=rates+(i-0.5)*width
		y,l,h=meanConfidenceInterval(perrorList[4+i]*100)
		ax.bar(xPos,y,width=width,yerr=(y-l,h-y),label=labelList[i],capsize=5)
	plt.title('IGI/PTR relative error')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('relative error(%)')
	plt.xticks(rates)
	plt.text(.15,.95,'95% CI errorbar(n:{})'.format(n),transform=ax.transAxes)
	plt.legend()
	plt.grid()
	if path:
		plt.savefig(path,bbox_inches='tight')
	else:
		plt.show()

def drawErrorCurve(errorList,n,path=None):
	labelList=['pathload','spruce','PTR','assolo','bqr']
	idxList=[2,3,4,6,7]
	fmtList=['.-b','s--g','o-.r','v:c','^-m','<--y','>-.k']
	fig,ax=plt.subplots(figsize=(10,10))
	for i,idx in enumerate(idxList):
		mean=np.mean(errorList[idx],axis=1)
		plt.plot(rates,mean,fmtList[i],label=labelList[i])
	plt.title('abw estimation error')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('error(Mbps)')
	ax.yaxis.set_major_locator(ticker.MultipleLocator(base=25))
	plt.xticks(rates)
	plt.legend()
	plt.grid()
	if path:
		plt.savefig(path,bbox_inches='tight')
	else:
		plt.show()

def drawPerrorCurve(perrorList,n,path=None):
	labelList=['pathload','spruce','PTR','assolo','bqr']
	idxList=[2,3,4,6,7]
	fmtList=['.-b','s--g','o-.r','v:c','^-m','<--y','>-.k']
	fig,ax=plt.subplots(figsize=(10,10))
	for i,idx in enumerate(idxList):
		mean=np.mean(perrorList[idx],axis=1)*100
		plt.plot(rates,mean,fmtList[i],label=labelList[i])
	plt.title('abw relative error')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('relative error(%)')
	plt.ylim(-50,150+1)
	plt.yticks(np.arange(-50,150+1,5))
	plt.xticks(rates)
	plt.legend()
	plt.grid()
	if path:
		plt.savefig(path,bbox_inches='tight')
	else:
		plt.show()

def drawBqrError(err,n,path=None):
	fig,ax=plt.subplots(figsize=(10,10))
	xPos=rates
	y,l,h=meanConfidenceInterval(err)
	ax.errorbar(xPos,y,yerr=(y-l,h-y),capsize=5,fmt='^-m')
	plt.title('Bqr error')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('error(Mbps)')
	plt.xticks(rates)
	plt.xlim(-50,950)
	plt.text(.40,.94,'95% CI errorbar(n:{})'.format(n),transform=ax.transAxes)
	plt.grid()
	if path:
		plt.savefig(path,bbox_inches='tight')
	else:
		plt.show()

def drawBqrPerror(err,n,path=None):
	fig,ax=plt.subplots(figsize=(10,10))
	xPos=rates
	y,l,h=meanConfidenceInterval(err*100)
	ax.errorbar(xPos,y,yerr=(y-l,h-y),capsize=5,fmt='^-m')
	plt.title('Bqr relative error')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('relative error(Mbps)')
	plt.xticks(rates)
	plt.text(.03,.96,'95% CI errorbar(n:{})'.format(n),transform=ax.transAxes)
	plt.grid()
	if path:
		plt.savefig(path,bbox_inches='tight')
	else:
		plt.show()

def avgArray(arr):
	ret=[]
	for a in arr:
		avg=np.mean(a,axis=0)
		ret.append(avg)
	return np.array(ret)

def loadBqrInfo():
	time=np.loadtxt('../version-x/data/exp6/finalTime.txt')
	time=time.reshape(19,100)
	time=np.mean(time,axis=1)*1e-6
	pnum=np.loadtxt('../version-x/data/exp6/runNumber.txt')
	pnum=pnum.reshape(19,100)
	pnum=np.mean(pnum,axis=1)*110
	time=time*pnum/110
	time=time[::realStep//minStep]
	pnum=pnum[::realStep//minStep]
	psize=1514
	psum=pnum*psize
	ret=[]
	for i in range(n):
		ret.append([time[i],pnum[i],psum[i],psize])
	return np.array(ret)

def simpleDraw(ax,infoList,idx,fmtList,labelList,scale=1.0):
	for i,it in enumerate(infoList):
		ax.plot(rates,it[:,idx]*scale,fmtList[i],label=labelList[i])
	
def drawTimeCurve(infoList,path=None):
	fig,ax=plt.subplots(figsize=(10,10))
	fmtList=['.-b','s--g','o-.r','v:c','^-m','<--y','>-.k']
	labelList=['pathload','spruce','PTR','assolo','bqr']
	simpleDraw(ax,infoList,0,fmtList,labelList)
	avgTime=np.mean(np.array(infoList),axis=1)[:,0]
	cellText=[]
	argSort=np.argsort(avgTime)
	for i in argSort[::-1]:
		cellText.append([labelList[i],'{:.3f}s'.format(avgTime[i])])
	tb=plt.table(cellText=cellText,cellLoc='center',rowLoc='center',loc='upper center')
	tb.scale(.18,1.4)
	plt.text(0.40,0.80,'average time for all rates',transform=ax.transAxes)
	plt.title('Measurement time comparison')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('time(s)')
	plt.ylim(-0.5,7.0)
	plt.yticks(np.arange(-.5,7.0+.5,.5))
	plt.xticks(rates)
	plt.grid()
	plt.legend()
	if path:
		plt.savefig(path,bbox_inches='tight')
	else:
		plt.show()
	
def drawPacketSumCurve(infoList,path=None):
	fig,ax=plt.subplots(figsize=(10,10))
	fmtList=['.-b','s--g','o-.r','v:c','^-m','<--y','>-.k']
	labelList=['pathload','spruce','PTR','assolo','bqr']
	scale=1/1024/1024
	simpleDraw(ax,infoList,2,fmtList,labelList,scale=scale)
	avgPacketSum=np.mean(np.array(infoList),axis=1)[:,2]
	argSort=np.argsort(avgPacketSum)
	cellText=[]
	for i in argSort[::-1]:
		cellText.append([labelList[i],'{:.2f}MB'.format(avgPacketSum[i]*scale)])
	tb=plt.table(cellText=cellText,cellLoc='center',rowLoc='center',loc='upper left')
	tb.scale(.19,1.4)
	plt.text(0.03,0.81,'average packet cost',transform=ax.transAxes)
	plt.title('Measurement packet cost comparison')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('packet cost(MB)')
	plt.ylim(-0.5,14.5)
	plt.yticks(np.arange(-0.5,14.5+.5,.5))
	plt.xticks(rates)
	plt.grid()
	plt.legend()
	if path:
		plt.savefig(path,bbox_inches='tight')
	else:
		plt.show()

def drawRateCurve(infoList,path=None):
	fig,ax=plt.subplots(figsize=(10,10))
	fmtList=['.-b','s--g','o-.r','v:c','^-m','<--y','>-.k']
	labelList=['pathload','spruce','PTR','assolo','bqr']
	scale=8.0/1024/1024
	avgRate=[]
	for i,it in enumerate(infoList):
		t,psum=it[:,0],it[:,2]
		rate=psum/t*scale
		avgRate.append(np.mean(rate))
		ax.plot(rates,rate,fmtList[i],label=labelList[i])
	argSort=np.argsort(avgRate)
	cellText=[]
	for i in argSort[::-1]:
		cellText.append([labelList[i],'{:.2f}Mbps'.format(avgRate[i])])
	tb=plt.table(cellText=cellText,cellLoc='center',rowLoc='center',loc='center right')
	tb.scale(.20,1.5)
	plt.text(0.79,0.6,'average probing rate',transform=ax.transAxes)
	plt.title('Probe rate comparison')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('probe rate(Mbps)')
	plt.ylim(0,500+1)
	plt.yticks(np.arange(0,500+1,50))
	plt.xticks(rates)
	plt.grid()
	plt.legend()
	if path:
		plt.savefig(path,bbox_inches='tight')
	else:
		plt.show()
oldDirectory=['pathload','spruce','igi-ptr','assolo']
ICDirectory=['pathload-IC','spruce-IC','igi-IC','assolo-IC']
noICDirectory=['pathload-noIC','spruce-noIC','igi-noIC','assolo-noIC']
paths=['error-{}.png','perror-{}.png','bqr-error-{}.png','bqr-perror-{}.png','time-{}.png','packet-cost-{}.png','average-rate-{}.png','pathload-error-{}.png','pathload-perror-{}.png','igi-error-{}.png','igi-perror-{}.png']
if __name__=='__main__':
	parser = argparse.ArgumentParser(description='parser')
	parser.add_argument('--type', type=str, default='old', help='noIC|IC|old')
	parser.add_argument('--show', action='store_true', help='show image')
	args=parser.parse_args()
	l=len(paths)
	if args.show:
		for i in range(l):
			paths[i]=None
	else:
		for i in range(l):
			paths[i]='images/{}/'.format(args.type)+paths[i].format(args.type)
	
	minStep=50
	realStep=100
	rates=np.arange(0,900+1,realStep)
	n=len(rates)
	if args.type=='old':
		abwLabel=oldDirectory
	elif args.type=='IC':
		abwLabel=ICDirectory
	elif args.type=='noIC':
		abwLabel=noICDirectory

	gt=np.loadtxt(gtFilename)
	gt=gt[::realStep//minStep]
	my=np.loadtxt(myMethod)
	my=my.reshape(19,100,3)[::realStep//minStep,:,0]
	

	abwList=[load(prefix,rates) for prefix in abwLabel]
	pinfos=[loadPacketInformation(prefix,rates) for prefix in abwLabel]
	# idx,time,pnum,psum,psize
	infoList=[]
	for i in range(3):
		avg=avgArray(pinfos[i])
		infoList.append(avg[:,1:])
	avg=[]
	for i,a in enumerate(pinfos[-1]):
		num=len(abwList[-1][i])
		avg.append(a/num)
	infoList.append(np.array(avg))
	bqrInfo=loadBqrInfo()
	infoList.append(bqrInfo)
	nAbw=len(abwList)
	minPts=min([getMinPts(abw) for abw in abwList])
	errorList=[]
	perrorList=[]
	for a in abwList:
		error=getError(a,gt,minPts)
		perror=getPercentageError(a,gt,minPts)
		if len(perror.shape)==2:
			perrorList.append(perror)
			errorList.append(error)
		else:
			for i in range(perror.shape[2]):
				perrorList.append(perror[:,:,i])
				errorList.append(error[:,:,i])
	myError=getError(my,gt,minPts)
	errorList.append(myError)
	myPerror=getPercentageError(my,gt,minPts)
	perrorList.append(myPerror)

	drawErrorCurve(errorList,minPts,path=paths[0])
	drawPerrorCurve(perrorList,minPts,path=paths[1])
	drawBqrError(myError,minPts,path=paths[2])
	drawBqrPerror(myPerror,minPts,path=paths[3])
	drawTimeCurve(infoList,path=paths[4])
	drawPacketSumCurve(infoList,path=paths[5])
	drawRateCurve(infoList,path=paths[6])
	drawPathloadError(errorList,minPts,paths[7])
	drawPathloadPerror(perrorList,minPts,paths[8])
	drawIGIError(errorList,minPts,paths[9])
	drawIGIPerror(perrorList,minPts,paths[10])
	#code.interact(local=dict(globals(),**locals()))
