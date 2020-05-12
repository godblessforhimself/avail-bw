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
EXPERIMENT_COUNT=3
CONTINIOUS_COUNT=10
PAIR_COUNT=1000
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
def rescale(Y):
    a=sorted(list(set(Y)))
    transform={v:i for i,v in enumerate(a)}
    y=np.vectorize(transform.get)(Y)
    return y
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
def logistic_regression(xtrain,xtest,ytrain,ytest,kargs):
    random_state=get_args('random_state',0,kargs)
    solver=get_args('solver','lbfgs',kargs)
    max_iter=get_args('max_iter',100,kargs)
    multi_class=get_args('multi_class','multinomial',kargs)
    verbose=get_args('verbose',0,kargs)
    penalty=get_args('penalty','none',kargs)
    n_jobs=get_args('n_jobs',-1,kargs)
    clf=LogisticRegression(random_state=random_state,solver=solver,max_iter=max_iter,multi_class=multi_class,verbose=verbose,penalty=penalty,n_jobs=n_jobs).fit(xtrain, ytrain)
    accuracy=clf.score(xtest, ytest)
    return accuracy
def lightgbm_method(xtrain,xtest,ytrain,ytest,kargs):
    lgb_train=lgb.Dataset(xtrain, ytrain)
    lgb_eval=lgb.Dataset(xtest, ytest, reference=lgb_train)
    params = {
        'boosting_type': 'gbdt',
        'objective': 'multiclass',
        'metric': 'multi_logloss',
        'num_class': len(set(ytrain)),
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.9,
        'bagging_freq': 5,
        'verbose': -1
    }
    params=get_args_dict(params,kargs)
    num_boost_round=get_args('num_boost_round',5000,kargs)
    early_stopping_rounds=get_args('early_stopping_rounds',500,kargs)
    gbm=lgb.train(params,lgb_train,num_boost_round=num_boost_round,valid_sets=lgb_eval,early_stopping_rounds=early_stopping_rounds,verbose_eval=False)
    preds=gbm.predict(xtest, num_iteration=gbm.best_iteration)
    preds=np.argmax(preds,axis=1).reshape(ytest.shape)
    accuracy=np.mean(preds==ytest)
    return accuracy
def xgboost_method(xtrain,xtest,ytrain,ytest,kargs):
    dtrain,dtest=xgb.DMatrix(xtrain,label=ytrain),xgb.DMatrix(xtest,label=ytest)
    param={
        'max_depth':6,
        'eta': 0.3,
        'verbosity': 0,
        'objective': 'multi:softprob',
        'num_class': 1,
        'tree_method': 'auto'
    }
    param=get_args_dict(param,kargs)
    num_round=get_args('num_round',100,kargs)
    early_stopping_rounds=get_args('early_stopping_rounds',20,kargs)
    dump_model=get_args('dump_model','xgb_model.txt',kargs)
    bst = xgb.train(param,dtrain,num_boost_round=num_round,early_stopping_rounds=early_stopping_rounds,evals=[(dtest,"Test")],verbose_eval=False)
    bst.dump_model(dump_model)
    preds=bst.predict(dtest)
    best_preds=np.asarray([np.argmax(line) for line in preds])
    return precision_score(ytest, best_preds, average='macro')
def keras_method(xtrain,xtest,ytrain,ytest,kargs):
    inshape=get_args('inshape',xtrain.shape[1],kargs)
    layer_num1=get_args('layer_num1',256,kargs)
    layer_num2=get_args('layer_num2',512,kargs)
    epochs=get_args('epochs',100,kargs)
    verbose=get_args('verbose',0,kargs)
    train_type=get_args('train_type','multiclass',kargs)
    if train_type=='regression':
        outshape=get_args('outshape',len(set(ytrain)),kargs)
    elif train_type=='multiclass':
        outshape=get_args('outshape',0,kargs)
    batch_size=get_args('batch_size',100,kargs)
    model=Sequential()
    model.add(Dense(layer_num1,input_dim=inshape,activation='relu'))
    model.add(Dense(layer_num2,activation='relu'))
    if train_type=='multiclass':
        model.add(Dense(outshape,activation='softmax'))
        model.compile(optimizer='sgd',loss='categorical_crossentropy',metrics=['accuracy'])
    elif train_type=='regression':
        model.add(Dense(1))
        model.compile(optimizer='sgd',loss='mae',metrics=['mae','mean_absolute_percentage_error','mean_squared_logarithmic_error'])
    es=EarlyStopping(monitor='accuracy',patience=50,verbose=0,mode='max')
    model.fit(xtrain,ytrain,epochs=epochs,batch_size=batch_size,validation_split=0.1,shuffle=True,verbose=verbose,callbacks=[es],use_multiprocessing=True)
    preds=model.predict(xtest)
    if train_type=='multiclass':
        preds_=np.argmax(preds,axis=1)
        real_=np.argmax(ytest,axis=1)
        accuracy=np.mean(preds_==real_)
    elif train_type=='regression':
        accuracy=np.mean(np.abs(preds-ytest))
    return accuracy
