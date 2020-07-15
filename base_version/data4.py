#utf-8
"""
    exp4
    * 为了减少训练时间，不作十折交叉验证
    * 减少可变参数
    * 使用naive bayes
    
"""
import os,time,code,logging,random,json
def set_tf_loglevel(level):
    if level >= logging.FATAL:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    if level >= logging.ERROR:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    if level >= logging.WARNING:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
    else:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'
    logging.getLogger('tensorflow').setLevel(level)
set_tf_loglevel(logging.FATAL)
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import CategoricalNB
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from keras import losses
from keras.models import Sequential
from keras.layers import Dropout
from keras.layers import Dense, Activation
from keras.utils.np_utils import to_categorical
from keras import backend as K
import lightgbm as lgb
import xgboost as xgb
import tensorflow as tf

CONST_PRECISION_DELTA=0.5

def line2floats(line):
    return np.array([np.float64(i) for i in line.split(',')])
def lines2floatsmatrix(lines):
    return np.array([line2floats(line) for line in lines])
def get_files(exp):
    ret=[]
    for filename in os.listdir('data'):
        if 'exp4testonload' in filename: continue
        experiment_count=int(filename[filename.find('exp')+3:-4])
        if experiment_count!=exp:
            continue
        link=int(filename[4:filename.find('load')])
        load=int(filename[filename.find('load')+4:filename.find('exp')])
        v=[filename,link,load]
        ret.append(v)
    return ret
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
def read_data(file_list):
    x,y=[],[]
    for item in file_list:
        file_path='data/{}'.format(item[0])
        link,load=item[1],item[2]
        data=read_file(file_path)
        x.append(data)
        y.append(load)
    n_sample,n_feature=x[0].shape
    n_class=len(x)
    x=np.array(x).reshape((-1,n_feature))
    y=np.repeat(np.array(y),n_sample)
    return x,y
def shuffle_data(x,y,seed=0):
    rng=np.random.default_rng(seed=seed)
    indices=np.arange(x.shape[0])
    rng.shuffle(indices)
    return x[indices],y[indices]
def run_method(name,param,measurement):
    t1=time.time()
    method=param['method']
    kargs=param['kargs']
    data=param['data']
    preds=method(data,kargs)
    ytest=data[3]
    ret=measurement(preds,ytest)
    t2=time.time()
    indices=np.abs(preds-ytest)>0.5
    verbose=np.concatenate((preds[indices],ytest[indices])).reshape((2,-1))
    verbose=np.transpose(verbose,axes=(1,0))
    np.savetxt('temp/{}.txt'.format(name),verbose,fmt='%6.2f',header='{:6s} {:6s}'.format('pred', 'ytest'))
    return ret,t2-t1
def get_args(key,value,kargs):
    if kargs:
        return kargs[key] if key in kargs else value
    else:
        return value
def get_args_dict(params:dict,kargs):
    ret={} if kargs==None else kargs.copy()
    for key in params.keys():
        if not key in ret:
            ret[key]=params[key]
    return ret
#pred-real<=d
def precision_acc(pred,real,d=CONST_PRECISION_DELTA):
    return np.mean(np.abs(pred-real)<=d)
def lightgbm_method(data,kargs):
    xtrain,xtest,ytrain,ytest=data
    lgb_train=lgb.Dataset(xtrain,ytrain)
    lgb_eval=lgb.Dataset(xtest,ytest,reference=lgb_train)
    num_boost_round=get_args('num_boost_round',5000,kargs)
    early_stopping_rounds=get_args('early_stopping_rounds',500,kargs)
    kargs.pop('num_boost_round')
    kargs.pop('early_stopping_rounds')
    gbm=lgb.train(kargs,lgb_train,num_boost_round=num_boost_round,valid_sets=lgb_eval,early_stopping_rounds=early_stopping_rounds,verbose_eval=False)
    preds=gbm.predict(xtest,num_iteration=gbm.best_iteration)
    return preds
def xgboost_method(data,kargs):
    xtrain,xtest,ytrain,ytest=data
    dtrain,dtest=xgb.DMatrix(xtrain,label=ytrain),xgb.DMatrix(xtest,label=ytest)
    num_round=get_args('num_round',100,kargs)
    early_stopping_rounds=get_args('early_stopping_rounds',20,kargs)
    kargs.pop('num_round')
    kargs.pop('early_stopping_rounds')
    bst=xgb.train(kargs,dtrain,num_boost_round=num_round,early_stopping_rounds=early_stopping_rounds,evals=[(dtest,"Test")],verbose_eval=False)
    if kargs['dump_model']:
        bst.dump_model(kargs['dump_model'])
    preds=bst.predict(dtest)
    return preds
