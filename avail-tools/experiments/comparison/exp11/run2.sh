source experiments/comparison/exp11/common.sh
# tcpreplay大约90秒+10秒
# bqr测量110秒
runWithParam test3 120 125 1200 bigFlows 100 10 200 10 300 10 400 10 500 10 600 10 700 10 800 10
runWithParam test4 120 125 1200 caida    100 10 200 10 300 10 400 10 500 10 600 10 700 10 800 10