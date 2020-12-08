import code,sys
import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='parser')
parser.add_argument('--file', type=str)
parser.add_argument('--ldn', help='load number', type=int, default=100)
parser.add_argument('--isn', help='inspect number', type=int, default=10)
parser.add_argument('--interact', action='store_true')
parser.add_argument('--show-image', action='store_true')
parser.add_argument('--save-image', action='store_true')
args = parser.parse_args()
# cluster load packet output gap to find the average gap
def remove_suffix(s):
	idx=s.find('.')
	return s[:idx]
def smooth(send,recv,ldn):
	delta=lambda x:x[1:]-x[:-1]
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
path='data/output.txt'
if args.file:
	path=args.file
	#print(path)
data=np.loadtxt(path)
data=data*1e6
load_number=args.ldn
inspect_number=args.isn

send,recv=data[:,0],data[:,1]
send,recv=smooth(send,recv,load_number)
offset=send[0]
send-=offset
recv-=offset
send=send.astype(np.int32)
recv=recv.astype(np.int32)
owd=recv-send
oowd=owd[100:]
timestamp=(send-send[0])
if args.show_image:
	plt.figure(figsize=(10,5))
	plt.subplot(1,2,1)
	plt.scatter(timestamp,owd,s=1)
	plt.subplot(1,2,2)
	plt.scatter(timestamp[load_number:],oowd,s=1)
	plt.grid()
	plt.show()
if args.save_image:
	plt.figure(figsize=(10,5))
	plt.subplot(1,2,1)
	plt.scatter(timestamp,owd,s=1)
	plt.subplot(1,2,2)
	plt.scatter(timestamp[load_number:],oowd,s=1)
	plt.grid()
	output_filename=remove_suffix(args.file)+'.png'
	plt.savefig(output_filename,bbox_inches='tight')

if args.interact:
	code.interact(local=dict(globals(),**locals()))