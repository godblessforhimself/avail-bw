import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import code
#将xgboost于实验78的结果画图
def get_xgboost_data(df,colname):
    arr=df[[colname]][df8['method']=='xgboost'].values
    arr=arr.reshape((-1,2))
    single,set=arr[:,0],arr[:,1]
    return (single,set)
df7,df8=pd.read_csv('temp/data7result.csv'),pd.read_csv('temp/data8result.csv')
single7,set7=get_xgboost_data(df7,'d=0.5')
single8,set8=get_xgboost_data(df8,'d=0.5')
x=np.arange(1500,9001,1500)
plt.figure(figsize=(10,10))
plt.plot(x,single7,label='100Mbps_single')
plt.plot(x,set7,label='100Mbps_set')
plt.plot(x,single8,label='1000Mbps_single')
plt.plot(x,set8,label='1000Mbps_set')
plt.legend()
plt.grid()
plt.xticks(np.arange(1500,9001,1500))
plt.yticks(np.arange(0,1,0.04))
plt.title('探测包大小对xgboost准确率的影响(d=0.5)', y=-0.1)
plt.savefig('temp/packetsize.png',bbox_inches='tight')
