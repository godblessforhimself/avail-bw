import code,argparse,sys,os
import numpy as np
import matplotlib.pyplot as plt
delta=lambda x:x[1:]-x[:-1]
def cdf(x, plot=True, *args, **kwargs):
	x, y = sorted(x), np.arange(len(x)) / len(x)
	return plt.plot(x, y, *args, **kwargs) if plot else (x, y)
def doInspect(filename):
	data=np.loadtxt(filename)
	time=data[:,0]
	gap=delta(time)
	cs=cluster(gap,0.5,2)
	means=[np.mean(gap[cs[i,0]:cs[i,1]+1]) for i in range(len(cs))]
	means=np.array(means)
	code.interact(local=dict(globals(),**locals()))
def cluster(gap,th1,th2):
	# return [[begin,end]]
	L=len(gap)
	ret=[]
	i=begin=0
	while i<L:
		if i==0:
			i+=1
		else:
			r=gap[i]/gap[i-1]
			normal=r<th2 and r>th1
			if not normal:
				end=i-1
				ret.append([begin,end])
				if i<L-1:
					begin=i
				else:
					ret.append([i,i])
			else:
				if i==L-1:
					ret.append([begin,i])
			i+=1
	return np.array(ret)

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='parser')
	parser.add_argument('--file', type=str, nargs='+', help='filename list')
	args=parser.parse_args()
	if args.file:
		for file in args.file:
			doInspect(file)