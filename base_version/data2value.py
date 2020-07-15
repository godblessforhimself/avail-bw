from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import precision_score
from keras.models import Sequential
from keras.layers import Dropout
from keras.layers import Dense, Activation
from keras.utils.np_utils import to_categorical
from keras.callbacks.callbacks import EarlyStopping
from keras.losses import huber_loss
from keras import optimizers
import lightgbm as lgb
import xgboost as xgb
import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import code,os,time
#训练集、测试集划分：十次十折交叉验证
#训练方法XGBoost、RandomForest、ANN、Logistic Regression、LightGBM
DIR_NAME='data'
EXPERIMENT_COUNT=2
CONTINIOUS_COUNT=10
PAIR_COUNT=1000
LOGLEVEL_FATAL=-1
LOGLEVEL_ERROR=0
LOGLEVEL_INFO=1
LOGLEVEL_DEBUG=2
LOGLEVEL=LOGLEVEL_ERROR
def read_raw_data(ex_count):
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
        #x.shape Pair,Continous,2
        x=np.transpose(np.array([send_time,recv_time]).reshape((2,PAIR_COUNT,CONTINIOUS_COUNT)), (1,2,0))
        if len(X)==0:
            X=x
        else:
            X=np.append(X,x,axis=0)
        #y.shape Pair,2
        y=np.tile([link,load],PAIR_COUNT).reshape(PAIR_COUNT,2)
        if len(Y)==0:
            Y=y
        else:
            Y=np.append(Y,y,axis=0)
    t2=time.time()
    print('read raw data uses {} seconds, incomplete {}, wrong order {}'.format(t2-t1, incomplete_count, wrong_order_count))
    return X,Y
def line2float64(line):
    return np.array([np.float64(i) for i in line.split(',') if i!=''])
def line2int32(line):
    return np.array([np.int32(i) for i in line.strip().split(',') if i!=''])
def check_order(sequence_number):
    for i,v in enumerate(sequence_number):
        if i!=v:
            return i
    return -1
def read_raw_file(filename):
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
def get_diff_data(X,scale=1e6):
    # X.shape is pair,continious,2
    diffX=(X[:,1:,:]-X[:,:-1,:])*scale
    return diffX
# preprocessor
def standard_preprocessor(X,Y):
    x=X.reshape(X.shape[0],-1)
    sc=StandardScaler()
    x=sc.fit_transform(x)
    y=Y
    return x,y
# training methods
def get_args(key,value,kargs):
    if kargs:
        return kargs[key] if key in kargs else value
    else:
        return value
def get_args_dict(params: dict, kargs):
    replacement=[]
    for key in params.keys():
        if key in kargs:
            replacement.append(key)
    for key in replacement:
        params[key]=kargs[key]
    return params
def lightgbm_method(xtrain,xtest,ytrain,ytest,kargs):
    lgb_train=lgb.Dataset(xtrain, ytrain)
    lgb_eval=lgb.Dataset(xtest, ytest, reference=lgb_train)
    params = {
        'boosting_type': 'gbdt',
        'objective': 'regression_l1',
        'metric': 'l1',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 1.0,
        'bagging_fraction': 1.0,
        'bagging_freq': 5,
        'verbose': 1
    }
    params=get_args_dict(params,kargs)
    num_boost_round=get_args('num_boost_round',5000,kargs)
    early_stopping_rounds=get_args('early_stopping_rounds',500,kargs)
    gbm=lgb.train(params,lgb_train,num_boost_round=num_boost_round,valid_sets=lgb_eval,early_stopping_rounds=early_stopping_rounds,verbose_eval=False)
    preds=gbm.predict(xtest, num_iteration=gbm.best_iteration)
    return mean_absolute_error(ytest,preds)
def xgboost_method(xtrain,xtest,ytrain,ytest,kargs):
    dtrain,dtest=xgb.DMatrix(xtrain,label=ytrain),xgb.DMatrix(xtest,label=ytest)
    param={
        'max_depth':6,
        'eta': 0.3,
        'verbosity': 2,
        'objective':'reg:squarederror',
        'early_stopping_rounds':10,
        'tree_method':'auto',
        'eval_metric': 'mae'
    }
    param=get_args_dict(param,kargs)
    num_round=get_args('num_round',100,kargs)
    early_stopping_rounds=get_args('early_stopping_rounds',20,kargs)
    bst = xgb.train(param,dtrain,num_boost_round=num_round,early_stopping_rounds=early_stopping_rounds,evals=[(dtest,"Test")],verbose_eval=True)
    preds=bst.predict(dtest)
    return mean_absolute_error(ytest,preds)
