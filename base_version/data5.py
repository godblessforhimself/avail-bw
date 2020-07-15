#utf-8
"""
    exp5
    * 两组数据集
    * 使用线性回归、xgboost、lightgbm
    * data1: 8train-2test; data1+data2: train-test
"""
import os,time,code,logging,random,json,re
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
import xgboost as xgb

def line2floats(line):
    return np.array([np.float64(i) for i in line.split(',')])
def lines2floatsmatrix(lines):
    return np.array([line2floats(line) for line in lines])
def read_file(filename):
    with open(filename,'r') as f:
        lines=f.read().split('\n')
    lines=[line.strip() for line in lines if line!='']
    mtx=lines2floatsmatrix(lines)
    dtime=mtx[:,2:]-mtx[:,1:-1]
    total_time=(mtx[:,-1]-mtx[:,1]).reshape((-1,1))
    time_client=mtx[:,0].reshape((-1,1))
    output_data=np.concatenate((time_client,total_time,dtime),axis=1)
    return output_data
def shuffle_data(x,y,seed=0):
    rng=np.random.default_rng(seed=seed)
    indices=np.arange(x.shape[0])
    rng.shuffle(indices)
    return x[indices],y[indices]

def precision_acc(pred,real,d):
    return np.mean(np.abs(pred-real)<=d)

def run_method(param,data,measurement):
    t1=time.time()
    method=param['method']
    kargs=param['kargs']
    preds=method(data,kargs)
    ret=measurement(preds,data)
    t2=time.time()
    return ret,t2-t1
def linear_method(data,kargs):
    xtrain,xtest,ytrain,ytest=data
    ymax,ymin=np.max(ytrain),np.min(ytrain)
    assert(ymax!=ymin)
    recv_max=np.mean(xtrain[ytrain==ymax,1])
    recv_min=np.mean(xtrain[ytrain==ymin,1])
    recv_time=xtest[:,1]
    pred=(ymax-ymin)*(recv_time-recv_min)/(recv_max-recv_min)+ymin
    return pred
def lightgbm_method(data,kargs_):
    xtrain,xtest,ytrain,ytest=data
    kargs=kargs_.copy()
    lgb_train=lgb.Dataset(xtrain,ytrain)
    num_boost_round=kargs['num_boost_round']
    kargs.pop('num_boost_round')
    gbm=lgb.train(kargs,lgb_train,num_boost_round=num_boost_round)
    pred=gbm.predict(xtest)
    return pred
def xgboost_method(data,kargs_):
    xtrain,xtest,ytrain,ytest=data
    kargs=kargs_.copy()
    dtrain,dtest=xgb.DMatrix(xtrain,label=ytrain),xgb.DMatrix(xtest)
    num_round=kargs['num_round']
    kargs.pop('num_round')
    bst=xgb.train(kargs,dtrain,num_boost_round=num_round)
    pred=bst.predict(dtest)
    return pred

def filter_data(patternstr):
    pattern=re.compile(patternstr)
    x,y=[],[]
    for filename in os.listdir('data'):
        if pattern.match(filename):
            begin=filename.find('load')+4
            end=filename.find('exp')
            load=np.float32(filename[begin:end])
            data=read_file('data/{}'.format(filename))
            x.append(data)
            y.append(load)
    return x,y
def get_train_data():
    #link1000load0exp5.txt
    pattern=r'^link1000load[0-9\.]+exp5\.txt'
    x,y=filter_data(pattern)
    n_feature=x[0].shape[1]
    n_sample_one=x[0].shape[0]
    x=np.array(x).reshape((-1,n_feature))
    y=np.repeat(np.array(y),n_sample_one)
    return x,y
def get_test_data():
    #link1000load0exp5test.txt
    pattern=r'^link1000load[0-9\.]+exp5test\.txt'
    x,y=filter_data(pattern)
    n_feature=x[0].shape[1]
    n_sample_one=x[0].shape[0]
    x=np.array(x).reshape((-1,n_feature))
    #x,y并非1对1
    y=np.array(y)
    return x,y
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
param_linear={
    'method':linear_method,
    'kargs':None
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

def train_experiment(x,y):
    data=train_test_split(x,y,test_size=0.2,random_state=0)
    method_list=param_dict.keys()
    r1,r2=[],[]
    for key in method_list:
        param=param_dict[key]
        ret,timecost=run_method(param,data,meas_normal)
        r1.append(ret)
        r2.append(timecost)
    print('train_experiment result:')
    for i,name in enumerate(method_list):
        print('{} use {} s, res {}'.format(name,r2[i],r1[i]))
    print('\n')

def test_experiment(xtrain,xtest,ytrain,ytest):
    data=xtrain,xtest,ytrain,ytest
    method_list=param_dict.keys()
    r1,r2=[],[]
    for key in method_list:
        param=param_dict[key]
        ret,timecost=run_method(param,data,meas_test)
        r1.append(ret)
        r2.append(timecost)
    print('test_experiment result:')
    for i,name in enumerate(method_list):
        print('{} use {} s, res {}\nres average {}'.format(name,r2[i],r1[i][0],r1[i][1]))
    print('\n')
    
if __name__=='__main__':
    t1=time.time()
    xtrain,ytrain=get_train_data()
    xtrain,ytrain=shuffle_data(xtrain,ytrain,0)
    xtest,ytest=get_test_data()
    t2=time.time()
    print('prepare data use {} s'.format(t2-t1))
    train_experiment(xtrain,ytrain)
    test_experiment(xtrain,xtest,ytrain,ytest)