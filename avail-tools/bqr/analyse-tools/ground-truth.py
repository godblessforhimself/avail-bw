# p = 1472 * (n-1) B
# t = t[-1]-t[0]   s
# v = p / t
# v t (n-1) min(g) mean(g) std(g)
# python analyse-tools/ground-truth.py --file-ranger 0 50 900 --prefix-suffix data/ground-truth/out- .txt --statistics data/ground-truth/stat.txt --raw data/ground-truth/raw.txt --abw data/ground-truth/abw.txt
#
#
#
import code,sys,copy
import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='parser')
parser.add_argument('--file', type=str, nargs='+', help='file list, the first is used as bandwidth')
parser.add_argument('--prefix-suffix', type=str, nargs='+', help='filename prefix,suffix')
parser.add_argument('--file-ranger', type=int, nargs='+', help='begin,step,end')
parser.add_argument('--statistics', type=str, help='human readable csv file')
parser.add_argument('--raw', type=str, help='raw stat file')
parser.add_argument('--abw', type=str, help='ground truth file of available bandwidth')
parser.add_argument('--interact', action='store_true')
args = parser.parse_args()

dif=lambda x:x[1:]-x[:-1]
def time2str(t):
	# unit is second
	if t<1e-6:
		s='{:d}ns'.format(int(t*1e9))
	elif t<1e-3:
		s='{:.3f}us'.format((t*1e6))
	elif t<1:
		s='{:.3f}ms'.format((t*1e3))
	elif t>=1:
		s='{:.3f}s'.format((t))
	return s
def statistics(filename):
	tout=np.loadtxt(filename)
	n=len(tout)
	p=1472*(n-1)*8
	t=(tout[-1]-tout[0])
	v=p/t*1e-6
	gout=dif(tout)
	gmin=np.min(gout)
	gmax=np.max(gout)
	gmean=np.mean(gout)
	gstd=np.std(gout)
	return v,t,n,gmean,gstd,gmin,gmax

label_list=[]
filename_list=[]
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
	filename_list=[prefix+middle+suffix for middle in label_list]
else:
	filename_list=copy.copy(label_list)

if len(filename_list)>0:
	matrix=[]
	for file in filename_list:
		tuple_=statistics(file)
		matrix.append(tuple_)

	header='file,v,t,n,mean,std,min,max\n'
	if args.statistics:
		with open(args.statistics,'w') as f:
			f.write(header)
			for i,item in enumerate(matrix):
				v,t,n,gmean,gstd,gmin,gmax=item
				stat='{:s},{:.2f},{:s},{:d},{:s},{:s},{:s},{:s}\n'.format(label_list[i],v,time2str(t),n-1,time2str(gmean),time2str(gstd),time2str(gmin),time2str(gmax))
				f.write(stat)
	if args.raw:
		with open(args.raw,'w') as f:
			f.write(header)
			for i,item in enumerate(matrix):
				v,t,n,gmean,gstd,gmin,gmax=item
				raw='{:s},{:.2f},{:.9f},{:d},{:.9f},{:.9f},{:.9f},{:.9f}\n'.format(label_list[i],v,t,n-1,gmean,gstd,gmin,gmax)
				f.write(raw)
	if args.abw:
		with open(args.abw,'w') as f:
			for i,item in enumerate(matrix):
				v,t,n,gmean,gstd,gmin,gmax=item
				if i==0:
					s='B:{:.2f}Mbps\n'.format(v)
					B=v
				else:
					s='A[{:s}]:{:.2f}Mbps\n'.format(label_list[i],B-v)
				f.write(s)
else:
	print('lack filename')
	parser.print_help(sys.stdout)
