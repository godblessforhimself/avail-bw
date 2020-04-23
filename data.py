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
    return send_gaps,np.sort(recv_gaps)

def analyse_array(a,s,f,multiple=1e6):
    b=a[a>f]*multiple
    print('{},base={}\nmean:{}\tmin:{}\tmax:{}\tlen:{}\n'.format(s,multiple,b.mean(),b.min(),b.max(), len(b)))

def analyse_file(fname):
    _,rg=get_gaps(read_file(fname))
    analyse_array(rg,fname,120e-6)
    return rg

if __name__=='__main__':
    for i in range(10,100,10):
        fname='build/c100t{}r10.txt'.format(i)
        rg=analyse_file(fname)
        rg=rg*1e6
        np.savetxt('build/{}.txt'.format(i), rg, fmt='%3.2f')

    code.interact(local=dict(globals(),**locals()))