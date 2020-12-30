# 需要使用相同的load number/inspect number
# read file array
# plot them in one figure by (width)
# raw does not smooth data
# usage 1: show one raw 
# python analyse-tools/multi-plot.py --file data/0.txt --raw --show-image
# usage 2: compare raw and smooth
# python analyse-tools/multi-plot.py --file data/0.txt data/200.txt data/400.txt data/600.txt --width 4 --raw-compare --show-image
# usage 3: plot multiple 
# python analyse-tools/multi-plot.py --file data/0.txt data/100.txt data/200.txt data/300.txt data/400.txt data/500.txt data/600.txt data/700.txt data/800.txt data/900.txt --width 5 --show-image
# usage 4: save any of above figure
# python analyse-tools/multi-plot.py --file data/0.txt data/100.txt data/200.txt data/300.txt data/400.txt data/500.txt data/600.txt data/700.txt data/800.txt data/900.txt --width 5 --show-image --save-image 1.png

# python analyse-tools/multi-plot.py --file data/300.txt data/700.txt data/900.txt --width 3 --save-image 1.png

# use prefix-suffix and file-ranger to simplify input
# python analyse-tools/multi-plot.py --file-ranger 0 50 900 --prefix-suffix data/exp1/ .txt --width 6 --save-image data/exp1/all.png --raw-compare

# python analyse-tools/multi-plot.py --width 2 --file data/exp2/0.txt --raw-compare --show-image --interact
# python analyse-tools/multi-plot.py --file data/exp3/0.txt --interact --raw
import code,sys,copy
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
o_path = os.getcwd()
sys.path.append(o_path)
import library.util as util

parser = argparse.ArgumentParser(description='parser')
parser.add_argument('--file', type=str, nargs='+')
parser.add_argument('--prefix-suffix', type=str, nargs='+', help='filename prefix,suffix')
parser.add_argument('--file-ranger', type=int, nargs='+', help='begin,step,end')
parser.add_argument('--ldn', help='load number', type=int, default=100)
parser.add_argument('--show-image', action='store_true')
parser.add_argument('--raw', action='store_true')
parser.add_argument('--raw-compare', action='store_true')
parser.add_argument('--gap-out',action='store_true')
parser.add_argument('--height', help='figure subplot height', type=int, default=1)
parser.add_argument('--save-image', help='save figure filename', type=str)
parser.add_argument('--size', help='single plot size', type=int, default=5)
parser.add_argument('--interact', action='store_true')

args = parser.parse_args()

delta=lambda x:x[1:]-x[:-1]
np.set_printoptions(precision=2,suppress=True)
def stat(x):
	print('{:.2f} {:.2f} {:.2f} {:.2f}'.format(np.mean(x),np.std(x),np.min(x),np.max(x)))

def extract_name(filename:str):
	p=0
	while True:
		r=filename.find('/',p)
		if r!=-1:
			p=r+1
		else:
			break
	return filename[p:]
def get_proper_size(w,h,size):
	width=w*size
	height=h*size
	return (width,height)

x_array=[]
recv_array=[]
y_array=[]
title_array=[]
load_number=args.ldn

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
	if len(args.prefix_suffix)==1:
		prefix=args.prefix_suffix[0]
		filename_list=[prefix+middle for middle in label_list]
	else:
		prefix,suffix=args.prefix_suffix[:2]
		filename_list=[prefix+middle+suffix for middle in label_list]
else:
	filename_list=copy.copy(label_list)


for i,path in enumerate(filename_list):
	data=np.loadtxt(path)
	send,recv=data[:,0],data[:,1]
	fname=extract_name(label_list[i])
	if args.raw:
		send,recv,owd=util.remove_offset(send,recv)
		x_array.append(send)
		recv_array.append(recv)
		y_array.append(owd)
		title_array.append('raw {}'.format(fname))
	elif args.raw_compare:
		send,recv,owd=util.remove_offset(send,recv)
		x_array.append(send)
		recv_array.append(recv)
		y_array.append(owd)
		title_array.append('raw {}'.format(fname))
		send_smooth,recv_smooth=util.smooth(send,recv,load_number)
		send_smooth,recv_smooth,owd_smooth=util.remove_offset(send_smooth,recv_smooth)
		x_array.append(send_smooth)
		recv_array.append(recv_smooth)
		y_array.append(owd_smooth)
		title_array.append('smooth {}'.format(fname))
	elif args.gap_out:
		x_array.append(np.arange(len(recv)-1))
		y_array.append(delta(recv))
		title_array.append('gap out {}'.format(fname))
	else:
		send_smooth,recv_smooth=util.smooth(send,recv,load_number)
		send_smooth,recv_smooth,owd_smooth=util.remove_offset(send_smooth,recv_smooth)
		x_array.append(send_smooth)
		recv_array.append(recv_smooth)
		y_array.append(owd_smooth)
		title_array.append('smooth {}'.format(fname))

num=len(x_array)
height=args.height
width=num//height if num%height==0 else num//height+1
app_figsize=get_proper_size(width,height,args.size)
fig=plt.figure(figsize=app_figsize,tight_layout=True)
for i in range(num):
	plt.subplot(height,width,i+1)
	if not args.gap_out:
		plt.scatter(x_array[i]*1e6, y_array[i]*1e6, s=1)
		plt.xlabel('time(us)')
		plt.ylabel('one way delay(us)')
	elif args.gap_out:
		plt.scatter(x_array[i], y_array[i]*1e6, s=1)
		plt.xlabel('gap index')
		plt.ylabel('gap value(us)')
	plt.grid()
	plt.title(title_array[i])
if args.show_image:
	plt.show()
if args.save_image!=None:
	fig.savefig(args.save_image,bbox_inches='tight')

if args.interact:
	s,r=x_array[-1],recv_array[-1]
	gin,gout=delta(s)*1e6,delta(r)*1e6
	owd=r-s
	owd=owd-owd[0]
	owd=owd*1e6
	code.interact(local=dict(globals(),**locals()))