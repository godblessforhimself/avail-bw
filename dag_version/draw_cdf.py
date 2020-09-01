import matplotlib.pyplot as plt
import numpy as np
import time
from scapy.all import *
in_traffic_filename='data/exp2/in.pcap'
out_traffic_filename='data/exp2/out.pcap'
def cdf(x, plot=True, *args, **kwargs):
    x, y = sorted(x), np.arange(len(x)) / len(x)
    return plt.plot(x, y, *args, **kwargs) if plot else (x, y)
def get_dtime(timestamp, scale):
    return (timestamp[1:]-timestamp[:-1])*scale
def intercept(x1,y1,x2,y2,y):
    # return x value where line cross (x1,y1) (x2,y2) intercept y
    return x1+(x2-x1)*(y-y1)/(y2-y1)
begin=time.time()
in_pkts=rdpcap(in_traffic_filename)
out_pkts=rdpcap(out_traffic_filename)
in_timestamps=np.array([np.float64(p.time) for p in in_pkts])
out_timestamps=np.array([np.float64(p.time) for p in out_pkts])
end=time.time()
print('use {} seconds'.format(end-begin))
scale=1e6
din=get_dtime(in_timestamps,scale)
dout=get_dtime(out_timestamps,scale)
delay=(out_timestamps-in_timestamps)*scale
plt.figure(figsize=(10,10))
ax1=plt.subplot(311)
ax1.title.set_text("in")
cdf(din,True)
#plt.xlim([0,16])
#ax1.set_xticks(np.arange(0,17,1))

ax2=plt.subplot(312)
ax2.title.set_text("out")
#plt.xlim([0,16])
#ax2.set_xticks(np.arange(0,17,1))
cdf(dout,True)

ax3=plt.subplot(313)
ax3.title.set_text("delay")
cdf(delay,True)
#plt.xlim([4.9,6.3])
#ax3.set_xticks(np.arange(4.9,6.4,0.1))
plt.show()
#10Gbps网卡，以1000Mbps的速率发包，1000个包的999个间隔cdf不是很均匀
expected=1472*8/1000
actual=(np.mean(din),np.mean(dout))
print('expect {:.4f} din {:.4f} dout {:.4f}'.format(expected,actual[0],actual[1]))