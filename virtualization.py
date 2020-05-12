#!/bin/python3
import util
import code
import numpy as np
import matplotlib.pyplot as plt
EXPERIMENT_COUNT=2
CONTINIOUS_COUNT=10
PAIR_COUNT=1000
def get_diff(x):
    sendtime=x[:,:,0]
    recvtime=x[:,:,1]
    ds1=sendtime[:,1:]-sendtime[:,:-1]
    ds2=(sendtime[:,-1]-sendtime[:,0]).reshape((-1,1))
    ds=np.concatenate((ds1,ds2),axis=1)
    dr1=recvtime[:,1:]-recvtime[:,:-1]
    dr2=(recvtime[:,-1]-recvtime[:,0]).reshape((-1,1))
    dr=np.concatenate((dr1,dr2),axis=1)
    dx=np.concatenate((ds,dr),axis=1)
    return dx
def filterbyload(y,load):
    loads=y[:,1]
    filter_=(loads==load)
    return filter_
def decompose(a):
    max_=int(np.floor(np.sqrt(a)))
    for i in range(max_,0,-1):
        if a%i==0:
            return i,a//i
    else:
        print('decompose {} failed'.format(a))
    return 1,a
def draw_hist(ax,data):
    weights=np.ones_like(data)/len(data)
    ax.hist(data,weights=weights)
    
def analyze(x,y,load,filename):
    filter_=filterbyload(y,load)
    xfiltered=x[filter_]*1e6
    dimens=xfiltered.shape[1]
    row,col=2,10
    fig,axs=plt.subplots(row,col,figsize=(30,7))
    i=0
    bins_normal=[i for i in range(0,101,10)]
    bins_sum=[i for i in range(40,241,20)]
    while i<dimens:
        r,c=i//col,i%col
        ax=axs[r,c]
        data=xfiltered[:,i]
        weights=np.ones_like(data)/len(data)
        ax.hist(data,weights=weights,bins=bins_normal if i!=9 and i!=19 else bins_sum)
        axs[r,c].set_title('dimen {}'.format(i))
        i+=1
    plt.savefig(filename,bbox_inches='tight')
    plt.close(fig)

if __name__=='__main__':
    x,y=util.read_raw_data(EXPERIMENT_COUNT,PAIR_COUNT,CONTINIOUS_COUNT)
    """
        link=1000，load=0-900
        分析一组link,load的数据，数据：时间戳相邻作差，加上末项-首项
        分析每一维差值：
        横坐标是时间差值(桶)，纵坐标是数据数量
    """
    dx=get_diff(x)
    for load in range(0,1000,100):
        filename='link1000load{}exp2.png'.format(load)
        analyze(dx,y,load,filename)

    #code.interact(local=dict(globals(),**locals()))