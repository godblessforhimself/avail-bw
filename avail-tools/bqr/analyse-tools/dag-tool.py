# python analyse-tools/dag-tool.py --file 0 --prefix-suffix data/exp3/ .txt --in-out in- out- --interact
import code,sys,copy
import numpy as np
import matplotlib.pyplot as plt
import argparse

np.set_printoptions(precision=2,suppress=True)
def stat(x):
	print('{:.2f} {:.2f} {:.2f} {:.2f}'.format(np.mean(x),np.std(x),np.min(x),np.max(x)))
	
parser = argparse.ArgumentParser(description='parser')
parser.add_argument('--file', type=str, nargs='+', help='file list, the first is used as bandwidth')
parser.add_argument('--prefix-suffix', type=str, nargs='+', help='filename prefix,suffix')
parser.add_argument('--in-out', type=str, nargs='+', help='in prefix,out prefix')
parser.add_argument('--file-ranger', type=int, nargs='+', help='begin,step,end')
parser.add_argument('--interact', action='store_true')
args = parser.parse_args()
if not args.in_out:
	parser.print_help(sys.stdout)
	exit(0)
in_prefix,out_prefix=args.in_out[:2]
label_list=[]
fin_list=[]
fout_list=[]
if args.file:
	label_list=copy.copy(args.file)
elif args.file_ranger:
	begin,step,end=args.file_ranger[:3]
	label_list=[str(i) for i in range(begin,end+1,step)]
else:
	parser.print_help(sys.stdout)
	exit(0)
if args.prefix_suffix:
	prefix,suffix=args.prefix_suffix[:2]
	fin_list=[prefix+in_prefix+middle+suffix for middle in label_list]
	fout_list=[prefix+out_prefix+middle+suffix for middle in label_list]
else:
	fin_list=[in_prefix+middle for middle in label_list]
	fout_list=[out_prefix+middle for middle in label_list]
N=len(label_list)

diff=lambda x:x[1:]-x[:-1]

def read(fin,fout,scale=1):
	s,r=np.loadtxt(fin)*scale,np.loadtxt(fout)*scale
	gin,gout=diff(s),diff(r)
	owd=r-s
	return s,r,owd,gin,gout

for i in range(N):
	s,r,owd,gin,gout=read(fin_list[i],fout_list[i],1)
	owd=owd*1e6
	gin=gin*1e6
	gout=gout*1e6
	if args.interact:
		code.interact(local=dict(globals(),**locals()))