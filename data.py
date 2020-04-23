import numpy as np
import code
files=['l{}.txt'.format(i) for i in range(1,4)]+['r{}.txt'.format(i) for i in range(1, 4)]
files=['build/'+f for f in files]
def line2float(line):
    return np.array([np.float64(s) for s in line.strip().split(',') if s!=''])

def read_file(file):
    with open(file, 'r') as f:
        lines=f.read().split('\n')
    lines=lines[:4]
    floats_list=np.array([line2float(line) for line in lines])
    return floats_list
def get_metrics(floats_list):
    send_duration=floats_list[1]-floats_list[0]
    send_interval=floats_list[0,1:]-floats_list[1,:-1]
    recv_duration=floats_list[3]-floats_list[2]
    recv_interval=floats_list[2,1:]-floats_list[3,:-1]
    return send_duration[1:], send_interval, recv_duration[1:], recv_interval[1:]
def get_std(arr,mi,ma):
    mi_,ra_=arr.min(),arr.max()-arr.min()
    
    if ra_>0:
        brr=(arr-mi_)/ra_
        brr*=(ma-mi)
        brr+=mi
        return brr
    else:
        print('avg is 0')
        return arr

def get_gaps(a):
    send_gaps=a[1]-a[0]
    recv_gaps=a[3]-a[2]
    return send_gaps,recv_gaps

def analyse_array(a,s,multiple=1e6):
    print('{},base={}\nmean:{}\nmin:{}\nmax:{}\n'.format(s,multiple,a.mean()*multiple,a.min()*multiple,a.max()*multiple))

if __name__=='__main__':
    ret=read_file('build/timestamp.txt')
    send_gaps,recv_gaps=get_gaps(ret)
    analyse_array(send_gaps,'send_gaps')
    analyse_array(recv_gaps,'recv_gaps')
    code.interact(local=dict(globals(),**locals()))