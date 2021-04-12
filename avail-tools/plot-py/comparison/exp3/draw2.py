# 实验3：BQR恢复的数量
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code
x=[900,900,900,900,0,400,400,0,0,0,400,400,400]
y=[0,0,0,20,0,0,20,0,20,40,0,20,40]
z=[0,400,900,900,900,900,900,0,0,0,400,400,400]
dirname='/data/comparison/exp3/{}-{}-{}/{}'
method='BQR'
N=len(x)
Capacity1=957.14
Capacity2=95.71
Discard=10
if __name__=='__main__':
	abwNumber=[]
	for i in range(N):
		prefix=dirname.format(x[i],y[i],z[i],method)
		abwfile='{}/abw'.format(prefix)
		A=np.loadtxt(abwfile)
		abwNumber.append(len(A))
	columns=['{}-{}-{}'.format(x[i],y[i],z[i]) for i in range(N)]
	abwNumber=np.array(abwNumber)
	df=pd.DataFrame(abwNumber[np.newaxis,:],columns=columns)
	df.to_csv('/data/comparison/exp3-csv/exp3-validNumber.csv',float_format='%.0f',index=False)
	#code.interact(local=dict(globals(),**locals()))
	