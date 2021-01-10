import numpy as np, matplotlib.pyplot as plt
import code,sys,os
import scipy.stats

getGap=lambda x: x[1::2]-x[::2]
getDuration=lambda x: x[-1]-x[0]
def cdf(x, plot=True, *args, **kwargs):
	x, y = sorted(x), np.arange(len(x)) / len(x)
	return plt.plot(x, y, *args, **kwargs) if plot else (x, y)

def load(f1,f2):
	real,meas=np.loadtxt(f1),np.loadtxt(f2)
	N=min(len(meas),len(real))
	real=real[:N]*1e6
	meas=meas[:N]*1e6
	realGap=getGap(real)
	measGap=getGap(meas)
	realGapSum=sum(realGap)
	measGapSum=sum(measGap)
	realDuration=getDuration(real)
	measDuration=getDuration(meas)
	realE=estimate(realGap)
	measE=estimate(measGap)
	print('gap sum: {:.0f} {:.0f}; duration: {:.0f} {:.0f}'.format(realGapSum,measGapSum,realDuration,measDuration))
	print('real {:.2f}; meas {:.2f}'.format(realE,measE))
	return real,meas,realGap,measGap

def estimate(gaps,capacity=957,size=1472):
	traffic=[]
	gin=size*8/capacity
	for gout in gaps:
		if gout<=gin:
			traffic.append(0)
		else:
			traffic.append((gout/gin-1)*capacity)
	return capacity-np.mean(traffic)

def drawRealError(realEstimation,gt):
	e=np.array(realEstimation)
	gt_=gt.reshape(-1,1)
	error=e-gt_
	m,l,h=meanConfidenceInterval(error)
	fig,ax=plt.subplots(figsize=(10,10))
	ax.errorbar(rates,m,(m-l,h-m),capsize=5,fmt='.-b')
	plt.title('real error')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('error(Mbps)')
	plt.text(.40,.94,'95% CI errorbar(n:{})'.format(error.shape[1]),transform=ax.transAxes)
	plt.xlim(rates[0]-5,rates[-1]+5)
	plt.xticks(rates)
	plt.ylim(-60,70+1)
	plt.yticks(np.arange(-60,70+1,10))
	plt.grid()
	plt.show()

def drawMeasError(Estimation,gt):
	e=np.array(Estimation)
	gt_=gt.reshape(-1,1)
	error=e-gt_
	m,l,h=meanConfidenceInterval(error)
	fig,ax=plt.subplots(figsize=(10,10))
	ax.errorbar(rates,m,(m-l,h-m),capsize=5,fmt='.-r')
	plt.title('spruce error')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('error(Mbps)')
	plt.text(.40,.94,'95% CI errorbar(n:{})'.format(error.shape[1]),transform=ax.transAxes)
	plt.xlim(rates[0]-5,rates[-1]+5)
	plt.xticks(rates)
	#plt.ylim(-60,70+1)
	#plt.yticks(np.arange(-60,70+1,10))
	plt.grid()
	plt.show()

def drawBothError(real,meas,gt):
	e1=np.array(real)
	e2=np.array(meas)
	gt_=gt.reshape(-1,1)
	error1=e1-gt_
	error2=e2-gt_
	fig,ax=plt.subplots(figsize=(10,10))
	m,l,h=meanConfidenceInterval(error1)
	eb=ax.errorbar(rates,m,(m-l,h-m),capsize=3,fmt='.-b',label='real')
	eb[-1][0].set_linestyle('dotted')
	m,l,h=meanConfidenceInterval(error2)
	eb=ax.errorbar(rates,m,(m-l,h-m),capsize=3,fmt='^-r',label='spruce')
	eb[-1][0].set_linestyle('dotted')
	plt.title('spruce estimation error')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('error(Mbps)')
	plt.text(.40,.94,'95% CI errorbar(n:{})'.format(error1.shape[1]),transform=ax.transAxes)
	plt.xlim(rates[0]-5,rates[-1]+5)
	plt.xticks(rates)
	plt.ylim(-360,240+1)
	plt.yticks(np.arange(-360,240+1,40))
	plt.grid()
	plt.legend()
	plt.savefig('images/spruce-real.png',bbox_inches='tight')

def meanConfidenceInterval(data_, confidence=0.95):
	# nrate,nsample
	data=np.array(data_)
	nSample=data.shape[1]
	m,se=np.mean(data,axis=1),scipy.stats.sem(data,axis=1)
	h=se*scipy.stats.t.ppf((1 + confidence) / 2., nSample-1)
	return m, m-h, m+h

def drawDuration(rd,md):
	fig,ax=plt.subplots(figsize=(10,10))
	width=realStep//3
	labels=['real','spruce']
	for i,data in enumerate([rd,md]):
		m,l,h=meanConfidenceInterval(np.array(data)*1e-3)
		ax.bar(rates+(i-0.5)*width,m,width=width,yerr=(m-l,h-m),capsize=5,label=labels[i])
	plt.title('Duration comparison')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('duration(ms)')
	plt.text(.40,.96,'95% CI errorbar(n:{})'.format(len(rd[0])),transform=ax.transAxes)
	plt.xlim(rates[0]-width*2,rates[-1]+width*2)
	plt.xticks(rates)
	plt.ylim(280,300)
	plt.yticks(np.arange(280,300+1,5))
	plt.grid()
	plt.legend()
	plt.savefig('images/spruce-duration.png',bbox_inches='tight')

