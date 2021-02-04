#### 配置华为s5731交换机的命令
查看活动的接口IP
```
display interface brief
display ip interface brief
```
XGigabitEthernet0/0/1
XGigabitEthernet0/0/2
XGigabitEthernet0/0/4

设置接口的IP地址
#### sw1
```
system-view
# 10Gbps
interface XGigabitEthernet0/0/1
undo portswitch
ip address 10.0.3.1 24
# 1Gbps
interface GigabitEthernet0/0/1
undo portswitch
ip address 10.0.3.1 24
# other
interface XGigabitEthernet0/0/2
undo portswitch
ip address 10.0.2.2 24
interface XGigabitEthernet0/0/4
undo portswitch
ip address 10.0.1.2 24
```
#### sw2
```
system-view
# 1Gbps
interface GigabitEthernet0/0/2
undo portswitch
ip address 10.0.3.2 24
# 10Gbps
interface XGigabitEthernet0/0/1
undo portswitch
ip address 10.0.3.2 24
# 
interface XGigabitEthernet0/0/2
undo portswitch
ip address 10.0.4.2 24
# 10Gbps 5.1
interface XGigabitEthernet0/0/4
undo portswitch
ip address 10.0.5.1 24
# 1Gbps 5.1
interface GigabitEthernet0/0/1
undo portswitch
ip address 10.0.5.1 24
```
#### sw3
```
system-view
interface XGigabitEthernet0/0/1
undo portswitch
ip address 10.0.5.2 24
interface XGigabitEthernet0/0/2
undo portswitch
ip address 10.0.6.2 24
interface XGigabitEthernet0/0/4
undo portswitch
ip address 10.0.7.2 24
```
设置路由表
```
display ip routing-table
system-view
# sw1
ip route-static 10.0.4.0 24 10.0.3.2
ip route-static 10.0.5.0 24 10.0.3.2
ip route-static 10.0.6.0 24 10.0.3.2
ip route-static 10.0.7.0 24 10.0.3.2
# sw2
ip route-static 10.0.1.0 24 10.0.3.1
ip route-static 10.0.2.0 24 10.0.3.1
ip route-static 10.0.6.0 24 10.0.5.2
ip route-static 10.0.7.0 24 10.0.5.2
# sw3
ip route-static 10.0.1.0 24 10.0.5.1
ip route-static 10.0.2.0 24 10.0.5.1
ip route-static 10.0.3.0 24 10.0.5.1
ip route-static 10.0.4.0 24 10.0.5.1
```
修改接口的速率
```
#查看接口速率
display interface XGigabitEthernet0/0/4
display this interface
#手动速率
system-view
interface XGigabitEthernet0/0/4
undo negotiation auto
speed { 10 | 100 | 1000 | 2500 | 5000 | 10000 }
#查看型号
display elabel
S5731-S48T4X
```
https://support.huawei.com/hedex/hdx.do?docid=EDOC1100126532&tocURL=resources/dc/S5731-S48P4X.html
#### 
sw1 的 XGigabitEthernet0/0/1 是3.1
sw2 的 XGigabitEthernet0/0/1 是3.2
光口电口不混用