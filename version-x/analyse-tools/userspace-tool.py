import code,sys
import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='parser')
parser.add_argument('--file', type=str)
parser.add_argument('--interact', action='store_true')
parser.add_argument('--show-image', action='store_true')
parser.add_argument('--save-image', action='store_true')
args = parser.parse_args()
# cluster load packet output gap to find the average gap
def remove_suffix(s):
	idx=s.find('.')
	return s[:idx]
def smooth(x,thres=10):
	# x[0]>thres
	# x[k]>thres
	# x[0]<thres x[k]>thres
	ret=np.zeros(x.shape,dtype=x.dtype)
	if x[0]<thres:
		pass
	return ret
	
path='data/output.txt'
if args.file:
	path=args.file
	#print(path)
data=np.loadtxt(path)
data=data*1e6
load_number=100
inspect_number=data.shape[0]-load_number
if False:
	load_send=data[:load_number,0]
	load_receive=data[:load_number,1]
	load_send=smooth(load_send)
	load_receive=smooth(load_receive)
	data[:load_number,0]=load_send
	data[:load_number,1]=load_receive

def diff(x):
	return x[1:]-x[:-1]

gin=diff(data[:,0])
gout=diff(data[:,1])
owd=data[:,1]-data[:,0]
oowd=owd[100:]
timestamp=(data[:,0]-data[0,0])
if args.show_image:
	plt.scatter(timestamp, owd, s=1)
	plt.grid()
	plt.show()
if args.save_image:
	plt.figure(figsize=(10,5))
	plt.subplot(1,2,1)
	plt.scatter(timestamp,owd,s=1)
	plt.subplot(1,2,2)
	plt.scatter(timestamp[load_number:],oowd,s=1)
	plt.grid()
	#plt.ylim((owdd.min()-1,owdd.max()+1))
	output_filename=remove_suffix(args.file)+'.png'
	plt.savefig(output_filename,bbox_inches='tight')
if False:
	plt.subplot(2,2,1)
	plt.plot(gin)
	plt.subplot(2,2,2)
	plt.plot(gout)
	plt.subplot(2,2,3)
	plt.plot(owd)
	plt.show()

array=[gin.mean(),gin.std(),gout.mean(),gout.std()]
if False:
	print('gin  {:.2f},{:.2f}\ngout {:.2f},{:.2f}\n'.format(*array))

if args.interact:
	code.interact(local=dict(globals(),**locals()))