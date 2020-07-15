import time
import numpy as np
import os
DIR_NAME='data'
def check_order(sequence_number):
    for i,v in enumerate(sequence_number):
        if i!=v:
            return i
    return -1
def line2float64(line):
    return np.array([np.float64(i) for i in line.split(',') if i!=''])
def line2int32(line):
    return np.array([np.int32(i) for i in line.strip().split(',') if i!=''])
def read_raw_file(filename):
    """
        读取文件中的三行
        sendtime,recvtime,sequence_number
        返回res,a,b
        res=-1，sequence顺序正确
        res=-2，缺少recvtime
        res>=0，res为出错的sequence的下标
        a,b在正确时分别为sendtime,recvtime
    """
    with open(filename,'r') as f:
        lines=f.read().split('\n')
    if len(lines)<3:
        return -2,None,None
    send_time,recv_time,sequence_number=line2float64(lines[0]),line2float64(lines[1]),line2int32(lines[2])
    wrong_order=check_order(sequence_number)
    if wrong_order==-1:
        return -1,send_time,recv_time
    else:
        return wrong_order,send_time,recv_time
def read_raw_data(ex_count,PAIR_COUNT,CONTINIOUS_COUNT):
    """
        读取link[link]load[load]exp[exp].txt中exp=ex_count的所有数据
        返回X，Y
        X：shape=(n_sample,n_point,2) 分别为样本数，数据维度，发送接收
        Y：shape=(n_sample,2) 样本数，链路参数(link,load)
    """
    t1=time.time()
    X,Y=[],[]
    incomplete_count,wrong_order_count=0,0
    for filename in os.listdir(DIR_NAME):
        link=int(filename[4:filename.find('load')])
        load=int(filename[filename.find('load')+4:filename.find('exp')])
        expcnt=int(filename[filename.find('exp')+3:-4])
        if expcnt!=ex_count:
            continue
        full_path=DIR_NAME+'/'+filename
        wrong_order,send_time,recv_time=read_raw_file(full_path)
        if wrong_order>=0:
            wrong_order_count+=1
            continue
        elif wrong_order==-2:
            incomplete_count+=1
            continue
        x=np.transpose(np.array([send_time,recv_time]).reshape((2,PAIR_COUNT,CONTINIOUS_COUNT)), (1,2,0))
        if len(X)==0:
            X=x
        else:
            X=np.append(X,x,axis=0)
        y=np.tile([link,load],PAIR_COUNT).reshape(PAIR_COUNT,2)
        if len(Y)==0:
            Y=y
        else:
            Y=np.append(Y,y,axis=0)
    t2=time.time()
    print('read raw data uses {} seconds, incomplete {}, wrong order {}'.format(t2-t1, incomplete_count, wrong_order_count))
    return X,Y
