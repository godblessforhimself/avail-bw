import argparse
import time,code
import numpy as np
import pandas as pd
"""
    format1:
        100*100 timestamp %10u.%9u separate by ',' 
        output 100*100 dt[99],sum in microsecond precision

    format4: 
        python preprocess.py -m format4 -o data/link100load0exp4.txt load0exp4.txt
        python preprocess.py -m format4 -o data/link100load45exp4.txt load45exp4.txt
        python preprocess.py -m format4 -o data/link100load46exp4.txt load46exp4.txt
        python preprocess.py -m format4 -o data/link100load90exp4.txt load90exp4.txt
        format used in experiment 4
        shape 100*101
        time_client, timestamp[100] 
        output 100*101 sample=[time_client,total_time,dtime[99]] in microsecond(us)

    format5: 
        python preprocess.py -m format5 -o data/link1000load0exp5.txt load0exp5.txt
        python preprocess.py -m format5 -o data/link1000load450exp5.txt load450exp5.txt
        python preprocess.py -m format5 -o data/link1000load451exp5.txt load451exp5.txt
        python preprocess.py -m format5 -o data/link1000load900exp5.txt load900exp5.txt

        experiment 5
        shape (n_sample,1001) 
                (send_duration,recv[1000])
        output:
            (n_sample,1001)
                (send_duration,recv_duration,difftime[999]), unit= us

    format_tcpdump: python preprocess.py -m format_tcpdump -o traffic.csv timestamps_out2.txt
        查看进入路由器的时间 tcpdump

"""
def cmd():
    args=argparse.ArgumentParser(description='Data process')
    args.add_argument('-m',"--mode",type=str,help='data process mode',default='format1',choices=['format1','format4','format5','format_tcpdump'])
    args.add_argument("-o","--filelist",type=str,help="filename list",nargs='*')
    args=args.parse_args()
    return args
def line2floats(line):
    return np.array([np.float64(i) for i in line.split(',')])
def lines2floatsmatrix(lines):
    return np.array([line2floats(line) for line in lines])
def format_data(fin,fout,with_sum=True):
    with open(fin,'r') as f:
        lines=f.read().split('\n')
    lines.remove('')
    mtx=lines2floatsmatrix(lines)
    delta=mtx[:,1:]-mtx[:,:-1]
    if with_sum:
        col=(mtx[:,-1]-mtx[:,0]).reshape((-1,1))
        delta=np.concatenate((delta,col),axis=1)
    #us precision
    delta=delta*1e6
    #np.set_printoptions(suppress=True,formatter={'float_kind':'{:0.1f}'.format})
    np.savetxt(fout,delta,fmt='%3.0f',delimiter=' ')
def f4m(fin,fout):
    """
        format4
    """
    with open(fin,'r') as f:
        lines=f.read().split('\n')
    lines=[line.strip() for line in lines if line!='']
    mtx=lines2floatsmatrix(lines)
    dtime=mtx[:,2:]-mtx[:,1:-1]
    total_time=(mtx[:,-1]-mtx[:,1]).reshape((-1,1))
    time_client=mtx[:,0].reshape((-1,1))
    output_data=np.concatenate((time_client,total_time,dtime),axis=1)
    output_data=output_data*1e6
    mean_=np.mean(output_data,axis=0).reshape((1,-1))
    output_data=np.concatenate((mean_,output_data),axis=0)
    np.savetxt(fout,output_data,fmt='%6.0f',delimiter=' ')
def read_file(filename):
    with open(filename,'r') as f:
        lines=f.read().split('\n')
    lines=[line.strip() for line in lines if line!='']
    mtx=lines2floatsmatrix(lines)
    return mtx
def format_5(fin,fout):
    """
        format 5
    """
    mtx=read_file(fin)
    print("original shape {}".format(mtx.shape))
    dt=mtx[:,2:]-mtx[:,1:-1]
    recv_duration=(mtx[:,-1]-mtx[:,1]).reshape((-1,1))
    send_duration=mtx[:,0].reshape((-1,1))
    output_data=np.concatenate((send_duration,recv_duration,dt),axis=1)*1e6
    mean_=np.mean(output_data,axis=0).reshape((1,-1))
    output_data=np.concatenate((mean_,output_data),axis=0)
    np.savetxt(fout,output_data,fmt='%6.0f',delimiter=' ')
def format_tcpdump(fin,fout):
    """
        tcpdump csv file
    """
    df=pd.read_csv(fin)
    mtx=(df['Time'].values).reshape((100,1000))
    dt=(mtx[:,1:]-mtx[:,:-1])
    recv_duration=(mtx[:,-1]-mtx[:,0]).reshape((-1,1))
    output_data=np.concatenate((recv_duration,dt),axis=1)*1e6
    np.savetxt(fout,output_data,fmt='%6.0f',delimiter=' ')
if __name__=="__main__":
    t1=time.time()
    args=cmd()
    fin,fout=args.filelist[0],args.filelist[1]
    if args.mode=='format1':
        format_data(args.filelist[0], args.filelist[1])
    elif args.mode=='format4':
        f4m(args.filelist[0],args.filelist[1])
    elif args.mode=='format5':
        format_5(args.filelist[0],args.filelist[1])
    elif args.mode=='format_tcpdump':
        format_tcpdump(fin,fout)
    t2=time.time()
    print('it takes {} seconds'.format(t2-t1))