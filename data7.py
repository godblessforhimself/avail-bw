#utf-8
"""
    exp7
    * 包大小1500-9000
    * 方法：线性回归、xgboost、lightgbm
    * 训练集+预测集
    * 数据不归一化
    * 调参：越简单越好
"""
import os,time,code,logging,random,json,re
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
import xgboost as xgb
import pandas as pd

def line2floats(line):
    return np.array([np.float64(i) for i in line.split(',')])
def lines2floatsmatrix(lines):
    return np.array([line2floats(line) for line in lines])
def read_file(filename):
    with open(filename,'r') as f:
        lines=f.read().split('\n')
    if len(lines)==1:
        return None
    lines=[line.strip() for line in lines if line!='']
    mtx=lines2floatsmatrix(lines)
    dtime=mtx[:,2:]-mtx[:,1:-1]
    total_time=(mtx[:,-1]-mtx[:,1]).reshape((-1,1))
    time_client=mtx[:,0].reshape((-1,1))
    output_data=np.concatenate((time_client,total_time,dtime),axis=1)
    return output_data

def precision_acc(pred,real,d):
    return np.mean(np.abs(pred-real)<=d)

def run_method(param,data,measurement,packet_size):
    t1=time.time()
    method=param['method']
    kargs=param['kargs']
    preds=method(data,kargs,packet_size)
    ret=measurement(preds,data)
    t2=time.time()
    return ret,t2-t1
def linear_log2file(f,packet_size,data):
    # xtest三个一组
    xtrain,xtest,ytrain,ytest=data
    f.write('packet size {:>3d} train:\n'.format(packet_size))
    yset=sorted(list(set(ytrain)))
    for i in yset:
        value_mean=np.mean(xtrain[ytrain==i,1])
        f.write('load {:.1f} mean {:.2f}\n'.format(i,value_mean*1e3))
    yset_test=sorted(list(set(ytest)))
    ymax,ymin=np.max(ytrain),np.min(ytrain)
    recv_max=np.mean(xtrain[ytrain==ymax,1])
    recv_min=np.mean(xtrain[ytrain==ymin,1])
    f.write('packet size {:>3d} test:\n'.format(packet_size))
    for i in yset_test:
        #10组
        v=(xtest[np.repeat(ytest==i,3),1]).reshape((-1,3))
        for j in v:
            value_str=list_formatter(j*1e3,'{:.2f}')
            pred=(ymax-ymin)*(j-recv_min)/(recv_max-recv_min)+ymin
            pred_mean=np.mean(pred)
            pred_str=list_formatter(pred,'{:.2f}')
            f.write('load {:.1f} recv_time {} load_pred {} pred_mean {:.2f}\n'.format(i, value_str, pred_str, pred_mean))
def list_formatter(arr,fmt):
    return ' '.join(fmt.format(a) for a in arr)
def linear_method(data,kargs,packet_size):
    xtrain,xtest,ytrain,ytest=data
    ymax,ymin=np.max(ytrain),np.min(ytrain)
    recv_max=np.mean(xtrain[ytrain==ymax,1])
    recv_min=np.mean(xtrain[ytrain==ymin,1])
    recv_time=xtest[:,1]
    pred=(ymax-ymin)*(recv_time-recv_min)/(recv_max-recv_min)+ymin
    if kargs and kargs['log']:
        linear_log2file(kargs['log'],packet_size,data)
    return pred
def lightgbm_method(data,kargs_,packet_size):
    xtrain,xtest,ytrain,ytest=data
    kargs=kargs_.copy()
    lgb_train=lgb.Dataset(xtrain,ytrain)
    num_boost_round=kargs['num_boost_round']
    kargs.pop('num_boost_round')
    gbm=lgb.train(kargs,lgb_train,num_boost_round=num_boost_round)
    pred=gbm.predict(xtest)
    return pred
def xgboost_method(data,kargs_,packet_size):
    xtrain,xtest,ytrain,ytest=data
    kargs=kargs_.copy()
    dtrain,dtest=xgb.DMatrix(xtrain,label=ytrain),xgb.DMatrix(xtest)
    num_round=kargs['num_round']
    kargs.pop('num_round')
    bst=xgb.train(kargs,dtrain,num_boost_round=num_round)
    pred=bst.predict(dtest)
    return pred

