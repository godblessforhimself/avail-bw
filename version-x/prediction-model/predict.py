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
send_rate=0
receive_rate=0
rate_change=0
lower_bound=0
upper_bound=0
owd_min=0
# global end
def parse():
	global args,load_number,packet_size
	parser = argparse.ArgumentParser(description='parser')
	parser.add_argument('--file', type=str)
	parser.add_argument('--ln', help='load packet number', type=int, default=100)
	parser.add_argument('--psz',help='load packet size',default=1472,type=int)
	parser.add_argument('--interact', action='store_true')
	args = parser.parse_args()
	load_number=args.ln
	packet_size=args.psz
def read():
	global send_time,recv_time,inspect_number,owd,inspect_owd
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
	if inspect_number<0:
		print('inspect number {}'.format(inspect_number))
		exit(0)
	inspect_owd=owd[load_number:]
	
def smooth():

	pass
def upper_bound():
	global send_rate,receive_rate,rate_change,lower_bound,upper_bound
	send_rate=get_rate(send_time[load_number-1]-send_time[0],packet_size*(load_number-1))
	receive_rate=get_rate(recv_time[load_number-1]-recv_time[0],packet_size*(load_number-1))
	rate_change=(receive_rate-send_rate)/send_rate
	print('send rate {:.2f}Mbps, receive rate {:.2f}Mbps, rate change {:.2f}'.format(send_rate,receive_rate,rate_change))
	if rate_change>-0.05:
		lower_bound=send_rate
		upper_bound=0
	else:
		upper_bound=receive_rate
		lower_bound=0
	print('lower bound {:.2f}, upper bound {:.2f}'.format(lower_bound, upper_bound))
def cluster_or_min():
	global owd_min
	owd_min=np.min(owd)
def locate_or_guess():
	decrease_trend=get_trend()
	if decrease_trend>0:
		upper_bound=0
	else:
		recover_time=0
	pass
def main():
	parse()
	read()
	smooth()
	upper_bound()
	cluster_or_min()
	locate_or_guess()

if __name__=='__main__':
	main()