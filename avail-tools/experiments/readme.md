part 1: illustrate the precision of software traffic generator
tool: iperf3 bqr
target rate: 10Mbps, 100Mbps, 1000Mbps
repeat,point: 10, 100
no cross traffic, no interrupt coalescing
show: histogram with MSE
conclusion: precision decreases at higher rate, but acceptable

part 2: the influence of CS and interrupt coalescing on constant rate train
tool: bqr
target rate: 10Mbps, 100Mbps, 500Mbps, 1000Mbps
repeat,point: 10, 100
interrupt coalescing: off, on
show: histogram with MSE
show: send, recv(ic off), recv(ic on)
deep analysis
conclusion: there is pattern, IC adds error, we can reduce noise

part 3: Spruce like method
tool: Spruce
target rate: 10Mbps, 100Mbps, 500Mbps, 1000Mbps
repeat, point: 10, 100
interrupt coalescing: off, on
show: histogram with MSE
show: send, recv(ic off), recv(ic on)
deep analysis
conclusion: pattern, IC adds, hard to reduce

part 4: one hop comparison

part 5: three hop comparison