def filter_data(pattern_train,pattern_test):
    ptrain=re.compile(pattern_train)
    ptest=re.compile(pattern_test)
    xtrain,xtest,ytrain,ytest=[],[],[],[]
    for filename in os.listdir('data'):
        begin=filename.find('load')+4
        end=filename.find('packetsize')
        if ptrain.match(filename):
            load=np.float32(filename[begin:end])
            data=read_file('data/{}'.format(filename))
            if not data is None:
                xtrain.append(data)
                ytrain.append(load)
            else:
                print('file {} is empty!'.format(filename))
        elif ptest.match(filename):
            load=np.float32(filename[begin:end])
            data=read_file('data/{}'.format(filename))
            if not data is None:
                xtest.append(data)
                ytest.append(load)
            else:
                print('file {} is empty!'.format(filename))
    if len(xtrain)==0:
        return (xtrain,xtest,ytrain,ytest)
    n_feature=xtrain[0].shape[1]
    train_repeat_count=xtrain[0].shape[0]
    xtrain=np.array(xtrain).reshape((-1,n_feature))
    ytrain=np.repeat(np.array(ytrain),train_repeat_count)
    xtest=np.array(xtest).reshape((-1,n_feature))
    ytest=np.array(ytest)
    return (xtrain,xtest,ytrain,ytest)

def get_data():
    data_set=[]
    for packet_size in range(1500,9001,1500):
        pattern_train=r'^link100load[0-9\.]+packetsize{}exp7\.txt'.format(packet_size)
        pattern_test=r'^link100load[0-9\.]+packetsize{}exp7test[0-9]*\.txt'.format(packet_size)
        data=filter_data(pattern_train,pattern_test)
        data_set.append(data)
    return data_set

param_lightgbm={
    'method':lightgbm_method,
    'kargs':{
        'boosting_type': 'gbdt',
        'objective': 'l2',
        'metric': 'l2',
        'num_leaves': 1000,
        'learning_rate': 0.1,
        'feature_fraction': 1,
        'bagging_fraction': 1,
        'bagging_freq': 5,
        'verbose': -1,
        'num_boost_round':100,
    }
}
param_xgboost={
    'method':xgboost_method,
    'kargs':{
        'max_depth':6,
        'eta':0.06,
        'verbosity':0,
        'objective':'reg:squarederror',
        'num_round':200,
        'tree_method':'auto',
        'dump_model':None
    }
}
if True:
    linear_log=open('temp/linear_log_exp7.txt','w')
param_linear={
    'method':linear_method,
    'kargs':{
        'log':linear_log
    }
}
param_dict={
    'linear':param_linear,
    'lightgbm':param_lightgbm,
    'xgboost':param_xgboost
}
def atomic_metric(pred,ytest):
    #pred ytest一一对应
    ret=[]
    for d in [0.5,1,2,5]:
        acc=precision_acc(pred,ytest,d)
        ret.append(acc)
    mae=np.mean(np.abs(pred-ytest))
    rmse=np.sqrt(mean_squared_error(pred,ytest))
    ret.extend([mae,rmse])
    return ret
def meas_normal(pred,data):
    ret=[]
    xtrain,xtest,ytrain,ytest=data
    return atomic_metric(pred,ytest)
def meas_test(pred,data):
    ret=[]
    xtrain,xtest,ytrain,ytest=data
    assert(xtest.shape[0]==3*ytest.shape[0])
    ratio=xtest.shape[0]//ytest.shape[0]
    ytest_full=np.repeat(ytest,ratio)
    ret1=atomic_metric(pred,ytest_full)
    pred_averaged=np.mean(pred.reshape((-1,3)), axis=1)
    ret2=atomic_metric(pred_averaged,ytest)
    return [ret1,ret2]

def run_experiment(data_set):
    colname=['packet size','method','single/set','d=0.5','d=1.0','d=2.0','d=5.0','mae','rmse','time']
    df_data=[]
    for i,packet_size in enumerate(range(1500,9001,1500)):
        data=data_set[i]
        if len(data[0])==0:
            break
        method_list=param_dict.keys()
        r1,r2=[],[]
        for key in method_list:
            param=param_dict[key]
            ret,timecost=run_method(param,data,meas_test,packet_size)
            r1.append(ret)
            r2.append(timecost)
            performance1,performance2=np.around(ret[0],decimals=4),np.around(ret[1],decimals=4)
            df_temp=[packet_size,key,'single']
            df_temp.extend(performance1)
            df_temp.append(np.around(timecost,decimals=4))
            df_data.append(df_temp)
            df_temp=[packet_size,key,'set']
            df_temp.extend(performance2)
            df_temp.append(np.around(timecost,decimals=4))
            df_data.append(df_temp)

        print('experiment at {} result:'.format(packet_size))
        for i,name in enumerate(method_list):
            print('{} use {:.2f} s\n\t{}\n\t{}'.format(name,r2[i],list_formatter(r1[i][0],'{:.2f}'),list_formatter(r1[i][1],'{:.2f}')))
        print('\n')

    df=pd.DataFrame(data=df_data,columns=colname)
    df.to_csv('temp/data7result.csv',index=False)
    
if __name__=='__main__':
    t1=time.time()
    data_set=get_data()
    t2=time.time()
    print('prepare data use {} s'.format(t2-t1))
    t1=time.time()
    run_experiment(data_set)
    if linear_log:
        linear_log.close()
    t2=time.time()
    print('use {} s'.format(t2-t1))