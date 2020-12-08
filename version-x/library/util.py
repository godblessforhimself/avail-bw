import numpy as np
delta=lambda x:x[1:]-x[:-1]
def smooth(send,recv,ldn):
	gin,gout=delta(send[:ldn]),delta(recv[:ldn])
	#smooth gin
	m1=np.mean(gin[1:])
	gin[0]=m1
	send[0]=send[1]-gin[0]
	#smooth gout
	median=np.median(gout)
	std=np.std(gout)
	cond=np.logical_and(gout>=median-std,gout<=median+std)
	valid=gout[np.where(cond)]
	m2,std=np.mean(valid),np.std(valid)
	for i in range(ldn-1):
		if gout[i]<m2-std or gout[i]>m2+std:
			gout[i]=m2
		else:
			for j in range(i-1,0-1,-1):
				recv[j]=recv[j+1]-gout[j]
			break
	return send,recv
def remove_offset(send,recv):
	offset=send[0]
	send-=offset
	recv-=offset
	send=send.astype(np.int32)
	recv=recv.astype(np.int32)
	owd=recv-send
	owd=owd-np.min(owd)
	return send,recv,owd