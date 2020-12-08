'''
timestamp file format
time precision = 6
sendtime,space,recvtime for n line
'''
import argparse,code
import numpy as np

# tool functions
def get_rate(time_second,packet_byte):
	rate=packet_byte*8/(time_second*1e6)
	return rate
def norm(x):
	mean=np.mean(x)
	std=np.std(x)
	return (x-mean)/std
def linear(x1,x2,y1,y2,y):
	if y1==y2:
		return None
	x=x2+(x1-x2)*(y-y2)/(y1-y2)
	return x
def non_zero(*arr):
	for i in arr:
		if i!=0:
			return i
	return None
def estimate_abw():
	# extreme cases:
	# 1. inspect owd is increasing caused by abw < inspect rate. So upper bound = inspect rate.
	# 2. inspect owd is decreasing but not fully recovered. So use last two points to estimate recover time
	# 3. inspect owd is decreasing and fully recovered. So find the index that fully recovered, and use last two before the index
	# connect every two point, get the recover time
	# sort it to get upper and lower bound
	# use the last two point as result
	global load_number,inspect_number,inspect_owd,send_time,packet_size,recover_time,owd_min,inspect_upper_bound
	if inspect_owd[-1]/inspect_owd[0]>=1:
		# owd increasing
		inspect_upper_bound=inspect_rate
		print('inspect upper bound {:.2f}'.format(inspect_upper_bound))
		return -1
	# we define 'fully recover' as owd is 5% around min owd
	fully_recover=False
	if owd_min<inspect_owd[0]:
		owd_decrease=inspect_owd[0]-owd_min
		bound=0.05*owd_decrease
		if owd_min-bound<=inspect_owd[-1] and inspect_owd[-1]<=owd_min+bound:
			fully_recover=True
			fully_recover_index=inspect_number-1
			while inspect_owd[fully_recover_index]<=owd_min+bound:
				fully_recover_index-=1
				if fully_recover_index==0: 
					print('owd increase not obvious')
					break
	
	if not fully_recover:	
		consider_count=inspect_number
	elif fully_recover:
		recover_time_upper_bound=send_time[load_number+fully_recover_index+1]-send_time[0]
		recover_time_lower_bound=send_time[load_number+fully_recover_index]-send_time[0]
		if fully_recover_index==0:
			print('only one point, use second point as time')
			recover_time=send_time[load_number+1]-send_time[0]
			return recover_time
		consider_count=fully_recover_index+1
	recover_time=np.zeros((consider_count,consider_count))
	for i in range(consider_count):
		for j in range(consider_count):
			if i>=j: continue
			temp=linear(send_time[load_number+i],send_time[load_number+j],inspect_owd[i],inspect_owd[j],owd_min)
			recover_time[i,j]=0 if temp is None else temp
	recover_time=np.where(recover_time>0,recover_time-send_time[0],0)
	recover_time_sorted=np.sort(recover_time,axis=None)
	min_recover_time=recover_time_sorted[0]
	max_recover_time=recover_time_sorted[-1]
	last_recover_time=recover_time[-2,-1]
	long_recover_time=recover_time[0,-1]
	positive_recover_time=non_zero(last_recover_time,long_recover_time,min_recover_time,max_recover_time)
	if positive_recover_time<=0:
		return -1
	if fully_recover:
		packet_byte=load_number*packet_size+(fully_recover_index+1)*inspect_size
		abw_lb=get_rate(recover_time_upper_bound,packet_byte)
		abw_ub=get_rate(recover_time_lower_bound,packet_byte)
		print('recover[lower bound {:.2f}, upper bound {:.2f}]'.format(abw_lb,abw_ub))
	else:
		packet_byte=load_number*packet_size + inspect_number*inspect_size
	#if fully_recover and (positive_recover_time>recover_time_upper_bound or positive_recover_time < recover_time_lower_bound):
	#	return -1
	code.interact(local=dict(globals(),**locals()))
	abw=get_rate(positive_recover_time,packet_byte)
	return abw
# tool end
# global declaration
args=0
load_number=0
packet_size=0
send_time=0
recv_time=0
owd=0
inspect_owd=0
inspect_number=0
inspect_upper_bound=0
inspect_rate=0
send_rate=0
receive_rate=0
rate_change=0
lower_bound=0
upper_bound=0
owd_min=0
inspect_size=0
# global end
def parse():
	global args,load_number,packet_size,inspect_size
	parser = argparse.ArgumentParser(description='parser')
	parser.add_argument('--file', type=str)
	parser.add_argument('--ln', help='load packet number', type=int, default=100)
	parser.add_argument('--psz',help='load packet size',default=1472,type=int)
	parser.add_argument('--isz',help='inspect packet size',default=24,type=int)
	parser.add_argument('--interact', action='store_true')
	args = parser.parse_args()
	load_number=args.ln
	packet_size=args.psz
	inspect_size=args.isz
	print('Predict at {}'.format(args.file))

def read():
	global send_time,recv_time,inspect_number,owd,inspect_owd,inspect_rate
	try:
		timestamp=np.loadtxt(args.file)
	except:
		print('file not found')
		exit(0)
	else:
		pass
	send_time=timestamp[:,0]
	recv_time=timestamp[:,1]
	owd=recv_time-send_time
	inspect_number=len(send_time)-load_number
	inspect_rate=get_rate(send_time[-1]-send_time[load_number],(inspect_number-1)*packet_size)
	if inspect_number<0:
		print('inspect number {}'.format(inspect_number))
		exit(0)
	inspect_owd=owd[load_number:]
	
def smooth():
	global send_time,recv_time,load_number
	send,recv,ldn=send_time,recv_time,load_number
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
	send_time,recv_time=send,recv
def upper_bound():
	global send_rate,receive_rate,rate_change,lower_bound,upper_bound
	send_rate=get_rate(send_time[load_number-1]-send_time[0],packet_size*(load_number-1))
	receive_rate=get_rate(recv_time[load_number-1]-recv_time[0],packet_size*(load_number-1))
	rate_change=(receive_rate-send_rate)/send_rate
	if rate_change>-0.05:
		lower_bound=send_rate
		upper_bound=0
	else:
		upper_bound=receive_rate
		lower_bound=0
	print('send rate {:.2f}, receive rate {:.2f}, rate change {:.2%}'.format(send_rate,receive_rate,rate_change))
	print('lower bound {:.2f}, upper bound {:.2f}'.format(lower_bound, upper_bound))
def cluster_or_min():
	global owd_min
	owd_min=np.min(owd)
def locate_or_guess():
	abw=estimate_abw()
	if abw>0:
		print('abw {:.2f}'.format(abw))
	
def main():
	parse()
	read()
	smooth()
	upper_bound()
	cluster_or_min()
	locate_or_guess()

if __name__=='__main__':
	main()