def drawGapSum(rgd,mgd):
	fig,ax=plt.subplots(figsize=(10,10))
	width=realStep//3
	labels=['real','spruce']
	for i,data in enumerate([rgd,mgd]):
		m,l,h=meanConfidenceInterval(np.array(data))
		ax.bar(rates+(i-0.5)*width,m,width=width,yerr=(m-l,h-m),capsize=5,label=labels[i])
	plt.title('gap sum comparison')
	plt.xlabel('traffic rate(Mbps)')
	plt.ylabel('gap sum(us)')
	plt.text(.40,.96,'95% CI errorbar(n:{})'.format(len(rgd[0])),transform=ax.transAxes)
	plt.xlim(rates[0]-width*2,rates[-1]+width*2)
	plt.xticks(rates)
	plt.ylim(1200,2400)
	plt.yticks(np.arange(1200,2400+1,100))
	plt.grid()
	plt.legend()
	plt.savefig('images/gap-sum.png',bbox_inches='tight')

def drawCdf(ax,g1,g2,gap,title):
	x,y=cdf(g1,False)
	ax.plot(x,y,label='real')
	x,y=cdf(g2,False)
	ax.plot(x,y,label='spruce')
	ax.axvline(x=gap,linestyle='--',color='grey')
	ax.annotate('min gap:{:.0f}us'.format(gap),(gap,0.9),xytext=(40,0.8),arrowprops=dict(facecolor='black',width=1,headwidth=4))
	ax.legend()
	ax.grid()
	ax.set_title(title)
	ax.set_xlabel('gap(us)')
	ax.set_xlim(0,100)
	ax.set_xticks(np.arange(0,100+1,10))
	ax.set_yticks(np.arange(0,1.0+.01,0.1))

def drawGapCDF(realGaps,measGaps):
	gap=1472*8/957
	fig,((ax1, ax2), (ax3, ax4))=plt.subplots(2,2,figsize=(10,10))
	fig.suptitle('CDF for gap', fontsize=12)
	drawCdf(ax1,realGaps[0],measGaps[0],gap,'traffic 0Mbps')
	drawCdf(ax2,realGaps[3],measGaps[3],gap,'traffic 300Mbps')
	drawCdf(ax3,realGaps[6],measGaps[6],gap,'traffic 600Mbps')
	drawCdf(ax4,realGaps[9],measGaps[9],gap,'traffic 900Mbps')
	plt.savefig('images/gap-cdf.png',bbox_inches='tight')

prefix='data/spruce-problem'
repeatNumber=100
pairNumber=98
realStep=100
minStep=50
rates=np.arange(0,900+1,realStep)
if __name__=='__main__':
	np.set_printoptions(suppress=True)
	gt=np.loadtxt('../version-x/data/exp6/gt.txt')
	gt=gt[::realStep//minStep]
	realEstimation=[]
	measEstimation=[]
	realDuration=[]
	realGapDuration=[]
	measDuration=[]
	measGapDuration=[]
	realGaps=[]
	measGaps=[]
	# awful code begins:
	for rate in rates:
		realAs=[]
		measAs=[]
		rds=[]
		rgds=[]
		mds=[]
		mgds=[]
		realGap_=[]
		measGap_=[]
		for i in range(repeatNumber):
			real=np.loadtxt('{}/{}-real-{}.txt'.format(prefix,rate,i+1))[:2*pairNumber]*1e6
			meas=np.loadtxt('{}/{}-meas-{}.txt'.format(prefix,rate,i+1))[:2*pairNumber]*1e6
			realGap=getGap(real)
			realGap_.extend(realGap)
			realA=estimate(realGap)
			measGap=getGap(meas)
			measGap_.extend(measGap)
			measA=estimate(measGap)
			rd=real[-1]-real[0]
			rgd=sum(realGap)
			md=meas[-1]-meas[0]
			mgd=sum(measGap)
			realAs.append(realA)
			measAs.append(measA)
			rds.append(rd)
			rgds.append(rgd)
			mds.append(md)
			mgds.append(mgd)
		realEstimation.append(realAs)
		measEstimation.append(measAs)
		realDuration.append(rds)
		measDuration.append(mds)
		realGapDuration.append(rgds)
		measGapDuration.append(mgds)
		realGaps.append(realGap_)
		measGaps.append(measGap_)
	# awful code ends
	#drawBothError(realEstimation,measEstimation,gt)
	#drawDuration(realDuration,measDuration)
	#drawGapSum(realGapDuration,measGapDuration)
	#drawGapCDF(realGaps,measGaps)
	#code.interact(local=dict(globals(),**locals()))