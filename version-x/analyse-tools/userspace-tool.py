import code,sys
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
o_path = os.getcwd()
sys.path.append(o_path)
import library.util as util
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

path='data/output.txt'
if args.file:
	path=args.file
	#print(path)
data=np.loadtxt(path)
data=data*1e6
load_number=args.ldn
inspect_number=args.isn

send,recv=data[:,0],data[:,1]
send,recv=util.smooth(send,recv,load_number)
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