def keras_method(xtrain,xtest,ytrain,ytest,kargs):
    inshape=get_args('inshape',xtrain.shape[1],kargs)
    layer_num1=get_args('layer_num1',256,kargs)
    layer_num2=get_args('layer_num2',512,kargs)
    epochs=get_args('epochs',100,kargs)
    verbose=get_args('verbose',0,kargs)
    batch_size=get_args('batch_size',100,kargs)
    model=Sequential()
    model.add(Dense(layer_num1,input_dim=inshape,activation='relu'))
    model.add(Dense(layer_num2,activation='relu'))
    model.add(Dense(1))
    sgd=optimizers.SGD(lr=1e-3)
    model.compile(optimizer=sgd,loss='mae',metrics=['mae'])
    model.fit(xtrain,ytrain,epochs=epochs,batch_size=batch_size,validation_split=0.1,shuffle=True,verbose=verbose,use_multiprocessing=True)
    preds=model.predict(xtest)
    return mean_absolute_error(ytest,preds)
# abstract function
def run_method(X,Y,preprocessor,splitor,training_method,kargs):
    x,y=preprocessor(X,Y)
    t1=time.time()
    metric=0
    i=0
    for train_index,test_index in splitor.split(x):
        xtrain,xtest=x[train_index],x[test_index]
        ytrain,ytest=y[train_index],y[test_index]
        metric_temp=training_method(xtrain,xtest,ytrain,ytest,kargs)
        metric+=metric_temp
        i+=1
        break
    metric/=i
    t2=time.time()
    print('{} takes {} s, mae {}'.format(training_method.__name__,t2-t1,metric))
    return metric,t2-t1
def shuffle_data(X,Y):
    rng = np.random.default_rng(seed=0)
    indices=np.arange(X.shape[0])
    rng.shuffle(indices)
    return X[indices], Y[indices]
def exp(X,Y):
    n_sample=X.shape[0]
    n_feature=X.shape[1]
    sendtime,recvtime=X[:,:,0],X[:,:,1]
    y=Y
    kfold_splitor=KFold(n_splits=10,shuffle=True,random_state=0)
    method_list=['lightgbm','xgboost','keras_ann']
    methods={
        method_list[0]: lightgbm_method,
        method_list[1]: xgboost_method,
        method_list[2]: keras_method
    }
    kargs={
        method_list[0]: {
            'boosting_type': 'gbdt',
            'objective': 'regression_l1',
            'metric': 'l1',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 1.0,
            'bagging_fraction': 1.0,
            'bagging_freq': 5,
            'verbose': 2,
            'num_boost_round': 100,
            'early_stopping_rounds': 10
        },
        method_list[1]: {
            'max_depth':6,
            'eta':0.3,
            'verbosity':2,
            'objective':'reg:squarederror',
            'num_round':100,
            'early_stopping_rounds':10,
            'tree_method':'auto',
            'eval_metric':'mae'
        },
        method_list[2]: {
            'layer_num1':128,
            'layer_num2':256,
            'epochs':200,
            'batch_size':512,
            'verbose':1
        }
    }
    #method_list=['keras_ann']

    #use sendtime,recvtime
    acc_row=[]
    time_row=[]
    x=np.zeros((n_sample,n_feature*2))
    x[:,:n_feature]=sendtime
    x[:,n_feature:2*n_feature]=recvtime
    for method_name in method_list:
        acc,t=run_method(x,y,standard_preprocessor,kfold_splitor,methods[method_name],kargs[method_name])
        acc_row.append(acc)
        time_row.append(t)
    for i in range(len(method_list)):
        print('method {} use {} seconds, metric {}'.format(method_list[i],time_row[i],acc_row[i]))

if __name__=='__main__':
    X,Y=read_raw_data(EXPERIMENT_COUNT)
    Y=Y[:,1]
    dX=get_diff_data(X)
    dX,Y=shuffle_data(dX,Y)
    exp(dX,Y)