# suggestion model

the old parameter: send rate, load number, inspect number, inspect gap

the original data stream: time series

metrics:

significance: owd max - owd min
recovery degree: (owd.max-owd.last)/(owd.max-owd.min)
increase rate: owd.delta/load gap
decrease rate: owd.delta/inspect gap
total measurement time:
total packet byte:

1. recovery degree 100%
2. decrease rate high
3. inspect gap low

the new parameter: send rate, load number, inspect number, inspect gap

restriction: max send rate, max load number, max inspect number

action: 

offline learning

online learning

state: 