def keras_method(data,kargs):
    xtrain,xtest,ytrain,ytest=data
    inshape=kargs['inshape']
    layer_num1=kargs['layer_num1']
    layer_num2=kargs['layer_num2']
    epochs=kargs['epochs']
    verbose=kargs['verbose']
    batch_size=kargs['batch_size']
    model=Sequential()
    model.add(Dense(layer_num1,input_dim=inshape,activation='selu'))
    model.add(Dense(layer_num2,activation='selu'))
    model.add(Dense(1))
    opt=tf.keras.optimizers.SGD(learning_rate=0.3)
    model.compile(optimizer=opt,loss=losses.mean_squared_logarithmic_error)
    model.fit(xtrain,ytrain,epochs=epochs,batch_size=batch_size,shuffle=True,verbose=verbose,use_multiprocessing=True)
    preds=model.predict(xtest)
    preds=preds.flatten()
    return preds
def measurement_fun(preds,ytest):
    ret=[]
    for d in [0.5,1,2,5]:
        acc=precision_acc(preds,ytest,d)
        ret.append(acc)
    diff=np.abs(preds-ytest)
    mae=np.mean(np.abs(preds-ytest))
    rmse=np.sqrt(mean_squared_error(preds,ytest))
    ret.extend([mae,rmse])
    return ret
def evaluate_different_method(x,y):
    x=StandardScaler().fit_transform(x)
    data=train_test_split(x,y,test_size=0.1,random_state=0)
    n_outshape=len(set(y))
    n_inshape=x.shape[1]
    method_list={
        'Lightgbm':{
            'method':lightgbm_method,
            'data':data,
            'kargs':{
                'boosting_type': 'gbdt',
                'objective': 'l2',
                'metric': 'l2',
                'num_leaves': 31,
                'learning_rate': 0.14,
                'feature_fraction': 1,
                'bagging_fraction': 1,
                'bagging_freq': 5,
                'verbose': -1,
                'num_boost_round':1000,
                'early_stopping_rounds':500
            }
        },
        'Xgboost':{
            'method':xgboost_method,
            'data':data,
            'kargs':{
                'max_depth':6,
                'eta':0.06,
                'verbosity':0,
                'objective':'reg:squarederror',
                'num_round':1000,
                'early_stopping_rounds':500,
                'tree_method':'auto',
                'eval_metric':'rmse',
                'dump_model':None
            }
        },
        'ANN':{
            'method':keras_method,
            'data':data,
            'kargs':{
                'inshape':n_inshape,
                'layer_num1':256,
                'layer_num2':512,
                'epochs':1000,
                'batch_size':64,
                'verbose':0
            }
        }
    }
    record_list=[]
    for k,v in method_list.items():
        ret,t=run_method(k,v,measurement_fun)
        record_list.append([k,ret,t])
    for item in record_list:
        print('{} {} {}'.format(item[0],item[1],item[2]))

def get_all_models(x,y):
    models=[]
    #lightgbm
    t1=time.time()
    lgb_train=lgb.Dataset(x,y)
    kargs={
        'boosting_type': 'gbdt',
        'objective': 'l2',
        'metric': 'l2',
        'num_leaves': 31,
        'learning_rate': 0.14,
        'feature_fraction': 1,
        'bagging_fraction': 1,
        'bagging_freq': 5,
        'verbose': -1,
    }
    num_boost_round=1000
    gbm=lgb.train(kargs,lgb_train,num_boost_round=num_boost_round)
    dic=gbm.dump_model()
    with open('temp/model_lightgbm.json','w') as f:
        f.write(json.dumps(dic))
    models.append(gbm)
    t2=time.time()
    print('lightgbm train use {} s'.format(t2-t1))
    #xgboost
    t1=time.time()
    dtrain=xgb.DMatrix(x,label=y)
    kargs={
        'max_depth':6,
        'eta':0.06,
        'verbosity':0,
        'objective':'reg:squarederror',
        'num_round':1000,
        'tree_method':'auto',
        'eval_metric':'rmse'
    }
    num_round=1000
    bst=xgb.train(kargs,dtrain,num_boost_round=num_round)
    bst.dump_model('temp/model_xgboost.txt',dump_format='text')
    models.append(bst)
    t2=time.time()
    print('xgboost train use {} s'.format(t2-t1))
    #ann
    t1=time.time()
    inshape=x.shape[1]
    layer_num1=256
    layer_num2=512
    epochs=1000
    verbose=0
    batch_size=64
    model=Sequential()
    model.add(Dense(layer_num1,input_dim=inshape,activation='selu'))
    model.add(Dense(layer_num2,activation='selu'))
    model.add(Dense(1))
    opt=tf.keras.optimizers.SGD(learning_rate=0.3)
    model.compile(optimizer=opt,loss=losses.mean_squared_logarithmic_error)
    model.fit(x,y,epochs=epochs,batch_size=batch_size,verbose=verbose,use_multiprocessing=True)
    models.append(model)
    t2=time.time()
    print('ann train use {} s'.format(t2-t1))
    names=['lightgbm','xgboost','ann']
    return models,names

