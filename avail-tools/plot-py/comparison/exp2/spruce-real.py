# 使用DAG的数据为spruce生成预测abw
# 背景流量T=(gout/gin-1)C
# 可用带宽A=C-(gout/gin-1)C=(2-gout/gin)C
# r=gout/gin
# /data/comparison/exp2/
import copy,code,os,time
import numpy as np
fin='/data/comparison/exp2/{}-{}-{}/spruce/dag.in'
fout='/data/comparison/exp2/{}-{}-{}/spruce/dag.out'
fwrite='/data/comparison/exp2/{}-{}-{}/spruce/abw'
rates=range(0,500+1,100)
x=[600]*len(rates)
x.extend(rates)
y=[i for i in rates]
y.extend([600]*len(rates))
z=2*len(rates)*[0]
N=len(x)
Capacity=957.14
Discard1=10
if __name__=='__main__':
	begin=time.time()
	gins=[]
	gouts=[]
	ratios=[]
	truth=[]
	for i in range(N):
		truth.append(max(x[i],y[i],z[i]))
	truth=np.array(truth)
	for i in range(len(x)):
		f1=fin.format(x[i],y[i],z[i])
		f2=fout.format(x[i],y[i],z[i])
		if not os.path.exists(f1):
			continue
		t1=np.loadtxt(f1)[:,0].reshape((100,200))
		t2=np.loadtxt(f2)[:,0].reshape((100,200))
		gin=t1[:,1::2]-t1[:,::2]
		gout=t2[:,1::2]-t2[:,::2]
		gins.append(gin)
		gouts.append(gout)
		r=gout/gin
		ratios.append(r)
	ratios=np.array(ratios)
	# （实验次数，100，100）
	# 舍去r小于1的部分
	# 取80%
	ratios.sort(2)
	if Discard1>0:
		ratios=ratios[:,:,Discard1:-Discard1]
	ratios=np.mean(ratios,2)
	traffics=(ratios-1)*Capacity
	traffics.sort(1)
	end=time.time()
	for i in range(len(x)):
		f=fwrite.format(x[i],y[i],z[i])
		np.savetxt(f,Capacity-traffics[i,:],fmt='%.2f')
	print('use {:.2f} s'.format(end-begin))
	#code.interact(local=dict(globals(),**locals()))