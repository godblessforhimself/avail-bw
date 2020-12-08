#
# input: old param, (send-i,recv-i)n
# output: new param, metrics for old param
# usage 1:
# python suggestion-model/suggest.py --data data/700.txt --old-param deploy-tools/sender-bak.sh --new-param deploy-tools/sender.sh --metric data/metric
import code,sys,argparse,time,os
import numpy as np
import matplotlib.pyplot as plt
o_path = os.getcwd()
sys.path.append(o_path)
import library.util as util

def parse_param(filename):
	with open(filename,'r') as f:
		cmdline=f.read()
	# Error process
	keyword='./send-main'
	begin=cmdline.find(keyword)
	cmdline=cmdline[begin+len(keyword)+1:]
	cmdline=cmdline.split(' ')
	parser = argparse.ArgumentParser(description='send parameter parser')
	parser.add_argument('--speed', help='load packet rate', type=float)
	parser.add_argument('--load-size', help='load packet size', type=int)
	parser.add_argument('--inspect-size', help='inspect packet size', type=int)
	parser.add_argument('--number', help='load packet number', type=int)
	parser.add_argument('--dest', help='IP destination', type=str)
	parser.add_argument('--port', help='destination port', type=int)
	parser.add_argument('--inspect', help='inspect packet time', nargs='+',type=int)
	args=parser.parse_args(cmdline)
	l=args.inspect
	inspect_number=len(l)
	inspect_gap=l[1]-l[0]
	begin_time=l[0]
	param={
		'speed':args.speed,
		'load_size':args.load_size,
		'inspect_size':args.inspect_size,
		'load_number':args.number,
		'inspect_number':inspect_number,
		'inspect_gap':inspect_gap,
		'begin_time':begin_time,
		'dest':args.dest,
		'port':args.port,
	}
	return param

def process(raw_data,param):
	send,recv=raw_data[:,0],raw_data[:,1]
	send,recv=util.smooth(send,recv,param['load_number'])
	send,recv,owd=util.remove_offset(send,recv)
	return send,recv,owd

def get_metric(send,recv,owd,param):
	metric_dic={}
	load_number=param['load_number']
	inspect_number=param['inspect_number']
	RD=(owd[load_number]-owd[-1])/(np.max(owd)-np.min(owd))
	print(RD)
	metric_dic['RD']=RD
	return metric_dic

def write_metric(metric, filename):
	with open(filename,'a') as f:
		time_line=time.strftime("%Y-%m-%d %H:%M:%S\n", time.localtime())
		f.write(time_line)
		f.write('Recover Degree: {:.2f}\n'.format(metric['RD']))

prefix='taskset -c 3 ./send-main'
def write_new_param(param,filename):
	inspect_array=[int(param['begin_time'])+i*param['inspect_gap'] for i in range(param['inspect_number'])]
	inspect_array=[str(i) for i in inspect_array]
	inspect_string=' '.join(inspect_array)
	with open(filename,'w') as f:
		f.write('{} --speed {:.2f} --load-size {:d} --inspect-size {:d} --dest {} --port {:d} --number {:d} --inspect {}'.format(prefix, param['speed'], param['load_size'], param['inspect_size'], param['dest'], param['port'], param['load_number'], inspect_string))

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='parser')
	parser.add_argument('--old-param', help='old parameter ', type=str)
	parser.add_argument('--data', help='data filename', type=str)
	parser.add_argument('--new-param', help='new parameter', type=str)
	parser.add_argument('--metric', help='metric filename', type=str)
	parser.add_argument('--interact', help='enter interactive mode', action='store_true')
	args = parser.parse_args()
	if args.old_param:
		param=parse_param(args.old_param)
		if args.data:
			raw_data=np.loadtxt(args.data)*1e6
			send,recv,owd=process(raw_data,param)
			metric_dic=get_metric(send,recv,owd,param)
			if args.metric:
				write_metric(metric_dic, args.metric)
			RD=metric_dic['RD']
			if RD<0.95 and RD>0:
				new_inspect_gap=int(param['inspect_gap']/metric_dic['RD'])+1
			else:
				new_inspect_gap=param['inspect_gap']
				pass
			print('{}->{}'.format(param['inspect_gap'], new_inspect_gap))
			param['inspect_gap']=new_inspect_gap
			if args.new_param:
				write_new_param(param,args.new_param)
	if args.interact:
		code.interact(local=dict(globals(),**locals()))