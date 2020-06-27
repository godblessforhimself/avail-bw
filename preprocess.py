import argparse
import time,code,re,os
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
    format6/7:
        python preprocess.py -m format5 -o data/link100load0packetsize1500exp6.txt link100load0packetsize1500exp6.txt
        python preprocess.py -m format5 -o data/link100load90packetsize1500exp6.txt link100load90packetsize1500exp6.txt
        python preprocess.py -m format5 -o data/link100load0packetsize9000exp6.txt link100load0packetsize9000exp6.txt
        python preprocess.py -m format5 -o data/link100load90packetsize9000exp6.txt link100load90packetsize9000exp6.txt
        python preprocess.py -m format5 -o data/link100load45.0packetsize1500exp6test.txt link100load45.0packetsize1500exp6test.txt

        python preprocess.py -m format5 -o data/link100load0packetsize1500exp7.txt link100load0packetsize1500exp7.txt
        python preprocess.py -m format5 -o data/link100load1packetsize1500exp7.txt link100load1packetsize1500exp7.txt
        python preprocess.py -m format5 -o data/link100load2packetsize1500exp7.txt link100load2packetsize1500exp7.txt
        python preprocess.py -m format5 -o data/link100load3packetsize1500exp7.txt link100load3packetsize1500exp7.txt
        python preprocess.py -m format5 -o data/link100load4packetsize1500exp7.txt link100load4packetsize1500exp7.txt
        python preprocess.py -m format5 -o data/link100load5packetsize1500exp7.txt link100load5packetsize1500exp7.txt
        python preprocess.py -m format5 -o data/link100load50packetsize1500exp7.txt link100load50packetsize1500exp7.txt

        python preprocess.py -m format5 -o data/link100load0packetsize3000exp7.txt link100load0packetsize3000exp7.txt
        python preprocess.py -m format5 -o data/link100load1packetsize3000exp7.txt link100load1packetsize3000exp7.txt
        python preprocess.py -m format5 -o data/link100load2packetsize3000exp7.txt link100load2packetsize3000exp7.txt
        python preprocess.py -m format5 -o data/link100load3packetsize3000exp7.txt link100load3packetsize3000exp7.txt
        python preprocess.py -m format5 -o data/link100load4packetsize3000exp7.txt link100load4packetsize3000exp7.txt
        python preprocess.py -m format5 -o data/link100load5packetsize3000exp7.txt link100load5packetsize3000exp7.txt
        python preprocess.py -m format5 -o data/link100load50packetsize3000exp7.txt link100load50packetsize3000exp7.txt


        python preprocess.py -m format5 -o data/link100load0.0packetsize1500exp7test1.txt link100load0.0packetsize1500exp7test1.txt


    peek:
        python preprocess.py -m peek -o temp/regex_file.txt temp/peek_result.txt

    format_tcpdump: python preprocess.py -m format_tcpdump -o traffic.csv timestamps_out2.txt
        查看进入路由器的时间 tcpdump

"""
def cmd():
    args=argparse.ArgumentParser(description='Data process')
    args.add_argument('-m',"--mode",type=str,help='data process mode',default='format1',choices=['format1','format4','format5','format_tcpdump','peek'])
    args.add_argument("-o","--filelist",type=str,help="filename list",nargs='*')
    args=args.parse_args()
    return args
def line2floats(line):
    return np.array([np.float64(i) for i in line.split(',')])
def lines2floatsmatrix(lines):
    return np.array([line2floats(line) for line in lines])
def transform_data(data):
    dt=data[:,2:]-data[:,1:-1]
    st=(data[:,0]).reshape((-1,1))
    rt=(data[:,-1]-data[:,1]).reshape((-1,1))
    return np.concatenate((st,rt,dt),axis=1)
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
def list_formatter(a,form):
    return ' '.join(form.format(i) for i in a)
def peek_files(fin,fout):
    f=open(fin,'r')
    fo=open(fout,'w')
    lines=f.read().split('\n')
    f.close()
    filelist=[]
    prefix=''
    for line in lines:
        if line!='' and line[0]!='^':
            filelist=os.listdir(line)
            prefix=line
        elif line!='' and line[0]=='^':
            if prefix=='':
                print('peek_files Error: {}'.format(line))
            pattern=re.compile(line)
            for filename in filelist:
                if pattern.match(filename):
                    data=read_file(prefix+filename)
                    data=transform_data(data)*1e6
                    avg=np.mean(data,axis=0)
                    fo.write('{} {}\n'.format(prefix,filename))
                    fo.write(list_formatter(avg,'{:.2f}')+'\n')
    fo.close()
    
if __name__=="__main__":
    t1=time.time()
    args=cmd()
    if len(args.filelist)==2:
        fin,fout=args.filelist[0],args.filelist[1]
    if args.mode=='format1':
        format_data(args.filelist[0], args.filelist[1])
    elif args.mode=='format4':
        f4m(args.filelist[0],args.filelist[1])
    elif args.mode=='format5':
        format_5(args.filelist[0],args.filelist[1])
    elif args.mode=='format_tcpdump':
        format_tcpdump(fin,fout)
    elif args.mode=='peek':
        peek_files(fin,fout)
    t2=time.time()
    print('it takes {} seconds'.format(t2-t1))