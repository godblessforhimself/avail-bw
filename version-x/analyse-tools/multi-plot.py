# 需要使用相同的load number/inspect number
# read file array
# plot them in one figure by (width)
# raw does not smooth data
# usage 1: show one raw 
# python analyse-tools/multi-plot.py --file data/0.txt --raw --show-image
# usage 2: compare raw and smooth
# python analyse-tools/multi-plot.py --file data/0.txt --width 2 --raw-compare --show-image
# usage 3: plot multiple 
# python analyse-tools/multi-plot.py --file data/0.txt data/100.txt data/200.txt data/300.txt data/400.txt data/500.txt data/600.txt data/700.txt data/800.txt data/900.txt --width 5 --show-image
# usage 4: save any of above figure
# python analyse-tools/multi-plot.py --file data/0.txt data/100.txt data/200.txt data/300.txt data/400.txt data/500.txt data/600.txt data/700.txt data/800.txt data/900.txt --width 5 --show-image --save-image data/0.png
import code,sys
import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='parser')
parser.add_argument('--file', type=str, nargs='+')
parser.add_argument('--ldn', help='load number', type=int, default=100)
parser.add_argument('--isn', help='inspect number', type=int, default=10)
parser.add_argument('--show-image', action='store_true')
parser.add_argument('--raw', action='store_true')
parser.add_argument('--raw-compare', action='store_true')
parser.add_argument('--width', help='figure subplot width', type=int, default=1)
parser.add_argument('--save-image', help='save figure filename', type=str)
parser.add_argument('--size', help='single plot size', type=int, default=5)
parser.add_argument('--interact', action='store_true')

args = parser.parse_args()

delta=lambda x:x[1:]-x[:-1]
def smooth(send,recv,ldn):
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
def remove_offset(send,recv):
	offset=send[0]
	send-=offset
	recv-=offset
	send=send.astype(np.int32)
	recv=recv.astype(np.int32)
	owd=recv-send
	owd=owd-np.min(owd)
	return send,recv,owd
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

send_array=[]
recv_array=[]
owd_array=[]
title_array=[]
load_number=args.ldn
inspect_number=args.isn
for path in args.file:
	data=np.loadtxt(path)*1e6
	send,recv=data[:,0],data[:,1]
	fname=extract_name(path)
	if args.raw:
		send,recv,owd=remove_offset(send,recv)
		send_array.append(send)
		recv_array.append(recv)
		owd_array.append(owd)
		title_array.append('raw {}'.format(fname))
	elif args.raw_compare:
		send,recv,owd=remove_offset(send,recv)
		send_array.append(send)
		recv_array.append(recv)
		owd_array.append(owd)
		title_array.append('raw {}'.format(fname))
		send_smooth,recv_smooth=smooth(send,recv,load_number)
		send_smooth,recv_smooth,owd_smooth=remove_offset(send_smooth,recv_smooth)
		send_array.append(send_smooth)
		recv_array.append(recv_smooth)
		owd_array.append(owd_smooth)
		title_array.append('smooth {}'.format(fname))
	else:
		send_smooth,recv_smooth=smooth(send,recv,load_number)
		send_smooth,recv_smooth,owd_smooth=remove_offset(send_smooth,recv_smooth)
		send_array.append(send_smooth)
		recv_array.append(recv_smooth)
		owd_array.append(owd_smooth)
		title_array.append('smooth {}'.format(fname))
num=len(send_array)
width=args.width
height=num//width if num%width==0 else num//width+1
app_figsize=get_proper_size(width,height,args.size)
fig=plt.figure(figsize=app_figsize,tight_layout=True)
for i in range(num):
	plt.subplot(height,width,i+1)
	plt.scatter(send_array[i], owd_array[i], s=1)
	plt.grid()
	plt.xlabel('time(us)')
	plt.ylabel('one way delay(us)')
	plt.title(title_array[i])
if args.show_image:
	plt.show()
if args.save_image!=None:
	fig.savefig(args.save_image,bbox_inches='tight')

if args.interact:
	code.interact(local=dict(globals(),**locals()))