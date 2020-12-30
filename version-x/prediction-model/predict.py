'''
timestamp file format
time precision = 6
sendtime,space,recvtime for n line
python prediction-model/predict.py --file data/exp1/0.txt --ln 100 --psz 1472 --isz 1472 --interact 
'''
import argparse,code,sys
import numpy as np
# to import util
import os
o_path = os.getcwd()
sys.path.append(o_path)
import library.util as util
logFile=sys.stdout
saveFile=sys.stdout

def read(filename):
	data=np.loadtxt(filename)
	send=data[:,0]
	recv=data[:,1]
	return send,recv

def get_rate(time_second,packet_byte):
	assert(time_second>0)
	rate=packet_byte*8/(time_second*1e6)
	return rate

def linear(x1,x2,y1,y2,y):
	assert(y1!=y2)
	x=x2+(x1-x2)*(y-y2)/(y1-y2)
	return x

def getEstimate(inspect_owd,recover_index,owd_min,t1,t2,send,error=0):
	# if recover_index=-1, not fully recover
	# t1 = -1 , ret<t2
	# t2 = -1 , ret>t1
	# t1>0 and t2>0, t1<ret<t2
	L=len(inspect_owd)
	loadNumber=len(send)-L
	if recover_index==-1:
		node=L-2
		end=L-1
	else:
		node=recover_index-2
		end=recover_index-1
	while node>=0:
		for i in range(end,node,-1):
			if inspect_owd[node]==inspect_owd[i]:
				continue
			t_i=linear(send[node+loadNumber],send[i+loadNumber],inspect_owd[node],inspect_owd[i],owd_min)
			if (t1==-1 or t_i>t1-error) and (t2==-1 or t_i<t2+error):
				return True,t_i-send[0]
		node-=1
	
	return False,-1
	
def initialBoundary(send_time,recv_time,owd,load_number,packet_size):
	# load stage:
	# if owd ++, A<v, let upper_bound=vout
	# if owd ==, A>v, let lower_bound=vin
	send_rate=get_rate(send_time[load_number-1]-send_time[0],packet_size*(load_number-1))
	receive_rate=get_rate(recv_time[load_number-1]-recv_time[0],packet_size*(load_number-1))
	dowd=util.delta(owd[:load_number])
	median_dowd=np.median(dowd)
	dowd_max=owd[load_number-1]-owd[0]
	rate_change=(receive_rate-send_rate)/send_rate
	lower_bound=upper_bound=-1
	hasLowerBound=hasUpperBound=False
	# flag1: receive rate not change
	# flag2: owd not increase
	flag1=flag2=False 
	if rate_change>-0.05:
		# receive rate remains the same
		flag1=True
	else:
		flag1=False
	if dowd_max<=0:
		flag2=True
	elif dowd_max>0:
		if median_dowd>0:
			z=dowd_max/median_dowd/load_number
			if z<0.5:
				flag2=True
		elif median_dowd<=0:
			flag2=True
			logFile.write('Weird load owd\n')
	if flag1 and flag2:
		hasLowerBound=True
	elif not flag1 and not flag2:
		hasUpperBound=True
	elif flag1 and not flag2:
		logFile.write('receive rate little change, owd obvious increase\n')
	elif not flag1 and flag2:
		logFile.write('receive rate increase, owd not change\n')
	if hasLowerBound:
		lower_bound=send_rate
	elif hasUpperBound:
		upper_bound=receive_rate
	logFile.write('send rate {:.2f}, receive rate {:.2f}, rate change {:.2%}\n'.format(send_rate,receive_rate,rate_change))
	logFile.write('lower bound {:.2f}, upper bound {:.2f}\n'.format(lower_bound, upper_bound))
	return lower_bound,upper_bound