def filename_key(e):
    magicstr='exp4testonload'
    start=len(magicstr)
    end=e.find('.txt')
    loadstr=e[start:end]
    return float(loadstr)
def get_validation_data():
    #exp4testonload1.2.txt
    magicstr='exp4testonload'
    start=len(magicstr)
    x,y=[],[]
    filelist=[]
    for filename in os.listdir('data'):
        if magicstr in filename:
            filelist.append(filename)
    filelist.sort(key=filename_key)
    for filename in filelist:
        end=filename.find('.txt')
        loadstr=filename[start:end]
        load=np.float32(loadstr)
        data=read_file('data/{}'.format(filename))
        x.append(data)
        y.append(load)
    n_feature=x[0].shape[1]
    x=np.array(x).reshape((-1,n_feature))
    y=np.array(y)
    return x,y

def validate(x,y):
    t1=time.time()
    standardScaler=StandardScaler()
    standardScaler.fit(x)
    x=standardScaler.transform(x)
    models,names=get_all_models(x,y)
    xtest,ytest_set=get_validation_data()
    xtest=standardScaler.transform(xtest)
    dtest=xgb.DMatrix(xtest)
    preds=[model.predict(xtest).flatten() if i!=1 else model.predict(dtest) for i,model in enumerate(models)]
    preds_set=[np.mean(pred.reshape((-1,3)),axis=1) for pred in preds]
    ytest=np.repeat(ytest_set,3)
    performances=[measurement_fun(pred,ytest) for pred in preds]
    performances_set=[measurement_fun(pred_set,ytest_set) for pred_set in preds_set]
    verboses=[np.concatenate((pred.reshape((-1,1)),ytest.reshape((-1,1))),axis=1) for pred in preds]
    verboses_set=[np.concatenate((pred_set.reshape((-1,1)),ytest_set.reshape((-1,1))),axis=1) for pred_set in preds_set]
    for i,name in enumerate(names):
        verbose,verbose_set=verboses[i],verboses_set[i]
        np.savetxt('temp/performance_{}.txt'.format(name),verbose,fmt='%6.2f',header='{:6s} {:6s}'.format('pred', 'ytest'))
        np.savetxt('temp/performance_{}_set.txt'.format(name),verbose_set,fmt='%6.2f',header='{:6s} {:6s}'.format('pred', 'ytest'))
        print('{} not set {}\n{} use set {}'.format(name,performances[i],name,performances_set[i]))
    t2=time.time()
    print('total {} s'.format(t2-t1))

def linear_validate(x,y):
    index=1
    max_time=np.mean(x[y==90,index])
    min_time=np.mean(x[y==0,index])
    def predict(e):
        total_time=e[:,index]
        return (total_time-min_time)/(max_time-min_time)*(90-0)+0
    pred=predict(x)
    ret=measurement_fun(pred,y)
    print('拟合原数据集 {}'.format(ret))
    xtest,ytest_set=get_validation_data()
    ytest=np.repeat(ytest_set,3)
    pred=predict(xtest)
    ret=measurement_fun(pred,ytest)
    print('测试集 {}'.format(ret))
    pred_set=np.mean(pred.reshape((-1,3)), axis=1)
    ret=measurement_fun(pred_set,ytest_set)
    print('测试集(组) {}'.format(ret))
    #code.interact(local=dict(globals(),**locals()))
if __name__=='__main__':
    t1=time.time()
    file_list=get_files(4)
    x,y=read_data(file_list)
    x,y=shuffle_data(x,y)
    t2=time.time()
    print('prepare data use {} s'.format(t2-t1))
    #evaluate_different_method(x,y)
    #validate(x,y)
    linear_validate(x,y)