# abstract function
def run_method(X,Y,preprocessor,splitor,training_method,kargs):
    if preprocessor!=None:
        x,y=preprocessor(X,Y)
    else:
        x,y=X,Y
    if training_method==keras_method and kargs['train_type']=='multiclass':
        y=to_categorical(y)
    t1=time.time()
    acc=0
    i=0
    for train_index,test_index in splitor.split(x):
        xtrain,xtest=x[train_index],x[test_index]
        ytrain,ytest=y[train_index],y[test_index]
        acc_=training_method(xtrain,xtest,ytrain,ytest,kargs)
        acc+=acc_
        i+=1
        break
    acc/=i
    t2=time.time()
    print('{} takes {} s, acc {}'.format(training_method.__name__,t2-t1,acc))
    return acc,t2-t1
def shuffle_data(X,Y):
    rng = np.random.default_rng(seed=0)
    indices=np.arange(X.shape[0])
    rng.shuffle(indices)
    return X[indices], Y[indices]
def exp2(X,Y):
    n_sample=X.shape[0]
    n_feature=X.shape[1]
    sendtime,recvtime=X[:,:,0],X[:,:,1]
    link,load=Y[:,0],Y[:,1]
    y=rescale(load)
    n_outshape=len(set(y))
    kfold_splitor=KFold(n_splits=10,shuffle=True,random_state=0)
    method_list=['logistic_regression','lightgbm','xgboost','keras_ann']
    methods={
        method_list[0]: logistic_regression,
        method_list[1]: lightgbm_method,
        method_list[2]: xgboost_method,
        method_list[3]: keras_method
    }
    kargs={
        method_list[0]: {
            'random_state':0,
            'solver':'lbfgs',
            'max_iter': 100,
            'multi_class':'multinomial',
            'verbose': 0,
            'penalty': 'none',
            'n_jobs':-1
        },
        method_list[1]: {
            'boosting_type': 'gbdt',
            'objective': 'multiclass',
            'metric': 'multi_logloss',
            'num_class': n_outshape,
            'num_leaves': 15,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.9,
            'bagging_freq': 1,
            'verbose': -1,
            'num_boost_round': 100,
            'early_stopping_rounds': 10
        },
        method_list[2]: {
            'max_depth':6,
            'eta':0.3,
            'verbosity':0,
            'objective':'multi:softprob',
            'num_class':n_outshape,
            'dump_model':'dump_model.txt',
            'num_round':100,
            'early_stopping_rounds':10,
            'tree_method':'auto'
        },
        method_list[3]: {
            'outshape':n_outshape,
            'layer_num1':128,
            'layer_num2':256,
            'epochs':400,
            'batch_size':64,
            'train_type':'multiclass',
            'verbose':1
        }
    }
    #use sendtime,recvtime,link
    acc_row=[]
    time_row=[]
    x=np.zeros((n_sample,n_feature*2+1))
    x[:,:n_feature]=sendtime
    x[:,n_feature:2*n_feature]=recvtime
    x[:,-1]=link
    for method_name in method_list:
        acc,t=run_method(x,y,standard_preprocessor,kfold_splitor,methods[method_name],kargs[method_name])
        acc_row.append(acc)
        time_row.append(t)
    for i in range(len(method_list)):
        print('method {} use {} seconds, acc {}'.format(method_list[i],time_row[i],acc_row[i]))


if __name__=='__main__':
    X,Y=read_raw_data(EXPERIMENT_COUNT)
    dX=get_diff_data(X)
    dX,Y=shuffle_data(dX,Y)
    exp2(dX,Y)
    #code.interact(local=dict(globals(),**locals()))