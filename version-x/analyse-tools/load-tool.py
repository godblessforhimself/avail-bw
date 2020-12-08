import code,sys
import numpy as np
import matplotlib.pyplot as plt

def smooth(gin,gout):
	#smooth gin
	m1=np.mean(gin[1:])
	gin[0]=m1
	#smooth gout
	median=np.median(gout)
	std=np.std(gout)
	cond=np.logical_and(gout>=median-std,gout<=median+std)
	valid=gout[np.where(cond)]
	m2,std=np.mean(valid),np.std(valid)
	for i in range(len(gin)):
		if gout[i]<m2-std or gout[i]>m2+std:
			gout[i]=m2
		else:
			break
	gin=np.full(gin.shape,np.mean(gin))
	gout=np.full(gout.shape,np.mean(gout))
	return gin,gout

dag_send={}
dag_recv={}
dag_gin={}
dag_gout={}
user_send={}
user_recv={}
user_gin={}
user_gout={}

delta=lambda x:x[1:]-x[:-1]
for rate in range(0,901,100):
	send,recv=np.loadtxt('data/dagin-{}.txt'.format(rate)), np.loadtxt('data/dagout-{}.txt'.format(rate))
	offset=send[0]
	send=((send-offset)*1e6).astype(np.int32)
	recv=((recv-offset)*1e6).astype(np.int32)
	user_data=np.loadtxt('data/dag-{}.txt'.format(rate))
	user_data=((user_data-user_data[0,0])*1e6).astype(np.int32)
	dag_send[rate]=send
	dag_recv[rate]=recv
	user_send[rate]=user_data[:,0]
	user_recv[rate]=user_data[:,1]
	user_gin[rate]=delta(user_send[rate])
	user_gout[rate]=delta(user_recv[rate])
	dag_gin[rate]=delta(dag_send[rate])
	dag_gout[rate]=delta(dag_recv[rate])

rate=200
x=np.arange(99)
plt.figure(figsize=(10,5))
if False:
	plt.subplot(1,2,1)
	plt.scatter(x,dag_gin[rate][:99],s=1,label='dag gin')
	plt.scatter(x,user_gin[rate][:99],s=1,label='user gin')
	plt.grid()
	plt.legend()
	plt.xlabel('gap index')
	plt.ylabel('gap value(us)')

	plt.subplot(1,2,2)
	plt.scatter(x,dag_gout[rate][:99],s=1,label='dag gout')
	plt.scatter(x,user_gout[rate][:99],s=1,label='user gout')
	plt.legend()
	plt.grid()
	plt.xlabel('gap index')
	plt.ylabel('gap value(us)')
	plt.savefig('user-dag-diff.png',bbox_inches='tight')
else:
	smooth_gin,smooth_gout=smooth(user_gin[rate][:99],user_gout[rate][:99])
	plt.subplot(1,2,1)
	plt.scatter(x,dag_gin[rate][:99],s=1,label='dag gin')
	plt.scatter(x,smooth_gin,s=1,label='smooth gin')
	plt.grid()
	plt.legend()
	plt.xlabel('gap index')
	plt.ylabel('gap value(us)')

	plt.subplot(1,2,2)
	plt.scatter(x,dag_gout[rate][:99],s=1,label='dag gout')
	plt.scatter(x,smooth_gout,s=1,label='smooth gout')
	plt.legend()
	plt.grid()
	plt.xlabel('gap index')
	plt.ylabel('gap value(us)')
	
	plt.show()
	code.interact(local=dict(globals(),**locals()))