def estimate_abw(inspect_owd,inspect_rate,owd_min,load_number,packet_size,inspect_size,send_time):
	# 1. inspect owd increasing: A < v(inspect) -> U = v(inspect) -> return -1,-1,U
	# 2. inspect owd decreasing & not recovered -> L=v(inspect) U=P/tmax -> return E,L,U
	# 3. inspect owd decreasing & recovered -> L=P/tmax, U=P/tmin -> return E,L,U

	# owd increasing
	if inspect_owd[-1]>=inspect_owd[0]:
		inspect_upper_bound=inspect_rate
		logFile.write('inspect owd increasing, upper bound {:.2f}\n'.format(inspect_upper_bound))
		return -1,-1,inspect_upper_bound
	# 'recovered': the first time owd is 5% around min owd
	fully_recover,fully_recover_index=util.findRecoverIndex(inspect_owd,owd_min,logFile,0.05)
	if fully_recover:
		timeLowerBoundary=send_time[load_number+fully_recover_index-1]
		timeUpperBoundary=send_time[load_number+fully_recover_index]
		permissibleError=(timeUpperBoundary-timeLowerBoundary)*0.6
		abwLowerBoundary=util.roughAbw(load_number,fully_recover_index+1,timeUpperBoundary,packet_size,inspect_size)
		abwUpperBoundary=util.roughAbw(load_number,fully_recover_index,timeLowerBoundary,packet_size,inspect_size)
		assert(abwLowerBoundary<abwUpperBoundary)
		canEstimate=fully_recover_index>2
		if canEstimate:
			ret,timeEstimate=getEstimate(inspect_owd,fully_recover_index,owd_min,timeLowerBoundary,timeUpperBoundary,send_time,permissibleError)
			#code.interact(local=dict(globals(),**locals()))
			if ret:
				abwEstimate=util.roughAbw(load_number,fully_recover_index,timeEstimate,packet_size,inspect_size)
				logFile.write('inspect owd recovered t:{:.6f}<{:.6f}<{:.6f}, a:{:.2f}<{:.2f}<{:.2f}\n'.format(timeLowerBoundary,timeEstimate,timeUpperBoundary,abwLowerBoundary,abwEstimate,abwUpperBoundary))
				return abwEstimate,abwLowerBoundary,abwUpperBoundary
			else:
				logFile.write('inspect owd recovered no valid estimation. t:{:.6f}<{:.6f}, a:{:.2f}<{:.2f}\n'.format(timeLowerBoundary,timeUpperBoundary,abwLowerBoundary,abwUpperBoundary))
				return -1,abwLowerBoundary,abwUpperBoundary
		else:
			logFile.write('inspect owd recovered {:d}. t:{:.6f}<{:.6f}, a:{:.2f}<{:.2f}\n'.format(fully_recover_index,timeLowerBoundary,timeUpperBoundary,abwLowerBoundary,abwUpperBoundary))
			return -1,abwLowerBoundary,abwUpperBoundary
	elif not fully_recover:	
		abwLowerBoundary=inspect_rate
		abwUpperBoundary=util.roughAbw(load_number,len(inspect_owd),send_time[-1],packet_size,inspect_size)
		ret,timeEstimate=getEstimate(inspect_owd,-1,owd_min,send_time[-1],-1,send_time)
		if ret:
			abwEstimate=util.roughAbw(load_number,len(inspect_owd),timeEstimate,packet_size,inspect_size)
			logFile.write('inspect owd not recovered t:{:.6f}<{:.6f}, a:{:.2f}<{:.2f}<{:.2f}\n'.format(send_time[-1],timeEstimate,abwLowerBoundary,abwEstimate,abwUpperBoundary))
			return abwEstimate,abwLowerBoundary,abwUpperBoundary
		else:
			logFile.write('inspect owd not recovered t:>{:.6f}, a:{:.6f}<{:.2f}\n'.format(send_time[-1],abwLowerBoundary,abwUpperBoundary))
			return -1,abwLowerBoundary,abwUpperBoundary
def safe_exit(code):
	if logFile!=sys.stdout:
		logFile.close()
	if saveFile!=sys.stdout:
		saveFile.close()
	exit(code)

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='parser')
	parser.add_argument('--file', type=str)
	parser.add_argument('--ln', help='load packet number', type=int, default=100)
	parser.add_argument('--psz',help='load packet size',default=1472,type=int)
	parser.add_argument('--isz',help='inspect packet size',default=24,type=int)
	parser.add_argument('--log',help='log filename(append mode)',default='',type=str)
	parser.add_argument('--output',help='output filename(append mode)',default='',type=str)
	parser.add_argument('--interact', action='store_true')
	args = parser.parse_args()
	load_number=args.ln
	packet_size=args.psz
	inspect_size=args.isz
	if args.log!='':
		logFile=open(args.log,'a')
	if args.output!='':
		saveFile=open(args.output,'a')

	if os.path.isfile(args.file):
		send,recv=read(args.file)
	else:
		logFile.write('file {} not exist\n'.format(args.file))
		safe_exit(-1)
	inspect_number=len(send)-load_number
	if inspect_number<0:
		logFile.write('load number {}, inspect number {} < 0\n'.format(load_number,inspect_number))
		safe_exit(-1)
	send,recv=util.smooth(send,recv,load_number)
	send,recv,owd=util.remove_offset(send,recv)
	owd_min=np.min(owd)
	inspect_rate=get_rate(send[-1]-send[load_number],(inspect_number-1)*inspect_size)
	inspect_owd=owd[load_number:]
	lowerBoundary,upperBoundary=initialBoundary(send,recv,owd,load_number,packet_size)
	E,L,U=estimate_abw(inspect_owd,inspect_rate,owd_min,load_number,packet_size,inspect_size,send)
	L=max(lowerBoundary,L)
	if upperBoundary!=-1 and U!=-1:
		U=min(upperBoundary,U)
	elif upperBoundary==-1 and U!=-1:
		U=U
	elif upperBoundary!=-1 and U==-1:
		U=upperBoundary
	saveFile.write('E {:.2f} L {:.2f} U {:.2f}\n'.format(E,L,U))
	safe_exit(0)

