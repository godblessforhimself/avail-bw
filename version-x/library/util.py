import numpy as np
import code
delta=lambda x:x[1:]-x[:-1]
def smooth(send,recv,ldn,extreme=False,extreme_n=-1):
	gin,gout=delta(send[:ldn]),delta(recv[:ldn])
	#smooth gin
	m1=np.mean(gin[1:])
	gin[0]=m1
	send[0]=send[1]-gin[0]
	#remove extreme small value of gout at beginning
	smooth_gout=False # we dont want to smooth gout, because it makes owd[0] < min owd
	if smooth_gout:
		mean=np.mean(gout)
		std=np.std(gout)
		cond=gout>mean-std
		valid=gout[np.where(cond)]
		m2,std=np.mean(valid),np.std(valid)
		for i in range(ldn-1):
			if gout[i]<m2-std:
				gout[i]=m2
			else:
				break
		for i in range(ldn-1,0,-1):
			recv[i-1]=recv[i]-gout[i-1]
	if extreme:
		if extreme_n==-1:
			m1=np.mean(gin)
			m2=np.mean(gout)
			for i in range(ldn-1,0,-1):
				send[i-1]=send[i]-m1
				recv[i-1]=recv[i]-m2
		elif extreme_n<=ldn-1:
			for i in range(ldn-2,0-1,-extreme_n):
				left=max(i-extreme_n+1,0)
				gin[left:i+1]=np.mean(gin[left:i+1])
			for i in range(ldn-1,0,-1):
				send[i-1]=send[i]-gin[i-1]
			for i in range(ldn-2,0-1,-extreme_n):
				left=max(i-extreme_n+1,0)
				gout[left:i+1]=np.mean(gout[left:i+1])
			for i in range(ldn-1,0,-1):
				recv[i-1]=recv[i]-gout[i-1]
		else:
			assert(False)
	
	return send,recv
def remove_offset(send,recv):
	offset=send[0]
	send-=offset
	recv-=offset
	owd=recv-send
	owd=owd-np.min(owd)
	return send,recv,owd
def roughA(i,send,ps=1472):
	p=(i+1)*ps*8
	t=send[i]*1e6
	return p/t
def roughAbw(nLoad,nInspect,t,pLoad,pInspect):
	p=(nLoad*pLoad+nInspect*pInspect)*8
	A=p/t*1e-6
	return A

def findRecoverIndex(inspect_owd,owd_min,logFile=None,bound_=0.05):
	inspect_number=len(inspect_owd)
	fully_recover=False
	if owd_min<inspect_owd[0]:
		owd_decrease=inspect_owd[0]-owd_min
		bound=bound_*owd_decrease
		dowd=delta(inspect_owd)
		fully_recover_index=0
		while fully_recover_index<inspect_number and inspect_owd[fully_recover_index]>owd_min+bound:
			fully_recover_index+=1
		# tricks to avoid unrecovered region less than bound: 
		if fully_recover_index+1<inspect_number and fully_recover_index>=2:
			flag1=inspect_owd[fully_recover_index]>inspect_owd[fully_recover_index+1]
			flag2=-dowd[fully_recover_index-1]>=-0.9*dowd[fully_recover_index-2]
			if flag1 and flag2:
				fully_recover_index+=1
				if logFile:
					logFile.write('tricks working\n')
		if fully_recover_index<inspect_number:
			fully_recover=True
			if logFile:
				logFile.write('fully recover\n')
		else:
			fully_recover=False
			if logFile:
				logFile.write('not fully recover\n')
		#code.interact(local=dict(globals(),**locals()))
	return fully_recover,fully_recover_index