#
# input: old param, (send-i,recv-i)n
# output: new param, metrics for old param
# usage 1:
# python suggestion-model/suggest.py --data data/700.txt --old-param deploy-tools/sender-bak.sh --new-param deploy-tools/sender.sh --metric data/metric
import code,sys,argparse,time
import numpy as np
import matplotlib.pyplot as plt
# to import util
import os
o_path = os.getcwd()
sys.path.append(o_path)
import library.util as util

prefix='taskset -c 23 ./send-main'

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
	parser.add_argument('--inspect', help='inspect packet time', nargs='+',type=float)
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
	recoverDegree=(owd[load_number]-owd[-1])/(np.max(owd)-np.min(owd))
	metric_dic['RD']=recoverDegree
	return metric_dic

def write_metric(metric, filename):
	with open(filename,'a') as f:
		time_line=time.strftime("%Y-%m-%d %H:%M:%S\n", time.localtime())
		f.write(time_line)
		f.write('Recover Degree: {:.2f}\n'.format(metric['RD']))

def write_new_param(param,filename):
	inspect_array=[int(param['begin_time']+i*param['inspect_gap']) for i in range(param['inspect_number'])]
	inspect_array=[str(i) for i in inspect_array]
	inspect_string=' '.join(inspect_array)
	with open(filename,'w') as f:
		f.write('{} --speed {:.2f} --load-size {:d} --inspect-size {:d} --dest {} --port {:d} --number {:d} --inspect {}'.format(prefix, param['speed'], param['load_size'], param['inspect_size'], param['dest'], param['port'], param['load_number'], inspect_string))

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='parser')
	parser.add_argument('--old-param', help='old parameter', type=str)
	parser.add_argument('--data', help='data filename', type=str)
	parser.add_argument('--new-param', help='new parameter', type=str)
	parser.add_argument('--metric', help='metric filename, append', type=str)
	parser.add_argument('--inspect-max', help='max inspect gap limit(us)', type=int, default=5e3)
	parser.add_argument('--inspect-min', help='min inspect gap limit(us)', type=int, default=120)
	parser.add_argument('--interact', help='enter interactive mode', action='store_true')
	args = parser.parse_args()

	gapMax=args.inspect_max
	gapMin=args.inspect_min
	satisfied=False
	if args.old_param:
		param=parse_param(args.old_param)
		loadNumber=param['load_number']
		inspectNumber=param['inspect_number']
		oldGap=param['inspect_gap']
		if args.data:
			raw_data=np.loadtxt(args.data)*1e6
			send,recv,owd=process(raw_data,param)
			inspectOwd=owd[loadNumber:]
			owdMin=np.min(owd)
			metric_dic=get_metric(send,recv,owd,param)
			if args.metric:
				write_metric(metric_dic, args.metric)
			recovered,recoverIndex=util.findRecoverIndex(inspectOwd,owdMin,None)
			recoverDegree=metric_dic['RD']
			if not recovered:
				# obvious trend
				if recoverDegree>0.15:
					new_inspect_gap=min(int(oldGap/recoverDegree)*2+1,gapMax)
				# vague trend
				elif recoverDegree<=0.15:
					new_inspect_gap=min(oldGap*2,gapMax)
			elif recovered:
				lowerBoundary=np.ceil(0.2*inspectNumber)
				upperBoundary=np.floor(0.7*inspectNumber)
				if recoverIndex>lowerBoundary and recoverIndex<upperBoundary:
					new_inspect_gap=oldGap
					satisfied=True
				elif recoverIndex<=lowerBoundary:
					new_inspect_gap=max(oldGap//2,gapMin)
				elif recoverIndex>=upperBoundary:
					new_inspect_gap=min(oldGap*2,gapMax)

			print('Gap adjust:{}->{}'.format(oldGap, new_inspect_gap))
			param['inspect_gap']=int(new_inspect_gap)
			if args.new_param:
				write_new_param(param,args.new_param)
	if args.interact:
		code.interact(local=dict(globals(),**locals()))

	if satisfied:
		exit(0)
	else:
		exit(1)